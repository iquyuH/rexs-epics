import socket
import struct

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("192.168.1.101", 8080))
sock.settimeout(5)

print("正在接收六自由度平台数据...")

try:
    for i in range(5):
        data, addr = sock.recvfrom(2048)

        if len(data) != 180:
            print("数据长度异常:", len(data))
            continue

        if data[:3] != bytes.fromhex("EB9011"):
            print("帧头异常:", data[:4].hex(" "))
            continue

        if data[3] != (sum(data[4:]) & 0xFF):
            print("校验失败")
            continue

        x, y, z, a, b, c = struct.unpack_from("<6f", data, 4)

        print(f"\n第{i+1}次读取：")
        print(f"X={x:.4f}, Y={y:.4f}, Z={z:.4f} mm")
        print(f"α={a:.4f}, β={b:.4f}, γ={c:.4f} °")

except socket.timeout:
    print("接收超时")

finally:
    sock.close()
