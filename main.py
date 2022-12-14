import socket
import sys
import threading
import re
import os.path

from termcolor import colored

from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Util import number

from base64 import b64encode
from base64 import b64decode

PORT = 5555

# Relevant links: 
# https://gist.github.com/aellerton/2988ff93c7d84f3dbf5b9b5a09f38ceb 
# https://www.pythontutorial.net/python-basics/python-check-if-file-exists/ 
# https://www.w3schools.com/python/ref_func_open.asp
# https://github.com/pycrypto/pycrypto/issues/233

def check_keys_existence():
    return os.path.exists('PrivateKey.txt') and not os.path.exists('PublicKey.txt')

def check_peers_keys_existence():
    return os.path.exists('PeersKeys.txt')

def generate_keys():
    pvk = RSA.generate(1024, Random.new().read)
    pbk = pvk.publickey()

    exp_pvk = pvk.exportKey('PEM')
    f = open('PrivateKey.txt', 'w')
    f.write(exp_pvk.decode('UTF-8'))
    f.close()

    exp_pbk = pbk.exportKey('PEM')
    f = open('PublicKey.txt', 'w')
    f.write(exp_pbk.decode('UTF-8'))
    f.close()

def get_personnal_keys():
    pvk = open('PrivateKey.txt', 'r').read()
    pbk = open('PublicKey.txt', 'r').read()

    return pvk, pbk

def get_signature(message, pvk):
    pvk = RSA.importKey(pvk)

    digest = SHA256.new()
    digest.update(message.encode())

    return PKCS1_v1_5.new(pvk).sign(digest)

def verify_message(message, signature, pbk):
    digest = SHA256.new()
    digest.update(message.encode())

    return PKCS1_v1_5.new(pbk).verify(digest, signature)

def encrypt_message(message, pbk):
    pbk = RSA.importKey(pbk)
    cipher = PKCS1_OAEP.new(pbk)

    SIZE_in_Bits = number.size(cipher._key.n)
    block = number.ceil_div(SIZE_in_Bits, 8)

    Hash_Digest_Size = cipher._hashObj.digest_size
    length = block - 2 * Hash_Digest_Size
    result_Digest = []

    for index in range(0, len(message), length):
        result_Digest.append(cipher.encrypt(message[index : index + length]))

    return b"".join(result_Digest)
    
def decrypt_message(message, pvk):
    pvk = RSA.importKey(pvk)
    cipher = PKCS1_OAEP.new(pvk)

    length = pvk.size_in_bytes() # if doesn't work, change to 256
    resultant_Text = []

    for index in range(0, len(message), length):
        decrypted_block = cipher.decrypt(message[index : index + length])
        resultant_Text.append(decrypted_block)

    return b"".join(resultant_Text)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close

print('User ip: {}'.format(IP))

if not check_keys_existence():
    generate_keys()

prv_key, pbl_key = get_personnal_keys()

s = IP + '#' + pbl_key

peers = []
peers.append(s)

def print_peers(n):
    if n == 1:
        print(colored('\rpeers list has been updated!', 'white', 'on_green'))
        print(colored('New peers list:', 'green'))

        for peer in peers:
            p_ip, p_key = peer.split('#')
            print(colored('Ip: {}\n{}\n'.format(p_ip, p_key), 'green'))
    elif n == 2:
        print(colored('peers list:', 'white', 'on_cyan'))

        for peer in peers:
            p_ip, p_key = peer.split('#')
            print(colored('Ip: {}\n{}\n'.format(p_ip, p_key), 'cyan'))

def get_ip_list():
    ip_list = []

    for peer in peers:
        p_ip, p_key = peer.split('#')
        ip_list.append(p_ip)

    return ip_list

def get_key_by_ip(ip):
    for peer in peers:
        p_ip, p_key = peer.split('#')

        if p_ip == ip:
            return p_key

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind(('0.0.0.0', PORT))

    connect_ip = ''
    send_ip = '0.0.0.0'

    while not re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])$", connect_ip) and not connect_ip == 'self':
        connect_ip = input('Connect to: ')

        connect_ip = connect_ip.strip()

        if not re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])$", connect_ip) and not connect_ip == 'self':
            print(colored('error: invalid ip address', 'white', 'on_red'))

    if connect_ip == 'self':
        print(colored('Network created', 'white', 'on_yellow'))
    else:
        s.sendto(pbl_key.encode(), (connect_ip, PORT))
        print('Public key sent')
        d = s.recv(4096)
        d = d.decode()

        peers.append(connect_ip + '#' + d)
        
    def get_peers_string():
        peers_str = ''

        for peer in peers:
            if peers.index(peer) == 0:
                peers_str = peer
            else:
                peers_str = peers_str + '&&' + peer

        return peers_str

    def listen():
        global peers
        global ip_list

        while True:
            data, addr = s.recvfrom(4096)
            data = data.decode()
            recv_ip, recv_port = addr

            if recv_ip not in get_ip_list():
                peers.append(recv_ip + '#' + data)

                s.sendto(pbl_key.encode(), (recv_ip, PORT))

                for peer in peers:
                    p_ip, p_key = peer.split('#')
                    s.sendto(get_peers_string().encode(), (p_ip, PORT))

            else:
                tmp = data.split('&&')

                if re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])", tmp[0]):
                    peers = data.split('&&')

                    print_peers(1)

                    if send_ip == '0.0.0.0':
                        print('\rSend to: ', end='')
                    else:
                        print('\rYou --> {}: '.format(send_ip), end='')
                else:
                    message, signature = data.split('###')
                    v = False

                    signature = b64decode(signature.encode())

                    message = b64decode(message.encode())
                    message = decrypt_message(message, prv_key).decode()

                    for peer in peers:
                        p_ip, p_key = peer.split('#')
                        p_key = RSA.importKey(p_key)

                        if verify_message(message, signature, p_key):
                            print(colored('\rMessage signature corresponds to ip {}'.format(p_ip), 'yellow'))
                            v = True

                            if p_ip != recv_ip:
                                print(colored('\rWarning: The ip address of the sender differs to the ip address registered to its public key', 'red'))

                            break
                    
                    if not v:
                        print(colored("\rWarning: Signature can't be verified with registered public keys", 'red'))

                    if send_ip == '0.0.0.0':
                        print('\r{} --> You: {}\nSend to: '.format(recv_ip, message), end='')
                    else:
                        print('\r{} --> You: {}\nYou --> {}: '.format(recv_ip, message, send_ip), end='')

    listener = threading.Thread(target=listen, daemon=True)
    listener.start()

    def exit_command():
        peers.remove(IP + '#' + pbl_key)

        for peer in peers:
            p_ip, p_key = peer.split('#')
            s.sendto(get_peers_string().encode(), (p_ip, PORT))

        sys.exit()

    while True:
        while send_ip not in get_ip_list() or not re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])$", send_ip):
            send_ip = input('Send to: ')

            send_ip = send_ip.strip()

            if send_ip == '/exit':
                exit_command()
            elif send_ip == '/peers':
                print_peers(2)
            elif send_ip not in get_ip_list() or not re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])$", send_ip):
                print(colored('error: ip adress invalid or not in peers', 'white', 'on_red'))
                send_ip = '0.0.0.0'

        while True:
            msg = input('You --> {}: '.format(send_ip))

            if msg == '/change':
                send_ip = '0.0.0.0'
                break
            elif msg == '/exit':
                exit_command()
            elif msg == '/peers':
                print_peers(2)
            else:
                sign = b64encode(get_signature(msg, prv_key))

                e_msg = b64encode(encrypt_message(msg.encode(), get_key_by_ip(send_ip))).decode()

                ms = e_msg + '###' + sign.decode()

                s.sendto(ms.encode(), (send_ip, PORT))
