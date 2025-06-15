import socket          # 用于TCP网络通信
import random          # 生成随机块长度
import argparse        # 解析命令行参数
import struct          # 处理二进制报文格式
import os              #处理文件
# 报文类型
TYPE_INIT = 1  # Initialization报文（客户端→服务器）
TYPE_AGREE = 2  # agree报文（服务器→客户端）
TYPE_REQUEST = 3  # reverseRequest报文（客户端→服务器）
TYPE_ANSWER = 4  # reverseAnswer报文（服务器→客户端）

# 报文格式模板（大端序，用>表示，网络字节序）
#TCP/IP 等网络协议 规定使用大端序作为网络字节序
#H：2 字节无符号短整型
#I：4 字节无符号整型
INIT_FORMAT = '>H I'  # Type(2B) + N(4B)要请求的块数
AGREE_FORMAT = '>H'  # Type(2B)
DATA_FORMAT = '>H I'  # Type(2B) + Length(4B)数据长度


def main():
    parser = argparse.ArgumentParser(description='TCP Reverse Client')
    parser.add_argument('--server_ip', required=True, help='Server IP address')
    parser.add_argument('--server_port', type=int, required=True, help='Server port')
    parser.add_argument('--lmin', type=int, required=True, help='Minimum block length')
    parser.add_argument('--lmax', type=int, required=True, help='Maximum block length')
    parser.add_argument('--input_file', default='test.txt', help='输入文件路径（ASCII格式）')
    args = parser.parse_args()

    # 客户端Socket初始化
    # socket.AF_INET：指定使用 IPv4 地址族。
    # socket.SOCK_STREAM：指定使用 TCP 协议。
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #防止程序在等待网络数据时陷入无限期阻塞状态
    client_socket.settimeout(10)  # 设置超时时间，避免阻塞卡死
    try:
        client_socket.connect((args.server_ip, args.server_port))
    except Exception as e:
        raise Exception(f"连接服务器失败: {str(e)}")

    # 读取原始文件（处理异常）
    try:
        with open(args.input_file, 'r', encoding='ascii') as f:
            # 将文本转换为字节流（网络传输需二进制数据）
            data = f.read().encode('ascii')#将字符串（str）转换为指定编码的字节流（bytes）。
    except FileNotFoundError:
        raise Exception(f"文件 {args.input_file} 不存在")
    except UnicodeDecodeError:
        raise Exception("文件包含非ASCII字符，请检查")

    # 分块逻辑
    blocks = []
    total_length = len(data)
    current_pos = 0
    while current_pos < total_length:
        remaining = total_length - current_pos
        if remaining <= args.lmax:  # 剩余数据作为最后一块
            block_len = remaining
        else:
            #生成随机块长
            block_len = random.randint(args.lmin, args.lmax)
        #切片操作获取块
        blocks.append(data[current_pos:current_pos + block_len])
        current_pos += block_len
    N = len(blocks)  # 总块数

    # 发送Initialization报文
    try:
        #struct.pack封装：将 Python 数据类型转为二进制字节流。
        init_packet = struct.pack(INIT_FORMAT, TYPE_INIT, N)#(格式，内容)
        #调用sendall() 操作系统会自动在 TCP 头部添加源端口和目的端口
        client_socket.sendall(init_packet)
    except Exception as e:
        raise Exception(f"发送初始化报文失败: {str(e)}")

    # 接收agree报文
    try:
        #接受2字节的报文
        agree_packet = client_socket.recv(2)
        if len(agree_packet) != 2:
            raise Exception("接收agree报文不完整")
        #struct.unpack解包返回元组，type_agree, = (...)提取单个元素。
        type_agree, = struct.unpack(AGREE_FORMAT, agree_packet)
        if type_agree != TYPE_AGREE:
            raise Exception("服务器未确认")
    except Exception as e:
        raise Exception(f"处理agree报文失败: {str(e)}")

    reversed_data = b''#初始化存储的字节流
    for idx, block in enumerate(blocks, 1):# idx从1开始计数
        try:
            # 发送reverseRequest报文
            length = len(block)
            request_packet = struct.pack(DATA_FORMAT, TYPE_REQUEST, length) + block
            client_socket.sendall(request_packet)

            # 接收reverseAnswer报文头部
            header = client_socket.recv(6)
            if len(header) != 6:
                raise Exception("接收头部不完整")
            type_answer, r_length = struct.unpack(DATA_FORMAT, header)#序列解包
            if type_answer != TYPE_ANSWER:
                raise Exception(f"无效应答类型: {type_answer}")

            # 接收反转数据
            r_data = b''  # 已接收的二进制数据
            received = 0  # 已接收的字节数
            while received < r_length:
                chunk = client_socket.recv(r_length - received) # 尝试接收剩余字节数(chunk片段)
                if not chunk: # 如果recv返回空字节串（b''），表示服务器关闭了连接
                    raise Exception("服务器断开连接")
                r_data += chunk
                received += len(chunk)
            if len(r_data) != r_length:
                raise Exception("接收数据长度不一致")

            # 打印结果
            print(f"第{idx}块: 反转的文本为 {r_data.decode('ascii')}")#将字节流（bytes）按指定编码解析为字符串（str）。
            reversed_data += r_data
        except Exception as e:
            raise Exception(f"处理第{idx}块失败: {str(e)}")

    # 写入最终文件
    try:
        filename, ext = os.path.splitext(args.input_file)  # 分离文件名和扩展名
        output_file = f"reversed_{filename}{ext}"  # 拼接新文件名
        with open(output_file, 'wb') as f:
            f.write(reversed_data)
    except Exception as e:
        raise Exception(f"写入文件失败: {str(e)}")

    client_socket.close()#关闭客户端套接字
    print(f"操作完成，结果已保存至 {output_file}")


if __name__ == "__main__":
    main()