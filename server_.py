import socket
import threading
import queue
import json  # json.dumps(some)打包   json.loads(some)解包
import time
import sys

from util.gettime import gettime
from util.log import log_

# IP = socket.gethostbyname(socket.getfqdn(socket.gethostname()))
IP = ''
PORT = 6789
que = queue.Queue()                             # 用于存放客户端发送的信息的队列
users = []                                      # 用于存放在线用户的信息  [conn, user, addr, [pubkey]]
lock = threading.Lock()                         # 创建锁, 防止多个线程写入数据的顺序打乱


# 将在线用户存入online列表并返回
def onlines():
    online = []
    for i in range(len(users)):
        online.append(users[i][1])
    return online



class ChatServer(threading.Thread):
    global users, que, lock
    global pubkey, privkey

    def __init__(self, port):
        threading.Thread.__init__(self)
        # self.setDaemon(True)
        self.ADDR = ('', port)
        # self.PORT = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.conn = None
        # self.addr = None

    # 用于接收所有客户端发送信息的函数
    def tcp_connect(self, conn, addr):
        # 连接后将用户信息添加到users列表
        user = conn.recv(1024)  # 接收用户名
        user = user.decode()

        for i in range(len(users)):
            if user == users[i][1]:
                # 用户名冲突则主动修改
                print('User  already exist')
                user = '' + user + '_2'
        if user == 'no':
            user = addr[0] + ':' + str(addr[1])
        users.append((conn, user, addr))
        print("\033[32m[" + gettime() + "]\033[0m\033[35m" + str(addr) + "\033[0m" + ' New Connection:', ':', user, end='')         # 打印用户名
        log_("[" + gettime() + "]" + str(addr) + "New Connection ::" + user)
        # 发送信息要求Client更新在线用户列表
        d = onlines()                                          # 有新连接则刷新客户端的在线用户显示
        self.recv(d, addr)
        print()
        try:
            while True:
                data = conn.recv(1024)
                data = data.decode()
                self.recv(data, addr)
            conn.close()
        except:
            print("\033[32m[" + gettime() + "]\033[0m\033[35m" + str(addr) + "\033[0m" + user + ' Connection lost')
            log_("[" + gettime() + "]" + str(addr) + user + ' Connection lost')
            self.delUsers(conn, addr)                             # 将断开用户移出users
            conn.close()

    # 判断断开用户在users中是第几位并移出列表, 刷新客户端的在线用户显示
    def delUsers(self, conn, addr):
        a = 0
        for i in users:
            if i[0] == conn:
                users.pop(a)
                # 打印剩余在线用户(conn)
                print("\033[32m[" + gettime() + "]\033[0m\033[35m" + str(addr) + "\033[0m" + ' 在线用户: ', end='')
                d = onlines()
                # 发送信息要求Client更新在线用户列表
                self.recv(d, addr)
                print(d)
                break
            a += 1

    # 将接收到的信息(ip,端口以及发送的信息)存入que队列
    def recv(self, data, addr):
        lock.acquire()
        try:
            que.put((addr, data))
        finally:
            lock.release()

    # 将队列que中的消息发送给所有连接到的用户
    def sendData(self):
        while True:
            if not que.empty():
                data = ''
                reply_text = ''
                message = que.get()                               # 取出队列第一个元素
                if isinstance(message[1], str):                   # 如果data是str则返回Ture
                    # message[0]是一个元组，内容是信息产生者的IP和端口
                    for i in range(len(users)):
                        # for k in users[i]:
                        #     print(k)
                        # print("*/-"*10)
                        # user[i][1]是用户名, users[i][2]是addr, 将message[0]改为用户名
                        for j in range(len(users)):
                            if message[0] == users[j][2]:
                                # 这边的意思是发现了发送信息的那个B~~站小伙伴
                                data = ' ' + users[j][1] + '：' + message[1]
                                outprint = "\033[32m[" + gettime() + "]\033[0m\033[35m" + str(message[0]) + "\033[0m" + "Receieve Message from \033[34m" + users[j][1] + "\033[0m.Value is \033[33m" + message[1].split(";:")[0] + "\033[0m "
                                log__ = "[" + gettime() + "]" + str(message[0]) + "Receieve Message from " + users[j][1] + ".Value is " + message[1].split(";:")[0]
                                # print(data)           # str类型，格式：" 发送者  : 发送的信息 ;: 信息发送者 :; 接受者（包括群发）"
                                # print(users[j][0])    # socket 套接字的信息
                                # print(users[j][1])    # 信息发送者
                                # print(users[j][3])    # 信息发送者的公钥
                                # print(message[0])     # 里边放的是一个元组：(IP:str、port:int)
                                # print(message[1])     # str类型，格式： " 发送的信息 ;: 信息发送者 :; 接受者（包括群发）"
                                break
                        # users[i][0]是目标的连接用套接字对象
                        # users[i][1]是目标用户名
                        # users[i][2]是目标用户的地址、端口（元组形式）
                        # users[i][3]是目标用户的公钥
                        # 在这里边需要注意的是，这种情况下需要发送出去的信息应当包括服务器的公钥信息，并且全部的信息应当由目标用户的公钥进行加密
                        '''
                        给用户更新用户列表的时候，发送多条信息，中间使用b'|*/*-*/*|'进行分割
                        从左到右依次的意义是：
                           信息加密后的结果
                           信息明文的md5哈希值
                           Server端公钥进行二进制编码后的结果
                        '''
                        # users[i][0].send(rsa_.rsaEncrypt(str=data, pubkey=users[i][3]) + b'|*/*-*/*|' + md5(data).encode() + b'|*/*-*/*|' + pk_dumps(pubkey))
                        users[i][0].send(data.encode())
                    try:
                        print(outprint)
                        log_(log__)
                    except:
                        pass
                # data = data.split(':;')[0]
                if isinstance(message[1], list):  # 同上
                    # print(message[1]) # 列表内容是所有的在线用户
                    # 如果是list则打包后直接发送
                    # 在这边采用了消息队列的形式，在此之前我是压根就没想到过的...
                    data = json.dumps(message[1])
                    # data = rsa_.rsaEncrypt(str=data, pubkey=pubkey)
                    for i in range(len(users)):
                        # users[i][0]是目标的连接用套接字对象
                        # users[i][1]是目标用户名
                        # users[i][2]是目标用户的地址、端口（元组形式）
                        # users[i][3]是目标用户的公钥
                        try:
                            # 在这里边需要注意的是，这种情况下需要发送出去的信息应当包括服务器的公钥信息，并且全部的信息应当由目标用户的公钥进行加密
                            '''
                            给用户更新用户列表的时候，发送多条信息，中间使用b'|*/*-*/*|'进行分割
                            从左到右依次的意义是：
                                信息加密后的结果
                                信息明文的md5哈希值
                                Server端公钥进行二进制编码后的结果
                            '''
                            # users[i][0].send(rsa_.rsaEncrypt(str=data, pubkey=users[i][3]) + b'|*/*-*/*|' + md5(data).encode() + b'|*/*-*/*|' + pk_dumps(pubkey))
                            users[i][0].send(data.encode())
                        except:
                            pass

    def run(self):
        self.s.bind(self.ADDR)
        self.s.listen(5)
        # print('服务器正在运行中...')
        log_("*********************\n[" + gettime() + "]  Server Listening")
        print("\033[32m[" + gettime() + "]\033[0m" + "Server Listening")
        q = threading.Thread(target=self.sendData)
        q.start()
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
            t.start()
        self.s.close()




if __name__ == '__main__':
    cserver = ChatServer(PORT)
    cserver.start()
    while True:
        time.sleep(1)
        try:
            if not cserver.isAlive():
                print("Chat connection lost...")
                sys.exit(0)
        except AttributeError:
            pass
