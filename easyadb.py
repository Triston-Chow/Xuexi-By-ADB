#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   easyadb.py
@Time    :   2020/03/30
@Version :   1.0
@Author  :   Triston Chow
@Contact :   triston2021@outlook.com
@License :   (C)Copyright 2020-2021, Triston Chow
@Desc    :   封装常用ADB指令，简化调用操作
'''


import os
import subprocess


class EasyADB:
    def __init__(self, device_tag=''):
        if device_tag == '':
            self.adb = 'adb'
        else:
            if device_tag.isdecimal():
                self.adb = f'adb -t {device_tag}'
            else:
                self.adb = f'adb -s {device_tag}'
        
        self.KEY = {
            'power':26, 'menu':82, 'home':3, 'back':4,
            'volume_up':24, 'volume_down':25, 'volume_mute':164,
            'screen_on':224, 'screen_off':223
        }
        
        self.APP = {
            '抖音':'com.ss.android.ugc.aweme/.splash.SplashActivity',
            '抖音极速版':'com.ss.android.ugc.aweme.lite/com.ss.android.ugc.aweme.main.MainActivity',
            '快手极速版':'com.kuaishou.nebula/com.yxcorp.gifshow.HomeActivity',
            '学习强国':'cn.xuexi.android/com.alibaba.android.rimet.biz.SplashActivity'
        }
        
        self.cwd = os.path.abspath(os.path.dirname(__file__)).replace('\\', '/')
        
        os.system(f'{self.adb} start-server')
    
    
    def showDeviceInfo(self):
        os.system(f'{self.adb} devices -l')
    
    
    def showActivity(self):
        os.system(f'{self.adb} shell dumpsys activity activities | findstr mResumedActivity')
    
    
    def startAPP(self, appname:str) -> bool:
        # 此处使用subprocess.Popen是为了捕获错误信息
        with subprocess.Popen(
            f'{self.adb} shell am start -n {self.APP[appname]}',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as p:
            result = p.stdout.read()
            error = p.stderr.read()
        
        if error == b'':
            print(str(result, encoding='utf-8'))
            return True
        else:
            print(str(error, encoding='utf-8'))
            return False
    
    
    def touchScreen(self, x, y):
        os.system(f'{self.adb} shell input tap {x} {y}')
    
    
    def swipeScreen(self, start_x, start_y, end_x, end_y, duration = ''):
        os.system(f'{self.adb} shell input swipe {start_x} {start_y} {end_x} {end_y} {duration}')
    
    
    def pressKeyCode(self, keycode):
        os.system(f'{self.adb} shell input keyevent {keycode}')
    
    
    def longPressKeyCode(self, keycode):
        os.system(f'{self.adb} shell input keyevent --longpress {keycode}')
    
    
    def pressKey(self, keyname):
        os.system(f'{self.adb} shell input keyevent {self.KEY[keyname]}')
    
    
    def uiDump(self, device_path=''):
        # 此处使用subprocess.Popen是为了避免控制台打印错误信息
        with subprocess.Popen(
            f'{self.adb} shell uiautomator dump --compressed {device_path}',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            ) as p:
            result = p.stdout.read()
        result = str(result, encoding='utf-8')
        
        if 'dumped to:' in result:
            return result.split()[-1]
    
    
    def pullFile(self, device_path, local_path=''):
        with subprocess.Popen(
            f'{self.adb} pull {device_path} {local_path}',
            shell=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            ) as p:
            result = p.stdout.read()
        result = str(result, encoding='utf-8')
        
        if 'pulled' in result:
            if local_path == '':
                local_path = f'{self.cwd}/{os.path.split(device_path)[-1]}'
            return local_path