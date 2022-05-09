"""
@Project ：python-chat-PLUS 
@File    ：coding.py
@Author  ：TXL
@Date    ：2022/5/6 11:30 
"""
# -*- coding: UTF-8 -*-
from Crypto.Cipher import DES3
import rsa
import random

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

def random_str(lens=5):
    return ''.join(random.sample(['z', 'y', 'x', 'w', 'v', 'u', 't', 's', 'r', 'q', 'p', 'o', 'n', 'm', 'l', 'k', 'j', 'i', 'h', 'g', 'f', 'e', 'd', 'c', 'b', 'a'], lens))