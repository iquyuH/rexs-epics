
import asyncio
import socket
import struct

from caproto.server import PVGroup, pvproperty, run


# ========== UDP 通信配置 ==========

LOCAL_IP = "192.168.1.101"
UDP_PORT = 8080
WINDOWS_IP = "192.168.1.100"


# ========== EPICS IOC ==========

class StageIOC(PVGroup):

    # 平台平移位置，单位 mm
    x = pvproperty(name="X:RBV", value=0.0,
                   dtype=float, read_only=True)

    y = pvproperty(name="Y:RBV", value=0.0,
                   dtype=float, read_only=True)

    z = pvproperty(name="Z:RBV", value=0.0,
                   dtype=float, read_only=True)

    # 平台旋转角度，单位 deg
    rx = pvproperty(name="RX:RBV", value=0.0,
                    dtype=float, read_only=True)

    ry = pvproperty(name="RY:RBV", value=0.0,
                    dtype=float, read_only=True)

    rz = pvproperty(name="RZ:RBV", value=0.0,
                    dtype=float, read_only=True)

    # IOC 启动后执行 UDP 接收
    @x.startup
    async def x(self, instance, async_lib):

        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM
        )

        sock.bind((LOCAL_IP, UDP_PORT))
        sock.setblocking(False)

        loop = asyncio.get_running_loop()

        print("EPICS IOC 已启动")
        print("正在监听六自由度平台 UDP 数据...")

        count = 0

        try:
            while True:

                # 异步接收 UDP 数据
                data, addr = await loop.sock_recvfrom(
                    sock, 2048
                )

                # 只接收 Windows 转发的数据
                if addr[0] != WINDOWS_IP:
                    continue

                # 检查数据长度
                if len(data) != 180:
                    print("数据长度异常:", len(data))
                    continue

                # 检查帧头
                if data[:3] != bytes.fromhex("EB9011"):
                    print("帧头错误")
                    continue

                # 校验和检查
                checksum = sum(data[4:]) & 0xFF

                if checksum != data[3]:
                    print("校验失败")
                    continue

                # 解析六自由度实际位姿
                values = struct.unpack_from(
                    "<6f", data, 4
                )

                x, y, z, rx, ry, rz = values

                # 更新 EPICS PV
                await self.x.write(x)
                await self.y.write(y)
                await self.z.write(z)

                await self.rx.write(rx)
                await self.ry.write(ry)
                await self.rz.write(rz)

                count += 1

                # 每 10 个有效数据包显示一次
                if count % 10 == 0:
                    print(
                        f"收到 {count} 包 | "
                        f"X={x:.4f}, Y={y:.4f}, "
                        f"Z={z:.4f} mm | "
                        f"RX={rx:.4f}, "
                        f"RY={ry:.4f}, "
                        f"RZ={rz:.4f} deg",
                        flush=True
                    )

        finally:
            sock.close()


# ========== 启动 IOC ==========

if __name__ == "__main__":

    ioc = StageIOC(prefix="STAGE:")

    run(
        ioc.pvdb,
        interfaces=[LOCAL_IP],
        log_pv_names=True
    )
