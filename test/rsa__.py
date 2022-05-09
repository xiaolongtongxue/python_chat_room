"""
@Project ：python-chat-PLUS 
@File    ：rsa.py
@Author  ：TXL
@Date    ：2022/5/6 10:22 
"""
# -*- coding: UTF-8 -*-
import rsa


# rsa加密
def rsaEncrypt(str, pubkey):
    # 生成公钥、私钥

    # 明文编码格式
    content = str.encode("utf-8")
    # 公钥加密
    crypto = rsa.encrypt(content, pubkey)
    return crypto


# rsa解密
def rsaDecrypt(str, pk):
    # 私钥解密
    content = rsa.decrypt(str, pk)
    con = content.decode("utf-8")
    return con


if __name__ == "__main__":
    (pubkey, privkey) = rsa.newkeys(512)
    print("公钥:\n%s\n私钥:\n%s" % (pubkey, privkey))
    # print(pubkey)
    # print(type(pubkey))
    # print(type(privkey))

    str = rsaEncrypt(str="password", pubkey = pubkey)
    print(type(str))
    print("加密后密文：\n%s" % str)

    content = rsaDecrypt(str, privkey)
    print("解密后明文：\n%s" % content)
    print(type(content))

    pass




