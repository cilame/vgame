import pygame
from pygame.locals import *

from .actor import Actor
from .actor import Player, Wall, Enemy, Bullet, NPC
from .actor import Menu, Background

from .dijkstra import shortest_path

import vgame

class Map:
    '''
    用于处理栅格类型游戏的方式，不过如果不需要单位强制栅格化
    那么这里的处理也可以简单的当作一种更加规范的单位初始化/地图绘制的方式
    '''

    DEBUG = False

    class Map2D:

        DEFAULT_OBSTRUCT = 1 # 默认阻值
        DEFAULT_GAP = 3

        def __init__(self, mapw, maph):
            '''
            地图存储，主要使用 world 调用资源，使用 graph 进行路径计算
            当物体移动的时候需要考虑物体移动的状态
            '''
            self.mapw  = mapw
            self.maph  = maph
            self.world = self._create_map2ds(2)
            self.graph = self._create_graph()
            self.gap   = self.DEFAULT_GAP
        def _create_map2ds(self, num):
            d = {}
            d['obstacle'] = self._create_map2d()
            d['extra']    = self._create_map2d() # 此处尚未用到，在这里写入仅为说明可以在此处进行扩展性开发。
            return d
        def _create_map2d(self):
            mp = []
            for i in range(self.maph):
                mp.append([0 for j in range(self.mapw)])
            return mp
        def _create_graph(self):
            d = {}
            for i in range(self.mapw):
                for j in range(self.maph):
                    d[(i, j)] = self._init_point(i, j)
            return d
        def _init_point(self, x, y):
            p = {}
            lx, ly = x-1, y # l
            rx, ry = x+1, y # r
            ux, uy = x, y-1 # u
            dx, dy = x, y+1 # d
            if lx >= 0:        p[(lx, ly)] = Map.Map2D.DEFAULT_OBSTRUCT
            if rx < self.mapw: p[(rx, ry)] = Map.Map2D.DEFAULT_OBSTRUCT
            if uy >= 0:        p[(ux, uy)] = Map.Map2D.DEFAULT_OBSTRUCT
            if dy < self.maph: p[(dx, dy)] = Map.Map2D.DEFAULT_OBSTRUCT
            return p
        def _shortest_path(self, actor_a, actor_b):
            axis_a = actor_a.axis
            axis_b = actor_b.axis
            return shortest_path(self.graph, axis_a, axis_b)
        def _local(self, actor, obstruct):
            val = obstruct
            axis = actor.axis
            self._local_set(axis, val)
        def _local_set(self, axis, val):
            self._local_axis_val(axis, val)
            self._local_axis_graph(axis, val)
        def _local_axis_val(self, axis, val):
            px, py = axis
            try:    self.world['obstacle'][py][px] = val
            except: raise "out of bounds"
        def _local_axis_graph(self, axis, val):
            try: 
                if val != 1: 
                    self._set_graph(axis, val)
            except: raise "out of bounds"
        def _set_graph(self, axis, val):
            px, py = axis
            self.world['obstacle'][py][px]
            for i in self.graph[axis]:
                if axis in self.graph[i]:
                    self.graph[i][axis] = val
        def __str__(self):
            pks = []
            for i in self.world['obstacle']:
                pks.append(' '.join(['_'*self.gap if j == 0 else ('{:'+str(self.gap)+'}').format(j) for j in i]))
            return '\n'.join(pks)

    def __init__(self, gw, gh, sw, sh):
        self.theater = None
        self.gridw   = gw
        self.gridh   = gh
        self.screenw = sw
        self.screenh = sh
        self.mapw    = int(sw/gw)
        self.maph    = int(sh/gh)
        self.map2d   = Map.Map2D(self.mapw, self.maph)
        # print(sw, sh, gw, gh, self.mapw, self.maph)

    def local(self, actor:'actor or sprite', axis, obstruct=None):
        # 这里处理某些精灵的定位，换算出真实坐标然后定位到目标位置
        _x, _y, w, h = actor.rect
        px, py = axis
        rx = self.gridw * px + self.gridw / 2 - w / 2
        ry = self.gridh * py + self.gridh / 2 - h / 2
        actor.rect.x = rx
        actor.rect.y = ry
        actor.axis = axis     # 让 actor 绑定一个坐标地址
        self.map2d._local(actor, obstruct if obstruct is not None else Map.Map2D.DEFAULT_OBSTRUCT)

    def move(self, axis, delay=True):
        # 处理部分“平滑移动”以及部分“状态转移”以及部分“操作延时”以及最重要的“坐标记录”
        # 操作延时：即让处于正在移动中的角色暂时不再接收控制信息
        # 坐标记录：即让路径算法能够快速算出最短路
        pass

    def trace(self, actor_a, actor_b):
        return self.map2d._shortest_path(actor_a, actor_b)

    def clear(self, axis):
        self.map2d._local_set(axis, Map.Map2D.DEFAULT_OBSTRUCT)

    def _draw_debug_grid(self, image):
        # 用于对背景栅格的调试，绘制显示栅格
        if vgame.DEBUG and Map.DEBUG:
            x, y, w, h = image.get_rect()
            for x in range(0, w, self.gridw):
                pygame.draw.line(image, vgame.Artist.GRID_LINE_COLOR_MAP_DEBUG, (x, 0), (x, h))
            for y in range(0, h, self.gridh):
                pygame.draw.line(image, vgame.Artist.GRID_LINE_COLOR_MAP_DEBUG, (0, y), (w, y))

    def __str__(self):
        return str(self.map2d)

class Camera:
    '''
    主要负责处理镜头的处理，看看后续能够扩展出多少的功能。
    '''

    DEBUG = False

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
        if vgame.DEBUG and Camera.DEBUG:
            if not self.debug_area:
                showsize  = (int(self.padding.x), int(self.padding.y))
                showpoint = (self.w/2-self.padding.x/2, self.h/2-self.padding.y/2)
                self.debug_area = Actor((0,0,0,30), showsize=showsize, showpoint=showpoint)
            self.debug_area.imager._delay_bind_debug()
            self.theater.screen.blit(self.debug_area.image, self.debug_area.rect)
            self.theater.screen.blit(self.debug_area.image, self.apply(self.debug_area))


class Theater:
    Map    = Map
    Camera = Camera # 用于快速定位并修改某些配置参数： vgame.Theater.Camera.DEBUG

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
                 camera_size = None, # 镜头的尺寸，默认情况下镜头尺寸和游戏背景大小一样
                 gridsize = (40, 40),
                 ):

        game_screen = pygame.display.get_surface() # 游戏屏幕(镜头)显示的大小
        if game_screen is None:
            raise 'pls use vgame.Initer() to init game first.'

        self.screen       = game_screen
        self.screen_size  = self.screen.get_size()
        self.theater_name = theater_name
        self.size         = size if size else self.screen_size
        self.gridsize    = gridsize
        self.group        = pygame.sprite.Group()
        self.background   = None
        self.artist       = None
        self.camera       = self.regist_camera(Camera(*self.screen_size))
        self.map          = self.regist_map(Map(*self.gridsize, *self.screen_size))

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

    def regist_map(self, camera):
        camera.theater = self
        return camera

    def _add_background(self, background):
        self.background = Background(background, showsize=self.size)
        self.background.theater = self
        if self.background.image:
            self.group.add(self.background)
            self.map._draw_debug_grid(self.background.image)
