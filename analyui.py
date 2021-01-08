#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   analyui.py
@Time    :   2021/01/05
@Version :   1.0
@Author  :   Triston Chow
@Contact :   triston2021@outlook.com
@License :   (C)Copyright 2020-2021, Triston Chow
@Desc    :   通过文本方式分析ADB dump文件，获取UI信息
'''


import os
from easyadb import EasyADB


class AnalyUIText(EasyADB):
    def __init__(self, device_tag=''):
        super().__init__(device_tag)
        
        if device_tag == '':
            self.device_tag = 'dev'
        else:
            self.device_tag = device_tag
        
        self.__dump_count = 0
    
    
    def gen_ui_lines(self) -> list:
        '''
        dump设备当前的UI层级文件并复制到本地当前目录下
        读取UI层级文件并按标签分行，作为列表返回
        '''
        if (device_path := self.uiDump()) != None:
            local_path = f'{self.cwd}/{self.device_tag}_ui_{self.__dump_count:03d}.xml'
            self.__dump_count += 1
            if (uifile := self.pullFile(device_path, local_path)) != None:
                with open(uifile, encoding='utf-8') as f:
                    result = f.read().split('>')
                os.remove(uifile)
                return result
    
    
    def get_click_coords(self, line:str, point:str) -> tuple:
        '''
        从UI层级文件的一行文本中分离出元素界限坐标范围
        再根据预定规则生成触摸点位置坐标值
        '''
        bounds = line.split('bounds=')[-1].strip('"[]" /').replace('][', ',').split(',')
        x1, y1, x2, y2 = [int(b) for b in bounds]
        if point == 'start':
            return x1, y1
        elif point == 'end':
            return x2, y2
        elif point == 'center':
            return (x2-x1)//2 + x1, (y2-y1)//2 + y1
        elif point == 'article_top':
            return x2-100, y2+10
        elif point == 'article_bottom':
            return x2-100, y1-10
    
    
    def find_text_in_ui(self, keywords:str, getcoords=False):
        '''
        逐行查找UI层级文件,匹配关键词,返回bool或者坐标值
        '''
        if (lines := self.gen_ui_lines()) != None:
            for line in lines:
                if keywords in line:
                    if getcoords:
                        return self.get_click_coords(line, 'center')
                    else:
                        return True
            if getcoords:
                print('当前页中找不到指定元素！\n')
                exit(0)
            else:
                return False