import pygame
from pygame.locals import *

from .actor import Actor
from .actor import Player, Wall, Enemy, Bullet, NPC
from .actor import Menu, Background

import vgame

class Map:
    def __init__(self,):
        pass


class Camera:
    '''
    主要负责处理镜头的处理，看看后续能够扩展出多少的功能。
    '''
    def __init__(self, width, height):
        self.w          = width
        self.h          = height
        self.camera     = pygame.Rect(0, 0, self.w, self.h)
        self.theater    = None
        self.follow     = None # 单角色跟随
        self.padding    = pygame.Vector2(200, 100)
        self.debug_area = None

        # 这里的处理稍微有点麻烦，因为要考虑到镜头的缩放
        # 有点类似于 死神vs火影 游戏中那种镜头拉远，两个角色始终在游戏屏幕中间的处理
        self.follows    = None # 尚在开发中的接口，后续将解决多角色跟随问题
        self.paddings   = None # 尚在开发中的接口，后续将解决多角色跟随问题

        self.margin     = pygame.Vector2(*((100, 100) if vgame.DEBUG else (0, 0))) # 调试时候使用，方便查看边界
        # self.margin     = pygame.Vector2(0, 0) # 调试时候使用，方便查看边界

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self):
        if self.follow:
            _x, _y = self.follow.rect.center
            x = -_x + int(self.w/2)
            y = -_y + int(self.h/2)
            x = min(self.margin.x, x) # top
            y = min(self.margin.y, y) # left
            x = max(x, -(self.theater.size[0] - self.w + self.margin.x)) # right
            y = max(y, -(self.theater.size[1] - self.h + self.margin.y)) # bottom
            self.camera = pygame.Rect(x, y, self.w, self.h)

    def debug_padding(self):
        if vgame.DEBUG:
            if not self.debug_area:
                showsize  = (int(self.padding.x), int(self.padding.y))
                showpoint = (self.w/2-self.padding.x/2, self.h/2-self.padding.y/2)
                self.debug_area = Actor((0,0,0,30), showsize=showsize, showpoint=showpoint)
            self.debug_area.imager._delay_bind_debug()
            # self.theater.screen.blit(self.debug_area.image, self.debug_area.rect)
            self.theater.screen.blit(self.debug_area.image, self.apply(self.debug_area))


class Theater:
    '''
    舞台对象，主要负责布景功能（地图信息主要就是放在这里）
    负责场景的资源加载（加载进全局，留下一个引用的结构）
    这样，已经加载的资源就不会再被加载进内存当中，并且
    调用资源仅仅需要通过自身的实例的绑定就能获取到
    '''
    def __init__(self,
                 theater_name,       # 场景名字，用于定位、调整、切换场景使用
                 background = None,  # 背景图片，可以传很多类型的数据，详细请看 Image 实例化时的参数
                 size = None,        # 游戏背景大小，背景大小如未设定则使用屏幕大小
                 camera_size = None, # 镜头的尺寸
                 ):

        game_screen = pygame.display.get_surface() # 游戏屏幕(镜头)显示的大小
        if game_screen is None:
            raise 'pls use vgame.Initer() to init game first.'

        self.screen       = game_screen
        self.screen_size  = self.screen.get_size()
        self.theater_name = theater_name
        self.size         = size if size else self.screen_size
        self.group        = pygame.sprite.Group()
        self.background   = None
        self.artist       = None
        self.camera       = self.regist_camera(Camera(*self.screen_size))

        # 用这个初始化不同场景下的物理检测的 Actor 列表
        Actor .RIGID_BODY[self.theater_name] = []
        Player.RIGID_BODY[self.theater_name] = []
        Wall  .RIGID_BODY[self.theater_name] = []
        Enemy .RIGID_BODY[self.theater_name] = []
        Bullet.RIGID_BODY[self.theater_name] = []
        NPC   .RIGID_BODY[self.theater_name] = []
        Menu  .RIGID_BODY[self.theater_name] = []

        # *暂未使用的参数，后续要考虑入场和出场的动画表演，否则切换场景会非常僵硬（至少要提供配置接口）
        # *后面可以考虑实现一些可配置的淡入淡出的效果
        self.enter        = None
        self.leave        = None

        # 初始化时可以传一张图片作为背景，也可以为空，透明的区域，用于限定游戏的范围，增加更多的可配置的空间
        # 主要用于限定镜头跟随的范围
        self._add_background(background if background else (0,0,0,0)) 

    def regist(self,*actors):
        for actor in actors:
            actor.theater = self
            if isinstance(actor, Actor):
                self.group.add(actor)

    def regist_camera(self, camera):
        camera.theater = self
        return camera

    def _add_background(self, background):
        self.background = Background(background, showsize=self.size)
        self.background.theater = self
        if self.background.image:
            self.group.add(self.background)
