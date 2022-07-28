import socket
import threading

PORT = 5555

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind(('0.0.0.0', PORT))

    print("-- Client launched --")

    send_ip = input('Send message to (ip address): ')

    print('Send to', send_ip)

    # test 8