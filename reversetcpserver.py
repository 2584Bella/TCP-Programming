import socket       # 用于TCP网络通信
import struct       # 处理二进制报文格式
import threading    #实现多线程

# 报文类型
TYPE_INIT = 1  # Initialization报文（客户端→服务器）
TYPE_AGREE = 2  # agree报文（服务器→客户端）
TYPE_REQUEST = 3  # reverseRequest报文（客户端→服务器）
TYPE_ANSWER = 4  # reverseAnswer报文（服务器→客户端）

# 报文格式模板（大端序，用>表示，网络字节序）
#H：2 字节无符号短整型
#I：4 字节无符号整型
INIT_FORMAT = '>H I'  # Type(2B) + N(4B)
AGREE_FORMAT = '>H'  # Type(2B)
DATA_FORMAT = '>H I'  # Type(2B) + Length(4B)

def handle_client(client_socket, addr):
    try:
        # 接收Initialization报文（Type=1, N=块数）
        init_packet = client_socket.recv(6)  # 2B Type + 4B N
        if len(init_packet) < 6:
            raise Exception("初始化报文接收不完整")
        # 解析初始化报文
        type_init, N = struct.unpack(INIT_FORMAT, init_packet)
        if type_init != TYPE_INIT:
            raise Exception("无效的初始化报文类型")

        # 发送agree报文（Type=2）
        agree_packet = struct.pack(AGREE_FORMAT, TYPE_AGREE)
        client_socket.sendall(agree_packet)

        # 处理N个reverseRequest请求
        for _ in range(N):
            # 接收reverseRequest报文头部（Type=3, Length=数据长度, Data=数据）
            header = client_socket.recv(6)
            if len(header) < 6:
                raise Exception("请求报文头部接收不完整")
            type_req, length = struct.unpack(DATA_FORMAT, header)
            if type_req != TYPE_REQUEST:
                raise Exception("无效的请求报文类型")
            data = client_socket.recv(length)
            if len(data) != length:
                raise Exception("请求数据接收不完整")

            # 反转数据
            reversed_data = data[::-1]  # 直接字节流反转（序列切片）

            # 构造reverseAnswer报文（Type=4, Length=反转后长度, reverseData=反转数据）
            answer_packet = struct.pack(DATA_FORMAT, TYPE_ANSWER, len(reversed_data)) + reversed_data
            client_socket.sendall(answer_packet)

    except Exception as e:
        print(f"客户端{addr}异常: {str(e)}")
    finally:
        # 确保关闭客户端连接
        client_socket.close()#关闭连接套接字


def main():
    #socket.AF_INET：指定使用 IPv4 地址族。
    #socket.SOCK_STREAM：指定使用 TCP 协议。
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#欢迎套接字
    #'0.0.0.0'：特殊 IP 地址，表示监听所有可用网络接口
    server_socket.bind(('0.0.0.0', 8888))  # 端口可自定义
    #表示允许等待处理的客户端连接数量。当有超过 5 个客户端同时连接时，超出的连接会被拒绝。
    server_socket.listen(5)
    print("服务器启动，等待客户端连接...")

    while True:
        #接收客户端连接（获取套接字和地址元组（Ip地址，端口号）
        client_socket, addr = server_socket.accept()#连接套接字
        print(f"新连接来自: {addr}")
        # 为每个客户端创建线程处理（多线程）
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))#指定线程要执行的函数和传递给handle_client函数的参数
        #启动线程
        client_thread.start()


if __name__ == "__main__":
    main()
