import sys
import traceback

import pygame
import pygame.font as font
from pygame import Rect
from pygame.locals import *

from .theater import Theater, Map
from .actor import Actor, Image, ImageMaker, Text
from .actor import Player, Wall, Bullet, Enemy, NPC, Anime, Menu, Background, Button # 比较高一层的封装
from .actor import Delayer, Controller
from .music import Music

DEBUG = False

class Artist:
    '''
    所有舞台、资源的存储以及调配
    后续会考虑增加更多相关的功能，
    比如在保存方面就有两种，游戏配置、游戏存档
    游戏配置：主要是配置游戏的各种操作或者屏幕或是各种与游戏内容无关的配置
    游戏存档：就是游戏存档
    由于所有的资源都会在这个类里面汇总，所以在这个类里面来实现保存和快照或者其他功能最合适不过
    '''

    BGCOLOR = (40, 40, 40)
    GRID_TILE = 32
    GRID_LINE_COLOR = (100, 100, 100)
    GRID_LINE_COLOR_MAP_DEBUG = (255, 0, 0)

    ARTIST = None # 想了想，既然 artist 是唯一的，那么就让 theater 实例化时候自动注册进来即可

    def __init__(self, screen, ticks, grid=(20,15)):
        self.screen      = screen
        self._screen     = self.screen
        self.screen_rect = self.screen.get_rect()
        self.screen_neor = self.screen_rect
        self.ticks       = ticks
        self.theaters    = {}
        self.framerate   = pygame.time.Clock()
        self.current     = None
        self.grid        = grid # 全局 theater 使用的默认的切割数量

    def update(self):
        self.framerate.tick(self.ticks)
        ticks = pygame.time.get_ticks()

        # self.screen.fill(self.BGCOLOR)
        if self.screen_rect[2:] != self.screen_neor[2:]:
            self._screen = pygame.Surface(self.screen_rect[2:]).convert_alpha()
        self._screen.fill(self.BGCOLOR)
        self._screen = self.draw_grid(self._screen) # 黑幕线，当没有背景时用于凸显黑幕的方式。

        # 这里就需要对指定的剧场进行更新，就是场景切换的扩展就都放在这里
        # 修改场景就只需要改场景的名字自动就修改掉了场景，方便切换。
        # cam_follow 用于是否镜头跟随，一般菜单不需要跟随地图变化进行移动
        if self.theaters:

            # 游戏内容
            self.theaters[self.current].group.update(ticks)
            _camera = self.theaters[self.current].camera
            _camera.update()
            for sprite in self.theaters[self.current].group:
                if sprite.cam_follow:
                    (x, y, w, h), (ox, oy) = _camera.apply(sprite), sprite.getoffset()
                    self._screen.blit(sprite.image, (x-ox, y-oy, w, h))
                else:
                    self._screen.blit(sprite.image, sprite.rect)
            _camera.debug_padding()

            # 菜单,总是置顶
            self.theaters[self.current].group_menu.update(ticks)
            for menu in self.theaters[self.current].group_menu:
                menu.group.update(ticks)
                self._screen.blit(menu.image, menu.rect)
                for sprite in menu.group:
                    self._screen.blit(sprite.image, sprite.rect)

            # 由于 pygame 缺陷，并发鼠标消息处理函数 pygame.mouse.get_pressed() 没有鼠标滚轮消息，
            # 所以用其他方式实现并发滚轮消息的接收处理，这里是收尾工作
            Controller.roll = 0

        self.screen_neor = self.screen.get_rect()
        self._screen = pygame.transform.scale(self._screen, self.screen_neor[2:])
        self.screen.blit(self._screen, self.screen_neor)
        pygame.display.flip()

    def draw_grid(self, image):
        rect = image.get_rect()
        for x in range(0, rect.width, self.GRID_TILE):
            pygame.draw.line(image, self.GRID_LINE_COLOR, (x, 0), (x, rect.height))
        for y in range(0, rect.height, self.GRID_TILE):
            pygame.draw.line(image, self.GRID_LINE_COLOR, (0, y), (rect.width, y))
        return image

    def change_theater(self, name):
        self.current = name.name if isinstance(name, Theater) else name

    def regist(self, theater):
        if theater.theater_name not in self.theaters:
            self.theaters[theater.theater_name] = theater
            theater.artist = self
            if not self.current:
                self.current = theater.theater_name # 第一次注册的舞台将默认作为入口舞台

class Initer:
    def __init__(self,
                 fps   = 60,         # 帧/秒
                 title = 'vgame',    # 标题名
                 size  = (640, 480), # 屏幕分辨率
                 flag  = pygame.RESIZABLE,          # pygame.display.set_mode 第二个参数
                 depth = 32,         # pygame.display.set_mode 第三个参数
                 ):

        pygame.init()
        self.ticks   = fps
        self.title   = title
        self.size    = size
        self.flag    = flag
        self.depth   = depth
        self.screen  = pygame.display.set_mode(size, flag, depth)
        self.artist  = Artist(self.screen, self.ticks)
        self.running = False
        Artist.ARTIST = self.artist
        pygame.display.set_caption(title)
        self.hook_without_run()

    def regist(self,*theaters):
        for theater in theaters:
            self.artist.regist(theater)

    def run(self):
        self.running = True
        while True:
            self.artist.update()

            # 测试时候使用
            # 在标题后面添加内容来显示 fps
            pygame.display.set_caption(self.title + " fps:{:.3f}".format(self.artist.framerate.get_fps()))

            # 测试时候使用
            # 按下 ESC 直接退出游戏
            if pygame.key.get_pressed()[K_ESCAPE]:
                self.quit()

            for event in pygame.event.get():
                if event.type == QUIT: exit()

                # 因为 pygame.event.get() 的处理方式类似于管道消息，不适合作为并行消息处理，
                # 所以在 controler.py 内使用的是 pygame.mouse.get_pressed() 处理多个并行消息。
                # 但是由于 pygame.mouse.get_pressed() 无法接收鼠标滚轮消息，所以，只有在这里处理滚轮消息了。
                # 这里处理的滚轮消息将会并入 actor.mouse 处理的消息当中。
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4: Controller.roll = 4
                    if event.button == 5: Controller.roll = 5

                # 动态修改高宽
                # 这里暂时还没有考虑好该怎么该，因为直接改会出现像素级的问题，
                # 人为直接拉伸那么鼠标的坐标信息就可能产生不准的问题，牵一发动全身，较真去改各个地方都需要改，
                # 暂时没考虑到有什么好的方法处理，这里就先留下一个半成品注释代码，是残缺功能的代码。
                # ## flag=pygame.RESIZABLE
                if event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(event.size, self.flag, self.depth)

    def change_theater(self, name):
        self.artist.change_theater(name)

    def quit(self):
        pygame.quit()
        sys.exit()

    def hook_without_run(self):
        # 让你在执行脚本的时候 vgame.Initer 实例不用再在最后执行 run() 函数。少写一行是一行。
        # 不过需要注意的是，这里处理的逻辑是：用钩子钩住主线程的线程收尾函数，
        # 所以，如果主线程里面有个什么循环啥卡住，这里是不会执行的，了解执行逻辑即可。
        # 当然你也可以直接用原来的 vgame.Initer() 实例在最末尾直接执行也行。
        self._hook_main_thread_end()
        self._hook_idlelib_console()

    def _hook_main_thread_end(self):
        from threading import current_thread, main_thread
        def _stop(s):
            if not self.running:
                try: self.run()
                except SystemExit: pass
            lock = s._tstate_lock
            if lock is not None:
                assert not lock.locked()
            s._is_stopped = True
            s._tstate_lock = None
        if current_thread() == main_thread():
            mt = main_thread()
            mt._stop = lambda: _stop(mt)
        else:
            raise Exception('If vgame.Initer is not in the main thread, it is likely to cause program exceptions')

    def _hook_idlelib_console(self):
        if 'idlelib' in str(sys.stdout):
            import idlelib.run
            _flush_stdout = idlelib.run.flush_stdout
            def flush_stdout(*a, **kw):
                if not self.running:
                    try: self.run()
                    except SystemExit: pass
                _flush_stdout(*a, **kw)
            idlelib.run.flush_stdout = flush_stdout

def change_theater(name):
    try:
        Artist.ARTIST.change_theater(name)
    except AttributeError as e:
        if 'NoneType' in str(e) and 'change_theater' in str(e):
            raise Exception('Use vgame.Initer to initialize the game before using this function')
    except:
        traceback.print_exc()



# pygame.draw.rect()
# 绘制矩形。
# rect(Surface, color, Rect, width=0) -> Rect
# 在 Surface  对象上绘制一个矩形。Rect 参数指定矩形的位置和尺寸。width 参数指定边框的宽度，如果设置为 0 则表示填充该矩形。
# pygame.draw.polygon()
# 绘制多边形。
# polygon(Surface, color, pointlist, width=0) -> Rect
# 在 Surface  对象上绘制一个多边形。pointlist 参数指定多边形的各个顶点。width 参数指定边框的宽度，如果设置为 0 则表示填充该矩形。
# 绘制一个抗锯齿的多边形，只需要将 aalines() 的 closed 参数设置为 True 即可。
# pygame.draw.circle()
# 根据圆心和半径绘制圆形。
# circle(Surface, color, pos, radius, width=0) -> Rect
# 在 Surface  对象上绘制一个圆形。pos 参数指定圆心的位置，radius 参数指定圆的半径。width 参数指定边框的宽度，如果设置为 0 则表示填充该矩形。
# pygame.draw.ellipse()
# 根据限定矩形绘制一个椭圆形。
# ellipse(Surface, color, Rect, width=0) -> Rect
# 在 Surface  对象上绘制一个椭圆形。Rect 参数指定椭圆外围的限定矩形。width 参数指定边框的宽度，如果设置为 0 则表示填充该矩形。
# pygame.draw.arc()
# 绘制弧线。
# arc(Surface, color, Rect, start_angle, stop_angle, width=1) -> Rect
# 在 Surface  对象上绘制一条弧线。Rect 参数指定弧线所在的椭圆外围的限定矩形。两个 angle 参数指定弧线的开始和结束位置。width 参数指定边框的宽度。
# pygame.draw.line()
# 绘制线段。
# line(Surface, color, start_pos, end_pos, width=1) -> Rect
# 在 Surface  对象上绘制一条线段。两端以方形结束。
# pygame.draw.lines()
# 绘制多条连续的线段。
# lines(Surface, color, closed, pointlist, width=1) -> Rect
# 在 Surface  对象上绘制一系列连续的线段。pointlist 参数是一系列短点。如果 closed 参数设置为 True，则绘制首尾相连。
# pygame.draw.aaline()
# 绘制抗锯齿的线段。
# aaline(Surface, color, startpos, endpos, blend=1) -> Rect
# 在 Surface  对象上绘制一条抗锯齿的线段。blend 参数指定是否通过绘制混合背景的阴影来实现抗锯齿功能。该函数的结束位置允许使用浮点数。
# pygame.draw.aalines()
# 绘制多条连续的线段（抗锯齿）。
# aalines(Surface, color, closed, pointlist, blend=1) -> Rect

class draw:
    def __init__(self, parent):
        self.parent = parent

    @staticmethod
    def handle_return(_Surface):
        if isinstance(_Surface, Background):
             _Surface = _Surface.theater
        return _Surface

    @staticmethod
    def rect(Surface, color, Rect, width=0):
        _Surface = Surface
        '''
        将 pygame 的 draw 增强，使其更加适用于 vgame，其中 Rect 如果为数字，自动作为 padding 参数
        '''
        imager = getattr(Surface, 'imager', None)
        if imager:
            Surface = imager.orig_image
        if isinstance(Rect, int):
            pad = Rect
            w,h = Surface.get_rect()[2:]
            Rect = (pad,pad,w-pad*2,h-pad*2)
        pygame.draw.rect(Surface, color, Rect, width)
        return draw.handle_return(_Surface)
    @staticmethod
    def polygon(Surface, color, pointlist, width=0):
        _Surface = Surface
        imager = getattr(Surface, 'imager', None)
        if imager:
            Surface = imager.orig_image
        pygame.draw.polygon(Surface, color, pointlist, width)
        return draw.handle_return(_Surface)
    @staticmethod
    def circle(Surface, color, pos, radius, width=0):
        _Surface = Surface
        imager = getattr(Surface, 'imager', None)
        if imager:
            Surface = imager.orig_image
        pygame.draw.circle(Surface, color, pos, radius, width)
        return draw.handle_return(_Surface)
    @staticmethod
    def ellipse(Surface, color, Rect, width=0):
        _Surface = Surface
        imager = getattr(Surface, 'imager', None)
        if imager:
            Surface = imager.orig_image
        pygame.draw.ellipse(Surface, color, Rect, width)
        return draw.handle_return(_Surface)
    @staticmethod
    def arc(Surface, color, Rect, start_angle, stop_angle, width=1):
        _Surface = Surface
        imager = getattr(Surface, 'imager', None)
        if imager:
            Surface = imager.orig_image
        pygame.draw.arc(Surface, color, Rect, start_angle, stop_angle, width)
        return draw.handle_return(_Surface)
    @staticmethod
    def line(Surface, color, start_pos, end_pos, width=1):
        _Surface = Surface
        imager = getattr(Surface, 'imager', None)
        if imager:
            Surface = imager.orig_image
        pygame.draw.line(Surface, color, start_pos, end_pos, width)
        return draw.handle_return(_Surface)
    @staticmethod
    def lines(Surface, color, closed, pointlist, width=1):
        _Surface = Surface
        imager = getattr(Surface, 'imager', None)
        if imager:
            Surface = imager.orig_image
        pygame.draw.lines(Surface, color, closed, pointlist, width)
        return draw.handle_return(_Surface)
    @staticmethod
    def aaline(Surface, color, startpos, endpos, blend=1):
        _Surface = Surface
        imager = getattr(Surface, 'imager', None)
        if imager:
            Surface = imager.orig_image
        pygame.draw.aaline(Surface, color, startpos, endpos, blend)
        return draw.handle_return(_Surface)
    @staticmethod
    def aalines(Surface, color, closed, pointlist, blend=1):
        _Surface = Surface
        imager = getattr(Surface, 'imager', None)
        if imager:
            Surface = imager.orig_image
        pygame.draw.aalines(Surface, color, closed, pointlist, blend)
        return draw.handle_return(_Surface)

    def __getattribute__(self, key):
        pare = super().__getattribute__('parent')
        func = super().__getattribute__(key)
        def _func(*a,**kw):
            if len(a):
                a = (pare, *a)
            else:
                kw['Surface'] = pare
            return func(*a,**kw)
        return _func












__author__ = 'cilame'
__version__ = '0.1.8'
__email__ = 'opaquism@hotmail.com'
__github__ = 'https://github.com/cilame/vgame'