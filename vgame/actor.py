import os, re, time, math
import traceback
from itertools import cycle, product

import pygame
from pygame.locals import *

from .image import Image
from .controller import Controller

class Idler:
    '''
    主要负责 actor 的一些持续行为，想要实现一些敌反馈机制
    目前开发的方向主要是想要能够通过 Actor 对象内直接调用到
    例如：
        act = Actor()
        act.idle
    '''
    def __init__(self):
        self.actor = None
        self.delay = 15 # 防止资源消耗过高
        self._tick = 0

    def update(self, ticks):
        if self._update_delay(ticks):
            return True

    def _update_delay(self,ticks):
        if ticks - self._tick > self.delay:
            self._tick = ticks
            return True



class Mover:
    '''
    用于处理碰撞检测的原始函数部分，一般的mover直接继承使用
    '''
    def _delay_bind(self):
        if not self.has_bind and self.in_entity:
            cur = self.actor.theater.artist.currrent
            self.actor.RIGID_BODY[cur].append(self.actor)
            self.has_bind = True

    def collide(self):
        cur = self.actor.theater.artist.currrent
        rigid_bodys = []
        for entitys in self.actor.in_entitys or []:
            if entitys in ENTITYS:
                rigid_bodys.extend([i for i in entitys.RIGID_BODY[cur] if i != self.actor])
            else:
                rigid_bodys.append(entitys) # 处理单独某个 Actor 对象的互斥
        scollide = []
        for rigid in rigid_bodys:
            if self.collide_rigid(self.actor, rigid):
                scollide.append(rigid)
        return scollide

    @staticmethod
    def collide_rigid(one, two):
        return pygame.Rect.colliderect(one.rect, two.rect)


class SmoothMover(Mover):
    '''
    平滑移动的处理
    '''

    ALLDIR = [6, 4, 2, 8]

    def __init__(self, in_entity=False):
        self.speed     = pygame.Vector2(5., 5.) # 初始化有个值，方便看到效果，可以通过对象修改
        self.in_entity = in_entity

    def move(self, d):
        if d: self.smooth_move(d, self.speed)

    def move_angle(self, angle):
        self.smooth_move([6], self.speed, angle)

    def smooth_move(self, d, speed, rotate=None):
        vx, vy = 0, 0
        if isinstance(d, int) and d in self.ALLDIR:
            d = [d]
        for i in d:
            if i == 6: vx = speed.x
            if i == 4: vx = -speed.x
            if i == 2: vy = speed.y
            if i == 8: vy = -speed.y
        speed = pygame.Vector2(vx, vy)
        if rotate:
            speed = speed.rotate(rotate)
        self.actor.rect[0] = self.actor.rect[0] + speed.x
        if self.in_entity:
            aw = self.collide()
            if aw:
                for w in aw:
                    if speed.x > 0: self.actor.rect.x = w.rect.left - self.actor.rect.width
                    if speed.x < 0: self.actor.rect.x = w.rect.right
        self.actor.rect[1] = self.actor.rect[1] + speed.y
        if self.in_entity:
            aw = self.collide()
            if aw:
                for w in aw:
                    if speed.y > 0: self.actor.rect.y = w.rect.top - self.actor.rect.height
                    if speed.y < 0: self.actor.rect.y = w.rect.bottom



class PhysicsMover(Mover):
    '''
    负责物理功能的处理，让方向的操作不仅仅只是像素的简单加减，想让一般物理性质能使用
    重力，惯性，速度，加速度一类的处理全部交给这里来处理，这里面会进行一定的更新处理
    将物理检测的部分交给这个函数，例如一些角色与墙体、路面的交互行为
    '''

    def __init__(self, in_entity=False):
        self.smooth_speed  = pygame.Vector2(7., 7.) # 初始化有个值，方便看到效果，可以通过对象修改
        self.gravity       = pygame.Vector2(0., 0.) # 重力和速度可以有方向，所以是一个两个数字的向量
        self.speed         = pygame.Vector2(0., 0.) # 与加速度相关的速度
        self.speed_inc     = pygame.Vector2(4., 3.) # 加速度，每个操作片x/y方向的速大小
        self.speed_dec     = pygame.Vector2(2., 2.) # 减速度，类似摩擦力，若为0，则增速之后会想速度方向无限移动下去
        self.speed_max     = pygame.Vector2(6., 9.) # x/y 两个方向上的最大速度
        self.actor         = None # 用于逆向绑定
        self.in_entity     = in_entity
        self.has_bind      = False
        self.is_idle_x     = True
        self.is_idle_y     = True
        self.curr_directs  = {8:None, 2:None, 6:None, 4:None}
        self.effect_start  = {8:None, 2:None, 6:None, 4:None}
        self.effect_toggle = {8:None, 2:None, 6:None, 4:None}
        self.effect_fall   = {8:None, 2:None, 6:None, 4:None}
        self.limit_highs   = None
        self._jump_times   = {8:1, 2:1, 6:1, 4:1}
        self._jump_default = {8:1, 2:1, 6:1, 4:1}
        self.jump_times    = None
        self.fall_grounds  = {8:None, 2:None, 6:None, 4:None}
        # 设置空闲状态的减速的频率，让速度变化有一个平滑的改变时间 # 后续可能这个参数会暴露出去？
        self._update_tick_delay  = 15 # 一般更新时间
        self._update_tick        = 0
        self._gravity_tick_delay = 45 # 重力状态更新时间
        self._gravity_tick       = 0

    def check_parameter_bug(self):
        # 最大速度必须大于重力速度，否则跳不起来
        # 如果存在重力，则重力速度必须大于加速度，否则跳跃时有可能让物体超越限制高度
        try:
            assert self.speed_max.x >= abs(self.gravity.x), "maximum speed must be greater than gravity"
            assert self.speed_max.y >= abs(self.gravity.y), "maximum speed must be greater than gravity"
            if self.gravity.x:
                assert abs(self.gravity.x) >= self.speed_inc.x, "gravity must be greater than acceleration"
            if self.gravity.y:
                assert abs(self.gravity.y) >= self.speed_inc.y, "gravity must be greater than acceleration"
        except Exception as e:
            print(('err actor id: {}\n    currrent gravity: {}\n    currrent speed_max: {}\n    currrent speed_inc: {}\n')
                        .format(id(self.actor), self.gravity, self.speed_max, self.speed_inc))
            raise e

    def move(self, d):
        for key in self.curr_directs:
            self.curr_directs[key] = True if key in (d or []) else False
        if d:
            self._effect_high_check_direction(d)
            self.inertia_speed_direction(d)
            self.is_idle_x = False if 6 in d or 4 in d else True
            self.is_idle_y = False if 8 in d or 2 in d else True
        else:
            self.is_idle_x = True
            self.is_idle_y = True

    def _effect_high_check_direction(self, d):
        # 这部分的开发尤为重要，为了能够固定住跳跃的高度，检测变化的函数需要与核心移动模块同频
        # 所以也就有了两个函数
        #  _effect_high_check_direction # 放在控制操作中，作为开关
        #  _effect_high_check_core_move # 放在核心移动操作中，与核心移动函数同频
        if self.limit_highs:
            for key in self.limit_highs:
                if key == 8 and self.gravity.y != 0:
                    if self.effect_start[key] == None and key in d:
                        self.effect_start[key] = self.actor.rect.y - self.speed.y
                        self.effect_toggle[key] = True
                    if not self.effect_toggle[key]:
                        if key in d: d.remove(key)
                if key == 2 and self.gravity.y != 0:
                    if self.effect_start[key] == None and key in d:
                        self.effect_start[key] = self.actor.rect.y - self.speed.y
                        self.effect_toggle[key] = True
                    if not self.effect_toggle[key]:
                        if key in d: d.remove(key)
                if key == 4 and self.gravity.x != 0:
                    if self.effect_start[key] == None and key in d:
                        self.effect_start[key] = self.actor.rect.x - self.speed.x
                        self.effect_toggle[key] = True
                    if not self.effect_toggle[key]:
                        if key in d: d.remove(key)
                if key == 6 and self.gravity.x != 0:
                    if self.effect_start[key] == None and key in d:
                        self.effect_start[key] = self.actor.rect.x - self.speed.x
                        self.effect_toggle[key] = True
                    if not self.effect_toggle[key]:
                        if key in d: d.remove(key)

    def _effect_high_check_core_move(self):
        # 这个函数必须放在核心移动函数 _core_move 里面，这个函数需要与核心函数同频
        # 否则会有很麻烦的问题。
        if self.limit_highs:
            for key in self.effect_toggle:
                if self.effect_start.get(key) is not None:
                    self._catch_jump_up(key)
                    self._catch_jumps(key)
                self._catch_jump_fall(key)

    def _catch_jump_up(self, key):
        if key == 8:
            if (  self.fall_grounds[key] or (self.effect_toggle[key] and 
                  self.actor.rect.y < self.effect_start[key] - self.limit_highs[key])  ):
                self.effect_toggle[key] = False
                self.effect_fall[key] = True
                if not self.fall_grounds[key]: 
                    self.actor.rect.y = self.effect_start[key] - self.limit_highs[key]
                self.speed.y = 0
        if key == 2:
            if (  self.fall_grounds[key] or self.effect_toggle[key] and 
                  self.actor.rect.y > self.effect_start[key] + self.limit_highs[key]  ):
                self.effect_toggle[key] = False
                self.effect_fall[key] = True
                if not self.fall_grounds[key]: 
                    self.actor.rect.y = self.effect_start[key] + self.limit_highs[key]
                self.speed.y = 0
        if key == 6:
            if (  self.fall_grounds[key] or self.effect_toggle[key] and 
                  self.actor.rect.x > self.effect_start[key] + self.limit_highs[key]  ):
                self.effect_toggle[key] = False
                self.effect_fall[key] = True
                if not self.fall_grounds[key]: 
                    self.actor.rect.x = self.effect_start[key] + self.limit_highs[key]
                self.speed.x = 0
        if key == 4:
            if (  self.fall_grounds[key] or self.effect_toggle[key] and 
                  self.actor.rect.x < self.effect_start[key] - self.limit_highs[key]  ):
                self.effect_toggle[key] = False
                self.effect_fall[key] = True
                if not self.fall_grounds[key]: 
                    self.actor.rect.x = self.effect_start[key] - self.limit_highs[key]
                self.speed.x = 0

    def _catch_jumps(self, key):
        if self.effect_toggle[key]:
            # 跳起阶段的松手
            if not self.curr_directs[key]: 
                if self.jump_times:
                    self._jump_times[key] -= 1
                    if self._jump_times[key] > 0:
                        self.effect_start[key] = None
                else:
                    self.effect_start[key] = None
                self.effect_toggle[key] = False
        if self.effect_fall[key]:
            # 下落阶段的松手
            if not self.curr_directs[key]: 
                if self.jump_times:
                    self._jump_times[key] -= 1
                    if self._jump_times[key] > 0:
                        self.effect_start[key] = None
                else:
                    self.effect_start[key] = None
                self.effect_toggle[key] = False
                self.effect_fall[key] = False

    def _catch_jump_fall(self, key):
        if key == 8:
            if self.fall_grounds[2] and self.jump_times:
                self._jump_times[key] = self.jump_times[key] if self.jump_times.get(key) is not None else self._jump_default[key]
                self.effect_start[key] = None
        if key == 2:
            if self.fall_grounds[8] and self.jump_times:
                self._jump_times[key] = self.jump_times[key] if self.jump_times.get(key) is not None else self._jump_default[key]
                self.effect_start[key] = None
        if key == 6:
            if self.fall_grounds[4] and self.jump_times:
                self._jump_times[key] = self.jump_times[key] if self.jump_times.get(key) is not None else self._jump_default[key]
                self.effect_start[key] = None
        if key == 4:
            if self.fall_grounds[6] and self.jump_times:
                self._jump_times[key] = self.jump_times[key] if self.jump_times.get(key) is not None else self._jump_default[key]
                self.effect_start[key] = None

    def update(self,ticks):
        # 之所以需要将 idle 处理放置在这里是因为考虑到当你没有操作更新的时候
        # 有时候有人在 inertia_move 操作的时候，可能先判断了 d 是否为空
        # 然后再进行的操作，那样的话，如果将这里的 idle 操作放在 inertia_move 里面
        # 那么 idle 状态的操作就永远不会执行。所以需要将这个函数执行放置在循环里面
        # 防止一些情况下操作失效的问题
        # *非常要注意的是！！！
        # 重力系统和摩擦系统不能用在一个系统里面，所以这里用了一个简单的处理
        # 当 gravity.x == 0 的时候就默认使用 x 方向归零式的摩擦
        # 当 gravity.x != 0 的时候就在 x 方向使用重力
        # y 方向同理
        # 所以对于一般的游戏来说，只要你给 gravity.y 设置一个比较小的数字
        # 对象的空间就有了重力系统。左右方向用的是一般的摩擦系统，这样和一般游戏的概念基本相等了
        if self._gravity_delay(ticks):
            if self.gravity.x != 0: self.gravity_speed_idle_x()
            if self.gravity.y != 0: self.gravity_speed_idle_y()

        if self._update_delay(ticks):
            if self.speed.x != 0 or self.speed.y != 0:
                if self.is_idle_x and self.gravity.x == 0: self.inertia_speed_idle_x()
                if self.is_idle_y and self.gravity.y == 0: self.inertia_speed_idle_y()
        self._core_move()

    def _update_delay(self,ticks):
        if ticks - self._update_tick > self._update_tick_delay:
            self._update_tick = ticks
            return True

    def _gravity_delay(self,ticks):
        if ticks - self._gravity_tick > self._gravity_tick_delay:
            self._gravity_tick = ticks
            return True

    def inertia_speed_direction(self, d):
        for dirc in d:
            if dirc == 6:
                if self.speed.x >= 0:
                    self.speed.x = min(self.speed.x + self.speed_inc.x, self.speed_max.x)
                if self.speed.x < 0:
                    self.speed.x = min(self.speed.x + self.speed_inc.x, 0)
            if dirc == 4:
                if self.speed.x <= 0:
                    self.speed.x = max(self.speed.x - self.speed_inc.x, -self.speed_max.x)
                if self.speed.x > 0:
                    self.speed.x = max(self.speed.x - self.speed_inc.x, 0)
            if dirc == 2:
                if self.speed.y >= 0:
                    self.speed.y = min(self.speed.y + self.speed_inc.y, self.speed_max.y)
                if self.speed.y < 0:
                    self.speed.y = min(self.speed.y + self.speed_inc.y, 0)
            if dirc == 8:
                if self.speed.y <= 0:
                    self.speed.y = max(self.speed.y - self.speed_inc.y, -self.speed_max.y)
                if self.speed.y > 0:
                    self.speed.y = max(self.speed.y - self.speed_inc.y, 0)

    def inertia_speed_idle_x(self):
        if self.speed.x < 0: self.speed.x = min(self.speed.x + self.speed_dec.x, 0)
        if self.speed.x > 0: self.speed.x = max(self.speed.x - self.speed_dec.x, 0)

    def inertia_speed_idle_y(self):
        if self.speed.y < 0: self.speed.y = min(self.speed.y + self.speed_dec.y, 0)
        if self.speed.y > 0: self.speed.y = max(self.speed.y - self.speed_dec.y, 0)

    def gravity_speed_idle_x(self):
        self.speed.x = max(min(self.speed.x + self.gravity.x, self.speed_max.x), -self.speed_max.y)

    def gravity_speed_idle_y(self):
        self.speed.y = max(min(self.speed.y + self.gravity.y, self.speed_max.y), -self.speed_max.y)

    def _core_move(self):
        self.actor.rect[0] = self.actor.rect[0] + self.speed.x
        x, y = 0, 0
        if self.in_entity:
            aw = self.collide()
            if aw:
                if self.gravity.x != 0: x = 1
                for w in aw:
                    if self.speed.x > 0: self.actor.rect.x = w.rect.left - self.actor.rect.width
                    if self.speed.x < 0: self.actor.rect.x = w.rect.right
        self.actor.rect[1] = self.actor.rect[1] + self.speed.y
        if self.in_entity:
            aw = self.collide()
            if aw:
                if self.gravity.y != 0: y = 1
                for w in aw:
                    if self.speed.y > 0: self.actor.rect.y = w.rect.top - self.actor.rect.height
                    if self.speed.y < 0: self.actor.rect.y = w.rect.bottom
        if x == 1 and y == 0:
            if self.speed.x > 0: self.fall_grounds[6] = True
            if self.speed.x < 0: self.fall_grounds[4] = True
            self.speed.x = 0
        else:
            self.fall_grounds[6] = False
            self.fall_grounds[4] = False
        if x == 0 and y == 1:
            if self.speed.y > 0: self.fall_grounds[2] = True
            if self.speed.y < 0: self.fall_grounds[8] = True
            self.speed.y = 0
        else:
            self.fall_grounds[2] = False
            self.fall_grounds[8] = False
        self._effect_high_check_core_move()




class Clicker:
    '''
    增强鼠标的功能，例如使用鼠标左键拖动对象之类的处理。
    后续看情况增强额外功能。
    '''
    def __init__(self,):
        self.m1    = None # 用于处理拖动图标功能
        self.m2    = None # 用于处理拖动图标功能
        self.actor = None

    def dnd(self, m, lr='left'): # 实现鼠标拖拽对象的功能
        # m 为鼠标的消息信息
        # m 如非 None，则为一个三元组：
        # m[0] 表示按键，数字0代表左键，数字2代表右键
        # m[1] 表示模式，数字0代表单击，数字2代表拖动
        # m[2] 表示两个点的坐标，m[2][0] 为按下鼠标时的坐标， m[2][1] 为松开鼠标时的坐标
        if m and m[1] == 2:
            if (lr == 'left'  and m[0] == 0) or \
               (lr == 'right' and m[0] == 2):
                x,y,w,h = self.actor.rect
                sx,sy = m[2][0]
                ex,ey = m[2][1]
                self.m1,self.m2 = ((sx,sy),(x, y, w, h)) if self.m1 != (sx,sy) else (self.m1,self.m2)
                if ( (sx >= self.m2[0] and sx <= self.m2[0] + self.m2[2]) and 
                     (sy >= self.m2[1] and sy <= self.m2[1] + self.m2[3]) ):
                    dx,dy = self.m1[0] - self.m2[0], self.m1[1] - self.m2[1]
                    self.actor.rect[0] = ex - dx
                    self.actor.rect[1] = ey - dy




class Actor(pygame.sprite.Sprite):
    '''
    单位对象，主要负责一个单位的包装，如果设置了 in_control 为 True 可以让该单位接收控制信号
    控制信号可以通过重写对象的 mouse direction control 函数来从外部处理 actor 实例对控制的交互
    showsize 参数只有在 img 为 None或一个“3/4个数字表示颜色的tuple” 的时候才会有效
    用于修改当你没有填充任何图片的时候默认展示的色块的矩形的大小，方便于一些仅需色块的游戏演示
    如果主动传入了 img(Image类的对象)，那么传入 Image 的 showsize 即可。
    '''
    DEBUG = False # 方便让全部的 Actor 对象都使用 debug 模式，方便开发
    DEBUG_MASK_LINE_CORLOR = (0, 200, 0, 200) # debug 模式将显示 actor 的 mask 边框线颜色
    DEBUG_RECT_LINE_CORLOR = (200, 0, 0, 200)

    RIGID_BODY = {}

    def __init__( self, 
                  img        = None,  # 图片信息
                  showsize   = None,  # 图片展示大小
                  masksize   = None,  # 实体方框大小
                  showpoint  = None,  # 图片初始位置
                  in_control = False, # 是否接收操作信息
                  in_entity  = True,  # 是否拥有实体
                  in_entitys = None,  # 需要互斥的实体列表，可以传入Actor对象也可以传入类对
                  rate       = 0,     # 动态图循环的速率
                  cam_follow = True,  # 镜头跟随，默认开启
                  debug      = False  # 是否开启单个 Actor 对象的 Debug 模式
            ):
        pygame.sprite.Sprite.__init__(self)

        # 后续这两行需要修改，因为角色的状态资源应该可以有多个，并且由于每个 Image 都要逆向绑定 Actor
        # 所以后续要考虑怎么更加合理的添加角色状态动画的处理
        self.rate       = rate
        self.showsize   = showsize # showsize 用于墙体检测，所以比较常用，尽量主动设置
        self.masksize   = masksize # masksize 用于碰撞检测，使用默认的从图片中读取即可
        self.imager     = None
        self.image      = None
        self.mask       = None
        self.aload_image(img)

        self.axis       = None # 用于栅格类游戏，角色可以在 theater.map 中的函数处理运动，最短路径计算等

        self.debug      = debug # 如果 DEBUG 为 False，这里为 True 则仅仅让该 Actor 这个对象用 debug 模式
        self.rect       = self.image.get_rect()
        self.theater    = None # 将该对象注册进 theater之后会自动绑定相应的 theater。
        self.controller = self.regist(Controller(in_control))
        self.idler      = self.regist(Idler())
        self.physics    = self.regist(PhysicsMover(in_entity))
        self.pmover     = self.physics # 简化使用名
        self.mover      = self.regist(SmoothMover(in_entity))
        self.clicker    = self.regist(Clicker())
        self.in_entitys = in_entitys if in_entitys is not None else ENTITYS_DEFAULT.copy()
        self.ticks      = None
        self.cam_follow = cam_follow

        if showpoint: self.rect[:2] = showpoint
        self.bug_check  = None

    def aload_image(self, img):
        if not (img is None or isinstance(img, (str, tuple, pygame.Surface))):
              self.imager = img  
        else: self.imager = Image(img, self.showsize, self.rate, self.masksize)
        self.image  = self.imager.image
        self.mask   = self.imager.mask
        self.imager.actor = self
        return self.imager

    def regist(self, reg):
        reg.actor = self # 逆向绑定
        return reg

    def update(self,ticks):
        if not self.bug_check:
            # 这小块的代码用于处理一些参数配置时候的不妥当，在运行时进行一次简单的自检，方便查出问题。
            self.bug_check = True
            self.physics.check_parameter_bug()

        self.ticks = ticks
        self.imager.update_image(ticks)
        self.image = self.imager.image
        self.mask  = self.imager.mask
        m, d, c = self.controller.update(ticks)
        # 用小技巧实现重载
        # 根据函数的参数数量，来决定是否传入 Actor 对象自身。
        # 但是有时候传入自身可能会对新手造成一定困惑，我也不想一定要传入自身，下面的代码可以兼容两者

        # 鼠标操作
        if self.mouse.__code__.co_argcount == 1:
            self.mouse(m)
        elif self.mouse.__code__.co_argcount == 2: 
            self.mouse(self, m)
        # 控制键操作
        if self.control.__code__.co_argcount == 1:
            self.control(c)    
        elif self.control.__code__.co_argcount == 2: 
            self.control(self, c)
        # 方向键操作
        if self.direction.__code__.co_argcount == 1:
            self.direction(d)
        elif self.direction.__code__.co_argcount == 2:
            self.direction(self, d)
        elif self.direction.__code__.co_argcount == 3:
            self.direction(self, d, c) # 2d卷轴游戏可能需要别的键作为跳跃功能，所以需要处理更多消息
        # 空闲状态的持续执行的函数
        if self.idler.update(ticks):
            if self.idle.__code__.co_argcount == 0:
                self.idle()
            elif self.idle.__code__.co_argcount == 1:
                self.idle(self)
            elif self.idle.__code__.co_argcount == 2:
                self.idle(self, {'mouse':m, 'direction':d, 'control':c})

        # 惯性，重力处理相关的内容
        self.physics._delay_bind()
        self.physics.update(ticks)

    def collide(self, *list_sprite):
        scollide = pygame.sprite.spritecollide(self, self.theater.group, False, pygame.sprite.collide_mask)
        rcollide = []
        for sprite in list_sprite:
            if sprite in scollide:
                rcollide.append(sprite)
        return rcollide

    def angle(self, sprite):
        sx, sy = self.rect.center
        tx, ty = sprite.rect.center
        return math.atan2((ty - sy), (tx - sx)) * 57.2958

    def kill(self):
        cur = self.theater.artist.currrent
        if self in self.RIGID_BODY[cur]:
            self.RIGID_BODY[cur].remove(self)
        super().kill()

    def change_theater(self, theatername):
        self.theater.artist.change_theater(theatername)

    @staticmethod
    def mouse(mouse_info): pass

    @staticmethod
    def direction(direction_info): pass

    @staticmethod
    def control(control_info): pass

    @staticmethod
    def idle(): pass




# 后面基于 Actor 封装出几种游戏元素的对象
# 1 玩家, 2 墙面, 3 子弹, 4 敌人, 5 NPC
# 默认情况下，除了墙以外，其他实体都不互斥，并且其他所有物体均与墙体互斥
# 如果想要单独修改某个对象是否互斥某些类型互斥就直接修改对象的属性
# eg.
#    import vgame
#    s = vgame.Actor()
#    b = vgame.Actor()
#    s.in_entitys = [vgame.Wall, vgame.Enemy, b] # 设置与墙和敌人互斥，也能设置与某些对象互斥
#
# 也可以实例化的时候就传入 in_entitys 的参数，不过那样的话不太便利，
# 因为游戏中有时是需要对某个单独的对象互斥而非某一类互斥，这个接口也可以传入 Actor 实例，
# 但是对实例对象处理的时候，需要考虑到有时候有些对象是后续才实例化的
# 如果非要在实例化时候传入会在代码排序上不够自由，所以十分推荐用动态修改属性的方式进行互斥配置
# 这样不用调整顺序，而且代码看上去会更加清晰一些。

class Player(Actor):
    RIGID_BODY = {}
    def __init__(self, *a, player='p1', **kw):
        kw['in_control'] = True
        super().__init__(*a, **kw)
class NPC(Actor):
    RIGID_BODY = {}
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
class Enemy(Actor):
    RIGID_BODY = {}
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
class Bullet(Actor):
    RIGID_BODY = {}
    def __init__(self, *a, **kw):
        kw['in_entity'] = False
        kw['in_entitys'] = [] # 默认情况只检测 ENTITYS_DEFAULT 内的物体，子弹类则无需实体检测
        super().__init__(*a, **kw)

class Wall(Actor):
    RIGID_BODY = {}
    def __init__(self, *a, **kw):
        kw['in_entitys'] = ENTITYS # 墙体也要自动对其他类型的数据进行互斥，否则墙体运动时候不会与
        super().__init__(*a, **kw)


ENTITYS = [Player, NPC, Enemy, Wall]
ENTITYS_DEFAULT = [Wall]


# 菜单的处理和游戏相关性不大，但是由于我开发的思路是每个场景统一使用一个 sprite.group 来装下所有的元素
# 所以菜单类仍旧使用继承自 Actor，这些所有的 sprite 后续统一在 Theater 里管理，
# 后续会最终在 Artist 类里面统一更新画面。
# 这里的菜单肯定需要增加一些更加像是菜单的菜单处理，预计会包含一些点击事件的 HOOK 之类的。
# 目前先就抽象出这样一个类来。
class Menu(Actor):
    RIGID_BODY = {}
    def __init__(self, *a, **kw):
        kw['in_entity'] = False
        kw['in_entitys'] = []
        kw['cam_follow'] = False # 菜单一般都不需要镜头跟随的处理，之所以都使用
        super().__init__(*a, **kw)

# 该处的背景类仅用于规范游戏的范围使用的
class Background(Actor):
    RIGID_BODY = {}
    def __init__(self, *a, **kw):
        kw['in_entity'] = False
        kw['in_entitys'] = []
        kw['cam_follow'] = True # 背景需要镜头跟随的处理，之所以都使用
        super().__init__(*a, **kw)