# 基于python开发的聊天室（安全通信）

>我这边有一门课《安全协议分析》的结课作业要求：
>
- **1.**使用某种语言编写Socket程序。实现Client与Server端基本功能
- **2.**Client端向服务器端发送数据，Server端能够接受数据，将接受到的数据显示到屏幕上。
- **3.**Server端接受数据之后将数据发送给Client端，Client显示接收到Server的数据。
- **4.**在Client端与Server端的通信过程中实现数据加密、身份认证与完整性校验
- **5.**提供Client端与Server端可选择的数据加密、身份认证和完整性校验方法。即安全加密套件。
- **6.**实现ClientA与ClientB通过Server进行安全聊天功能。并且可以进阶为一种聊天室功能。

> 看完之后我“啪”的一声就站起来了，很快昂，然后就开始构思怎么写
>
> 然后我写了两天，感觉不对呀，还没有写到设计安全协议的关键部分呢，就快把我熬死了...更关键的是因为写完整模块写的并不多，再加上写的时候没有提前划定好一个完整的规模，导致我写写删删，最终烂到我自己都看不下去（还不如之前某个烂尾的玩意儿呢QWQ）
>
>> 然后我就开始了百度，准备从现成的项目上找，这不就找到了嘛！[https://blog.csdn.net/qq_38951154/article/details/107270408](https://blog.csdn.net/qq_38951154/article/details/107270408)
>>
>>然后我就开始了针对项目源码的审计作业，然后对其增加安全性校验的方法，以及加密套件。最终我选定的加密功能由：
>>
>> - **RSA非对称加密算法**（可以替换为其他加密算法）
>> - **DES对称加密算法**（可以替换为其他对称加密算法）
>> - **md5哈希算法**（可以替换为SHA-1、SHA-256等其他哈希算法，md5的安全性可能已经不再有那么高）

项目已开源，是针对[https://blog.csdn.net/qq_38951154/article/details/107270408](https://blog.csdn.net/qq_38951154/article/details/107270408)的改进版本

Github地址（记得来点个STAR呀，也别忘了[原作者的](https://gitee.com/yangzhenman/python-chat "原作者的")呢）：[https://github.com/xiaolongtongxue/python_chat_room](https://github.com/xiaolongtongxue/python_chat_room)

## 运行效果

[![](https://gitee.com/xiaolongtongxue/imagebed/raw/master/img/202205092001794.png)](https://gitee.com/xiaolongtongxue/imagebed/raw/master/img/202205092001794.png)

[![](https://gitee.com/xiaolongtongxue/imagebed/raw/master/img/202205092003739.png)](https://gitee.com/xiaolongtongxue/imagebed/raw/master/img/202205092003739.png)

## 逻辑简单展示

**Server端缓存用户列表、信息列表等内容，在其发生变化（用户登入登出、用户发送消息）的时候极使广播更新，因此客户端发送端口仍需保持监听状态**

[![](https://gitee.com/xiaolongtongxue/imagebed/raw/master/img/202205092014124.png)](https://gitee.com/xiaolongtongxue/imagebed/raw/master/img/202205092014124.png)

**安全层面**

除了第一次建立连接的使用的是对称加密方式，其他时候都使用了非对称加密。并且都坚持了使用对方公钥签名加密的原则。

无论是什么事后，在通信的事后都会再三次握手成功之后坚持进行哈希加盐验证，盐的组成是五位的随机数，如果验证失败，则消息可能被篡改，此时应当及时停止通信

## 关键代码分析

在这边拿出来一些关键性的源代码进行分析

> ***日志备份***

```python
# -*- coding: UTF-8 -*-
def log_(loging: str):
    with open("log/log.log", "a") as file:
        file.write(loging + "\n")
```
> 首先一套完备的系统的访问记录一定是要由日志记录的，这边也是设置了日志文件，这边就是目前日志文件的一截选段

[![](https://gitee.com/xiaolongtongxue/imagebed/raw/master/img/202205091726619.png)](https://gitee.com/xiaolongtongxue/imagebed/raw/master/img/202205091726619.png)

> ***RSA加解密***
>> 每次Server端或者Client端启动的都要运行一个rsa_.getkey算法获取本机的公私钥，并且在彼此的交互之间交换彼此的公钥

```python
# -*- coding: UTF-8 -*-
import rsa
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
```

> ***DES加解密***
>> 在某些来不及交换密钥的情况下，DES密钥交换不失为一种可行的方法，Client端拿到的是exe文件，需要经过逆向破解才有拿到密钥的可能，在一定程度上保证了一定的安全性。但是这种算法只能用来发送那些公开性比较强的信息防止其在信道传输的过程中被篡改。

```python
from Crypto.Cipher import DES3
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
```

> ***MD5哈希算法***
>> 作为一款老牌哈希算法，虽然在王小云教授团队的实验下可能安全性已经不再是那么的高，但是对于小型站点来讲也已经足够了，当然如果有兴趣，在这里使用**SHA-1**、**SHA-256**也都是没有问题的！

```python
def md5(string: str):
    import hashlib
    return hashlib.md5(bytes(string, 'utf-8')).hexdigest()
```

> **加盐哈希**
>> 加盐哈希算法可以使得哈希算法更加安全，一般是采用随机生成字符串的形式，这边也就简单写写

```python
import random
def random_str(lens=5):
    return ''.join(random.sample(['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e', 'd', 'c', 'b', 'a'], lens))
```

>***pickle库实现对象序列化与反序列化***
>> 实际传输的过程中，很多时候需要将对象进行二进制转换，pickle库为我们提供了一种不错的方法

```python
# -*- coding: UTF-8 -*-
import pickle as pk

def pk_dumps(_object: object):
    return pk.dumps(_object)

def pk_loads(_object: bytes):
    return pk.loads(_object)
```

### Client端的接发包设计

> ***登录状态发包***
> > 此时还不知道Server端的公钥信息，所以先用对称加密算法先应对一下。
>>
> > 其实这时候我本人的最开始想法是：模仿HTTPS协议的连接建立方式，进行一段身份认证，但是这边，由于实际发送的信息仅仅有用户名这样的公开信息，所以就使用保密性相对略有缺失的加密算法进行加密处理。但如果时间充沛的话，我本人更倾向于提前让C-S两端沟通了解彼此的公钥信息的做法，但迫于Server端架构问题没有实现。当然为了保证尽可能的安全，在这边Client也需要发送出自己的公钥。

```python
user = user
rand1 = random_str()
user_des = des_key.encrypt(user + rand1)
send_user = user_des.encode() + b'|*/*-*/*|' + pk_dumps(pubkey) + b'|*/*-*/*|' + md5(user+rand1).encode() + b'|*/*-*/*|' + rand1.encode()
# 发送用户名信息
s.send(send_user)
```

> ***接收Server端发送的广播信息***
>> 为了实现Server端及时更新的消息（比如说其他用户的登入、登出，或者是自己可以接收到的信息的发送），Client需要将对应的端口开放出来用来接收Server端发送的广播信息。这种情况下对于接收的信息一定是进行了加密处理的。同时在这种时候应当更新本机缓存的Server端公钥信息。于是这一段我在接收到信息后是这样改进的：

```python
def recv():
    global users
    while True:
        data = s.recv(4096)
        data_head = data.split(b'|*/*-*/*|')
        global Serverkey
        Serverkey = pk_loads(data_head[2])
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
        # 继续运行xxxxxx
```

> ***主动发送信息***
> > 聊天室嘛，肯定要发消息啦！根据设定，此时至少接收了一次Server端发送的广播信息，一定是知道Server的公钥的。这个时候就很方便了，标准的**公钥加密，私钥解密**啦！

```python
def send(*args):
    xxx # 组成文本框发送信息的编辑工作
    mes = entry.get() + ':;' + user + ':;' + chat  # 添加聊天对象标记
    send_data = rsa_.rsaEncrypt(str=mes, pubkey=Serverkey) + b'|*/*-*/*|' + md5(mes).encode()
    s.send(send_data)
    a.set('')  # 发送后清空文本框
```

### Server端的接发包设计

> ***广播发包方法sendata()***
>> 在主线程开启的同时，为了方便发包，在这边专门设计了一个线程用来广播发包或者针对局部用户发包

```python
# 线程开启
q = threading.Thread(target=self.sendData)
```

>> 关键源码：

```python
def sendData(self):
    while True:
        if not que.empty():
            data = ''
            reply_text = ''
            message = que.get()                               # 取出队列第一个元素
            if isinstance(message[1], str):                   # 如果data是str则返回Ture
                for i in range(len(users)):户名
                    for j in range(len(users)):
                        if message[0] == users[j][2]:
                            data = ' ' + users[j][1] + '：' + message[1]
                            outprint = "\033[32m[" + gettime() + "]\033[0m\033[35m" + str(message[0]) + "\033[0m" + "Receieve Message from \033[34m" + users[j][1] + "\033[0m.Value is \033[33m" + message[1].split(";:")[0] + "\033[0m "
                            log__ = "[" + gettime() + "]" + str(message[0]) + "Receieve Message from " + users[j][1] + ".Value is " + message[1].split(";:")[0]
                            break
                    users[i][0].send(rsa_.rsaEncrypt(str=data, pubkey=users[i][3]) + b'|*/*-*/*|' + md5(data).encode() + b'|*/*-*/*|' + pk_dumps(pubkey))
                try:
                    print(outprint)
                    log_(log__)
                except:
                    pass
            if isinstance(message[1], list):
                data = json.dumps(message[1])
                for i in range(len(users)):
                    try:
                        users[i][0].send(rsa_.rsaEncrypt(str=data, pubkey=users[i][3]) + b'|*/*-*/*|' + md5(data).encode() + b'|*/*-*/*|' + pk_dumps(pubkey))
                    except:
                        pass
```

>> **基本逻辑简单说明**
>>> - 首先广播发包分为两种情况，
>>> - 一是出现**用户登入/登出**的情况，这种情况下需要要求全体在线用户刷新各自Client界面，这就需要及时向Client端发送最新的用户信息，这边的设计是将其转化为列表的形式，相较于另一种方式的字符串格式，就很容易通过类型做出对应的判断了，列表格式通过**json.dump(list)**方法也可以较为轻松地实现一些功能。
>>> - 二是出现**用户发送信息**地情况，这也是Server需要转发信息最多的情况，这种消息的直接形式便是字符串形式，也是比较容易判断出来的。
>>
>> **加密套件使用展示**
>>
>> ```users[i][0].send(rsa_.rsaEncrypt(str=data, pubkey=users[i][3]) + b'|*/*-*/*|' + md5(data).encode() + b'|*/*-*/*|' + pk_dumps(pubkey))```
>>
>>* 发送了对应的数据报，对应的哈希值以及及时更新了Server的公钥


> ***针对单个用户的接包tcp_connect(self, conn, addr)方法***
>> Server端的最主要功能还得是接收客户端发来的数据呀，这边设计了一个**tcp_connect(self, conn, addr)**方法专门针对单个用户进行设置。下边的第一段是Server端的主程序中包含的一段调用该方法的代码段

```python
while True:
    conn, addr = self.s.accept()
    t = threading.Thread(target=self.tcp_connect, args=(conn, addr))
    t.start()
self.s.close()
```

>> 源码都放出来了（有删减），一个用户连接上来直接出现一个子线程来为其服务，直到用户退出的时候捕获到异常，才会结束当前这个线程，其中的解码我就把源码放在下边了

```python
    def tcp_connect(self, conn, addr):
        user = conn.recv(2048)
        user_head = user.split(b'|*/*-*/*|')
        xxxxxx  # 接收用户登录信息，送去分片处理
        if md5(user+salt) == md5_:
            pass
        else:# 身份验证无法通过则强制退出
            return None
        for i in range(len(users)):
            if user == users[i][1]:# 用户名冲突（已存在）则主动修改
                print('User  already exist')
                user = '' + user + '_2'
        if user == 'no':
            user = addr[0] + ':' + str(addr[1])
        users.append((conn, user, addr, client_key))
        xxxxx # 日志记录
        d = onlines()       # 发送信息要求Client更新在线用户列表
        self.recv(d, addr)
        print()
        try:
            while True:
                data = conn.recv(4096)
                xxxxx # 用户发送消息，并分片处理尔后进行验证
                if md5(data) == date_md5:
                    pass
                else:
                    print(Nonnnn)
                print(data)
                # 发送发出去的信息
                self.recv(data, addr)   # 保存信息到队列
            conn.close()
        except:
            # 删除用户
```

## 事后了解

> 阿西

这玩意儿的CPU占用率是真的高，云服务器跑了一会儿还以为谁来拿我机器挖矿去了呢.....

*top看了下后台心凉了半截（这玩意儿的服务器占用比我六七个docker外加好几个nginx站点都要高）*

[![](https://gitee.com/xiaolongtongxue/imagebed/raw/master/img/202205092102515.png)](https://gitee.com/xiaolongtongxue/imagebed/raw/master/img/202205092102515.png)

*云端的监控截图*

[![](https://gitee.com/xiaolongtongxue/imagebed/raw/master/img/202205092104548.png)](https://gitee.com/xiaolongtongxue/imagebed/raw/master/img/202205092104548.png)

> 阿西

通过对整个源代码的复盘分析,感觉到自己对于稍微大一点的项目，全局能力还不够强，可能还是因为写得少吧...之前哪个Java项目后台也是socket结构结果写成那个鸟样......

python的队列真是个好东西

基础架构决定上层建筑。架构师的重要性不言而喻

在因为某些原因导致信息安全作品赛失利之后，写完这个，感觉也能放下来一些了。未来的路还很长，那么就跑起来吧！少年！
