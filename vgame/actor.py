import os, re, time
import traceback
from itertools import cycle, product

import pygame
from pygame.locals import *

from .controller import Controller

class Image:
    '''
    用于单个图片资源的加载，可以是动图，不过现在实现暂时还是不够好
    因为动图的加载模式有时候很不一样，会有细微的位置需要调整
    '''
    def __init__(self, img=None, showsize=None, rate=0):
        # 一些默认配置，用于图片动画的刷新率，可以通过图片名字进行配置
        self.showsize   = showsize # 该参数仅用于对象
        self.rate       = rate # 不同的单位可以使用不同的速率
        self.actor      = None
        self.active     = None # 会在加载图片的时候根据图片类型自动设置
        self.src_image  = None
        self.cur_tick   = 0
        self.rects      = None # 后续用于动图
        self.image      = self.load_img(img)
        self.mask       = pygame.mask.from_surface(self.image)
        self.rigid_mask = None # TODO 这里需要考虑怎么加载成 rect 形式的 mask

    def load_img(self,img):
        try:
            if img is None:
                image = pygame.Surface((60, 60)).convert_alpha()
                image.fill((255,255,255,255))
            elif isinstance(img, tuple):
                image = pygame.Surface((60, 60)).convert_alpha()
                image.fill(img)
            elif isinstance(img, str) and os.path.isdir(img):
                imgfs, imgfv = {}, []
                for idx, imgf in enumerate(sorted(os.listdir(img))):
                    v = tuple(map(int, re.findall(r'\d+', imgf)))
                    v = v if v else idx
                    imgfs[v] = imgf
                    imgfv.append(v)
                func = lambda i:pygame.image.load(os.path.join(img,i)).convert_alpha()
                all_rects = [func(imgfs[i]) for i in sorted(imgfv)]
                self.active    = True
                self.src_image = None
                self.cur_tick  = 0
                self.rects     = cycle(all_rects)
                image = next(self.rects)
            elif isinstance(img, str) and os.path.isfile(img):
                image = pygame.image.load(img).convert_alpha()
                move = re.findall(r'_(\d+)x(\d+)\.', img.lower()) # 根据图片的命名自动切割图片，生成动图
                if move:
                    move        = list(map(int,move[0]))
                    src_h,src_w = image.get_height(),image.get_width()
                    pro_h,pro_w = move[:2]
                    nraws,ncols = int(src_h/pro_h),int(src_w/pro_w)
                    mfunc       = lambda i:(i[0]*pro_w, i[1]*pro_h, pro_w, pro_h)
                    all_rects   = list(map(mfunc,product(range(ncols),range(nraws))))
                    self.active    = True
                    self.src_image = image
                    self.cur_tick  = 0
                    self.rects     = cycle(all_rects)
                    image = self.src_image.subsurface(next(self.rects))
            if self.showsize:
                image = pygame.transform.scale(image, self.showsize)
        except:
            print("无法加载图片.",img)
            print(traceback.format_exc())
            image = None
        return image

    def update_image(self, ticks):
        if self.active and self._time_update(ticks):
            self.image = self.src_image.subsurface(next(self.rects)) if self.src_image else next(self.rects)
            if self.showsize: 
                self.image = pygame.transform.scale(self.image, self.showsize)
            self.mask  = pygame.mask.from_surface(self.image)
        # 显示 mask 边框线，让边框检测处理起来更加的直观
        if self.actor and (self.actor.debug or self.actor.DEBUG):
            pygame.draw.polygon(self.image, self.actor.DEBUG_MASK_LINE_CORLOR, self.mask.outline(), 1)
            pygame.draw.rect(self.image, self.actor.DEBUG_MASK_LINE_CORLOR, self.actor.rect, 1)

    def _time_update(self, ticks):
        if ticks - self.cur_tick > self.rate:
            self.cur_tick = ticks
            return True

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

class Physics:
    '''
    负责物理功能的处理，让方向的操作不仅仅只是像素的简单加减，想让一般物理性质能使用
    重力，惯性，速度，加速度一类的处理全部交给这里来处理，这里面会进行一定的更新处理
    将物理检测的部分交给这个函数，例如一些角色与墙体、路面的交互行为
    '''

    RIGID_BODY = {}
    # 将所有设置 in_physics 为 True 的对象都加入刚体检测
    # 另外这里使用的刚体检测函数，这里将仿照 pygame.sprite.collide_mask 的源代码来实现新的检测
    # 使用的 rect 直接来检测即可

    def __init__(self, in_physics=False):
        self.smooth_speed  = pygame.Vector2(7., 7.) # 初始化有个值，方便看到效果，可以通过对象修改
        self.gravity       = pygame.Vector2(0., 0.) # 重力和速度可以有方向，所以是一个两个数字的向量
        self.speed         = pygame.Vector2(0., 0.) # 与加速度相关的速度
        self.speed_inc     = pygame.Vector2(2., 6.) # 加速度，每个操作片x/y方向的速大小
        self.speed_dec     = pygame.Vector2(1., 1.) # 减速度，类似摩擦力，若为0，则增速之后会想速度方向无限移动下去
        self.speed_max     = pygame.Vector2(10., 10.) # x/y 两个方向上的最大速度
        self.actor         = None # 用于逆向绑定
        self.in_physics    = in_physics
        self.has_bind      = False
        self.is_idle_x     = True
        self.is_idle_y     = True
        self.curr_directs  = {8:None, 2:None, 6:None, 4:None}
        self.effect_start  = {8:None, 2:None, 6:None, 4:None}
        self.effect_toggle = {8:None, 2:None, 6:None, 4:None}
        self.effect_fall   = {8:None, 2:None, 6:None, 4:None}
        self.limit_highs  = None
        self._jump_times   = {8:1, 2:1, 6:1, 4:1}
        self._jump_default = {8:1, 2:1, 6:1, 4:1}
        self.jump_times    = None
        self.fall_ground_l = False # 可以用于检测什么时候落到地面
        self.fall_ground_r = False # 
        self.fall_ground_u = False # 
        self.fall_ground_d = False # 一般2d卷轴基本上都用这个检测

        # 设置空闲状态的减速的频率，让速度变化有一个平滑的改变时间 # 后续可能这个参数会暴露出去？
        self._update_tick_delay  = 15 # 一般更新时间
        self._update_tick        = 0
        self._gravity_tick_delay = 45 # 重力状态更新时间
        self._gravity_tick       = 0

    def move(self, d):
        if d: self.smooth_move(d)

    def move2(self, d):
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
            if (  self.fall_ground_u or (self.effect_toggle[key] and 
                  self.actor.rect.y < self.effect_start[key] - self.limit_highs[key])  ):
                self.effect_toggle[key] = False
                self.effect_fall[key] = True
                if not self.fall_ground_u: 
                    self.actor.rect.y = self.effect_start[key] - self.limit_highs[key]
                self.speed.y = 0
        if key == 2:
            if (  self.fall_ground_d or self.effect_toggle[key] and 
                  self.actor.rect.y > self.effect_start[key] + self.limit_highs[key]  ):
                self.effect_toggle[key] = False
                self.effect_fall[key] = True
                if not self.fall_ground_d: 
                    self.actor.rect.y = self.effect_start[key] + self.limit_highs[key]
                self.speed.y = 0
        if key == 6:
            if (  self.fall_ground_r or self.effect_toggle[key] and 
                  self.actor.rect.x > self.effect_start[key] + self.limit_highs[key]  ):
                self.effect_toggle[key] = False
                self.effect_fall[key] = True
                if not self.fall_ground_r: 
                    self.actor.rect.x = self.effect_start[key] + self.limit_highs[key]
                self.speed.x = 0
        if key == 4:
            if (  self.fall_ground_l or self.effect_toggle[key] and 
                  self.actor.rect.x < self.effect_start[key] - self.limit_highs[key]  ):
                self.effect_toggle[key] = False
                self.effect_fall[key] = True
                if not self.fall_ground_l: 
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
            if self.fall_ground_d and self.jump_times:
                self._jump_times[key] = self.jump_times[key] if self.jump_times.get(key) is not None else self._jump_default[key]
                self.effect_start[key] = None
        if key == 2:
            if self.fall_ground_u and self.jump_times:
                self._jump_times[key] = self.jump_times[key] if self.jump_times.get(key) is not None else self._jump_default[key]
                self.effect_start[key] = None
        if key == 6:
            if self.fall_ground_l and self.jump_times:
                self._jump_times[key] = self.jump_times[key] if self.jump_times.get(key) is not None else self._jump_default[key]
                self.effect_start[key] = None
        if key == 4:
            if self.fall_ground_r and self.jump_times:
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
        aw = self.collide()
        x, y = 0, 0
        if aw:
            if self.gravity.x != 0: x = 1
            for w in aw:
                if self.speed.x > 0: self.actor.rect.x = w.rect.left - self.actor.rect.width
                if self.speed.x < 0: self.actor.rect.x = w.rect.right
        self.actor.rect[1] = self.actor.rect[1] + self.speed.y
        aw = self.collide()
        if aw:
            if self.gravity.y != 0: y = 1
            for w in aw:
                if self.speed.y > 0: self.actor.rect.y = w.rect.top - self.actor.rect.height
                if self.speed.y < 0: self.actor.rect.y = w.rect.bottom
        if x == 1 and y == 0:
            if self.speed.x > 0:
                self.fall_ground_r = True
            if self.speed.x < 0:
                self.fall_ground_l = True
            self.speed.x = 0
        else:
            self.fall_ground_r = False
            self.fall_ground_l = False
        if x == 0 and y == 1:
            if self.speed.y > 0:
                self.fall_ground_d = True
            if self.speed.y < 0:
                self.fall_ground_u = True
            self.speed.y = 0
        else:
            self.fall_ground_d = False
            self.fall_ground_u = False
        self._effect_high_check_core_move()

    def smooth_move(self, d):
        # 这里的 d 为一个方向数字的列表，例如: [2,4] 代表的左下角的方向
        # 这里的处理也只能是平滑移动相关，和重力速度无关
        for i in d:
            if i == 6: self.actor.rect[0] = self.actor.rect[0] + self.smooth_speed.x
            if i == 4: self.actor.rect[0] = self.actor.rect[0] - self.smooth_speed.x
            aw = self.collide()
            if aw:
                for w in aw:
                    if 6 in d: self.actor.rect.x = w.rect.left - self.actor.rect.width
                    if 4 in d: self.actor.rect.x = w.rect.right
            if i == 2: self.actor.rect[1] = self.actor.rect[1] + self.smooth_speed.y
            if i == 8: self.actor.rect[1] = self.actor.rect[1] - self.smooth_speed.y
            aw = self.collide()
            if aw:
                for w in aw:
                    if 2 in d: self.actor.rect.y = w.rect.top - self.actor.rect.height
                    if 8 in d: self.actor.rect.y = w.rect.bottom

    def _delay_bind(self):
        # 这里之所以用 self.actor.theater.artist.currrent 获取当前场景的原因是因为可以节省资源
        # 尽量将一个物体的物理属性只跟当前场景的其他对象进行对比，比每次都与所有对象对比要好。
        # 只能延迟绑定，因为在实例化的时候是不确定 actor 或 theater 有没有绑定上 artist。
        if not self.has_bind and self.in_physics:
            cur = self.actor.theater.artist.currrent
            if cur not in self.RIGID_BODY: self.RIGID_BODY[cur] = []
            self.RIGID_BODY[cur].append(self.actor)
            self.has_bind = True

    def collide(self):
        # 这里的 collide 和 Actor 里面的不一样，这里主要用于处理检测移动相关的内容
        # 所以可以不用直接暴露给用户使用，
        cur = self.actor.theater.artist.currrent
        rigid_bodys = [i for i in self.RIGID_BODY[cur] if self.actor != i]
        scollide = []
        for rigid in rigid_bodys:
            if self.collide_rigid_rect(self.actor, rigid):
                scollide.append(rigid)
        return scollide

    @staticmethod
    def collide_rigid_rect(one, two):
        return pygame.Rect.colliderect(one.rect, two.rect)


class Actor(pygame.sprite.Sprite):
    '''
    单位对象，主要负责一个单位的包装，如果设置了 in_control 为 True 可以让该单位接收控制信号
    控制信号可以通过重写对象的 mouse direction control 函数来从外部处理 actor 实例对控制的交互
    showsize 参数只有在 img 为 None或一个“3/4个数字表示颜色的tuple” 的时候才会有效
    用于修改当你没有填充任何图片的时候默认展示的色块的矩形的大小，方便于一些仅需色块的游戏演示
    如果主动传入了 img(Image类的对象)，那么传入 Image 的 showsize 即可。
    '''
    DEBUG = False # 方便让全部的 Actor 对象都使用 debug 模式，方便开发
    DEBUG_MASK_LINE_CORLOR = (0, 255, 0) # debug 模式将显示 actor 的 mask 边框线颜色

    def __init__(self, img=None, showsize=None, in_control=False, in_physics=True, rate=0, debug=False):
        pygame.sprite.Sprite.__init__(self)

        # 后续这两行需要修改，因为角色的状态资源应该可以有多个，并且由于每个 Image 都要逆向绑定 Actor
        # 所以后续要考虑怎么更加合理的添加角色状态动画的处理
        self._image       = img if not (img is None or isinstance(img, (str, tuple))) else Image(img, showsize, rate)
        self._image.actor = self

        self.debug        = debug # 如果 DEBUG 为 False，这里为 True 则仅仅让该 Actor 这个对象用 debug 模式
        self.image        = self._image.image
        self.mask         = self._image.mask
        self.rect         = self.image.get_rect()
        self.theater      = None # 将该对象注册进 theater之后会自动绑定相应的 theater。
        self.controller   = self.regist_controller(Controller(in_control))
        self.idler        = self.regist_idler(Idler())
        self.physics      = self.regist_physics(Physics(in_physics))
        self.ticks        = None

    def regist_idler(self,idler):
        idler.actor = self # 让事件对象能找到宿主本身
        self.idler  = idler # 这里是为了兼容外部 idler 的注册
        return idler

    def regist_controller(self,controller):
        controller.actor = self # 让事件对象能找到宿主本身
        self.controller  = controller # 这里是为了兼容外部 controller 的注册
        return controller

    def regist_physics(self,physics):
        physics.actor = self
        self.physics = physics
        return physics

    def update(self,ticks):
        self.ticks = ticks
        self._image.update_image(ticks)
        self.physics._delay_bind()
        self.image = self._image.image
        self.mask  = self._image.mask
        m, d, c = self.controller.update(ticks)
        # 根据函数的参数数量，来决定是否传入 Actor 对象自身。
        # 但是有时候传入自身可能会对新手造成一定困惑，我也不想一定要传入自身，下面的代码可以兼容两者
        self.mouse(m)     if self.mouse.__code__.co_argcount     == 1 else self.mouse(self, m)
        self.control(c)   if self.control.__code__.co_argcount   == 1 else self.control(self, c)
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
                operations = {}
                operations['mouse'] = m
                operations['direction'] = d
                operations['control'] = c
                self.idle(self, operations)
        # 惯性，重力处理相关的内容
        self.physics.update(ticks)

    def collide(self, *list_sprite):
        scollide = pygame.sprite.spritecollide(self, self.theater.group, False, pygame.sprite.collide_mask)
        rcollide = []
        for sprite in list_sprite:
            if sprite in scollide:
                rcollide.append(sprite)
        return rcollide

    @staticmethod
    def mouse(mouse_info): pass

    @staticmethod
    def direction(direction_info): pass

    @staticmethod
    def control(control_info): pass

    @staticmethod
    def idle(): pass