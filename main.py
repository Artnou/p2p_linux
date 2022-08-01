import socket
import sys
import threading

PORT = 5555

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind(('0.0.0.0', PORT))

    # host_ip = socket.gethostbyname(socket.gethostname())

    print('-- Client launched --')

    def listen():
        while True:
            data, addr = s.recvfrom(1024)
            data = data.decode()
            recv_ip, recv_port = addr
            print('\r{} --> You: {}'.format(recv_ip, data))
            print('You --> {}'.format(send_ip))

    listener = threading.Thread(target=listen, daemon=True)
    listener.start()

    while True:
        send_ip = input('Send message to (ip address): ')

        if send_ip == 'exit':
            sys.exit()
        
        while True:
            msg = input('You --> {}: '.format(send_ip))

            if msg == 'change':
                break
            elif msg == 'exit':
                sys.exit()

            s.sendto(msg.encode(), (send_ip, PORT))
    
    