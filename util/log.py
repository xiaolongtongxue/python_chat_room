"""
@Project ：python-chat 
@File    ：log.py
@Author  ：TXL
@Date    ：2022/5/4 10:34 
"""
# -*- coding: UTF-8 -*-
def log_(loging: str):
    with open("log/log.log", "a") as file:
        file.write(loging + "\n")