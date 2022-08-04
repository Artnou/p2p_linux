import socket
import sys
import threading
from termcolor import colored

PORT = 5555

peers = []
colors = ['red','green','yellow','cyan','magenta','blue']

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind(('0.0.0.0', PORT))

    send_ip = '0.0.0.0'

    print(colored('-- Client launched --', 'grey', 'on_white'))

    def listen():
        while True:
            data, addr = s.recvfrom(1024)
            data = data.decode()
            recv_ip, recv_port = addr

            if recv_ip not in peers:
                peers.append(recv_ip)

            color = colors[peers.index(recv_ip)]

            if send_ip == '0.0.0.0':
                print(colored('\r{} --> You: '.format(recv_ip), color) + '{}\nSend to: '.format(data), end='')
            else:
                print(colored('\r{} --> You: '.format(recv_ip), color) + '{}\nYou --> {}: '.format(data, send_ip), end='')

    listener = threading.Thread(target=listen, daemon=True)
    listener.start()

    while True:
        send_ip = input('Send to: ')

        if send_ip == '/exit':
            sys.exit()
        
        while True:
            msg = input('You --> {}: '.format(send_ip))

            if msg == '/change':
                send_ip = '0.0.0.0'
                break
            elif msg == '/exit':
                sys.exit()

            s.sendto(msg.encode(), (send_ip, PORT))
       