import pygame
from pygame.locals import *

from .theater import Theater
from .actor import Actor, Image

class Artist:
    '''
    所有舞台、资源的存储以及调配
    后续会考虑增加更多相关的功能，
    比如在保存方面就有两种，游戏配置、游戏存档
    游戏配置：主要是配置游戏的各种操作或者屏幕或是各种与游戏内容无关的配置
    游戏存档：就是游戏存档
    由于所有的资源都会在这个类里面汇总，所以在这个类里面来实现保存和快照或者其他功能最合适不过
    '''
    def __init__(self, screen, ticks):
        self.screen     = screen
        self.ticks      = ticks
        self.theaters   = {}
        self.framerate  = pygame.time.Clock()
        self.currrent   = None

    def update(self):
        self.framerate.tick(self.ticks)
        ticks = pygame.time.get_ticks()

        # 先把底层涂满颜色
        self.screen.fill((0,0,100))

        # 这里就需要对指定的剧场进行更新，就是场景切换的扩展就都放在这里
        if self.theaters:
            self.theaters[self.currrent].group.update(ticks)
            self.theaters[self.currrent].group.draw(self.screen)
        else:
            pass

        pygame.display.flip()

    # 通过名字切换场景 # *或许这里后期会增加一些淡入、淡出的效果
    def change_theater(self, name):
        self.currrent = name

    # 注册舞台组件的方法
    def regist(self,theater):
        self.theaters[theater.theater_name] = theater
        theater.artist = self
        if not self.currrent:
            self.currrent = theater.theater_name # 第一次注册的舞台将默认作为入口舞台


class Initer:
    def __init__(self,
                 fps   = 60,         # 帧/秒
                 title = 'vgame',    # 标题名
                 size  = (640, 480), # 屏幕分辨率
                 flag  = 0,          # pygame.display.set_mode 第二个参数
                 depth = 32,         # pygame.display.set_mode 第三个参数
                 ):

        pygame.init()
        self.title  = title
        self.ticks  = fps
        self.size   = size
        self.screen = pygame.display.set_mode(size, flag, depth)
        self.artist = Artist(self.screen, self.ticks)
        pygame.display.set_caption(title)

    def regist(self,theater):
        self.artist.regist(theater)

    def run(self):
        while True:
            self.artist.update()

            # 测试时候使用
            # 在标题后面添加内容来显示 fps
            pygame.display.set_caption(self.title + " fps:{:.2f}".format(self.artist.framerate.get_fps()))

            # 测试时候使用
            # 按下 ESC 直接退出游戏
            if pygame.key.get_pressed()[K_ESCAPE]:
                self.quit()

            # 该处仅为测试使用，功能为按下 TAB 键按照一定的顺序循环切换至下一个场景
            # 后期肯定会删除掉的功能
            def _random_change(self):
                v = list(self.artist.theaters)
                i = (v.index(self.artist.currrent)+1)%len(v)
                self.artist.change_theater(v[i])
            for event in pygame.event.get():
                if event.type == QUIT :exit()
                if event.type == KEYDOWN:
                    if event.key == K_TAB :_random_change(self)# 键盘C测试切换触发随机场景的变化

    def change_theater(self, name):
        self.artist.change_theater(name)

    def quit(self):
        pygame.quit()
        exit()


__author__ = 'cilame'
__version__ = '0.0.6'
__email__ = 'opaquism@hotmail.com'
__github__ = 'https://github.com/cilame/vgame'