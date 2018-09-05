import pygame
from pygame.locals import *

import re
import random
import time
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
        self.screen.fill((0,0,0))

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
                 bg_filename,       # 背景图片（不确定开发：动态背景？例如白天黑夜效果？其实，白天黑夜可以通过加一层半透明黑的actor实现。）
                 theater_name,      # 场景名字，用于定位、调整、切换场景使用
                 blocks=None,       # 后期扩展，用于配置该场景是否需要切分细块，可指定两个数字参数的tuple或list，作为横纵切分数量
                 singles=[(30,30),(40,40),(60,60),(80,80)],   # 单元大小，blocks被设定时，该参数会被使用，默认使用第一个，扩展地图缩放，以后考虑扩展更顺滑的缩放
                 single_line=[(255,255,255,150),1],           # 单元格分割线的颜色和粗细，这个默认值暂且是为了开发方便
                 music=None         # 后期扩展，音乐
                 ):
        self.theater_name   = theater_name
        self.screen_pos     = (0,0)
        self.group          = pygame.sprite.Group()
        self.background     = None
        self.artist         = None

        # *暂未使用的参数，后续要考虑入场和出场的动画表演，否则切换场景会非常僵硬（至少要提供配置接口）
        self.enter          = None
        self.leave          = None

        # 用于缩放功能的参数，后续考虑默认最大屏的接口
        self.blocks         = blocks
        self.single         = singles[0]
        self.singles        = singles
        self.singles_image  = {}
        self.single_color   = single_line[0] if single_line else None
        self.single_thick   = single_line[1] if single_line else None
        self.toggle         = True

        # 创建每个场景都需要一个默认的背景，图片加载失败就会用默认的某种颜色填充
        self._add_background(bg_filename)

        # 用于坐标定位的参数
        self.point2coord      = None
        self.coord2point      = None

        if blocks:
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
            self.single_color = None # 解决由于地图缩放，导致的线条重绘制使得显示线条变粗的问题


    # 每个场景的创建必须要一张图片作为背景。
    def _add_background(self, bg_filename):
        
        # 背景也是通过 actor类实例化实现
        act = actor(bg_filename)
        def _default_theater(screen, ticks):
            
            # 键盘 + - 控制缩放
            if self._change_size():
                self.toggle = True

            # 控制缩放时的坐标。用toggle的好处为：在初始化时能够执行一次，之后需要缩放成功修改配置
            if self.toggle:
                sw,sh = screen.get_size()
                bw,bh = self.background.image.get_size()
                kw,kh = sw/2 - self.screen_pos[0], sh/2 - self.screen_pos[1]
                tw,th = int(kw - bw/2), int(kh - bh/2)
                px = (sw-bw)/2 if bw<=sw else tw
                py = (sh-bh)/2 if bh<=sh else th
                act.rect[0] = px # 通过修改rect来修改放置的中心点
                act.rect[1] = py
                self.screen_pos = (px, py) # 存储在类里面，后续应用于与其他函数交互
                self.toggle = False

        act.update = _default_theater

        if act.image:
            self.group.add(act)
            self.background = act


    # 目前用简单的 + 和 - 键来控制地图缩放
    def _change_size(self):

        def _change_blocks(toggle):
            v = list(range(len(self.singles)))
            x = self.singles.index(self.single)
            if toggle == '+': ret = self.singles[x+1] if x+1 in v else self.single
            if toggle == '-': ret = self.singles[x-1] if x-1 in v else self.single
            if self.single != ret:
                self.single = ret
                self._mk_blocks_map()
                return True

        # 这里进行了一次统一，之后都统一使用blocks式的缩放。因为这样实现可以更方便。
        # 也就是说，如果你需要缩放功能，请设置blocks参数，另外，将方块黏着的需求交给开发者会更能扩展实现功能。
        # 这里暂时想不到更巧妙的按键设计，pygame.event.get() 属于消耗型事件，所以不能随便堆加使用。
        if pygame.key.get_pressed()[K_KP_PLUS]:
            if self.blocks:
                v = _change_blocks('+'); time.sleep(.1)
                return v
        if pygame.key.get_pressed()[K_KP_MINUS]:
            if self.blocks:
                v = _change_blocks('-'); time.sleep(.1)
                return v
        

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
        self.theater    = None # 将该对象注册进 theater之后会自动绑定相应的 theater。
        self.viscous    = False

        self.events     = pygame.sprite.Group()

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

        return image

    # 控制速率的函数，使任意帧率情况下都保持相同速度的函数
    def _time_update(self,ticks):
        if ticks - self.cur_tick > self.rate:
            self.cur_tick = ticks
            return True


    def regist(self,event):
        
        # 目前的任务就是将actor扩展出一个 event类的接口，和 theater类似的处理方法
        # 该处理方法可以很方便的添加一些类似于对话框一类的插件，让插件和 actor对象进行分离
        # 因为同一个剧场内的游戏表现方式会非常之多，有很多表演呈叠加状态，在同一剧场实现表演
        # 所以让一些对象来承载这些功能可能会更好一些。这样的话也可以让游戏更好开发。
        # 例如： slg 类型游戏可以通过实现一个光标（actor类实例），添加一个event，让光标承载显示属性框功能
        #        slg 类型游戏可以通过实现一个角色（actor类实例），添加一个event，让角色承载某些触发型对话的实现
        # 这样开发会更加自由
        #
        # 而基本的 theater 和 actor 就提供一些非常常用到的大类接口：
        #     方块分割类游戏：方块黏着，坐标点之类的函数
        #==============================================================================
        self.events.add(event)
        event.actor = self # 让事件对象能找到宿主本身


    def update(self,screen,ticks):

        _flash = self._time_update(ticks) # 由于 actor天生需要非常多的速度控制，所以 _flash这个数值复用性很高
        
        if _flash and self.active:
            self.image = self.src_image.subsurface(next(self.rects))
            # 通过以下方法可以实现修改图片大小，不过由于修改大小这部应该会消耗资源，
            # 每次加载都要修改一次大小，所以之后考虑优化的方式，让速度变得更快一些
            # 或者可以考虑放在 self.load_img函数当中，地图切块时需要考虑单元块的适配
            # 将 actor注册进 theater可以获取 theater里面设定的单位大小，后续可能需要扩展多格单位
            # 另外，这里的配置也不太科学。如果有blocks必然会修改尺寸，写太死了，后续再改。目前用于测试比较方便。
            if self.theater.blocks:
                self.image = pygame.transform.scale(self.image,self.theater.single)


        # 事件对象的更新执行可能需要放在这里，且Sprite对象需要image和rect参数
        # 所以用group.update不能没有image单单考虑逻辑问题~~~或者后续这里根据image的有无来判断是否用group.update来跟新？
        # 还要考虑图层的问题，直接通过对self.theater.artist.screen来用draw函数的话，是不行的
        # 因为这样的会被theater自己的后置执行的background覆盖，所以考虑直接画在background（Sprite）的image上面会比较好一些
        # 但是这个图层的问题还是很难解决，如果只是把
        #==============================================================================
        self.events.update()
        self.events.draw(self.theater.background.image)


        # 测试鼠标跟随，后期删除
        x, y = pygame.mouse.get_pos()
        x-= self.image.get_width() // 2
        y-= self.image.get_height() // 2
        v = self.rect_viscous() # 方块黏性测试
        if v:
            x,y = v[0]
        self.rect[0] = x
        self.rect[1] = y
        
        # 测试删除对象本身，后期删除
        if pygame.key.get_pressed()[K_s]:# 键盘s键删除自身单位
            self.kill()

    # 黏性方块，让该对象具备blocks黏性，传入参数可以是地图坐标，或者是一个鼠标坐标
    # 如果该 actor所在的 theater没有进行 blocks切分，那么就返回空，不整齐的地址也会返回空
    def rect_viscous(self,point=None):

        # 需要参与计算的环境参数有
        sizex,sizey = self.theater.artist.screen.get_size()
        diffw,diffh = self.theater.screen_pos
        singw,singh = self.theater.single
        point2coord = self.theater.point2coord

        if self.theater.blocks:
            # 如果 point为一个地图坐标，就获取坐标的界面坐标地址
            if point:
                if point in point2coord:
                    _mapx,_mapy = point2coord[point]
                    _mapx,_mapy = _mapx + diffw,_mapy + diffh
                    return int(_mapx),int(_mapy)

            # 如果 point为 None就获取的是鼠标地址下的方块左上角的坐标
            else:
                posx,posy = pygame.mouse.get_pos()
                # 判断 diff* 参数是为了兼容地图小于界面时的情况
                if diffw>0:
                    if posx>sizex-diffw: posx = sizex-diffw-singw*.5
                    elif posx<diffw: posx = diffw
                if diffh>0:
                    if posy>sizey-diffh: posy = sizey-diffh-singh*.5
                    elif posy<diffh: posy = diffh
                mapx,mapy = posx - diffw,posy - diffh
                cols,raws = self.theater.blocks
                point = min(int(mapx/singw),cols-1),min(int(mapy/singh),raws-1)
                if point in point2coord:
                    _mapx,_mapy = point2coord[point]
                    _mapx,_mapy = _mapx + diffw,_mapy + diffh
                    return (int(_mapx),int(_mapy)),point # 该函数同样返回坐标点数据，便于鼠标与数据交互







# 重要！！！后续可能不将event作为一个sprite对象来处理
# 因为sprite对象非常局限 # 后面都可能将events对象用来捕捉行为和调度功能！！！
# 所以下面的注释之类的和相关的一切代码都会受到修改。慢慢开发吧。后续可能会修改关键字为events。





# 感觉有必要抽象出一个事件类出来 # 但是有点复杂 # 必要性暂不可考证
# 暂时就用 event 这个关键字了，暂时找不到更合适的单词，使用时候注意不要和pygame.event冲突就行
class event(pygame.sprite.Sprite):
    '''
    #====================================================================
    # 事件对象，主要用于实现各式各样依附于角色的事件
    #====================================================================
    '''
    def __init__(self,img=None):
        pygame.sprite.Sprite.__init__(self)
        self.actor = None


        # 需要定义这两个参数 # 仅用于测试
        # 没有image和rect参数的话是不能被group.update执行的
        self.image  = pygame.image.load(img).convert_alpha() if img else None
        self.rect   = self.image.get_rect() if self.image else None
        


    def update(self):
        pass
        























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
    actor1 = actor(cur)

    e = event(cur)
    
    actor1.regist(e)
    v1.regist(actor1)
    

    # 指定blocks之后会按照列行数量对图片切分，然后以每块大小默认为（30，30）进行缩放显示，支持动态缩放
    v2 = theater(bg2,'sea',blocks=(16,12))
    actor2 = actor(cur)
    v2.regist(actor2)

    s.regist(v1)
    s.regist(v2)
    s.run()








