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

def check_keys_existence():
    return os.path.exists('PrivateKey.txt') and not os.path.exists('PublicKey.txt')

def check_peers_keys_existence():
    return os.path.exists('PeersKeys.txt')

def generate_keys():
    pvk = RSA.generate(1024, Random.new().read())
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

def sign_message(message, pvk):
    d = SHA256.new()
    d.update(message.encode())

    return PKCS1_v1_5.new(pvk).sign(d)

def verify_message(message, signature, pbk):
    return PKCS1_v1_5.new(pbk).verify(message, signature)


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

s = IP + '-' + pbl_key

peers = []
peers.append(s)

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
        # peers.append(connect_ip)

    def get_peers_string():
        peers_str = ''

        for peer in peers:
            if peers.index(peer) == 0:
                peers_str = peer
            else:
                peers_str = peers_str + ' ' + peer

        return peers_str

    def listen():
        global peers

        while True:
            data, addr = s.recvfrom(1024)
            data = data.decode()
            recv_ip, recv_port = addr

            if recv_ip not in peers:
                peers.append(recv_ip + '-' + data)

                for peer in peers:
                    p_ip, p_key = peer.split('-')
                    s.sendto(get_peers_string().encode(), (peer, PORT))

            else:
                tmp = data.split(' ')

                if re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])+\-", tmp[0]):
                    peers = data.split(' ')

                    print(colored('\rpeers list has been updated!', 'white', 'on_green'))
                    print(colored('New peers list:', 'green'))

                    for peer in peers:
                        p_ip, p_key = peer.split('-')
                        print(colored('Ip: {}; Public Key: {}'.format(p_ip, p_key), 'green'))

                    if send_ip == '0.0.0.0':
                        print('\rSend to: ', end='')
                    else:
                        print('\rYou --> {}: '.format(send_ip), end='')
                else:
                    if send_ip == '0.0.0.0':
                        print('\r{} --> You: {}\nSend to: '.format(recv_ip, data), end='')
                    else:
                        print('\r{} --> You: {}\nYou --> {}: '.format(recv_ip, data, send_ip), end='')

    listener = threading.Thread(target=listen, daemon=True)
    listener.start()

    def exit_command():
        peers.remove(IP)

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
                print(colored('peers list:', 'white', 'on_cyan'))

                for peer in peers:
                    print(peer)
            else:
                s.sendto(msg.encode(), (send_ip, PORT))
