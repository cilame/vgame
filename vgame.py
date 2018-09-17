import pygame
from pygame.locals import *

import re
import random
import time
from itertools import cycle, product
from string import printable


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
# 事件（events）默认每个actor对象默认自带一个，可以通过actor的参数进行一定程度的配置
#       events 的实现就是这个框架比较功能性的核心扩展部分，所有我能想到的游戏功能就将会再events里面实现。
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
    def __init__(self, screen, ticks):
        self.screen     = screen
        self.ticks      = ticks
        self.theaters   = {}
        self.framerate  = pygame.time.Clock()
        self.currrent   = None

    def update(self):
        self.framerate.tick(self.ticks)
        ticks = pygame.time.get_ticks()

        # 先把底层涂黑
        self.screen.fill((0,0,100))

        # 这里就需要对指定的剧场进行更新，就是场景切换的扩展就在这里
        self.theaters[self.currrent].group.update(self.screen, ticks)
        self.theaters[self.currrent].group.draw(self.screen)

        # 测试按键，后期删除，一般关于舞台的控制操作尽量封装在舞台类里面会更好一些
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
        if not self.currrent:
            self.currrent = theater.theater_name # 第一次注册的舞台将默认作为入口舞台


    # test func. 随机切换到非当前场景的其他场景的方法，只有一个场景的话不会切换，该函数仅用于测试
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
        self.bg_actor       = None
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

        # 创建每个场景都需要一个默认的背景，图片加载失败就会用默认的某种颜色填充
        self._add_background(bg_filename)

        # 用于坐标定位的参数
        self.point2coord    = None
        self.coord2point    = None

        # 用于对地图尺寸操作时的强制延迟硬编码，以及修改尺寸前一刻的地图尺寸（用于尺寸转换时的定位）
        self.cur_tick       = 0
        self.map_uprate     = 100
        self.image_size     = None

        if self.blocks:
            self._mk_blocks_map() # 对背景切块,blocks切块参数传递的地方

    def regist(self,actor):
        if actor.image:
            # 注册时将单位与当前舞台（theater）相关联，这样的话
            # 演员（actor）也能通过self.theater参数来获取舞台信息，例如地图信息，以及其他演员的信息
            # 演员（actor）对象需要通过注册进行关联在一起
            self.group.add(actor)
            actor.theater = self

    # 创建切块的地图信息，slg，2drpg...绝大多数非动作类游戏都有这样的需求。
    def _mk_blocks_map(self):

        # 背景大小，一般用这个作为地图切割。扩展地图的缩放功能，否则该类型游戏表现力将会很差
        ncols,   nraws   = self.blocks
        singlew, singleh = self.single
        width,   height  = self.background.image.get_size()
        new_w,   new_h   = singlew*ncols, singleh*nraws
        cur_single       = int(width/ncols),int(height/nraws)

        # 角色坐标与地图坐标的双向dict寻址，方便 actor的计算
        px,py = list(range(ncols)),         list(range(nraws))
        qx,qy = map(lambda i:i*singlew,px), map(lambda i:i*singleh,py)
        point = list(product(px,py))
        coord = list(product(qx,qy))
        self.point2coord = dict(zip(point,coord))
        self.coord2point = dict(zip(coord,point))

        # 节约资源的做法，同时也能保证不会因为尺寸变化丢失背景图片精度
        if self.single in self.singles_image:
            self.background.image = self.singles_image[self.single]
        else:
            self.singles_image[self.single] = pygame.transform.scale(self.background.image,(new_w,new_h))

        if self.single != cur_single:
            self.background.image = self.singles_image[self.single]

        # 画切割线，当然也有其他扩展的方法能更节省资源。目前没有动态开关线条的功能，后续再考虑开发。
        if self.single_color:
            color,thick = self.single_color,self.single_thick
            for i in range(1,ncols):
                pygame.draw.line(self.background.image,color,(i*singlew,0),(i*singlew,new_h),thick)
            for i in range(1,nraws):
                pygame.draw.line(self.background.image,color,(0,i*singleh),(new_w,i*singleh),thick)


    # 每个场景的创建必须要一张图片作为背景。
    def _add_background(self, bg_filename):
        
        # 背景也是通过 actor类实例化实现
        self.bg_actor = actor(bg_filename)
        def _default_theater(screen, ticks):
            
            # 键盘 + - 控制缩放
            if self._change_size(ticks):
                self.toggle = True

            # 控制缩放时的坐标。用toggle的好处为：在初始化时能够执行一次，之后需要缩放成功修改配置
            if self.toggle:
                self._change_size_local(screen,self.screen_pos)

        self.bg_actor.update = _default_theater
        if self.bg_actor.image:
            self.group.add(self.bg_actor)
            self.background = self.bg_actor


    # 改变地图尺寸时，修改当前的 screen_pos
    def _change_size_local(self,screen,screen_pos):
        sw,sh = screen.get_size()
        bw,bh = self.image_size if self.image_size else self.background.image.get_size()
        aw,ah = self.background.image.get_size() # 这是变后尺寸，之前没有指明变前尺寸，所以造成BUG
        wk,hk = aw/bw, ah/bh
        tw,th = int(sw/2-(sw/2-screen_pos[0])*wk),int(sh/2-(sh/2-screen_pos[1])*hk)
        self.image_size = aw,ah # 更新变前尺寸
        px = (sw-aw)/2 if aw<=sw else tw
        py = (sh-ah)/2 if ah<=sh else th
        self.bg_actor.rect[0] = px # 通过修改rect来修改放置的中心点
        self.bg_actor.rect[1] = py
        self.screen_pos = (px, py) # 存储在类里面，后续应用于与其他函数交互
        self.toggle = False


    # 目前用简单的 + 和 - 键来控制地图缩放
    def _change_size(self,ticks):

        def _change_blocks(toggle):
            v = list(range(len(self.singles)))
            x = self.singles.index(self.single)
            if toggle == '+': ret = self.singles[x+1] if x+1 in v else self.single
            if toggle == '-': ret = self.singles[x-1] if x-1 in v else self.single
            if self.single != ret:
                if self._delay(ticks): # 延时设计，避免按键功能漂移
                    self.single = ret
                    self._mk_blocks_map()
                    return True

        # 这里进行了一次统一，之后都统一使用 blocks式的缩放。blocks 不设置的话会通过背景图片进行自动设置。
        if pygame.key.get_pressed()[K_KP_PLUS]: return _change_blocks('+')
        if pygame.key.get_pressed()[K_KP_MINUS]:return _change_blocks('-')


    def _delay(self,ticks):
        if ticks - self.cur_tick > self.map_uprate:
            self.cur_tick = ticks
            return True
        


















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
            print("无法加载图片.",img)
            image = None

        return image

    # 控制速率的函数，使任意帧率情况下都保持相同速度的函数
    def _time_update(self,ticks):
        if ticks - self.cur_tick > self.rate:
            self.cur_tick = ticks
            return True


    def regist(self,events):
        events.actor = self # 让事件对象能找到宿主本身
        self.events = events # 这里是为了兼容外部events的注册
        return events


    def update(self,screen,ticks):

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


class events:
    '''
    #====================================================================
    # 事件对象，主要用于实现各式各样依附于角色的事件
    #====================================================================
    '''
    def __init__(self, action=None, event_rate=60):
        # 作为一个良性发展中的框架，每个actor都会生成一个属于他们自身的events对象在类内部
        # 而且后续也会写一些比较适合一般游戏配置的框架，这就这个框架所要事项的功能主要做的事情了
        # 状态转化 # 战斗计算 # 血条显示之类 # 属性配置之类 # 子弹发射 # 我个人想到什么就扩展什么，各种功能...
        # 让开发者只需要通过 actor 进行配置即可拥有这些功能，通过action来配置这些场景内的功能。
        # 如果实现功能太过专一就有点像是写游戏而非框架了。
        #
        # 主要是在这个类里面实现对操作的捕捉功能
        self.action     = action
        self.actor      = None
        self.rate       = event_rate

        # 帧率延时临时变量
        self.cur_tick   = 0

        # 用于鼠标操作的参数（一般只有在鼠标按下时候会更新，所以不用担心资源浪费问题）
        self.mouse_id     = None # in (0,1,2) 0代表左键，2代表右键，1代表中键
        self.mouse_pos    = None
        self.mouse_status = 0    # 按键状态（0无按，1按下，2松开瞬间）
        self.mouse_toggle = True
        self.mouse_tick   = 0
        self.mouse_delay  = 160  # 鼠标按下多久不动后转变成地图拖拽模式     # 关于延迟的动态配置后期再做，这里先硬编码
        self.cross_time   = False
        self.cross_status = 0    # 判断状态（0判断，1单击，2框选，3地图拖拽）
        self.limit_len    = 3.   # 一个阈值，与鼠标按下松开时，两点坐标点距离有关
        self.drag_map_pos = None # 地图拖拽时最先按下的那个点与地图相关的坐标（注意是和地图相关而不是和界面相关）
        self.drag_old_pos = None # 上一帧拖拽时，鼠标于界面的坐标点

        # 用于键盘操作的参数
        self.direction_key_tick     = 0    # 后期发现只用 self._delay 函数，如果混合其他操作可能会出现灵敏丢失的情况
        self.direction_key_delay    = 100  # 所以最后还是把键盘的操作延时也单独出来了 # 关于延迟的动态配置后期再做，这里先硬编码
        self.un_oblique             = 0    # 如果没有斜角操作的话，处理斜角的操作滞粘操作参数

        # 对象创建默认为未被控制，按照一般slg思路而已，控制的触发需要通过光标对象来修改实现
        # 实际上，需要配置的参数有非常的多，不必将参数放置在这里，之后可以考虑将配置都放入actor里面
        # 后期通过 events向上调用来查看问题发生在什么地方。
        self.be_control   = False # 后期可能抛弃的参数



        # 一般图片画框 # 这里需要重新设计，因为画框可能会有叠加的情况。
        # 或许还需要添加更多的配置。（栈式的画框事件[我说完你说之类的]，并行画框事件[一些渐渐消失的对话框之类]）
        self.draw_rect    = []   # 关闭时需要
        self.draw_rect_id = 0    # 关闭时需要
        self.text_size    = 14   # 字体大小

        # 用于实现栈效果式的更新函数
        self.update_stack = []

        # 直接通过 action参数实现对update函数的内置函数的配置
        if self.action == 'cursor':
            self.update_stack.append(self.update_select_cursor)

        # 这里需要配置一个可移动对象作为一种调试性触发功能的对象
        if self.action == 'actor':
            self.update_stack.append(self.update_actor)

    def update(self,ticks):
        # 戏大部分功能是一种开关式的处理，就是开启之后必要会考虑的关闭，
        # 所以实际上，这里的处理如果是使用栈来实现的话，那些功能叠加的时候也能通过简单的pop-
        # 来回到上层的功能，这样的设计一般在这里都是找栈最上层的函数进行更新，不过栈在这里独立出来之后
        # 就可以更容易扩展出多场景捕捉功能的叠加。
        if self.update_stack:
            self.update_stack[-1](ticks)

    def update_select_cursor(self,ticks):
        # 光标的核心功能应该是改变当前坐标下的单位的被选择状态 # 这里需要着重处理鼠标事件的多样性
        # 因为鼠标对于被选择而言有非常多的种类，单击选择，按住超过几秒进入拖拽模式，拖拽，或者是复选的实现需要打磨
        
        # 这里实现一般的光标选择框的功能。
        # 考虑是否有黏着框
        # 考虑方向键事件
        # 考虑移动时候地图跟随的问题
        # 考虑选择框按下事件以及属性查看的功能（这个还是能够轻松获取到该点下的坐标点以及坐标下角色坐标的属性）
        # 考虑展示框的问题
        # 考虑对话框功能
        # 不过以上功能尽量以函数组件组件形式存在会更可控一些。

        # 以下这些函数都用于测试，后面会大修，因为触及到某些函数时候会进行update转移的情况
        # 之所以要update转移是因为在某些场景情况下，有些控制功能是有必要进行无效限制的（比如slg在进入对话时，人物就不应该能被控制了。）
        # 但是只在一个update里面进行针对性的无效限制并不是一个好的开发方法，并且还可能出现其他未知的开发情况，所以非常硬的开发方案是不行的
        # 所以后续决定使用 update类的函数进行对一个场景进行行为处理，这样的话，各种场景的行为控制就能有效的进行开发分离
        # 当然如果将“转移过程”（eg. self.update = update_*）直接硬编在任意一个update函数中时，会有严重的开发麻烦，后续会再考虑
        if self._delay(ticks,self.rate):
            self.general_direction_key(ticks,wasd=True)   # 处理通常方向键
            self.general_mouse(ticks)               # 处理通常鼠标键（鼠标需要处理一个延时所以传入ticks）
            test_rects = self.general_create_rect("测试ascii和文字输出!" * 250) # 测试字符框，第二个参数pos_w_h_pw_ph默认None# ((0,0),640,480,40,40)
            self.general_draw_rect()                # 测试对话框的输出



    def update_character_info(self,ticks):
        # 最开始我写这个游戏框架就有奔着slg去的，所以我会先在这里实现信息展示的功能
        # 战场上的单位信息框就在这里实现，一般游戏中被选择后就实现简单的属性展示
        pass

    def update_dialog(self,ticks):
        # 顾名思义，对话框。任何现代的的游戏没有对话框的实现都是非常难以接受的。
        # 哪怕像是矮人要塞那种游戏也有一个界面用来展示人物情绪一类的界面。
        # 这个接口就是任何需要显示大段文字时提供一个文字展示框。
        pass

    def update_actor(self,ticks):
        self.general_direction_key(ticks,wasd=True)




    #============#
    #            #
    #  组合功能  #
    #            #
    #============#
    # 这些直接对应了各类的游戏的功能，不过一些接口不能通用于任何游戏
    # 所以这里以后也会考虑设计一些相似但是更为针对某些类型游戏的接口

    #================#
    # 一般浮窗选择框 #
    #================#
    def general_draw_choice(self,pos_w_h_pw_ph):
        # 一个游戏怎么能少了选项框，这个函数的主要目的就是用于在界面的任意位置上放置自己的选项框
        pass

    #==================#
    # 一般浮窗文本显示 #
    #==================#
    def general_draw_rect(self):
        # 因为浮窗文本可能会出现量非常多的情况，这时候需要在这里处理多个文本显示的问题，
        # 因为多个文本若是在相同位置的地方显示的话，不可以叠加，所以需要设计触发式的“下一段话”
        # 这里的触发的设计需要再完善一下。

        if self.draw_rect:
            if self.draw_rect_id == 0:
                self.actor.theater.group.add(self.draw_rect[self.draw_rect_id])
                self.draw_rect_id += 1
            if any(pygame.key.get_pressed()): # 触发问题就在这里考虑 # 这里可以考虑速度配置问题
                if self.draw_rect_id == len(self.draw_rect):
                    self.draw_rect[self.draw_rect_id - 1].kill()
                    self.draw_rect = []
                    self.draw_rect_id = 0
                else:
                    self.draw_rect[self.draw_rect_id - 1].kill()
                    self.actor.theater.group.add(self.draw_rect[self.draw_rect_id])
                    self.draw_rect_id += 1
            #print(self.draw_rect_id,len(self.draw_rect))
        else:
            pass#print(111)


        # 用完后让各个显示图片自行删除，并且清空文字缓存内容
        #for text_rect in self.draw_rect:
        #    text_rect.kill()
        #self.draw_rect = []
        #self.draw_rect_id = 0

    #==================#
    # 一般浮窗文本生成 #
    #==================#
    # (翻页式文字浮窗，**后续考虑背景图片的配置，没有则用目前使用的画框)
    # 这里的浮窗类型属于以文字量进行分割后的多个sprite对象的框。
    # 实现框的下一页的方法主要是通过theater里面的group队列的添加和自删除来实现的效果。
    def general_create_rect(self,text,pos_w_h_pw_ph=None):
        # 一般的通过设定（坐标定位，画框长宽，内边框padding实现文字浮窗）
        # 1 文本显示通过添加入 theater.group 的最后一个实现，通过 kill 来结束显示（个人选择）
        # 2 直接通过地图背景，绘制在地图上面，效果和实现的难度都不尽人意。

        # *新修改：放弃通过 self.draw_rect来实现对话框的传递，因为这样不能拓展成多个对话框。
        # 返回传入按照单文字框的最大量分割后的list->[sprite...]
        def _limit_text_px_width(text,limit):
            # 文字宽度的限制，中文算两个长度
            ret,strs,q = [],'',0
            for i in text:
                val = 1 if i in printable[:95] else 2
                if q < limit: q += val; strs += i
                else: ret.append(strs); q = 0; strs = ''
            if strs: ret.append(strs)
            return ret

        def _limit_text_px_height(textsplit,limit):
            # 文字高度的限制，任何字符都算一个长度
            ret,ls,q = [],[],0
            for i in textsplit:
                if q < limit: q += 1; ls.append(i)
                else: ret.append(ls); q = 0; ls = []
            if ls: ret.append(ls)
            return ret

        def _mk_draw_rect(text,pos,w,h,pw,ph):
            # 配置框的大小，默认使用界面以下的25%实现，字体大小使用12大小的字体，内边框分别为（h/8,h/16）
            # 这种边框类的很不好写成一种扩展，要考虑的很多，所以这里都用比较硬的处理方式
            limitw,limith = w - pw*2,h - ph*2
            textsplit = _limit_text_px_width(text,limitw/self.text_size*2)
            text_list = _limit_text_px_height(textsplit,limith/(self.text_size + 1))
            ft = pygame.font.Font("simsun.ttc", self.text_size)
            p = []
            for texts in text_list:
                v = pygame.Surface((w, h)).convert_alpha()
                v.fill((0,0,100,150))
                temp_draw_rect = pygame.sprite.Sprite()
                temp_draw_rect.image = v
                temp_draw_rect.rect  = pos
                for idx,text in enumerate(texts):
                    fs = ft.render(text,False,(255,255,255))
                    temp_draw_rect.image.blit(fs,(pw,ph+idx*self.text_size))
                    pygame.draw.rect(temp_draw_rect.image,(0,0,0),      (0,0,w,h),6)
                    pygame.draw.rect(temp_draw_rect.image,(255,255,255),(2,2,w-4,h-4),2)
                p.append(temp_draw_rect)
            return p

        if pos_w_h_pw_ph:
            pos,w,h,pw,ph = pos_w_h_pw_ph
        else:
            # 一般对话文本显示 
            # 配置框的大小，默认使用界面以下的25%实现，字体大小使用12大小的字体，内边框分别为（h/8,h/16）
            # 其实这种对话框类的很不好写成一种扩展，要考虑的很多，所以这里都用比较硬的处理方式
            w, h  = self.actor.theater.artist.screen.get_size()
            h = int(h/4)
            pw,ph = int(h/2), int(h/4)
            pos = (0,(h*3))

        return _mk_draw_rect(text,pos,w,h,pw,ph)







    #============#
    #            #
    #  操作功能  #
    #            #
    #============#
    # 包装的延迟操作
    # 下级功能的向上封装，其中考虑了一些延时或一些地图处理一类
    # 后续可能会开发一些和地图无关的接口，所以抽象这一层也是为了操作的多样性

    #==============#
    # 一般鼠标操作 #
    #==============#
    def general_mouse(self,ticks):
        # 这里考虑的是怎么实现鼠标对大地图的拖动，这里主要实现的是组合功能的事情。
        #
        # 条件：
        # if 起始点坐标与鼠标当前坐标的长度超过限制：
        #     当作选框事件处理（在按键松开时执行）
        # else:
        #     1 如果按时未超过x秒，则一般处理（在按键松开时执行）
        #     2 如果按时超过x秒，且起始点坐标当前坐标的长度未超过限制，地图拖拽处理（可以不止用于地图拖拽）
        #       （在按键为松开时就以某个延迟循环执行）
        #
        # 设计时，因为有放下或松开问题，所以需要考虑到状态转换，
        # 目前暂时只处理左键的功能，右键的功能暂时不知道是否应该放在这里处理。
        # 
        rem = self._mouse_pressed() # 获取当前鼠标操作数据
        if rem and rem[0] == 0:
            if self.cross_status == 0:
                # rem：按键id，按键状态（0无按，1按下，2松开瞬间），起止两个坐标点，两坐标之间的长
                if rem[1] == 1:
                    # 随时检查长度和时间
                    if self._mouse_delay(ticks,self.mouse_delay):
                        if self.cross_time:
                            if rem[4] < self.limit_len:
                                self.cross_status = 3
                                px,py = pygame.mouse.get_pos()
                                mx,my = self.actor.theater.screen_pos
                                self.drag_map_pos = px-mx,py-my
                                self.drag_old_pos = px,py
                            if rem[4] >= self.limit_len:
                                # 框选状态需要考虑持续问题，因为需要考虑画选择框的矩形线
                                # 所以后续这里再扩展矩形线的问题。（大概属于 rts 类的问题）
                                # 这里的实现如果放在 rts 上存在着一定的缺陷，暂时不考虑而已。
                                self.cross_status = 2
                        self.cross_time = True
                        
                if rem[1] == 2:
                    if rem[4] >= self.limit_len:
                        self.cross_status = 2
                    else:
                        self.cross_status = 1
                        self.cross_time = False

            # 目前接口将返回当前状态码和一次半完整点击的松开起止两个坐标点
            # 单击状态1，框选状态2，地图拖拽状态3
            if self.cross_status == 1:
                # 单击状态
                self.cross_status = 0
                return 1,rem[2:4]

            if self.cross_status == 2:
                # 框选状态 # 框选状态和地图状态的返回值就只有状态值不一样，这样方便选择性需要地图状态
                if rem[1] == 2:
                    self.cross_status = 0
                    self.cross_time = False
                else:
                    return 2,rem[2:4]

            if self.cross_status == 3:
                # 地图状态 # 框选状态和地图状态的返回值就只有状态值不一样，这样方便选择性需要地图状态
                if rem[1] == 2:
                    self.drag_map_pos = None # 联动 _map_mouse 函数的参数，注意使用
                    self.drag_old_pos = None # 联动 _map_mouse 函数的参数，注意使用
                    self.cross_status = 0
                    self.cross_time = False
                else:
                    self._map_mouse(rem[3])
                    return 3,rem[2:4]

    #================#
    # 一般方向键操作 #
    #================#
    # 带有粘性的方块操作
    # 非粘性方块设计的操作通过这里实现，不规则光标移动在很多游戏里面非常常见，所以有必要更好的考虑这点
    def general_direction_key(self,ticks,wasd=False,oblique=True):
        # 普通方向键处理（一般单个单位的方向移动处理）
        # 处理一般的方向键的按键事件处理，一般用于角色移动或光标移动，（角色和光标都可以通过actor实现）
        # 判断剧场是否使用粘性方块设计，然后再选择响应的方式，总之这个函数返回的是一个坐标或是像素坐标
        # 控制粘性方块的上下左右需要的参数

        rek = self._direction_key_pressed(wasd) # 获取当前按键（或组合键）的方向，以小键盘八方向数字为准

        # 需要先判断rek再判断延迟才能防止出现灵敏丢失的情况
        if rek and self._direction_key_delay(ticks,self.direction_key_delay):
            px,py = self.actor.point
            pw,ph = self.actor.theater.blocks
            # 使用粘性方块的时候还需要考虑到是否point不为空 # 另外还需要考虑当前角色是否被控制（新参数）
            # 方向操作需要实现的各个参数，而且不良组合键需要考虑，比如同时按上和下不需要执行任何动作

            def up():   nonlocal py;py = max(py - 1, 0)
            def down(): nonlocal py;py = min(py + 1, ph-1)
            def left(): nonlocal px;px = max(px - 1, 0)
            def right():nonlocal px;px = min(px + 1, pw-1)

            if rek == 4: left()
            if rek == 6: right()
            if rek == 8: up()
            if rek == 2: down()
            if oblique:
                # 允许有斜角的处理方法（默认允许斜角处理）
                if rek == 7: left(); up()
                if rek == 1: left(); down()
                if rek == 9: right(); up()
                if rek == 3: down(); right()
            else:
                # 只允许正方向键[只有上下左右]的处理方法（最优解是根据后一个按下的正方向键[只有上下左右]来实现）
                if rek in [2,4,6,8]:
                    self.un_oblique = rek
                if rek == 7:
                    if self.un_oblique == 8: left()
                    if self.un_oblique == 4: up()
                if rek == 1:
                    if self.un_oblique == 2: left()
                    if self.un_oblique == 4: down()
                if rek == 9:
                    if self.un_oblique == 8: right()
                    if self.un_oblique == 6: up()
                if rek == 3:
                    if self.un_oblique == 2: right()
                    if self.un_oblique == 6: down()

            self.actor.change_point((px,py)) # 测试
            # 废弃对blocks的判断，因为现在无论什么类型都将对图片进行切分，不过初始化不设定blocks会自动根据全屏最大化来初始化blocks
            # 等我slg这边能够实现之后再考虑吧，rts的扩展考虑得稍微有点远了点。

    #================#
    # 一般控制键操作 #
    #================#
    def general_control_key(self):
        # 类似于一般手柄上面的AB键位的功能，简单的提供一些接口
        # 让某些键位注册后返回一些对于编写者来说更方便查调用的数据接口
        # 类似注册了键盘zx键位为ab（手柄），按z、x键时候返回为a、b，之类的。ab会更好进行功能辨识
        pass





    


    #============#
    #            #
    #  操作底层  #
    #            #
    #============#
    # 直接与鼠标和按键接触的接口
    # 比较难看懂，因为这里混合了我个人设计的返回数据结构，这里没有设计延迟

    def _mouse_pressed(self):
        # 鼠标的话需要考虑几个状态
        # 1 左键单击（持续按，不超过一个很微小的时间，然后松开）
        # 2 左键持续（持续按，超过一个很微小的时间）
        # 3 右键同理
        # 4 右键同理
        # 5 复选模式（可能需要返回一个界面区域的rect交给后续处理，返回值也要考虑
        # ...
        # （暂时不需要支持双键同时按的情况）
        # 由于以上功能需求，这里的返回的数据可以这样设计，以按下松开为一个周期进行返回
        # 返回：按下的按键，按下的界面坐标，松开的界面坐标，前两个坐标的距离
        # （时长就不封装在这个函数里面了，因为太集成不太好）
        mouse = pygame.mouse.get_pressed()

        # 鼠标未被按下
        if self.mouse_status == 0:
            if mouse.count(1) == 1:
                # 这里需要扩展滚轮操作吗？（暂时没有硬需求，不考虑）
                self.mouse_id     = mouse.index(1)
                self.mouse_status = 1

        # 鼠标按下的处理
        if self.mouse_status == 1:
            if self.mouse_toggle:
                self.mouse_pos = pygame.mouse.get_pos() # 起始坐标
                self.mouse_toggle = False
            if mouse.count(1) != 1:
                self.mouse_status = 2
            cur_pos = pygame.mouse.get_pos() # 鼠标松开的坐标点
            len_for_2point = ((self.mouse_pos[0]-cur_pos[0])**2 + (self.mouse_pos[1]-cur_pos[1])**2)**.5
            return self.mouse_id, self.mouse_status ,self.mouse_pos, cur_pos, len_for_2point

        # 鼠标松开的瞬间
        if self.mouse_status == 2:
            self.mouse_status = 0 # 松开后立马将状态转换成未按下的状态，让鼠标松开的操作仅返回一次
            self.mouse_toggle = True # 同时将鼠标单次记录开关打开
            cur_pos = pygame.mouse.get_pos() # 鼠标松开的坐标点
            len_for_2point = ((self.mouse_pos[0]-cur_pos[0])**2 + (self.mouse_pos[1]-cur_pos[1])**2)**.5
            # 按键id，按键状态，起止两个坐标点，两坐标之间的长度
            return self.mouse_id, self.mouse_status, self.mouse_pos, cur_pos, len_for_2point

    def _direction_key_pressed(self,wasd=False):
        # 一个简单获取八个方向的函数，如果是方向键则优先方向键
        # 方向键最大同时按两个方向组合键，且要合法（不能同时上下之类）
        # 如果没有用方向键用小键盘则只能同时按一个按键
        # 返回参数为小键盘上八个方向的数字，没有则为0，其他函数根据数字进行后续操作即可
        key = pygame.key.get_pressed()
        ret = 0
        if wasd:
            a = key[pygame.K_UP]    or key[pygame.K_w]
            b = key[pygame.K_DOWN]  or key[pygame.K_s]
            c = key[pygame.K_LEFT]  or key[pygame.K_a]
            d = key[pygame.K_RIGHT] or key[pygame.K_d]
        else:
            a = key[pygame.K_UP]
            b = key[pygame.K_DOWN]
            c = key[pygame.K_LEFT]
            d = key[pygame.K_RIGHT]
        v = [a,b,c,d]
        if any(v):
            if v.count(1) == 1:
                if a: ret = 8
                if b: ret = 2
                if c: ret = 4
                if d: ret = 6
            if v.count(1) == 2:
                if a and c: ret = 7
                if a and d: ret = 9
                if b and c: ret = 1
                if b and d: ret = 3

        if ret == 0:
            e = key[pygame.K_KP8]
            f = key[pygame.K_KP2]
            g = key[pygame.K_KP4]
            h = key[pygame.K_KP6]
            i = key[pygame.K_KP7]
            j = key[pygame.K_KP1]
            k = key[pygame.K_KP9]
            l = key[pygame.K_KP3]
            v = [e,f,g,h,i,j,k,l]
            if v.count(1) == 1:
                if e: ret = 8
                if f: ret = 2
                if g: ret = 4
                if h: ret = 6
                if i: ret = 7
                if j: ret = 1
                if k: ret = 9
                if l: ret = 3
        return ret

    def _control_key_pressed(self):
        # 一些普通的键盘非方向键的按键返回，这里需要考虑的是一般游戏ab键的单按和连发的区分和识别
        # 所以可能需要和鼠标那样的方式去实现功能。方向键和ab键和鼠标都是需要各自的延迟参数(必须)
        # 动作类游戏不可能按住方向键ab键就不能使用，分开延迟就可以实现互不影响
        # 这里先实现分类，向上封装后再由上一层进行延迟封装，这里需要实现注册功能，因为wasd本身就是键盘上的按键，所以需要考虑
        pass




    #============#
    #            #
    #  其他功能  #
    #            #
    #============#
    # 杂项


    # 后续将会把地图缩放放在这里面来实现，因为这样的话才会让功能分割得更为整洁一些，
    # 背景actor：地图缩放类功能，全局配置功能，像是速度音量之类的配置框选择
    # 角色actor：属性一类的功能以及自身的一些技能功能（这类不需要events配置操作捕捉的功能）
    # 光标actor：实现操作捕捉的关键功能
    #
    # 把地图迁移到这里来实现的一个好处就是，地图移动之类的和操作本身就紧密联系着
    # 这样theater内部就能更好的去关注于其他东西，为了整洁，也是为了资源调配函数作准备。
    #==================================================================================

    
    
    def _map_mouse(self,cur_pos):
        # 地图拖动功能在这里实现 # 计算出于上一坐标关键帧的坐标差值，然后根据限制更新
        if cur_pos != self.drag_old_pos:
            cx,cy = cur_pos
            ox,oy = self.drag_old_pos
            mx,my = self.actor.theater.screen_pos
            w, h  = self.actor.theater.background.image.get_size() # 这里的参数将用于边界限制使用
            sw,sh = pygame.display.get_surface().get_size()
            nx = max(min(mx+cx-ox,0),sw-w) if sw<w else mx
            ny = max(min(my+cy-oy,0),sh-h) if sh<h else my
            self.actor.theater.screen_pos = nx,ny
            self.actor.theater.bg_actor.rect[0] = nx
            self.actor.theater.bg_actor.rect[1] = ny
            self.drag_old_pos = cur_pos

    def _delay(self,ticks,rate):
        # 目前该函数没有被使用，因为目前暂时还不需要考虑帧率的问题，
        # 键盘鼠标的操作延时也独立出去防止延迟混乱，后期这里很可能会被使用，这里保留
        
        # 因为之后设计的所有按键操作都将会“放弃”通过 pygame.event.get() 获取事件的方式来获取控制
        # 因为 pygame.event.get() 多次在不同地方使用的时候，会出现各种问题（测试结论）。
        # 这无疑是对单击事件是非常灾难性的。灵敏度丢失不可接受， 所以这里一律使用 pygame.key.get_pressed() 来实现功能，
        # 这里通过延迟来实现按键执行的速率，避免任意需要延迟的操作漂移。
        # 这个地方为通用延时，和鼠标延时（鼠标延时类似于一种等待）还是有一些不太一样的。
        if ticks - self.cur_tick > rate:
            self.cur_tick = ticks
            return True

    def _mouse_delay(self,ticks,rate):
        # 鼠标的延迟在这里更类似于一种等待，实现鼠标长按功能
        if ticks - self.mouse_tick > rate:
            self.mouse_tick = ticks
            return True

    def _direction_key_delay(self,ticks,rate):
        # 键盘的延迟单独出来（如果直接用 self._delay控制所有的操作事件会出现灵敏丢失的情况。）
        if ticks - self.direction_key_tick > rate:
            self.direction_key_tick = ticks
            return True

    # *该函数会废弃，留下注释是为以后提供灵感
    def combined_direction_key(self):
        # 组合体的方向键处理问题（处理多个物体同时移动的状况）
        # 暂时只能缓存一个开发的轮廓概念，因为这部分在写完一般方向键处理之后，
        # 再估计一下组合体用一般方向键函数处理实现的难度再考虑后续的是否需要单独出这个函数出来。
        pass










# 对了，单位的属性和计算需要封装在什么地方好呢？
# 装载的地方可以是放在全局的artist里面，但是也有一些数据仅仅只在theater舞台初始化时候才会出现
# 例如一些角色的等级经验肯定是需要全局存储的
# 例如一些角色进入新的战场后血量需要初始化为满值一类的，不同的单位之间的战斗也需要考虑到数据怎么交互和计算
# 先就考虑slg的框架来实现功能吧，后期看看能不能把一些其他类型的游戏也兼容进去的，比如avg、rts、比如动作类，这些也都是slg之后的事情了。


#
# 如果说目前先就按照火纹那样的方式来实现的话，那么怎么去装载这些单位对象的属性参数？
# 考虑：
# 1 +-全部都放在全局内部，包括当前hp与最大hp这样两种参数
#   | 那么类似转场回复满血的动作，可以考虑在场景切换的时候对切换函数进行挂钩实现？
#   | 哪些需要在场景切换时候实现初始化的参数就通过场景切换的时候进行统一“再初始化”
#   | 这种实现看起来不错（不过，挂钩接口的考虑以及实现可能会稍微有点难度）
#   | 另外就是全局的数据结构要设计要有很强得把控，不然配置一些计算函数会比较麻烦
#   | 要知道，artist类需要配置的数据很可能有非常多的舞台参数，舞台资源，和全局角色参数混在一起来设计
#   | 数据结构的设计……
#
# 2 +-当专场的时候，将当前hp类似的临时参数（这里仅考虑火纹）放在舞台里面，通过舞台进行调配，
#   | 这样的好处就在于，你可以预先定义一些装载这些属性的结构，提前配置一些对这些参数的调配函数，
#   | 通过转场传入舞台的数据可以通过一些规范化的方式进行调用，这样开发起来可能会更有结构感
#   | 不过有问题就是，这样实现起来就感觉稍微臃肿了一点，后期扩展起来找各种函数会比较麻烦
#
# 这里暂时比较青睐的是1号方案，因为由于所有配置都放在全局的话，配置起来感觉就很一次性（个人感觉而已），真好~
# 前提是要承载所有数据的数据结构要设计好。
#











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
                 ):

        pygame.init()
        self.ticks      = ticks
        self.screen     = pygame.display.set_mode(size, flag, depth)
        self.artist     = artist(self.screen,self.ticks)
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

            # 一些非常全局，关闭之类的事件可以考虑放在这里，快照存档之类也可
            # 不过另一些关于触发式的关闭保存类就还是尽量放在舞台里面会更好一些
            if pygame.key.get_pressed()[K_ESCAPE]:
                pygame.quit()
                exit()







if __name__ == "__main__":
    bg1 = 'sushiplate.jpg'
    bg2 = 'sea.jpg'
    cur = 'sprite_100x100_32.png'

    s = initer(120) # 第一个参数为全局帧率，默认60
    v1 = theater(bg1,'123') # theater必须要指定两个元素，背景图片地址，舞台名字（舞台切换用，键盘C键测试切换）
    actor1 = actor(cur,action='cursor')
    # 现在每个actor内部都会产生一个events对象来实现自身的功能，不过仍然可以通过外部注册的方式将外部events对象注入actor内部

    e = events(cur)
    actor1.regist(e)

    
    v1.regist(actor1)
    

    # 指定blocks之后会按照列行数量对图片切分，然后以每块大小默认为（30，30）进行缩放显示，支持地图缩放
    v2 = theater(bg2,'sea',blocks=(16,12))
    actor2 = actor(cur)
    actor3 = actor(cur,(3,3),'actor',100)
    v2.regist(actor2)
    v2.regist(actor3)

    s.regist(v1)
    s.regist(v2)
    s.run()







