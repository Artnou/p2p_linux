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
                    print('\npeer: {}\nmessage: {}\n'.format(peer, peer_string))
                    s.sendto(peer_string.encode(), (peer, PORT))

            else:
                tmp = data.split(' ')

                if re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])$", tmp[0]):
                    peers = data.split(' ')

                    print(colored('peers list has been updated!', 'white', 'on_green'))
                    print('New peers list:')

                    for peer in peers:
                        print(peer)
                else:
                    if send_ip == '0.0.0.0':
                        print('\r{} --> You: {}\nSend to: '.format(recv_ip, data), end='')
                    else:
                        print('\r{} --> You: {}\nYou --> {}'.format(recv_ip, data, send_ip))

    listener = threading.Thread(target=listen, daemon=True)
    listener.start()

    while True:
        while True:
            send_ip = input('Send to: ')

            if send_ip == '/exit':
                sys.exit()

            if send_ip in peers:
                break
            else:
                print(colored('error: ip adress invalid or not in peers', 'white', 'on_red'))

        while True:
            msg = input('You --> {}: '.format(send_ip))

            if msg == '/change':
                send_ip = '0.0.0.0'
                break
            elif msg == '/exit':
                sys.exit()
            else:
                s.sendto(msg.encode(), (send_ip, PORT))

# Old peer-to-peer communication

#colors = ['red','green','yellow','cyan','magenta','blue']
#
#with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#    s.bind(('0.0.0.0', PORT))
#
#    send_ip = '0.0.0.0'
#
#    print(colored('-- Client launched --', 'grey', 'on_white'))
#
#    def listen():
#        while True:
#            data, addr = s.recvfrom(1024)
#            data = data.decode()
#            recv_ip, recv_port = addr
#
#            if recv_ip not in peers:
#                peers.append(recv_ip)
#
#            color = colors[peers.index(recv_ip)]
#
#            if send_ip == '0.0.0.0':
#                print(colored('\r{} --> You: '.format(recv_ip), color) + '{}\nSend to: '.format(data), end='')
#            else:
#                print(colored('\r{} --> You: '.format(recv_ip), color) + '{}\nYou --> {}: '.format(data, send_ip), end='')
#
#    listener = threading.Thread(target=listen, daemon=True)
#    listener.start()
#
#    while True:
#        while True:
#            send_ip = input('Send to: ')
#
#            if send_ip == '/exit':
#                sys.exit()
#
#            if re.match(r"192+\.+168+\.+5+\.+\b([01]?[0-9][0-9]?|2[0-4][0-9]|25[0-5])$", send_ip):
#                break
#            else:
#                print(colored('error: invalid ip address', 'white', 'on_red'))
#        
#        while True:
#            msg = input('You --> {}: '.format(send_ip))
#
#            if msg == '/change':
#                send_ip = '0.0.0.0'
#                break
#            elif msg == '/exit':
#                sys.exit()
#
#            s.sendto(msg.encode(), (send_ip, PORT))