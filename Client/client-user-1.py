import socket
import threading
import json  # json.dumps(some)打包   json.loads(some)解包
import tkinter
import tkinter.messagebox
from tkinter.scrolledtext import ScrolledText  # 导入多行文本框用到的包
import rsa
import random
from Crypto.Cipher import DES3
import pickle as pk

# 密钥对象的序列化与反序列化
def pk_dumps(_object: object):
    return pk.dumps(_object)
def pk_loads(_object: bytes):
    return pk.loads(_object)
# 生成随机字符串用于加盐操作
def random_str(lens=5):
    return ''.join(random.sample(['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e', 'd', 'c', 'b', 'a'], lens))
class rsa_:
    # rsa加密
    @staticmethod
    def rsaEncrypt(str, pubkey):
        # 明文编码格式
        content = str.encode("utf-8")
        # 公钥加密
        crypto = rsa.encrypt(content, pubkey)
        return crypto
    @staticmethod
    def rsaDecrypt(str, privkey):
        # 私钥解密
        content = rsa.decrypt(str, privkey)
        con = content.decode("utf-8")
        return con
    @staticmethod
    def getkey(len=512):
        return rsa.newkeys(len)
        # 返回信息格式：([公钥],[私钥])
class des_:
    def __init__(self, key):
        self.key = key
        self.length = DES3.block_size
        self.aes = DES3.new(self.key, DES3.MODE_CBC, b'12345678')  # 初始化AES,ECB模式的实例
        self.unpad = lambda date: date[0:-ord(date[-1])]
    def pad(self, text):
        count = len(text.encode('utf-8'))
        add = self.length - (count % self.length)
        entext = text + (chr(add) * add)
        return entext
    def encrypt(self, encrData):  # 加密函数
        res = self.aes.encrypt(self.pad(encrData).encode("utf8"))
        msg = res.hex()
        return msg
    def decrypt(self, decrData):  # 解密函数
        res = bytes.fromhex(decrData)
        msg = self.aes.decrypt(res).decode("utf8")
        return self.unpad(msg)
def md5(string: str):
    import hashlib
    return hashlib.md5(bytes(string, 'utf-8')).hexdigest()


IP = ''
PORT = ''
user = ''
listbox1 = ''  # 用于显示在线用户的列表框
ii = 0  # 用于判断是开还是关闭列表框
users = []  # 在线用户列表
chat = '【群发】'  # 聊天对象, 默认为群聊
DES = des_("xiaolongtongxue#")
des_key = des_("xiaolongtongxue#")
des_key1 = des_("xiaolongtongxue#")
(pubkey, privkey) = rsa_.getkey()


# 登陆窗口
loginRoot = tkinter.Tk()
loginRoot.title('聊天室')
loginRoot['height'] = 110
loginRoot['width'] = 270
loginRoot.resizable(0, 0)  # 限制窗口大小

IP1 = tkinter.StringVar()
IP1.set('127.0.0.1:6789')  # 默认显示的ip和端口
User = tkinter.StringVar()
User.set('')

# 服务器标签
labelIP = tkinter.Label(loginRoot, text='地址:端口')
labelIP.place(x=20, y=10, width=100, height=20)

entryIP = tkinter.Entry(loginRoot, width=80, textvariable=IP1)
entryIP.place(x=120, y=10, width=130, height=20)

# 用户名标签
labelUser = tkinter.Label(loginRoot, text='昵称')
labelUser.place(x=30, y=40, width=80, height=20)

entryUser = tkinter.Entry(loginRoot, width=80, textvariable=User)
entryUser.place(x=120, y=40, width=130, height=20)


# 登录按钮
def login(*args):
    global IP, PORT, user
    IP, PORT = entryIP.get().split(':')  # 获取IP和端口号
    PORT = int(PORT)                     # 端口号需要为int类型
    user = entryUser.get()
    if not user:
        tkinter.messagebox.showerror('温馨提示', message='请输入任意的用户名！')
    else:
        loginRoot.destroy()                  # 关闭窗口


loginRoot.bind('<Return>', login)            # 回车绑定登录功能
but = tkinter.Button(loginRoot, text='登录', command=login)
but.place(x=100, y=70, width=70, height=30)

loginRoot.mainloop()

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((IP, PORT))
if user:
    pass
else:
    user = 'no'

'''
测试代码可用性时留下的痕迹
'''
# user = user
# rand1 = random_str()
# user_des = des_key.encrypt(user + rand1)
# print(user)
# print(rand1)
# print(user_des)
# print(type(user_des))
# des_key = DES
# print(des_key1.decrypt(user_des).split(rand1)[0])

user = user
rand1 = random_str()
user_des = des_key.encrypt(user + rand1)
send_user = user_des.encode() + b'|*/*-*/*|' + pk_dumps(pubkey) + b'|*/*-*/*|' + md5(user+rand1).encode() + b'|*/*-*/*|' + rand1.encode()
# 发送用户名信息
s.send(send_user)

# 如果没有用户名则将ip和端口号设置为用户名
addr = s.getsockname()  # 获取客户端ip和端口号
addr = addr[0] + ':' + str(addr[1])
if user == '':
    user = addr

# 聊天窗口
# 创建图形界面
root = tkinter.Tk()
root.title(user)  # 窗口命名为用户名
root['height'] = 400
root['width'] = 580
root.resizable(0, 0)  # 限制窗口大小

# 创建多行文本框
listbox = ScrolledText(root)
listbox.place(x=5, y=0, width=570, height=320)
# 文本框使用的字体颜色
listbox.tag_config('red', foreground='red')
listbox.tag_config('blue', foreground='blue')
listbox.tag_config('green', foreground='green')
listbox.tag_config('pink', foreground='pink')
listbox.insert(tkinter.END, '欢迎加入聊天室 ！', 'blue')

# 表情功能代码部分
# 四个按钮, 使用全局变量, 方便创建和销毁
b1 = ''
b2 = ''
b3 = ''
b4 = ''
# 将图片打开存入变量中
p1 = tkinter.PhotoImage(file='emoji/facepalm.png')
p2 = tkinter.PhotoImage(file='emoji/smirk.png')
p3 = tkinter.PhotoImage(file='emoji/concerned.png')
p4 = tkinter.PhotoImage(file='emoji/smart.png')
# 用字典将标记与表情图片一一对应, 用于后面接收标记判断表情贴图
dic = {'aa**': p1, 'bb**': p2, 'cc**': p3, 'dd**': p4}
ee = 0  # 判断表情面板开关的标志


# 发送表情图标记的函数, 在按钮点击事件中调用
def mark(exp):  # 参数是发的表情图标记, 发送后将按钮销毁
    print("asdasd")
    print(Serverkey)
    global ee
    mes = exp + ':;' + user + ':;' + chat
    # print(mes)    # 发送的是一个表情信息

    send_data = rsa_.rsaEncrypt(str=mes, pubkey=Serverkey) + b'|*/*-*/*|' + md5(mes).encode()
    # s.send(mes.encode())
    s.send(send_data)
    b1.destroy()
    b2.destroy()
    b3.destroy()
    b4.destroy()
    ee = 0


# 四个对应的函数
def bb1():
    mark('aa**')


def bb2():
    mark('bb**')


def bb3():
    mark('cc**')


def bb4():
    mark('dd**')


def express():
    global b1, b2, b3, b4, ee
    if ee == 0:
        ee = 1
        b1 = tkinter.Button(root, command=bb1, image=p1,
                            relief=tkinter.FLAT, bd=0)
        b2 = tkinter.Button(root, command=bb2, image=p2,
                            relief=tkinter.FLAT, bd=0)
        b3 = tkinter.Button(root, command=bb3, image=p3,
                            relief=tkinter.FLAT, bd=0)
        b4 = tkinter.Button(root, command=bb4, image=p4,
                            relief=tkinter.FLAT, bd=0)

        b1.place(x=5, y=248)
        b2.place(x=75, y=248)
        b3.place(x=145, y=248)
        b4.place(x=215, y=248)
    else:
        ee = 0
        b1.destroy()
        b2.destroy()
        b3.destroy()
        b4.destroy()


# 创建表情按钮
eBut = tkinter.Button(root, text='表情', command=express)
eBut.place(x=5, y=320, width=60, height=30)


# 创建多行文本框, 显示在线用户
listbox1 = tkinter.Listbox(root)
listbox1.place(x=445, y=0, width=130, height=320)


def showUsers():
    global listbox1, ii
    if ii == 1:
        listbox1.place(x=445, y=0, width=130, height=320)
        ii = 0
    else:
        listbox1.place_forget()  # 隐藏控件
        ii = 1


# 查看在线用户按钮
button1 = tkinter.Button(root, text='用户列表', command=showUsers)
button1.place(x=485, y=320, width=90, height=30)

# 创建输入文本框和关联变量
a = tkinter.StringVar()
a.set('')
entry = tkinter.Entry(root, width=120, textvariable=a)
entry.place(x=5, y=350, width=570, height=40)


def send(*args):
    # 没有添加的话发送信息时会提示没有聊天对象
    users.append('【群发】')
    print(chat)
    if chat not in users:
        tkinter.messagebox.showerror('温馨提示', message='没有聊天对象!')
        return
    if chat == user:
        tkinter.messagebox.showerror('温馨提示', message='自己不能和自己进行对话!')
        return
    mes = entry.get() + ':;' + user + ':;' + chat  # 添加聊天对象标记
    # print(mes)  # 发送的聊天信息。格式： [发送内容]:;[发送人用户名]:;[接受者]
    print(Serverkey)
    send_data = rsa_.rsaEncrypt(str=mes, pubkey=Serverkey) + b'|*/*-*/*|' + md5(mes).encode()
    print(send_data)
    # s.send(mes.encode())
    s.send(send_data)
    a.set('')  # 发送后清空文本框


# 创建发送按钮
button = tkinter.Button(root, text='发送', command=send)
button.place(x=515, y=353, width=60, height=30)
root.bind('<Return>', send)  # 绑定回车发送信息


# 私聊功能
def private(*args):
    global chat
    # 获取点击的索引然后得到内容(用户名)
    indexs = listbox1.curselection()
    index = indexs[0]
    if index > 0:
        chat = listbox1.get(index)
        # 修改客户端名称
        if chat == '【群发】':
            root.title(user)
            return
        ti = user + '  -->  ' + chat
        root.title(ti)


# 在显示用户列表框上设置绑定事件
listbox1.bind('<ButtonRelease-1>', private)


# 用于时刻接收服务端发送的信息并打印
def recv():
    global users
    while True:
        data = s.recv(4096)
        data_head = data.split(b'|*/*-*/*|')

        global Serverkey
        Serverkey = pk_loads(data_head[2])

        # print(Serverkey)
        data_e = rsa_.rsaDecrypt(str=data_head[0], privkey=privkey)
        if md5(data_e) == data_head[1].decode():
            pass
        else:
            tkinter.messagebox.showerror('Warning', message='信息或许被监听,五秒内程序自动结束')
            import time
            time.sleep(5)
            exit(0)

        # 这一段接收到
        data = data_e

        # 没有捕获到异常则表示接收到的是在线用户列表
        try:
            data = json.loads(data)
            # print(data)   # data内容为用户列表
            users = data
            listbox1.delete(0, tkinter.END)  # 清空列表框
            number = ('   在线用户数: ' + str(len(data)))
            listbox1.insert(tkinter.END, number)
            listbox1.itemconfig(tkinter.END, fg='green', bg="#f0f0ff")
            listbox1.insert(tkinter.END, '【群发】')
            listbox1.itemconfig(tkinter.END, fg='green')
            for i in range(len(data)):
                listbox1.insert(tkinter.END, (data[i]))
                listbox1.itemconfig(tkinter.END, fg='green')
        except:
            data = data.split(':;')
            data1 = data[0].strip()  # 消息
            data2 = data[1]  # 发送信息的用户名
            data3 = data[2]  # 聊天对象
            markk = data1.split('：')[1]
            # 判断是不是图片
            pic = markk.split('#')
            # 判断是不是表情
            # 如果字典里有则贴图
            if (markk in dic) or pic[0] == '``':
                data4 = '\n' + data2 + '：'  # 例:名字-> \n名字：
                if data3 == '【群发】':
                    if data2 == user:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(tkinter.END, data4, 'blue')
                    else:
                        listbox.insert(tkinter.END, data4, 'green')  # END将信息加在最后一行
                elif data2 == user or data3 == user:  # 显示私聊
                    listbox.insert(tkinter.END, data4, 'red')  # END将信息加在最后一行
                listbox.image_create(tkinter.END, image=dic[markk])
            else:
                data1 = '\n' + data1
                if data3 == '【群发】':
                    if data2 == user:  # 如果是自己则将则字体变为蓝色
                        listbox.insert(tkinter.END, data1, 'blue')
                    else:
                        listbox.insert(tkinter.END, data1, 'green')  # END将信息加在最后一行
                    if len(data) == 4:
                        listbox.insert(tkinter.END, '\n' + data[3], 'pink')
                elif data2 == user or data3 == user:  # 显示私聊
                    listbox.insert(tkinter.END, data1, 'red')  # END将信息加在最后一行
            listbox.see(tkinter.END)  # 显示在最后


r = threading.Thread(target=recv)
r.start()  # 开始线程接收信息

root.mainloop()
s.close()  # 关闭图形界面后关闭TCP连接


