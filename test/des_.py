"""
@Project ：python-chat-PLUS 
@File    ：des_.py
@Author  ：TXL
@Date    ：2022/5/6 11:26 
"""
# -*- coding: UTF-8 -*-

from Crypto.Cipher import DES3
import codecs
import base64

class EncryptDate:
    def __init__(self, key):
        self.key = key  # 初始化密钥
        self.length = DES3.block_size  # 初始化数据块大小
        self.aes = DES3.new(self.key, DES3.MODE_CBC, b'12345678')  # 初始化AES,ECB模式的实例
        # 截断函数，去除填充的字符
        self.unpad = lambda date: date[0:-ord(date[-1])]

    def pad(self, text):
        """
        #填充函数，使被加密数据的字节码长度是block_size的整数倍
        """
        count = len(text.encode('utf-8'))
        add = self.length - (count % self.length)
        entext = text + (chr(add) * add)
        return entext

    def encrypt(self, encrData):  # 加密函数
        res = self.aes.encrypt(self.pad(encrData).encode("utf8"))
        # msg = str(base64.b64encode(res), encoding="utf8")
        msg =  res.hex()
        return msg

    def decrypt(self, decrData):  # 解密函数
        # res = base64.decodebytes(decrData.encode("utf8"))
        res = bytes.fromhex(decrData)
        # print("*"*30)
        # print(self.aes.decrypt(res).decode("utf8"))
        # print("*"*30)
        msg = self.aes.decrypt(res).decode("utf8")
        # print("*-"*15)
        # print(self.aes.decrypt(res))
        # print("*-" * 15)
        return self.unpad(msg)

# eg1 = EncryptDate("xiaolongtongxue#")
eg = EncryptDate("xiaolongtongxue#")  # 这里密钥的长度必须是16的倍数
res = eg.encrypt("zhangs")
print(res)
eg1 = EncryptDate("xiaolongtongxue#")
print(eg1.decrypt(res))
eg1 = EncryptDate("xiaolongtongxue#")
print(eg1.decrypt("b6ddac8fb6d91f3960d12beb4cf3dbbe121e573478d7c625"))
