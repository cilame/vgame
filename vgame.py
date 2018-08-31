import pygame
from pygame.locals import *

import re
import random
from itertools import cycle, product


# 主要处理框架问题，实现普通的各类默认配置
# 让 pygame的 coding更方便，开发更简单
#
# 这个框架的设计思路是以简单的场景化，将每个场景都进行抽象出来
# 抽象出了以下四个类别（个人习惯：类的数量不多的话就用小写做类，除非自己看着不爽了，再改）
#
# initer    类负责搭建最初始的环境，其中包含了全局信息的默认配置
#           主要是一个启动的入口
#
# artist    类负责所有资源的管理，实现各式各样的资源场景的调度
#           当你开发一个游戏的时候，所有需要添加的游戏资源都需要通过这个类进行调度
#           主要在画面的统一更新上有更方便的调配
#
# theater   类负责任意一个场景的搭建，场景处理中需要考虑部分问题
#           其中还需要实现各种：
#               动画的表演的实现就需要存储在这里（细部分需要考虑一些表演锁的问题）
#
# actor     类负责任意一个单位的功能实现
#           其中需要实现：
#               单位的各种属性，渐变一类的动作
# 


'''
#
# 考虑一下表演资源的存储结构
# 这样一个数据结构将要存储在artist类里面统一调配
# artist对象在 initer创建时候就在 initer内部自动创建
# 其他情况下都是通过initer进行对新的场景和其他物体进行资源的注册
#
{
    # 开场场景的资源结构
    'entry':{
        'background':...
        'map':...
        'music':...
        ...
    }
    # 后续的一些舞台设计用名字来存储
    'global_map':{
        'background':...
        'map':...
        'music':...
        ...
    }
}

#
# 考虑一下表演的顺序
#
# ::音乐暂时不需要考虑，后续再想，这个资源需要考虑开启停止
# ::刚开始搭建结构，先不要把所有问题搞得太复杂。
#
# 加载背景
# 加载地图
# 加载动作者
#
# 逻辑判断写在什么地方好呢？
#
#
# 用initer  类生成主要的类，该类里面封装了一个artist类
# 用theater 类生成舞台
# 用actor   类生成演员
#
# 其中 initer，artist，theater 里面都有一个regist函数
# 用于将下级资源进上级资源的方法，其中initer和artist的注册函数相等，就是为了方便而已
# 资源结构如下
# 
#        artist
#        /     \
#   theater1  ...
#    /    \
# actor1  ...
#
# 演员（actor）对象注册进舞台
# 舞台（theater）对象注册进总的表演类
#
# 注册函数都包含一个反向关联的方法
# 这样的方式可以让所有的演员（actor）也能有结构的找到全局数据
# eg. 如果 actor_1 是一个演员对象，通过一般注册之后，那么他可以通过 actor_1.theater 找到当前剧场资源
# 也可以通过 actor_1.theater.artist 找到全局数据存储地方
#
'''


class artist:
    '''
    #====================================================================
    # 所有舞台、资源的存储以及调配
    #====================================================================
    '''
    def __init__(self, screen, ticks, entry):
        self.screen     = screen
        self.ticks      = ticks
        self.theaters   = {}
        self.framerate  = pygame.time.Clock()
        self.currrent   = entry

    def update(self):
        self.framerate.tick(self.ticks)
        ticks = pygame.time.get_ticks()

        # 这里就需要对指定的剧场进行更新，就是场景切换的扩展就在这里
        self.theaters[self.currrent].group.update(self.screen, ticks)
        self.theaters[self.currrent].group.draw(self.screen)




        # 测试按键，后期删除
        #============================================
        for event in pygame.event.get():
            if event.type == QUIT :exit()
            if event.type == KEYDOWN:
                if event.key == K_c :self._random_change()# 键盘C测试切换触发随机场景的变化
        #============================================



        pygame.display.flip()

    # 通过名字切换场景
    def change_theater(self, name):
        self.currrent = name


    # 注册舞台组件的方法
    def regist(self,theater):
        # 所有的舞台都要与artist进行关联，这样方便建立不同舞台之间的数据交互
        # 例如在A场景内改变的对象，可以通过A场景关联到总的artist对象，操作全局数据，在切换到B场景时候
        # 在B场景内的东西就自动改变，一种设计思路。
        self.theaters[theater.theater_name] = theater
        theater.artist = self



    # test func. 随机切换到非当前场景的其他场景的方法，只有一个场景的话不会切换，用于测试
    def _random_change(self):
        v = list(self.theaters)
        v.remove(self.currrent)
        if v:
            name = random.choice(v)
            self.change_theater(name)
    

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
                 bg_filename,       # 背景图片（不确定开发：动态背景？例如白天黑夜效果？其实，白天黑夜可以通过加一层半透明黑的actor实现。）
                 theater_name,      # 场景名字，用于定位、调整、切换场景使用
                 screen_pos=(0,0),  # 后期扩展，扩大缩小地图时候可能需要的参数（可能不仅限于此）
                 gametype='slg',    # 后期扩展，用于配置该场景的游戏类型
                 music=None         # 后期扩展，音乐
                 ):
        self.theater_name   = theater_name
        self.screen_pos     = screen_pos
        self.group          = pygame.sprite.Group()
        self.background     = None
        self.artist         = None

        # 创建每个场景都需要一个默认的背景，图片加载失败就会用默认的某种颜色填充
        self._add_background(bg_filename)


        self._slg_mk_map(10,10)

    def regist(self,actor):
        if actor.image:
            # 注册时将单位与当前舞台（theater）相关联，这样的话
            # 演员（actor）也能通过self.theater参数来获取舞台信息，例如地图信息，以及其他演员的信息
            # 演员（actor）对象需要通过注册进行关联在一起
            self.group.add(actor)
            actor.theater = self


    # 创建slg游戏类型的地图信息
    def _slg_mk_map(self, nraws, ncols):
##        测试函数内容
##        v = self.background.image
##        for i in dir(v):
##            print(i)
##        print(v.get_size())

        # 背景大小，一般用这个作为地图切割
        width, height = self.background.image.get_size()
        
        ncols, nraws




    # 每个场景的创建必须要一张图片作为背景。
    def _add_background(self, bg_filename):
        act = actor(bg_filename)
        act.update = lambda screen, ticks: screen.blit(act.image, self.screen_pos) if act.image else \
                     lambda screen, ticks: screen.fill((0,0,100)) # 默认背景，暂时有点bug，以后再改
        if act.image:
            self.group.add(act)
            self.background = act


class actor(pygame.sprite.Sprite):
    '''
    #====================================================================
    # 行为对象，主要用于实现更方便的加载图片资源的方法
    #====================================================================
    '''
    def __init__(self, img=None):
        pygame.sprite.Sprite.__init__(self)

        self.active     = False

        # 加载图片倘若名字符合动图处理规则加载函数内就会修改self.active，用动图处理方式
        self.image      = self.load_img(img)
        self.rect       = self.image.get_rect() if self.image else None
        self.theater    = None

    def load_img(self,img):
        if img is None: return None
        try:
            image = pygame.image.load(img).convert_alpha()
        except:
            print("无法加载图片.",img)
            image = None

        # 后面判断是否使用动态展示图片
        # 就是一种更为方便的配置图片数据的方法。原本打算用gif的，不过考虑到gif需要外部库
        # 而且经过测试，图片缩小方法似乎并不好用。所以暂时放弃兼容gif。
        # 后续必须考虑兼容，因为用任意gif作为角色确实很有意思。
        # ...
        #
        # 如果图片以例如 someimg_100x100_32.png 的名字存储的话，则会识别成动态图
        # 100x100代表单帧图片的大小，32代表了动态速率
        # 请尽量将名字配置中的100x100与长宽成倍数比，详细判定规则见下面这行代码
        # 下面的代码还是在配置上稍微有一些局限，比如原图有200x200只取三张图，这点就无法配置
        # 后续遇到其他情况再改
        # ...
        move = re.findall('_(\d+)x(\d+)_(\d+)\.',img.lower())
        if move:
            move = list(map(int,move[0]))
            self.active = True
            src_h,src_w = image.get_height(),image.get_width()
            pro_h,pro_w = move[:2]
            nraws,ncols = int(src_h/pro_h),int(src_w/pro_w)
            mfunc = lambda i:(i[0]*pro_w, i[1]*pro_h, pro_w, pro_h)

            self.src_image  = image
            self.rate       = move[2] # 用于控制速率
            self.cur_tick   = 0
            self.rects      = cycle(map(mfunc,product(range(ncols),range(nraws))))

        return image

    def _time_update(self, ticks):
        if ticks - self.cur_tick > self.rate:
            self.cur_tick = ticks
            return True

    def update(self,screen,ticks):
        if self.active and self._time_update(ticks):
            self.image = self.src_image.subsurface(next(self.rects))

        # 通过这样的方法可以实现修改图片大小，不过由于修改大小这部应该会消耗资源，
        # 每次加载都要修改一次大小，所以之后考虑优化的方式，让速度变得更快一些
        # 或者可以考虑放在 self.load_img函数当中
        self.image = pygame.transform.scale(self.image, (200,100))

        # 测试鼠标跟随，后期删除
        x, y = pygame.mouse.get_pos()
        x-= self.image.get_width() // 2
        y-= self.image.get_height() // 2
        self.rect[0] = x
        self.rect[1] = y
        
        # self.rect.fit(self.rect.inflate(-50,-50)) # rect对象只能修改区域大小，不能修改图片大小

        # 测试删除对象本身，后期删除
        if pygame.key.get_pressed()[K_s]:
            self.kill()


class initer:
    '''
    #====================================================================w
    # 处理许多默认值的初始化工作，也是程序入口
    #====================================================================
    '''
    def __init__(self,
                 ticks  = 60,
                 title  = 'vgame',       # title
                 size   = (640, 480),    # screen
                 flag   = 0,
                 depth  = 32,
                 entry  = 'entry'
                 ):

        self.ticks      = ticks
        self.entry      = entry
        self.screen     = pygame.display.set_mode(size, flag, depth)
        self.artist     = artist(self.screen,self.ticks,self.entry)
        pygame.display.set_caption(title)

    def regist(self,theater):
        '''
        #
        # 将组件注册进整体循环里面
        #
        # 之前是将背景加载直接放在initer里面，这样是不行的。
        # 对于每一个场景，应该都需要使用 舞台类（theater）来进行搭建，
        # 这样可是让每一个场景变得更加容易调配和转换
        # 另外，在一个游戏场景里面存在着一些可能被使用的全局资源，
        # 这些资源的保存尽量交给 artist来保存
        # 需要考虑实现一个比较方便存储的数据型来保存资源，
        # 造一个类来存储可能太重（个人感觉而已，看后续开发）
        #
        '''
        self.artist.regist(theater)


    def run(self):
        while True:
            self.artist.update()

            # 一些非常全局，关闭之类的事件可以考虑放在这里
            # 不过另一些关于触发式的关闭保存类就还是尽量放在场景里面会更好一些
            if pygame.key.get_pressed()[K_ESCAPE]:
                exit()
        
                






if __name__ == "__main__":
    bg1 = 'sushiplate.jpg'
    bg2 = 'sea.jpg'
    cur = 'sprite_100x100_32.png'

    s = initer()
    v1 = theater(bg1,'entry')
    actor1 = actor(cur)
    v1.regist(actor1)
    

    v2 = theater(bg2,'sea')
    actor2 = actor(cur)
    v2.regist(actor2)

    s.regist(v1)
    s.regist(v2)
    s.run()








