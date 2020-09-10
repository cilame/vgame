import pygame
import pygame.font as font
from pygame import Rect
from pygame.locals import *

from .theater import Theater
from .actor import Actor, Image
from .actor import Player, Wall, Bullet, Enemy, NPC, Menu, Background # 比较高一层的封装

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

    def __init__(self, screen, ticks):
        self.screen      = screen
        self.screen_rect = self.screen.get_rect()
        self.ticks       = ticks
        self.theaters    = {}
        self.framerate   = pygame.time.Clock()
        self.current    = None

    def update(self):
        self.framerate.tick(self.ticks)
        ticks = pygame.time.get_ticks()

        self.screen.fill(self.BGCOLOR)
        self.draw_grid() # 黑幕线，当没有背景时用于凸显黑幕的方式。

        # 这里就需要对指定的剧场进行更新，就是场景切换的扩展就都放在这里
        # 修改场景就只需要改场景的名字自动就修改掉了场景，方便切换。
        if self.theaters:
            self.theaters[self.current].group.update(ticks)
            _camera = self.theaters[self.current].camera
            _camera.update()
            for sprite in self.theaters[self.current].group:
                if sprite.cam_follow:
                    # 镜头跟随，用于基本上全部的游戏元素
                    self.screen.blit(sprite.image, _camera.apply(sprite))
                else:
                    # 不使用镜头跟随，一般用于菜单类的处理。
                    self.screen.blit(sprite.image, sprite.rect)
            _camera.debug_padding()

        pygame.display.flip()

    def draw_grid(self):
        for x in range(0, self.screen_rect.width, self.GRID_TILE):
            pygame.draw.line(self.screen, self.GRID_LINE_COLOR, (x, 0), (x, self.screen_rect.height))
        for y in range(0, self.screen_rect.height, self.GRID_TILE):
            pygame.draw.line(self.screen, self.GRID_LINE_COLOR, (0, y), (self.screen_rect.width, y))

    def change_theater(self, name):
        self.current = name

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
                 flag  = 0,          # pygame.display.set_mode 第二个参数
                 depth = 32,         # pygame.display.set_mode 第三个参数
                 ):

        pygame.init()
        self.ticks  = fps
        self.title  = title
        self.size   = size
        self.screen = pygame.display.set_mode(size, flag, depth)
        self.artist = Artist(self.screen, self.ticks)
        Artist.ARTIST = self.artist
        pygame.display.set_caption(title)

    def regist(self,*theaters):
        for theater in theaters:
            self.artist.regist(theater)

    def run(self):
        while True:
            self.artist.update()

            # 测试时候使用
            # 在标题后面添加内容来显示 fps
            pygame.display.set_caption(self.title + " fps:{:.3f}".format(self.artist.framerate.get_fps()))

            # 测试时候使用
            # 按下 ESC 直接退出游戏
            if pygame.key.get_pressed()[K_ESCAPE]:
                self.quit()

            # 测试时候使用
            # 按下 TAB 键按照一定的顺序循环切换至下一个场景
            # 后期肯定会删除掉的功能
            def _random_change(self):
                v = list(self.artist.theaters)
                i = (v.index(self.artist.current)+1)%len(v)
                self.artist.change_theater(v[i])
            for event in pygame.event.get():
                if event.type == QUIT :exit()
                if event.type == KEYDOWN:
                    if event.key == K_TAB :_random_change(self) # 键盘C测试切换触发随机场景的变化

    def change_theater(self, name):
        self.artist.change_theater(name)

    def quit(self):
        pygame.quit()
        exit()


__author__ = 'cilame'
__version__ = '0.0.9'
__email__ = 'opaquism@hotmail.com'
__github__ = 'https://github.com/cilame/vgame'