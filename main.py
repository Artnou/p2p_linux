import socket
import sys
import threading
from termcolor import colored
import re

PORT = 5555

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close

print('User ip: {}'.format(IP))

peers = []
peers.append(IP)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind(('0.0.0.0', PORT))

    connect_ip = ''
    send_ip = '0.0.0.0'

    while not re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])$", connect_ip) and not connect_ip == 'self':
        connect_ip = input('Connect to: ')

        if not re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])$", connect_ip) and not connect_ip == 'self':
            print(colored('error: invalid ip address', 'white', 'on_red'))

    if connect_ip == 'self':
        print('Network created')
    else:
        s.sendto('0'.encode(), (connect_ip, PORT))
        print('Ip sent')
        peers.append(connect_ip)

    def listen():
        global peers

        while True:
            data, addr = s.recvfrom(1024)
            data = data.decode()
            recv_ip, recv_port = addr

            if recv_ip not in peers:
                peers.append(recv_ip)
                peer_string = ''

                for peer in peers:
                    if peers.index(peer) == 0:
                        peer_string = peer
                    else:
                        peer_string = peer_string + ' ' + peer

                for peer in peers:
                    s.sendto(peer_string.encode(), (peer, PORT))

            else:
                tmp = data.split(' ')

                if re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])$", tmp[0]):
                    peers = data.split(' ')

                    print(colored('\rpeers list has been updated!', 'white', 'on_green'))
                    print('New peers list:')

                    for peer in peers:
                        print(peer)

                    if send_ip == '0.0.0.0':
                        print('\rSend to: ', end='')
                    else:
                        print('\rYou --> {}'.format(send_ip), end='')
                else:
                    if send_ip == '0.0.0.0':
                        print('\r{} --> You: {}\nSend to: '.format(recv_ip, data), end='')
                    else:
                        print('\r{} --> You: {}\nYou --> {}: '.format(recv_ip, data, send_ip), end='')

    listener = threading.Thread(target=listen, daemon=True)
    listener.start()

    while True:
        while send_ip not in peers:
            send_ip = input('Send to: ')

            if send_ip == '/exit':
                sys.exit()
            elif send_ip == '/peers':
                print(colored('peers list:', 'white', 'on_cyan'))

                for peer in peers:
                    print(peer)
            else:
                print(colored('error: ip adress invalid or not in peers', 'white', 'on_red'))

        while True:
            msg = input('You --> {}: '.format(send_ip))

            if msg == '/change':
                send_ip = '0.0.0.0'
                break
            elif msg == '/exit':
                sys.exit()
            elif msg == '/peers':
                print(colored('peers list:', 'white', 'on_cyan'))

                for peer in peers:
                    print(peer)
            else:
                s.sendto(msg.encode(), (send_ip, PORT))
