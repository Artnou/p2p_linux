import socket
import threading

PORT = 5555

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind(('0.0.0.0', PORT))

    # host_ip = socket.gethostbyname(socket.gethostname())

    print('-- Client launched --')

    while True:
        send_ip = input('Send message to (ip address): ')
        msg = input('To {} > '.format(send_ip))

        s.sendto(msg.encode(), (send_ip, PORT))

        print('You --> {}: {}'.format(send_ip, msg))
    
    