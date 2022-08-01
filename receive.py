import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--ip", nargs='?', type=str)
args = parser.parse_args()

HOST_IP = args.ip

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST_IP, 5555))

    print("-- Reception debug launched --")
    print("Receiver ip:", HOST_IP)

    while True:
        data, recv_ip = s.recvfrom(1024)
        data = data.decode()

        print("Message received from {}: {}".format(recv_ip, data))