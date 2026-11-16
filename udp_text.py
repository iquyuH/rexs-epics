import socket
import struct

# 六自由度平台控制器地址
IP = "192.168.1.88"
PORT = 8080

# 创建 UDP 通信
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("192.168.1.101",8080))
sock.settimeout(3)

try:
    # 发送读取指令
    sock.sendto(bytes.fromhex("EB901103"), (IP, PORT))

    # 接收返回数据
    data, addr = sock.recvfrom(2048)

    print("收到字节数：", len(data))
    print("原始数据：", data.hex(" "))

    if len(data) == 180 and data[:3] == bytes.fromhex("EB9011"):
        # 校验数据
        checksum = sum(data[4:]) & 0xFF

        if checksum != data[3]:
            print("数据校验失败")
        else:
            # 解析六自由度位姿（小端浮点数）
            x, y, z, rx, ry, rz = struct.unpack_from("<6f", data, 4)

            print("\n平台实时位姿：")
            print(f"X = {x:.4f} mm")
            print(f"Y = {y:.4f} mm")
            print(f"Z = {z:.4f} mm")
            print(f"α = {rx:.4f}°")
            print(f"β = {ry:.4f}°")
            print(f"γ = {rz:.4f}°")
    else:
        print("返回数据格式与协议不符")

except socket.timeout:
    print("通信超时：没有收到控制器回复")

finally:
    sock.close()
