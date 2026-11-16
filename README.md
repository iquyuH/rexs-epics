# REXS 实验站设备 EPICS 接入

以六自由度支撑平台为起点，逐步将 REXS 实验站设备接入 EPICS，实现统一监控、控制与实验自动化。

> 仓库当前仅提供项目说明。下述进展来自现有设备部署；脚本及依赖文件待整理上传，使用命令供代码补齐后参考。

## 当前进展

已完成真实平台的只读位姿监控，发布 `STAGE:X:RBV`、`STAGE:Y:RBV`、`STAGE:Z:RBV`、`STAGE:RX:RBV`、`STAGE:RY:RBV`、`STAGE:RZ:RBV` 六个 PV。已验证 `caget STAGE:Z:RBV` 返回 `584.085`。

该平台用于调整真空腔体的位置和姿态，与腔体内负责样品定位及扫描的样品台不同。目前尚未实现运动控制和断线报警。

## 系统架构

```text
平台控制器 192.168.1.88:8080
    ↓ UDP，180 字节/帧，周期 100 ms
Windows 192.168.1.100
    ↓ udp_forward.py 原样转发
Ubuntu 虚拟机 192.168.1.101:8080
    ↓ stage_ioc.py（caproto IOC）
EPICS 客户端：caget / camonitor
```

当前设备反馈发往 Windows，而 IOC 运行在 Ubuntu 虚拟机，因此需要转发。后续若设备支持直接向 Ubuntu 发送数据，可取消这一中转。

IOC 检查帧头 `EB9011`、帧长度和协议校验，从偏移 4 按小端格式 `<6f` 解析 X、Y、Z、α、β、γ，并发布对应 PV。单位与角度定义以设备协议为准。

## 项目文件（待上传）

```text
udp_forward.py    Windows UDP 转发脚本
stage_ioc.py      Ubuntu EPICS IOC
requirements.txt Python 依赖（caproto==1.3.0）
```

## 使用方法

以下步骤在脚本及依赖文件上传后适用。配置上述 IP 地址，确保 Windows 与 Ubuntu 网络互通，并放行相应 UDP 和 EPICS Channel Access 通信。

Windows 启动转发：

```powershell
uv run udp_forward.py
```

Ubuntu 安装依赖并启动 IOC：

```bash
uv venv
uv pip install -r requirements.txt
uv run --no-project stage_ioc.py
```

在已安装 EPICS 命令行工具的终端读取数据：

```bash
export EPICS_CA_ADDR_LIST=192.168.1.101
export EPICS_CA_AUTO_ADDR_LIST=NO

caget STAGE:Z:RBV
camonitor STAGE:X:RBV STAGE:Y:RBV STAGE:Z:RBV
```

设备断线后，当前 PV 可能保留最后一次读数，不代表实时位置。

## 最终目标

逐步将 REXS 实验站的支撑平台、样品台、衍射臂、探测器、温磁系统及辅助设备接入 EPICS，统一提供控制、状态监测和报警接口，再通过 Ophyd 与 Bluesky 实现扫描、采集和数据保存。

近期先完善通信可靠性、断线报警和设备状态，再扩展运动控制及其他设备。实时伺服、精确同步和必要的硬件保护由底层控制器及专用硬件承担。
