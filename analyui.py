#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   analyui.py
@Time    :   2021/01/11
@Version :   1.0.1
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
        
        self._dump_count = 0
        self._ui_lines = []
    
    
    def gen_ui_lines(self) -> list:
        result = []
        '''
        dump设备当前的UI层级文件并复制到本地当前目录下
        读取UI层级文件并提取文本显示组件，作为列表返回
        '''
        if (device_path := self.uiDump()) != None:
            local_path = f'{self.cwd}/{self.device_tag}_ui_{self._dump_count:03d}.xml'
            self._dump_count += 1
            if (uifile := self.pullFile(device_path, local_path)) != None:
                with open(uifile, encoding='utf-8') as f:
                    lines = f.read().split('>')
                result = [line for line in lines if 'class="android.widget.TextView"' in line]
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
    
    
    def find_ui_text(self, keyword:str, getcoords=False, redump=True):
        '''
        逐行查找UI层级文件,匹配单个关键词,返回bool或坐标值
        '''
        if redump:
            self._ui_lines = self.gen_ui_lines()
        
        for line in self._ui_lines:
            if keyword in line:
                if getcoords:
                    return self.get_click_coords(line, 'center')
                else:
                    return True
        
        if getcoords:
            print('当前页中找不到指定元素！\n')
            exit(0)
        else:
            return False
    
    
    def find_ui_multi_text(self, *keywords, getcoords=False):
        result = {}
        '''
        逐行查找UI层级文件,匹配多个关键词,返回包含bool和坐标值的字典
        '''
        if (lines := self._ui_lines) != []:
            for i, keyword in enumerate(keywords) :
                found = False
                for line in lines:
                    if keyword in line:
                        found = True
                        if getcoords:
                            coords = self.get_click_coords(line, 'center')
                        else:
                            coords = ()
                        break
                if not found:
                    coords = ()
                result.update({i:{'found':found, 'coords':coords}})
            return result
