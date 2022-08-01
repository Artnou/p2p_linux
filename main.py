import socket
import sys
import threading

PORT = 5555

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind(('0.0.0.0', PORT))

    send_ip = '0.0.0.0'

    print('-- Client launched --')

    def listen():
        while True:
            data, addr = s.recvfrom(1024)
            data = data.decode()
            recv_ip, recv_port = addr

            if send_ip == '0.0.0.0':
                print('\r{} --> You: {}\nSend to: '.format(recv_ip, data), end='')
            else:
                print('\r{} --> You: {}\nYou --> {}: '.format(recv_ip, data, send_ip), end='')

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
       