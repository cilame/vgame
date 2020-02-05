import re
import traceback
from itertools import cycle, product

import pygame
from pygame.locals import *

from .events import Events

class Actor(pygame.sprite.Sprite):
    '''
    #====================================================================
    # 行为对象，主要用于实现更方便的加载图片资源的方法
    #====================================================================
    '''
    def __init__(self, img=None, showsize=None, event_rate=60, in_control=False):
        pygame.sprite.Sprite.__init__(self)

        self.active   = False # 能自己动的图片，类似动图的处理。会在加载图片的时候进行自动设置。
        self.showsize = showsize

        # 一些默认配置，用于图片动画的刷新率，可以通过图片名字进行配置，注意这里的配置要放在self.load_img(img)函数之前
        # self.load_img(img)函数过后，如果有匹配到图片名字的配置，会自动配置新的参数。防止图片加载失败报错弹出。
        self.rate     = 0
        self.cur_tick = 0

        # 加载图片倘若名字符合动图处理规则加载函数内就会修改self.active，用动图处理方式
        self.image    = self.load_img(img)
        self.rect     = self.image.get_rect() if self.image else None
        self.theater  = None # 将该对象注册进 theater之后会自动绑定相应的 theater。
        self.events   = self.regist(Events(event_rate, in_control))

    def load_img(self,img):
        if img is None: return None
        try:
            image = pygame.image.load(img).convert_alpha()
            move = re.findall(r'_(\d+)x(\d+)_(\d+)\.', img.lower())
            if move:
                move = list(map(int,move[0]))
                self.active = True
                src_h,src_w = image.get_height(),image.get_width()
                pro_h,pro_w = move[:2]
                nraws,ncols = int(src_h/pro_h),int(src_w/pro_w)
                mfunc       = lambda i:(i[0]*pro_w, i[1]*pro_h, pro_w, pro_h)
                all_rects   = list(map(mfunc,product(range(ncols),range(nraws)))) # 后期可以添加配置参数考虑用切片方式操作这里

                self.src_image  = image
                self.rate       = move[2] # 用于控制速率
                self.cur_tick   = 0
                self.rects      = cycle(all_rects)
        except:
            print("无法加载图片.",img)
            print(traceback.format_exc())
            image = None
        return image

    def regist(self,events):
        events.actor = self # 让事件对象能找到宿主本身
        self.events = events # 这里是为了兼容外部events的注册
        return events

    def update(self,ticks):
        if self.active and self._time_update(ticks):
            self.image = self.src_image.subsurface(next(self.rects))
            if self.showsize:
                self.image = pygame.transform.scale(self.image, self.showsize)

        self.events.update(ticks)

        # 测试删除对象本身，后期删除
        if pygame.key.get_pressed()[K_q]:# 键盘q键删除自身单位
            self.kill()

    # 控制速率的函数，使任意帧率情况下都保持相同速度的函数
    def _time_update(self,ticks):
        if ticks - self.cur_tick > self.rate:
            self.cur_tick = ticks
            return True