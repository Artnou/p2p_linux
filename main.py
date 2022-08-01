import socket
import threading
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--ip", nargs='?', type=str)
args = parser.parse_args()

HOST_IP = args.ip
# HOST_IP = socket.gethostbyname_ex(socket.getfqdn())
PORT = 5555

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind(('0.0.0.0', PORT))

    # host_ip = socket.gethostbyname(socket.gethostname())

    print("-- Client launched --")
    print("Host ip:", HOST_IP)

    send_ip = input('Send message to (ip address): ')

    print('Send to', send_ip)

    s.sendto("Message from".encode(), (send_ip, PORT))
    
    