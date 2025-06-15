TCP 数据反转服务器与客户端程序
一、运行环境
1. 服务器端（虚拟机）
操作系统：Linux
依赖环境：
python3 >= 3.6        # Python 3.6及以上版本
pip3                  # Python包管理工具

网络配置：
虚拟机网络模式建议使用桥接模式，确保与主机网络互通。
虚拟机 IP 地址可通过 ifconfig 命令（若不存在，可先下载net-tools）查看（如 192.168.223.128）。

2. 客户端（主机）
操作系统：Windows
依赖环境：与服务器端一致。

二、参数配置
1. 服务器端参数（代码内配置）
#python
# reversetcpserver.py 关键配置
server_socket.bind(('0.0.0.0', 8888))  # 监听所有IP的8888端口（可修改端口）

端口说明：需确保防火墙开放该端口（执行 sudo ufw allow 8888/tcp）。
2. 客户端参数（命令行传入）

python reversetcpclient.py --server_ip <虚拟机IP> --server_port 8888 [--其他参数]

必选参数：
--server_ip：虚拟机 IP 地址（如 192.168.223.128）。
--server_port：服务器端口（默认 8888，需与服务器代码一致）。
--lmin：数据块最小大小 。
--lmax：数据块最大大小 。
可选参数：
--input_file：待反转的输入文件路径（如 --input_file data.txt）。

三、启动命令
1. 服务器端（虚拟机）
#bash
# 启动服务器
python3 reversetcpserver.py

预期输出：
服务器启动，等待客户端连接...
新连接来自: ('192.168.223.1', 50001)  # 客户端连接时显示

2. 客户端（主机）
#bash
# Windows
python reversetcpclient.py --server_ip 192.168.223.128 --server_port 8888 --lmin 10 --lmax 20

预期输出：
第1块反转的文本为 reve olleh
第2块反转的文本为 ...

四、防火墙与网络配置
1. 虚拟机防火墙
#bash
sudo ufw allow 8888/tcp  # 开放端口
sudo ufw enable         # 启用防火墙（若未启用）
sudo ufw status         # 检查防火墙状态
2. 网络连通性测试
#bash
# 在主机终端ping虚拟机IP
ping 192.168.223.128

# 预期结果：能正常ping通
