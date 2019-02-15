import pygame
from pygame.locals import *

from .actor import actor

class theater:
    '''
    #====================================================================
    # 舞台对象，主要负责布景功能（地图信息主要就是放在这里）
    #
    # 负责场景的资源加载（加载进全局，留下一个引用的结构）
    # 这样，已经加载的资源就不会再被加载进内存当中，并且
    # 调用资源仅仅需要通过自身就可以拿到
    #====================================================================
    '''
    def __init__(self,
                 bg_filename,       # 背景图片（不确定开发：动态背景？例如白天黑夜效果？其实，白天黑夜可以通过加一层半透明的actor实现。）
                 theater_name,      # 场景名字，用于定位、调整、切换场景使用
                 blocks=None,       # 后期扩展，用于配置该场景是否需要切分细块，可指定两个数字参数的tuple或list，作为横纵切分数量
                 singles=[(30,30),(40,40),(60,60),(80,80)], # 单元大小，blocks被设定时，该参数会被使用，默认使用第一个，扩展地图缩放，以后考虑扩展更顺滑的缩放
                 single_line=[(255,255,255,150),1],         # |单元格分割线的颜色和粗细，这个默认值暂且是为了开发方便
                 music=None         # 后期扩展，音乐        # |细粒度测试使用的尺寸 [(i,i) for i in range(30,80)]，细粒度会照成背景变形
                 ):


        org_screen          = pygame.display.get_surface()
        if org_screen is None:
            raise 'None screen, pls use initer class to init.'

        self.theater_name   = theater_name
        self.screen_pos     = (0,0)
        self.group          = pygame.sprite.Group()
        self.background     = None
        self.artist         = None

        # *暂未使用的参数，后续要考虑入场和出场的动画表演，否则切换场景会非常僵硬（至少要提供配置接口）
        # *后面可以考虑实现一些可配置的淡入淡出的效果
        self.enter          = None
        self.leave          = None

        # 用于缩放功能的参数，后续考虑默认最大屏的接口
        # 从现在开始，每张图传入的时候必然会进行切割，不同的是，
        # 如果没有设置blocks，则默认以screen进行全屏最大化，并且不会画线条
        self.single         = singles[0]
        siw,sih             = self.single 
        scw,sch             = org_screen.get_size()
        self.blocks         = blocks if blocks else (int(scw/siw),int(sch/sih))
        self.singles        = singles
        self.singles_image  = {}
        self.single_color   = single_line[0] if single_line and blocks else None
        self.single_thick   = single_line[1] if single_line and blocks else None
        self.toggle         = True

        # 用于坐标定位的参数
        self.point2coord    = None
        self.coord2point    = None


        # 创建每个场景都需要一个默认的背景，图片加载失败就会用默认的某种颜色填充
        self._add_background(bg_filename)
        self.background.events._mk_blocks_map(self) # 对背景切块,blocks切块参数传递的地方

    def regist(self,actor):
        if actor.image:
            # 注册时将单位与当前舞台（theater）相关联，这样的话
            # 演员（actor）也能通过self.theater参数来获取舞台信息，例如地图信息，以及其他演员的信息
            # 演员（actor）对象需要通过注册进行关联在一起
            self.group.add(actor)
            actor.theater = self


    # 每个场景的创建必须要一张图片作为背景。
    def _add_background(self, bg_filename):
        # 背景也是通过 actor类实例化实现
        self.background = actor(bg_filename)
        self.background.theater = self
        def _default_theater(ticks):
            self.background.events.change_map_size(ticks)

        self.background.update = _default_theater
        if self.background.image:
            self.group.add(self.background)
