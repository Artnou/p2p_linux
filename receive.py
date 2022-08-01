import socket

HOST_IP = '0.0.0.0'

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
    s.bind((HOST_IP, 5555))

    print("-- Reception debug launched --")

    while True:
        data, addr = s.recvfrom(1024)
        data = data.decode()
        recv_ip, recv_port = addr

        print("{} --> You: {}".format(recv_ip, data))