"""
@Project ：python-chat-PLUS 
@File    ：to_byte.py
@Author  ：TXL
@Date    ：2022/5/9 10:47 
"""
# -*- coding: UTF-8 -*-
import pickle as pk

def pk_dumps(_object: object):
    return pk.dumps(_object)

def pk_loads(_object: bytes):
    return pk.loads(_object)