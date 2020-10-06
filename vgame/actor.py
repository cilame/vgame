import os, re, time, math
import inspect
import traceback
from itertools import cycle, product

import pygame
from pygame.locals import *
from pygame.mask import from_surface

from .image import Image, ImageMaker, Text
from .controller import Controller

import vgame

class Delayer:
    '''
    主要负责 actor 的一些持续行为，想要实现一些敌反馈机制
    目前开发的方向主要是想要能够通过 Actor 对象内直接调用到
    例如：
        act = Actor()
        act.idle
    '''
    def __init__(self, delay=15):
        self.actor = None
        self.delay = delay # 防止资源消耗过高
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
    def __init__(self):
        self.has_bind = False

    def _delay_bind(self):
        if not self.has_bind and self.in_entity:
            cur = self.actor.theater.artist.current
            self.actor.RIGID_BODY[cur].append(self.actor)
            self.has_bind = True

    def collide(self):
        cur = self.actor.theater.artist.current
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

    def __init__(self, in_entity=False, in_bounds=True):
        self.actor     = None
        self.speed     = pygame.Vector2(5., 5.) # 初始化有个值，方便看到效果，可以通过对象修改
        self.in_entity = in_entity
        self.in_bounds = in_bounds
        super().__init__()

    def move(self, d, speed=None):
        if d and not self.actor._toggle['gridmove_start']:
            self.auto_change_local()
            self.auto_change_direct(d)
            self.smooth_move(d, self.speed if speed is None else pygame.Vector2(speed, speed))

    def auto_change_local(self):
        try:
            actor = self.actor
            caxis = actor.axis
            if caxis:
                naxis = actor.theater.map._calc_center_by_rect(actor)
                obstruct = actor.obstruct or 0
                if caxis != naxis:
                    actor.axis = naxis
                    if obstruct:
                        actor.theater.map.map2d._local_add_del(caxis, naxis, obstruct)
        except:
            traceback.print_exc()
            print('Actor out of bounds. {}'.format(self.actor.axis))

    def auto_change_direct(self, d):
        curr = self.actor.status['current']
        if 4 in d or 6 in d:
            if 4 in d: targ = self.actor.status['direction'].get('left')
            if 6 in d: targ = self.actor.status['direction'].get('right')
        else:
            if 2 in d: targ = self.actor.status['direction'].get('down')
            if 8 in d: targ = self.actor.status['direction'].get('up')
        if targ and curr != targ: self.actor.aload_image(targ)

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
        if self.in_bounds:
            w, h = self.actor.theater.size
            w = w - self.actor.rect.width
            h = h - self.actor.rect.height
            if self.actor.rect.x < 0: self.actor.rect.x = 0
            if self.actor.rect.x > w: self.actor.rect.x = w
            if self.actor.rect.y < 0: self.actor.rect.y = 0
            if self.actor.rect.y > h: self.actor.rect.y = h

    def gridmove(self, actor, curr_xy, new_xy, speed):
        # 这里的xy均为 actor 的左上角像素级坐标，所以使用这个函数时请先转换到正确的数据再运行
        _x, _y = curr_xy
        nx, ny = new_xy
        speed = int(1 if speed is None else speed)
        xline = []
        yline = []
        if _y < ny:
            ty = _y
            while ty < ny:
                ty += speed
                if ty <= ny: yline.append(ty)
            if ty != ny:
                yline.append(ny)
        if _y > ny:
            ty = _y
            while ty > ny:
                ty -= speed
                if ty >= ny: yline.append(ty)
            if ty != ny:
                yline.append(ny)
        if _y == ny: yline.append(ny)
        if _x < nx:
            tx = _x
            while tx < nx:
                tx += speed
                if tx <= nx: xline.append(tx)
            if tx != nx:
                xline.append(nx)
        if _x > nx:
            tx = _x
            while tx > nx:
                tx -= speed
                if tx >= nx: xline.append(tx)
            if tx != nx:
                xline.append(nx)
        if _x == nx: xline.append(nx)
        if len(xline) > len(yline):
            for i in range(len(xline)-len(yline)):
                yline.append(yline[-1])
        if len(yline) > len(xline):
            for i in range(len(yline)-len(xline)):
                xline.append(xline[-1])
        chain = []
        for x, y in zip(xline, yline):
            def func(x, y):
                actor.rect.x = x
                actor.rect.y = y
            chain.append([func, (x, y), False])
        return chain

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

    def collide(self, pos):
        return self.actor.rect.collidepoint(pos)

class Actor(pygame.sprite.Sprite):
    '''
    单位对象，主要负责一个单位的包装，如果设置了 in_control 为 True 可以让该单位接收控制信号
    控制信号可以通过重写对象的 mouse direction control 函数来从外部处理 actor 实例对控制的交互
    showsize 参数只有在 img 为 None或一个“3/4个数字表示颜色的tuple” 的时候才会有效
    用于修改当你没有填充任何图片的时候默认展示的色块的矩形的大小，方便于一些仅需色块的游戏演示
    如果主动传入了 img(Image类的对象)，那么传入 Image 的 showsize 即可。
    '''
    DEBUG = False # 方便让全部的 Actor 对象都使用 debug 模式，方便开发
    DEBUG_RECT_LINE_CORLOR = (0, 200, 0, 200) # debug 模式将显示 actor 的 mask 边框线颜色
    DEBUG_MASK_LINE_CORLOR = (200, 0, 0, 200)
    DEBUG_REALIMAGE_CORLOR = (200, 200, 200, 200)

    RIGID_BODY = {}

    def __init__( self, 
                  img        = None,  # 图片信息
                  showsize   = None,  # 图片展示大小
                  masksize   = None,  # 实体方框大小
                  rectsize   = None,
                  showpoint  = None,  # 图片初始位置
                  in_control = False, # 是否接收操作信息
                  in_entity  = True,  # 是否拥有实体
                  in_bounds  = True,  # 是否允许地图边界约束，# 默认True，即为物体移动不会超出边界
                  in_entitys = None,  # 需要互斥的实体列表，可以传入Actor对象也可以传入类对
                  rate       = 0,     # 动态图循环的速率
                  offsets    = (0,0), # 图片的偏移位置
                  cam_follow = True,  # 镜头跟随，默认开启
                  debug      = False  # 是否开启单个 Actor 对象的 Debug 模式
            ):
        pygame.sprite.Sprite.__init__(self)

        # 后续这两行需要修改，因为角色的状态资源应该可以有多个，并且由于每个 Image 都要逆向绑定 Actor
        # 所以后续要考虑怎么更加合理的添加角色状态动画的处理
        self.img        = img
        self.rate       = rate
        self.showsize   = showsize # showsize 用于墙体检测，所以比较常用，尽量主动设置
        self.rectsize   = rectsize # 默认情况下直接使用 showsize 作为墙体检测
        self.masksize   = masksize # masksize 用于碰撞检测，使用默认的从图片中读取即可
        self.offsets    = offsets
        self.in_control = in_control
        self.imager     = None
        self.image      = None
        self.mask       = None
        self.status     = {}
        self.status['current']   = None
        self.status['before']    = None
        self.status['default']   = self.aload_image(img)
        self.status['direction'] = {}

        self.axis       = None # 用于栅格类游戏，角色可以在 theater.map 中的函数处理运动，最短路径计算等
        self.obstruct   = None # 用于栅格类游戏，用于寻路算法，使用

        self.debug      = debug # 如果 DEBUG 为 False，这里为 True 则仅仅让该 Actor 这个对象用 debug 模式
        self.rect       = self.getrect()
        self.offsets    = self.getoffset()
        self.theater    = None # 将该对象注册进 theater之后会自动绑定相应的 theater。
        self.controller = self.regist(Controller())
        self.delayers   = {}
        self.repeaters  = {}
        self._regist    = None
        self._inner_dly = self.regist(Delayer())
        self._idler_dly = self.regist(Delayer())
        self._mouse_dly = self.regist(Delayer())
        self._dirct_dly = self.regist(Delayer())
        self._contl_dly = self.regist(Delayer())
        self._chain     = {}
        self._chain['gridmove'] = []
        self._toggle    = {'gridmove_start': False}
        self.mover      = self.regist(SmoothMover(in_entity, in_bounds))
        self.clicker    = self.regist(Clicker())
        self.in_entitys = in_entitys if in_entitys is not None else ENTITYS_DEFAULT.copy()
        self.ticks      = None
        self.cam_follow = cam_follow
        self._tuning    = {}

        self._set_showpoint(showpoint)
        self.bug_check  = None

    def _get_showpoint(self):
        return self.rect[:2]

    def _set_showpoint(self, value):
        if value: self.rect[:2] = value

    showpoint = property(_get_showpoint, _set_showpoint)

    def aload_image(self, img):
        self.status['before'] = self.imager
        if not (img is None or isinstance(img, (str, tuple, pygame.Surface))):
              self.imager = img
        else: self.imager = Image(img, showsize=self.showsize, rate=self.rate, 
                                       masksize=self.masksize, offsets=self.offsets)
        self.image        = self.imager.image
        self.mask         = self.imager.mask
        self.showsize     = self.image.get_size()
        self.imager.actor = self
        self.status['current'] = self.imager
        return self.imager

    def bload_image(self, img):
        # 这个不太像是直接的状态转移，这里需要考虑一下，动画演出时候，某些动画可能只需要一个循环就马上停止
        # 然后恢复该动画循环之前的一个状态动画。
        imager = self.aload_image(img)
        return imager

    def getrect(self):
        if not self.rectsize:
            return self.image.get_rect()
        else:
            rect = self.image.get_rect()
            sx, sy, sw, sh = rect
            rw, rh = self.rectsize
            rx = int(sx + sw/2 - rw/2)
            ry = int(sy + sh/2 - rh/2)
            rect.x = rx
            rect.y = ry
            rect.w = rw
            rect.h = rh
            return rect

    def getoffset(self):
        if not self.rectsize:
            return self.imager.offsets
        else:
            rx, ry, rw, rh = rect = self.getrect()
            x, y = self.imager.offsets
            rx, ry = rx + x, ry + y
            return (rx, ry)

    def regist(self, reg):
        reg.actor = self # 逆向绑定
        return reg

    def update(self,ticks):
        if not self.bug_check:
            # 这小块的代码用于处理一些参数配置时候的不妥当，在运行时进行一次简单的自检，方便查出问题。
            # 有什么需要检测的 actor 配置参数异常的可能性，可以在该处预先检查，不过目前暂时没用了。
            self.bug_check = True

        self.ticks = ticks
        self.imager.update_image(ticks)
        self.image = self.imager.image
        self.mask  = self.imager.mask
        if self.in_control:
            m, d, c = self.controller.update(ticks)
            # [鼠标操作/控制键操作/方向键操作]
            if self._mouse_dly.update(ticks): self._amouse(m, ticks)
            if self._contl_dly.update(ticks): self._acontrol(c, ticks)
            if self._dirct_dly.update(ticks): self._adirction(d, c, ticks)
        # 空闲状态时执行的函数
        if self._idler_dly.update(ticks): self._aidle(ticks)
        # 不对外暴露的循环，用于处理某些需要延时操作的动作
        if self._inner_dly.update(ticks):
            for ch in self._chain:
                if self._chain[ch]:
                    # immediate 为是否立即执行，用于在有序执行中插入无耗时函数的方式
                    # 这样这个操作就不会消耗一个时间片来执行无耗时函数而产生顿挫感
                    func, a, immediate = self._chain[ch].pop(0)
                    func(*a)
                    while immediate and self._chain[ch]:
                        func, a, immediate = self._chain[ch].pop(0)
                        func(*a)

        self.mover._delay_bind()
        self._image_tuning()

    def collide(self, *list_sprite):
        def collide_mask(left, right):
            # 不能直接使用 pygame.sprite.collide_mask
            # 因为我所处理的 rect 和实际的图片可能存在一定程度上的偏移
            if getattr(right, 'rectsize', None):
                ox, oy = right.imager.offsets
                dx, dy = (right.imager.maskdx, right.imager.maskdy) if getattr(right.imager, 'maskdx', None) else (0, 0)
                right_rectx = int(right.rect[0] + right.rect[2]/2 - right.showsize[0]/2 - ox + dx)
                right_recty = int(right.rect[1] + right.rect[3]/2 - right.showsize[1]/2 - oy + dy)
            else:
                right_rectx = right.rect[0]
                right_recty = right.rect[1]
            if getattr(left, 'rectsize', None):
                ox, oy = left.imager.offsets
                dx, dy = (left.imager.maskdx, left.imager.maskdy) if getattr(left.imager, 'maskdx', None) else (0, 0)
                left_rectx = int(left.rect[0] + left.rect[2]/2 - left.showsize[0]/2 - ox)
                left_recty = int(left.rect[1] + left.rect[3]/2 - left.showsize[1]/2 - oy)
            else:
                left_rectx = left.rect[0]
                left_recty = left.rect[1]
            xoffset = right_rectx - left_rectx
            yoffset = right_recty - left_recty
            try:
                leftmask = left.mask
            except AttributeError:
                leftmask = from_surface(left.image)
            try:
                rightmask = right.mask
            except AttributeError:
                rightmask = from_surface(right.image)
            return leftmask.overlap(rightmask, (xoffset, yoffset))

        scollide = pygame.sprite.spritecollide(self, self.theater.group, False, collide_mask)
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
        cur = self.theater.artist.current
        if self in self.RIGID_BODY[cur]:
            self.RIGID_BODY[cur].remove(self)
        super().kill()

    def change_theater(self, theatername):
        self.theater.artist.change_theater(theatername)

    @staticmethod
    def mouse(mouse_info): pass
    def _amouse(self, m, ticks):
        if   self.mouse.__code__.co_argcount == 1: self.mouse(m)
        elif self.mouse.__code__.co_argcount == 2: self.mouse(self, m)
        elif self.mouse.__code__.co_argcount == 3: self.mouse(self, m, ticks)
    @staticmethod
    def direction(direction_info): pass
    def _adirction(self, d, c, ticks):
        if   self.direction.__code__.co_argcount == 1: self.direction(d)
        elif self.direction.__code__.co_argcount == 2: self.direction(self, d)
        elif self.direction.__code__.co_argcount == 3: self.direction(self, d, c)
        elif self.direction.__code__.co_argcount == 4: self.direction(self, d, c, ticks) # 2d卷轴游戏可能需要别的键作为跳跃功能，所以需要处理更多消息
    @staticmethod
    def control(control_info): pass
    def _acontrol(self, c, ticks):
        if   self.control.__code__.co_argcount == 1: self.control(c)    
        elif self.control.__code__.co_argcount == 2: self.control(self, c)
        elif self.control.__code__.co_argcount == 3: self.control(self, c, ticks)
    @staticmethod
    def idle(): pass
    def _aidle(self, ticks):
        if   self.idle.__code__.co_argcount == 0: self.idle()
        elif self.idle.__code__.co_argcount == 1: self.idle(self)
        elif self.idle.__code__.co_argcount == 2: self.idle(self, ticks)

    @property
    def map(self):
        class _map:
            def move(s, trace, speed=4.):
                self.theater.map.move(self, trace, speed)
            def local(s, theater, axis, obstruct=0):
                if theater:
                    theater.regist(self)
                    theater.map.local(self, axis, obstruct)
                else:
                    try:
                        self.theater.map.local(self, axis, obstruct)
                    except AttributeError as e:
                        if 'map' in str(e) and 'NoneType' in str(e):
                            raise Exception('pls use theater.regist to register the object in theater, '
                                            'or use the third parameter of map.local to register automatically.')
                return self
            def trace(s, actor_or_point):
                return self.theater.map.trace(self, actor_or_point)
            def direct(s, side, speed=4.):
                return self.theater.map.direct(self, side, speed)
            def __str__(s):
                return str(self.theater.map)
        return _map()

    def _delay(self, time, delayer, deep=3):
        try:
            # 这里的 delay 函数事实上是运行在 Actor.update 函数里面的"函数的内部"，
            # 调用的深度固定，所以用指定调用栈可以准确的用如下方式找到 ticks ，这样就避免了让开发者直接接触到 ticks 的处理
            if delayer not in self.delayers:
                self.delayers[delayer] = self.regist(Delayer())
            self.delayers[delayer].delay = time # 毫秒
            return self.delayers[delayer].update(inspect.stack()[deep][0].f_locals['ticks'])
        except:
            raise 'delay function must work in (Actor.mouse, Actor.control, Actor.direction, Actor.idle).'

    def _repeat(self, judge, delayer):
        if delayer not in self.repeaters:
            self.repeaters[delayer] = False
        pjudge = self.repeaters[delayer]
        self.repeaters[delayer] = judge
        return bool(judge) != bool(pjudge)

    def delay(self, judge, time=0, repeat=False, delayer=None):
        if delayer == None:
            # 让 delay 函数调用在不同的位置使用不同的 delayer 的魔法
            s = inspect.stack()[1]
            delayer = '{}:{}'.format(id(s.frame), s.lineno)
        if repeat or self._repeat(judge, delayer):
            return judge and self._delay(time, delayer)

    def toggle(self, open_close:bool=None):
        # 可以将 open_close 设置成 Ture 或 False 来指定变化的开关状态
        # 这样也会更方便一些
        alive = self.alive()
        if open_close != None:
            if bool(open_close) == True  and     alive: return
            if bool(open_close) == False and not alive: return
        if alive:
            self.kill()
        else:
            # 恢复碰撞检测
            self._regist(self)
            cur = self.theater.artist.current
            if self not in self.RIGID_BODY[cur]:
                self.RIGID_BODY[cur].append(self)
        if self.axis:
            # 清理/恢复栅格游戏类型中的阻值
            if alive:
                if self.obstruct == float('inf'):
                    self.theater.map.map2d._local_set(self.axis, 0)
                else:
                    self.theater.map.map2d._local_del(self.axis, self.obstruct)
            else:
                self.theater.map.map2d._local_add(self.axis, self.obstruct)

    def _image_tuning(self):
        for k in sorted(self._tuning):
            self.image = self._tuning[k](self.image)

    def __setattr__(self, key, value):
        if 'in_control' in self.__dict__ \
            and not self.in_control \
            and key in ('mouse', 'direction', 'control'):
            raise Exception('If {}(in_control=False) mode is used, the set '
                            .format(self.__class__.__name__)+ '(mouse,direction,control) will be invalid.')
        self.__dict__[key] = value
        if isinstance(self.__class__, Text) and key == 'text':      self._set_btn_text(value)
        if isinstance(self.__class__, Text) and key == 'textcolor': self._set_btn_textcolor(value)
        if isinstance(self.__class__, Text) and key == 'textscale': self._set_btn_textscale(value)
        if isinstance(self.__class__, Text) and key == 'textside':  self._set_btn_textside(value)

    # 处理文字类的自动状态修改，让使用了 vgame.Text 作为 Actor 类中的图片属性时
    # 可以通过 Actor 对象的属性直接动态修改里面的数字内容
    def _get_btn_text(self): return self.imager.text
    def _set_btn_text(self, value): self.imager.text = value
    text = property(_get_btn_text, _set_btn_text)
    def _get_btn_textcolor(self): return self.imager.textcolor
    def _set_btn_textcolor(self, value): self.imager.textcolor = value
    textcolor = property(_get_btn_textcolor, _set_btn_textcolor)
    def _get_btn_textscale(self): return self.imager.textscale
    def _set_btn_textscale(self, value): self.imager.textscale = value
    textscale = property(_get_btn_textscale, _set_btn_textscale)
    def _get_btn_textside(self): return self.imager.textside
    def _set_btn_textside(self, value): self.imager.textside = value
    textside = property(_get_btn_textside, _set_btn_textside)
    def __setattr__(self, key, value):
        super().__setattr__(key, value)




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

# 后来发现一个场景一个 sprite.group 可能不够，要更加方便的管理应该是 一个大类元素使用一个 sprite.group
# 因为这样分层管理起来会更加容易的实现前景，背景之类谁先谁后渲染顺序的处理，例如“菜单”必须要置顶于游戏之上
# 否则菜单就没有意义。
class Menu(Actor):
    DEBUG = False
    RIGID_BODY = {}
    # Hover
    class HoverImage(Actor):
        RIGID_BODY = {}
        def __init__(self, *a, **kw):
            kw['in_entity'] = False
            kw['in_entitys'] = []
            kw['cam_follow'] = False # 背景需要镜头跟随的处理，之所以都使用
            super().__init__(*a, **kw)

    def __init__(self, *a, **kw):
        kw['in_entity'] = False
        kw['in_entitys'] = []
        kw['cam_follow'] = False # 菜单一般都不需要镜头跟随的处理，之所以都使用
        if not a:
            kw['img'] = (70, 70, 70, 100)
        super().__init__(*a, **kw)
        self.group = pygame.sprite.Group()
        self.grid = (1, 1)

    def init(self, theater, grid=None, side=None, ratio=(1, 1), offsets=(0, 0)):
        '''
        grid    --> 用于划分格子，后续用格子坐标来整理/展示图文。
        ratio   --> 如果 ratio 只有一个数字，则 side 所用的方向均使用这个比例，两个数字则分别为宽/高比例
        side    --> udlr:up,down,left,right，只能用最大两个(合法角落)字母，即为不能同时上下，不能同时左右
        offsets --> 初始化整块图片时的坐标偏移，和 ratio 一样以宽/高比例做偏移。
        '''
        theater.regist_menu(self)
        if isinstance(ratio, (int, float)): kw = kh = ratio
        if isinstance(ratio, (tuple, list)): kw, kh = ratio
        if isinstance(offsets, (int, float)): kx = ky = offsets
        if isinstance(offsets, (tuple, list)): kx, ky = offsets
        side = 'd' if side is None else side
        ta = 'd' in side or 'u' in side
        tb = 'r' in side or 'l' in side
        if ta and tb: self.rect.h, self.rect.w = theater.size[1]*kh, theater.size[0]*kw
        else:
            if ta: self.rect.h, self.rect.w = theater.size[1]*kh, theater.size[0]
            if tb: self.rect.w, self.rect.h = theater.size[0]*kw, theater.size[1]
        w, h = theater.size
        if 'd' in side: self.rect.y = h - self.rect.h
        if 'r' in side: self.rect.x = w - self.rect.w
        self.rect.x += theater.size[0] * kx
        self.rect.y += theater.size[1] * ky
        self.showsize = int(self.rect.w), int(self.rect.h)
        img = self.aload_image(self.img)
        if self.DEBUG:
            self.aload_image(self._griddraw(img.image, grid))

        # self._get_gridcenter(theater, img.image, grid)
        self.grid    = grid    if grid    else self.grid
        self.theater = theater if theater else self.theater
        return self

    def local(self, actor, axis):
        center_map = self._get_gridcenter(self.theater, self.grid)
        cx, cy = center_map[tuple(axis)]
        actor.rect.x = int(cx-actor.showsize[0]/2)
        actor.rect.y = int(cy-actor.showsize[1]/2)
        actor.axis = axis
        self.group.add(actor)

    def _griddraw(self, image, grid):
        x, y, w, h = image.get_rect()
        xw, xh = grid
        gw, gh = int(w/xw), int(h/xh)
        for x in range(0, w, gw):
            pygame.draw.line(image, vgame.Artist.GRID_LINE_COLOR_MAP_DEBUG, (x, 0), (x, h))
        for y in range(0, h, gh):
            pygame.draw.line(image, vgame.Artist.GRID_LINE_COLOR_MAP_DEBUG, (0, y), (w, y))
        return image

    def _get_gridcenter(self, theater, grid):
        ox, oy, w, h = self.rect
        ww, wh = theater.size
        xw, xh = grid
        gw, gh = int(w/xw), int(h/xh)
        center_map = {}
        for ix, x in enumerate(range(0, w, gw)):
            for iy, y in enumerate(range(0, h, gh)):
                _x, _y = int(x+gw/2+ox), int(y+gh/2+oy)
                if _x <= ww and _y <= wh:
                    center_map[(ix, iy)] = _x, _y
        return center_map

class Button(Actor):
    RIGID_BODY = {}
    def __init__(self, *a, **kw):
        kw['in_entity'] = False
        kw['in_entitys'] = []
        kw['cam_follow'] = False # 菜单一般都不需要镜头跟随的处理，之所以都使用
        kw['in_control'] = True
        super().__init__(*a, **kw)
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_stat = self._get_mouse_stat()
        self._hover_dly = self.regist(Delayer(30))
        self._init_hover_color()

    @staticmethod
    def mouse(self, m):
        if m:
            if m[1] == 0:
                if self.clicker.collide(m[2][0]):
                    self._click(m)

    @staticmethod
    def click(): pass

    def _click(self, m):
        if   self.click.__code__.co_argcount == 0: self.click()
        elif self.click.__code__.co_argcount == 1: self.click(m)
        elif self.click.__code__.co_argcount == 2: self.click(self, m)

    @staticmethod
    def idle(self, ticks):
        pos = pygame.mouse.get_pos()
        if self.mouse_pos != pos:
            self.mouse_pos = pos
            mstat = self._get_mouse_stat()
            if mstat != self.mouse_stat:
                self.mouse_stat = mstat
                if mstat == 'over':
                    self._mouseover()
                    self.hover(True)
                elif mstat == 'out':
                    self._mouseout()
                    self.hover(False)
        if self._hover_dly.update(ticks):
            self._hover_aph = next(self._hover_lst)

    def _get_mouse_stat(self):
        dx, dy = self.mouse_pos
        dx = int(dx + self.rect[2]/2 - self.showsize[0]/2)
        dy = int(dy + self.rect[3]/2 - self.showsize[1]/2)
        return 'over' if self.clicker.collide((dx, dy)) else 'out'

    @staticmethod
    def mouseover(self): pass
    def _mouseover(self):
        if   self.mouseover.__code__.co_argcount == 0: self.mouseover()
        elif self.mouseover.__code__.co_argcount == 1: self.mouseover(self)
    @staticmethod
    def mouseout(self): pass
    def _mouseout(self):
        if   self.mouseout.__code__.co_argcount == 0: self.mouseout()
        elif self.mouseout.__code__.co_argcount == 1: self.mouseout(self)

    def _init_hover_color(self):
        colors = list(range(20, 200, 20))
        self._hover_lst = cycle(colors + colors[::-1])
        self._hover_col = (255, 255, 255)
        self._hover_aph = next(self._hover_lst)
        def func(image):
            bg = Menu.HoverImage((*self._hover_col,self._hover_aph), showsize=image.get_rect()[2:])
            image.blit(bg.image, bg.rect)
            del bg
            return image
        return func

    def hover(self, toggle=True):
        if toggle:
            self._tuning[0] = self._init_hover_color()
        else:
            del self._tuning[0]

    @property
    def menu(self):
        class _menu:
            def local(s, menu, axis):
                assert isinstance(menu, Menu), 'menu must be vgame.Menu object.'
                menu.local(self, axis)
                return self
        return _menu()






# 该处的背景类仅用于规范游戏的范围使用的
class Background(Actor):
    RIGID_BODY = {}
    def __init__(self, *a, **kw):
        kw['in_entity'] = False
        kw['in_entitys'] = []
        kw['cam_follow'] = True # 背景需要镜头跟随的处理，之所以都使用
        super().__init__(*a, **kw)