import os, re
import traceback
from itertools import cycle, product

import pygame
from pygame.locals import *

from .controller import Controller

class Image:
    '''
    用于单个图片资源的加载，可以是动图但是
    '''
    def __init__(self, img=None, showsize=None, rate=0):
        # 一些默认配置，用于图片动画的刷新率，可以通过图片名字进行配置
        self.showsize  = showsize # 该参数仅用于对象
        self.rate      = rate # 不同的单位可以使用不同的速率
        self.actor     = None
        self.active    = None # 会在加载图片的时候根据图片类型自动设置
        self.src_image = None
        self.cur_tick  = 0
        self.rects     = None # 后续用于动图
        self.image     = self.load_img(img)
        self.mask      = pygame.mask.from_surface(self.image)

    def load_img(self,img):
        try:
            if img is None:
                image = pygame.Surface((60, 60)).convert_alpha()
                image.fill((255,255,255,255))
            elif isinstance(img, tuple):
                image = pygame.Surface((60, 60)).convert_alpha()
                image.fill(img)
            elif isinstance(img, str) and os.path.isdir(img):
                imgfs, imgfv = {}, []
                for idx, imgf in enumerate(sorted(os.listdir(img))):
                    v = tuple(map(int, re.findall(r'\d+', imgf)))
                    v = v if v else idx
                    imgfs[v] = imgf
                    imgfv.append(v)
                func = lambda i:pygame.image.load(os.path.join(img,i)).convert_alpha()
                all_rects = [func(imgfs[i]) for i in sorted(imgfv)]
                self.active    = True
                self.src_image = None
                self.cur_tick  = 0
                self.rects     = cycle(all_rects)
                image = next(self.rects)
            elif isinstance(img, str) and os.path.isfile(img):
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
        except:
            print("无法加载图片.",img)
            print(traceback.format_exc())
            image = None
        return image

    def update_image(self, ticks):
        if self.active and self._time_update(ticks):
            self.image = self.src_image.subsurface(next(self.rects)) if self.src_image else next(self.rects)
            if self.showsize: 
                self.image = pygame.transform.scale(self.image, self.showsize)
            self.mask  = pygame.mask.from_surface(self.image)
        # 显示 mask 边框线，让边框检测处理起来更加的直观
        if self.actor and (self.actor.debug or self.actor.DEBUG):
            pygame.draw.polygon(self.image, self.actor.DEBUG_MASK_LINE_CORLOR, self.mask.outline(), 1)

    def _time_update(self, ticks):
        if ticks - self.cur_tick > self.rate:
            self.cur_tick = ticks
            return True

class Idler:
    '''
    主要负责 actor 的一些持续行为，想要实现一些敌反馈机制
    目前开发的方向主要是想要能够通过 Actor 对象内直接调用到
    例如：
        act = Actor()
        act.idle
    '''
    def __init__(self):
        self.actor = None
        self.delay = 15 # 防止资源消耗过高
        self._tick = 0

    def update(self, ticks):
        if self._update_delay( ticks):
            return True

    def _update_delay(self,ticks):
        if ticks - self._tick > self.delay:
            self._tick = ticks
            return True

class Actor(pygame.sprite.Sprite):
    '''
    单位对象，主要负责一个单位的包装，如果设置了 in_control 为 True 可以让该单位接收控制信号
    控制信号可以通过重写对象的 mouse direction control 函数来从外部处理 actor 实例对控制的交互
    showsize 参数只有在 img 为 None或一个“3/4个数字表示颜色的tuple” 的时候才会有效
    用于修改当你没有填充任何图片的时候默认展示的色块的矩形的大小，方便于一些仅需色块的游戏演示
    如果主动传入了 img(Image类的对象)，那么传入 Image 的 showsize 即可。
    '''
    DEBUG = False # 方便让全部的 Actor 对象都使用 debug 模式，方便开发
    DEBUG_MASK_LINE_CORLOR = (0,255,0) # debug 模式将显示 actor 的 mask 边框线

    def __init__(self, img=None, in_control=False, showsize=None, debug=False):
        pygame.sprite.Sprite.__init__(self)

        # 后续这两行需要修改，因为角色的状态资源应该可以有多个，并且由于每个 Image 都要逆向绑定 Actor
        # 所以后续要考虑怎么更加合理的添加角色状态动画的处理
        self._image       = img if not (img is None or isinstance(img, tuple)) else Image(img, showsize)
        self._image.actor = self

        self.debug        = debug # 如果 DEBUG 为 False，这里为 True 则仅仅让该 Actor 这个对象用 debug 模式
        self.image        = self._image.image
        self.mask         = self._image.mask
        self.rect         = self.image.get_rect() if self.image else None
        self.theater      = None # 将该对象注册进 theater之后会自动绑定相应的 theater。
        self.controller   = self.regist_controller(Controller(in_control))
        self.computer     = self.regist_idle(Idler())

    def regist_idle(self,computer):
        computer.actor = self # 让事件对象能找到宿主本身
        self.computer  = computer # 这里是为了兼容外部 computer 的注册
        return computer

    def regist_controller(self,controller):
        controller.actor = self # 让事件对象能找到宿主本身
        self.controller  = controller # 这里是为了兼容外部 controller 的注册
        return controller

    def update(self,ticks):
        self._image.update_image(ticks)
        self.image = self._image.image
        self.mask  = self._image.mask
        i = self.computer.update(ticks)
        m, d, c = self.controller.update(ticks)
        # 根据函数的参数数量，来决定是否传入 Actor 对象自身。
        # 但是有时候传入自身可能会对新手造成一定困惑，我也不想一定要传入自身，下面的代码可以兼容两者
        if m: self.mouse(m)     if self.mouse.__code__.co_argcount     == 1 else self.mouse(self, m)
        if d: self.direction(d) if self.direction.__code__.co_argcount == 1 else self.direction(self, d)
        if c: self.control(c)   if self.control.__code__.co_argcount   == 1 else self.control(self, c)
        if i: self.idle()       if self.idle.__code__.co_argcount      == 0 else self.idle(self)

    def collide(self, *list_sprite):
        scollide = pygame.sprite.spritecollide(self, self.theater.group, False, pygame.sprite.collide_mask)
        rcollide = []
        for sprite in list_sprite:
            if sprite in scollide:
                rcollide.append(sprite)
        return rcollide

    @staticmethod
    def mouse(mouse_info): pass

    @staticmethod
    def direction(direction_info): pass

    @staticmethod
    def control(control_info): pass

    @staticmethod
    def idle(): pass