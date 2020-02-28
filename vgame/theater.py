import pygame
from pygame.locals import *

from .actor import Actor
from .actor import Player, Wall, Enemy, Bullet, NPC, Menu



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
        self.padding    = pygame.Vector2(100, 100) # 被镜头跟随的角色的在游戏屏幕中间的长宽范围

        # 这里的处理稍微有点麻烦，因为要考虑到镜头的缩放
        # 有点类似于 死神vs火影 游戏中那种镜头拉远，两个角色始终在游戏屏幕中间的处理
        self.follows    = None # 尚在开发中的接口，后续将解决多角色跟随问题
        self.paddings   = None # 尚在开发中的接口，后续将解决多角色跟随问题

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self):
        if self.follow:
            x, y = self.follow.rect.center
            x = -x + int(self.w/2)
            y = -y + int(self.h/2)
            x = min(self.padding.x, x)
            y = min(self.padding.y, y)
            x = max(x, -(self.w - self.w + self.padding.x))
            y = max(y, -(self.h - self.h + self.padding.y))
            self.camera = pygame.Rect(x, y, self.w, self.h)

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
                 camera_size = None, # 镜头的尺寸
                 ):

        game_screen = pygame.display.get_surface()
        if game_screen is None:
            raise 'pls use vgame.Initer() to init game first.'

        self.screen         = game_screen
        self.screen_size    = self.screen.get_size()
        self.theater_name   = theater_name
        self.group          = pygame.sprite.Group()
        self.background     = None
        self.artist         = None
        self.camera         = self.regist_camera(Camera(*self.screen.get_size()))

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
        self.enter          = None
        self.leave          = None

        # 初始化时可以传一张图片作为背景，也可以为空，默认会使用
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
        self.background = Actor(background, showsize=self.screen_size, in_entity=False)
        self.background.theater = self
        if self.background.image:
            self.group.add(self.background)
