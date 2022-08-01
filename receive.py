import socket
import argparse

# parser = argparse.ArgumentParser()
# parser.add_argument("--ip", nargs='?', type=str)
# args = parser.parse_args()
# 
# HOST_IP = args.ip

HOST_IP = '0.0.0.0'

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST_IP, 5555))

    print("-- Reception debug launched --")

    while True:
        data, addr = s.recvfrom(1024)
        data = data.decode()
        recv_ip, recv_port = addr

        print("{} --> You: {}".format(recv_ip, data))