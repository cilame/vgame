import pygame
from pygame.locals import *

from .actor import Actor

class Theater:
    '''
    舞台对象，主要负责布景功能（地图信息主要就是放在这里）
    负责场景的资源加载（加载进全局，留下一个引用的结构）
    这样，已经加载的资源就不会再被加载进内存当中，并且
    调用资源仅仅需要通过自身的实例的绑定就能获取到
    '''
    def __init__(self,
                 theater_name,       # 场景名字，用于定位、调整、切换场景使用
                 bg_filename = None, # 背景图片（不确定开发：动态背景？例如白天黑夜效果？其实，白天黑夜可以通过加一层半透明的actor实现。）
                 music = None        # 后期扩展，音乐
                 ):

        org_screen = pygame.display.get_surface()
        if org_screen is None:
            raise 'pls use Initer class to init game.'

        self.theater_name   = theater_name
        self.group          = pygame.sprite.Group()
        self.background     = None
        self.artist         = None

        # *暂未使用的参数，后续要考虑入场和出场的动画表演，否则切换场景会非常僵硬（至少要提供配置接口）
        # *后面可以考虑实现一些可配置的淡入淡出的效果
        self.enter          = None
        self.leave          = None

        # 创建每个场景都需要一个默认的背景，图片加载失败就会用默认的某种颜色填充
        if bg_filename:
            self._add_background(bg_filename)

    def regist(self,actor):
        if actor.image:
            self.group.add(actor)
            actor.theater = self

    def _add_background(self, bg_filename):
        self.background = Actor(bg_filename)
        self.background.theater = self
        if self.background.image:
            self.group.add(self.background)
