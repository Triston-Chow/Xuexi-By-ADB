#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   xuexi.py
@Time    :   2021/01/07
@Version :   1.0
@Author  :   Triston Chow
@Contact :   triston2021@outlook.com
@License :   (C)Copyright 2020-2021, Triston Chow
@Desc    :   基于ADB的“学习强国”APP自动化脚本
'''


import sys
import time
import re
from analyui import AnalyUIText


class XuexiByADB(AnalyUIText):
    def __init__(self, device_tag):
        super().__init__(device_tag)
    
    
    def select_topic(self, pattern:str, week_sn:int):
        week = ('星期一', '星期二', '星期三', '星期四', '星期五', '星期六', '星期日')
        topics = {
            'article':((0,'重要活动'), (0,'重要会议'), (0,'重要讲话'), (0,'重要文章'), (1,'重要学习'), (1,'指示批示'), (4,'学习金句')),
            'video':((0,'学习新视界'), (0,'奋斗新时代'), (0,'强军之路'), (0,'绿水青山'), (1,'一带一路'), (1,'初心使命'), (1,'强国建设'))
        }
        
        print(f'\r正在定位到学习栏目，请稍候...', end='')
        
        if pattern == 'article':
            x, y = self.find_text_in_ui('text="新思想"', getcoords=True)
            self.touchScreen(x, y)
        elif pattern == 'video':
            x, y = self.find_text_in_ui('text="电视台"', getcoords=True)
            self.touchScreen(x, y)
            x, y = self.find_text_in_ui('text="学习视频"', getcoords=True)
            self.touchScreen(x, y)
        
        x1, y1 = self.find_text_in_ui(f'text="{topics[pattern][0][1]}"', getcoords=True)
        x2, y2 = self.find_text_in_ui(f'text="{topics[pattern][3][1]}"', getcoords=True)
        
        times, topic = topics[pattern][week_sn]
        print(f'\r今天是{week[week_sn]}，按计划学习【{topic}】')
        
        for i in range(times):
            self.swipeScreen(x2, y2, x1, y1, 600)
        
        x, y = self.find_text_in_ui(f'text="{topic}"', getcoords=True)
        self.touchScreen(x, y)
    
    
    def get_article_titles(self) -> list:
        title_lines = []  # 第一遍过滤后得到的含有标题行列表
        result = []  # 返回结果列表
        
        if (lines := self.gen_ui_lines()) != None:
            for line in lines:
                if 'general_card_title_id' in line:
                    title_lines.append(line)
            
            for line in title_lines:
                text = line.split('" ')[1].strip('text="')
                '''
                根据标题的位置(最上、最下、中间)设定点击坐标
                '''
                if line == title_lines[0]:
                    x, y = self.get_click_coords(line, 'article_top')
                elif line == title_lines[-1]:
                    x, y = self.get_click_coords(line, 'article_bottom')
                else:
                    x, y = self.get_click_coords(line, 'center')
                
                result.append({'text':text, 'coords':(x,y)})
        return result
    
    
    def get_video_titles(self) -> list:
        usable_lines = []  # 第一遍过滤后得到的可用行列表
        result = []  # 返回结果列表
        title_flag = False  # 标志前一行文本内容为时间长度“mm:ss”形式
        
        avoid_keywords = {
            '强国通', '百灵', '电视台', '电台',
            '积分', '第一频道', '学习视频', '联播频道', '看电视', '看理论',
            '中央广播电视总台', '新华社', '央视新闻', '央视网', '央视频', '人民日报',
            '学习新视界', '奋斗新时代', '强军之路', '绿水青山', '一带一路', '初心使命', '强国建设',
            }
        
        if (lines := self.gen_ui_lines()) != None:
            for line in lines:
                if 'index="0"'in line or 'index="1"' in line:
                    if 'text=' in line and 'text=""' not in line:
                        usable_lines.append(line)
            
            for line in usable_lines:
                text = line.split('" ')[1].strip('text="')
                if text not in avoid_keywords and not text.isdecimal():
                    '''
                    正则匹配文本内容是否为时间长度“mm:ss”形式，且范围从'0:00'至'23:59'
                    若匹配，则取文本内容和坐标值，并将操作下一行的标志变量置为True
                    若不匹配，根据标志变量状态添加记录
                    '''
                    match_length = re.compile(r'^(([0-9]{1})|([0-1][0-9])|([1-2][0-3])):([0-5][0-9])$').search(text)
                    if match_length != None:
                        length = match_length.group()
                        x, y = self.get_click_coords(line, 'start')
                        title_flag = True
                    else:
                        if title_flag:
                            result.append({'text':text, 'length':length, 'coords':(x,y)})
                            title_flag = False
        return result
    
    
    def xuexi(self, pattern:str):
        count = 0  # 已完成数
        total_time = 0  # 已完成总秒数
        completed = []  # 已完成的标题列表
        new_title = True  # 主循环条件(执行开关)
        trigger_keywords = {
            'name': {'article': '篇文章', 'video': '条视频'},
            'back': {'article': 'text="观点"', 'video': 'text="重新播放"'},
            'maxlen': {'article': 40, 'video': 36},
            'passtime': {'article': 370, 'video': 390}
            }
        
        print('='*120)
        
        while new_title:
            if self.find_text_in_ui('你已经看到我的底线了'):
                new_title = False
            
            '''
            取当前页面所展示的文章或视频标题列表
            '''
            if pattern == 'article':
                titles = self.get_article_titles()
            elif pattern == 'video':
                titles = self.get_video_titles()
            else:
                titles = []
            
            if titles == []:
                print('当前页中找不到标题！')
                new_title = False
            else:
                '''
                遍历标题列表(for循环)
                若当前标题未被点击过则点击进入
                循环检测页面，出现标志结束的关键字时，返回原页面
                检查是否满足每日积分上限条件，若满足则结束遍历(退出for循环)
                '''
                for title in titles:
                    if title['text'] not in completed:
                        x, y = title['coords']
                        self.touchScreen(x, y)
                        
                        count += 1
                        print(f'第{count}{trigger_keywords["name"][pattern]} => '.rjust(10), end='')
                        if len(text := title['text']) > (maxlen := trigger_keywords["maxlen"][pattern]):
                            text = text[:maxlen] + '...'
                        
                        if pattern == 'video':
                            print(f'{text} ({title["length"]})')
                        else:
                            print(text)
                        
                        start_cputime = time.perf_counter()
                        while True:
                            if self.find_text_in_ui(trigger_keywords["back"][pattern]):
                                break
                            else:
                                if pattern == 'article':
                                    self.swipeScreen(540, 1440, 540, 480, 2000)
                                elif pattern == 'video':
                                    time.sleep(6)
                        single_time = time.perf_counter()- start_cputime
                        
                        print(f'<第{count}{trigger_keywords["name"][pattern]}耗时：{single_time:6.2f}s>'.rjust(113, '-'))
                        self.pressKey('back')
                        
                        completed.append(title['text'])
                        total_time += single_time
                        
                        if count >= 6 and total_time >= trigger_keywords["passtime"][pattern]:
                            new_title = False
                            break
                        time.sleep(1)
            '''
            若主循环未结束则上滑更新标题列表页面
            '''
            if new_title:
                self.swipeScreen(540, 1400, 540, 520)
        
        print('='*120)
        print(f'累计耗时：{total_time/60:6.2f}m '.rjust(115))
    
    
    def auto_xuexi(self):
        if self.startAPP('学习强国'):
            for i in range(12, 0, -1):
                print(f'\r正在启动应用，{i:02d}秒后开始学习。', end='')
                time.sleep(1)
            
            week_sn = time.localtime().tm_wday
            
            self.select_topic('article', week_sn)
            self.xuexi('article')
            
            print('\n')
            self.select_topic('video', week_sn)
            self.xuexi('video')


def main():
    try:
        arg1 = sys.argv[1]
    except IndexError:
        arg1 = '-a'
    
    try:
        arg2 = sys.argv[2]
    except IndexError:
        arg2 = ''
    
    tips ='''
    参数错误！
    
    第一个参数必须为下列开关选项：
    -a：全自动运行
    -d：列出当前连接的所有设备
    -t：手动启动应用，手动选择栏目，自动阅读文章
    -v：手动启动应用，手动选择栏目，自动播放视频
    '''
    
    mode = {
        '-a':'xuexi.auto_xuexi()',
        '-d':'xuexi.showDeviceInfo()',
        '-t':'xuexi.xuexi("article")',
        '-v':'xuexi.xuexi("video")'
        }
    
    try:
        cmd = mode[arg1]
    except KeyError:
        print(tips)
    else:
        xuexi = XuexiByADB(arg2)
        exec(cmd)


if __name__ =='__main__':
    main()