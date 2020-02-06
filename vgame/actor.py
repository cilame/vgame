import re
import traceback
from itertools import cycle, product

import pygame
from pygame.locals import *

from .events import Events

class Image:
    '''
    用于单个图片资源的加载，可以是动图但是
    '''
    def __init__(self, img, showsize=None, rate=0):
        # 一些默认配置，用于图片动画的刷新率，可以通过图片名字进行配置
        self.showsize  = showsize # 该参数仅用于对象
        self.rate      = rate # 不同的单位可以使用不同的速率
        self.active    = None # 会在加载图片的时候根据图片类型自动设置
        self.src_image = None
        self.cur_tick  = 0
        self.rects     = None # 后续用于动图
        self.image     = self.load_img(img)
        self.mask      = pygame.mask.from_surface(self.image)

    def load_img(self,img):
        try:
            image = pygame.image.load(img).convert_alpha()
            move = re.findall(r'_(\d+)x(\d+)\.', img.lower()) # 根据图片的命名自动切割图片，生成动图
            if move:
                move        = list(map(int,move[0]))
                src_h,src_w = image.get_height(),image.get_width()
                pro_h,pro_w = move[:2]
                nraws,ncols = int(src_h/pro_h),int(src_w/pro_w)
                mfunc       = lambda i:(i[0]*pro_w, i[1]*pro_h, pro_w, pro_h)
                all_rects   = list(map(mfunc,product(range(ncols),range(nraws))))

                self.active    = True
                self.src_image = image
                self.cur_tick  = 0
                self.rects     = cycle(all_rects)
                image = self.src_image.subsurface(next(self.rects))
                if self.showsize:
                    image = pygame.transform.scale(image, self.showsize)
            else:
                if self.showsize:
                    image = pygame.transform.scale(image, self.showsize)
        except:
            print("无法加载图片.",img)
            print(traceback.format_exc())
            image = None
        return image

    def update_image(self, ticks):
        if self.active and self._time_update(ticks):
            self.image = self.src_image.subsurface(next(self.rects))
            if self.showsize:
                self.image = pygame.transform.scale(self.image, self.showsize)
                self.mask  = pygame.mask.from_surface(self.image)

    # 控制速率的函数，解耦单位的动图显示速率
    def _time_update(self, ticks):
        if ticks - self.cur_tick > self.rate:
            self.cur_tick = ticks
            return True

class Actor(pygame.sprite.Sprite):
    '''
    单位对象，主要负责一个单位的包装，如果设置了 in_control 为 True 可以让该单位接收控制信号
    控制信号可以通过重写对象的 mouse direction control 函数来从外部处理 actor 实例对控制的交互
    '''
    def __init__(self, img=None, event_rate=60, in_control=False):
        pygame.sprite.Sprite.__init__(self)
        self._image  = img
        self.image   = self._image.image
        self.mask    = self._image.mask
        self.rect    = self.image.get_rect() if self.image else None
        self.theater = None # 将该对象注册进 theater之后会自动绑定相应的 theater。
        self.events  = self.regist(Events(event_rate, in_control))

    def regist(self,events):
        events.actor = self # 让事件对象能找到宿主本身
        self.events = events # 这里是为了兼容外部events的注册
        return events

    def update(self,ticks):
        self._image.update_image(ticks)
        self.image = self._image.image
        self.mask  = self._image.mask
        m, d, c = self.events.update(ticks)
        if m: self.mouse(m)
        if d: self.direction(d)
        if c: self.control(c)

    def collide(self, *list_sprite):
        scollide = pygame.sprite.spritecollide(self, self.theater.group, False, pygame.sprite.collide_mask)
        rcollide = []
        for sprite in list_sprite:
            if (sprite in scollide):
                rcollide.append(sprite)
        return rcollide

    @staticmethod
    def mouse(mouse_info): pass

    @staticmethod
    def direction(direction_info): pass

    @staticmethod
    def control(control_info): pass