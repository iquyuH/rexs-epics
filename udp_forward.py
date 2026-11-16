import socket

receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver.bind(("192.168.1.100", 8080))

sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("正在监听控制器的UDP数据...")

while True:
    data, addr = receiver.recvfrom(2048)

    if addr[0] == "192.168.1.88":
        print("收到:", len(data), "字节")
        sender.sendto(
            data, ("192.168.1.101", 8080)
        )