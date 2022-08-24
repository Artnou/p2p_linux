import socket
import sys
import threading
import re

from termcolor import colored

from Crypto.PublicKey import RSA
from Crypto import Random
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5

import os.path

PORT = 5555

# Relevant links: 
# https://gist.github.com/aellerton/2988ff93c7d84f3dbf5b9b5a09f38ceb 
# https://www.pythontutorial.net/python-basics/python-check-if-file-exists/ 
# https://www.w3schools.com/python/ref_func_open.asp

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
    pbk = RSA.importKey(pbk)

    digest = SHA256.new()
    digest.update(message.encode())

    return PKCS1_v1_5.new(pbk).verify(digest, signature)


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
            p_ip, p_key = peer.split('-')
            print(colored('Ip: {}\n{}\n'.format(p_ip, p_key), 'green'))
    elif n == 2:
        print(colored('peers list:', 'white', 'on_cyan'))

        for peer in peers:
            p_ip, p_key = peer.split('-')
            print(colored('Ip: {}\n{}\n'.format(p_ip, p_key), 'cyan'))


with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind(('0.0.0.0', PORT))

    connect_ip = ''
    send_ip = '0.0.0.0'

    while not re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])$", connect_ip) and not connect_ip == 'self':
        connect_ip = input('Connect to: ')

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

        while True:
            data, addr = s.recvfrom(4096)
            data = data.decode()
            recv_ip, recv_port = addr

            if recv_ip not in peers:
                peers.append(recv_ip + '#' + data)

                # peers ok

                s.sendto(pbl_key.encode(), (recv_ip, PORT))

                for peer in peers:
                    print('\nPEER {}'.format(peers.index(peer)))
                    print(peer)

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

                    for peer in peers:
                        p_ip, p_key = peer.split('#')
                        p_key = RSA.importKey(p_key)

                        if verify_message(message, signature, pbl_key):
                            print(colored('Message signature corresponds to ip {}'.format(p_ip), 'yellow'))
                            v = True

                            if p_ip != recv_ip:
                                print(colored('Warning: The ip address of the sender differs to the ip address registered to its public key', 'red'))

                            break
                    
                    if not v:
                        print(colored("Warning: Signature can't be verified with registered public keys", 'red'))

                    if send_ip == '0.0.0.0':
                        print('\r{} --> You: {}\nSend to: '.format(recv_ip, data), end='')
                    else:
                        print('\r{} --> You: {}\nYou --> {}: '.format(recv_ip, data, send_ip), end='')

    listener = threading.Thread(target=listen, daemon=True)
    listener.start()

    def exit_command():
        peers.remove(IP + '#' + pbl_key)

        for peer in peers:
            s.sendto(get_peers_string().encode(), (peer, PORT))

        sys.exit()

    while True:
        while send_ip not in peers or not re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])$", send_ip):
            send_ip = input('Send to: ')

            if send_ip == '/exit':
                exit_command()
            elif send_ip == '/peers':
                print(colored('peers list:', 'white', 'on_cyan'))

                for peer in peers:
                    print(peer)
            elif send_ip not in peers or not re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])$", send_ip):
                print(colored('error: ip adress invalid or not in peers', 'white', 'on_red'))

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
                sign = get_signature(msg, prv_key)
                ms = msg + '###' + sign

                s.sendto(ms.encode(), (send_ip, PORT))
