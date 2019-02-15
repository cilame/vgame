import re
import traceback
from itertools import cycle, product

import pygame
from pygame.locals import *

from .events import events

class actor(pygame.sprite.Sprite):
    '''
    #====================================================================
    # 行为对象，主要用于实现更方便的加载图片资源的方法
    #====================================================================
    '''
    def __init__(self, img=None, point=None, action=None, event_rate=60):
        pygame.sprite.Sprite.__init__(self)

        self.active     = False
        self.point      = point # point参数，如果theater里面存在blocks，point被设置就放置在坐标位置

        # 一些默认配置，用于图片动画的刷新率，可以通过图片名字进行配置，注意这里的配置要放在self.load_img(img)函数之前
        # self.load_img(img)函数过后，如果有匹配到图片名字的配置，会自动配置新的参数。防止图片加载失败报错弹出。
        self.rate       = 0
        self.cur_tick   = 0

        # 加载图片倘若名字符合动图处理规则加载函数内就会修改self.active，用动图处理方式
        self.image      = self.load_img(img)
        self.rect       = self.image.get_rect() if self.image else None
        self.theater    = None # 将该对象注册进 theater之后会自动绑定相应的 theater。
        self.viscous    = False

        self.events     = self.regist(events(action, event_rate))

        self.init_toggle= True # 测试使用的参数，后期可能删除，重新设计

    def load_img(self,img):
        if img is None: return None
        try:
            image = pygame.image.load(img).convert_alpha()
            # 后面判断是否使用动态展示图片
            # 就是一种更为方便的配置图片数据的方法。原本打算用gif的，不过考虑到gif需要外部库
            # 而且经过测试，图片缩小方法似乎并不好用。所以暂时放弃兼容gif。
            # 后续必须考虑兼容，因为用任意gif作为角色确实很有意思。
            # ...
            #
            # 如果图片以例如 someimg_100x100_32.png 的名字存储的话，则会识别成动态图
            # 100x100代表单帧图片的大小，32代表了动态速率
            # 请尽量将名字配置中的100x100与长宽成倍数比，详细判定规则见下面这行代码
            # 下面的代码还是在配置上稍微有一些局限，比如原图有200x200只取三张100x100的图，目前就无法配置
            # 后续遇到其他情况再改
            # ...
            move = re.findall('_(\d+)x(\d+)_(\d+)\.',img.lower())
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
            traceback.print_exc()
            print("无法加载图片.",img)
            image = None

        return image


    def regist(self,events):
        events.actor = self # 让事件对象能找到宿主本身
        self.events = events # 这里是为了兼容外部events的注册
        return events


    def update(self,ticks):

        if self.active and self._time_update(ticks):
            self.image = self.src_image.subsurface(next(self.rects))
            # 通过以下方法可以实现修改图片大小，不过由于修改大小这部应该会消耗资源，
            # 每次加载都要修改一次大小，所以之后考虑优化的方式，让速度变得更快一些
            # 或者可以考虑放在 self.load_img函数当中，地图切块时需要考虑单元块的适配？
            # 将 actor注册进 theater可以获取 theater里面设定的单位大小，后续可能需要扩展多格单位
            # 另外，这里的配置也不太科学，写太死了，后续再改。目前用于测试比较方便。
            self.image = pygame.transform.scale(self.image,self.theater.single)

        self.events.update(ticks)

        # 测试时候使用的部分
        if self.init_toggle:
            self.init_property()
            self.init_toggle = False
        
        # 测试删除对象本身，后期删除
        if pygame.key.get_pressed()[K_q]:# 键盘q键删除自身单位
            self.kill()


    # 黏性方块，让该对象具备blocks黏性，传入参数可以是地图坐标，或者是一个鼠标坐标
    # 如果该 actor所在的 theater没有进行 blocks切分，那么就返回空，不整齐的地址也会返回空
    def rect_viscous(self,point=None):

        # 需要参与计算的环境参数有
        sizex,sizey = self.theater.artist.screen.get_size()
        diffw,diffh = self.theater.screen_pos
        singw,singh = self.theater.single
        point2coord = self.theater.point2coord

        # 如果 point为一个地图坐标，就获取坐标的界面坐标地址
        if point:
            if point in point2coord:
                _mapx,_mapy = point2coord[point]
                _mapx,_mapy = _mapx + diffw,_mapy + diffh
                return (int(_mapx),int(_mapy)),point

        # 如果 point为 None就获取的是鼠标地址下的方块左上角的坐标
        else:
            posx,posy = pygame.mouse.get_pos()
            mapx,mapy = posx - diffw,posy - diffh
            cols,raws = self.theater.blocks
            point = max(min(int(mapx/singw),cols-1),0),max(min(int(mapy/singh),raws-1),0)
            if point in point2coord:
                _mapx,_mapy = point2coord[point]
                _mapx,_mapy = _mapx + diffw,_mapy + diffh
                return (int(_mapx),int(_mapy)),point # 该函数同样返回坐标点数据，便于鼠标与数据交互

    # 通过方块坐标修改角色当前坐标
    def change_point(self,point):
        rect,point   = self.rect_viscous(point)
        self.rect    = rect
        self.point   = point

    # 后期很可能删除的函数
    def init_property(self):
        x, y = pygame.mouse.get_pos()
        x-= self.image.get_width() // 2
        y-= self.image.get_height() // 2
        v = self.rect_viscous(self.point) # 方块黏性测试
        if v:
            self.change_point(v[1])
        else:
            self.rect[0] = x
            self.rect[1] = y

    # 控制速率的函数，使任意帧率情况下都保持相同速度的函数
    def _time_update(self,ticks):
        if ticks - self.cur_tick > self.rate:
            self.cur_tick = ticks
            return True