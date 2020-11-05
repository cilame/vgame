import os, re, sys, time, math
import traceback
from itertools import cycle, product

import pygame
from pygame.locals import *
from pygame.mask import from_surface

from .image import Image, ImageMaker, Text
from .controller import Controller
from .dijkstra import shortest_path

import vgame

class Delayer:
    '''
    延迟器，很重要的一个类，用于循环内分离不同操作需要的不同的更新频率
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

class _Mover:
    '''
    用于处理碰撞检测的原始函数部分，一般的mover直接继承使用
    '''
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


class SmoothMover(_Mover):
    '''
    平滑移动的处理
    '''
    ALLDIR = [6, 4, 2, 8]

    def __init__(self):
        self.actor = None
        self.speed = pygame.Vector2(5., 5.) # 初始化有个值，方便看到效果，可以通过对象修改
        super().__init__()
        self.tempx = None
        self.tempy = None

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
                naxis = actor._map.map2d._calc_center_by_rect(actor)
                obstruct = actor.obstruct or 0
                if caxis != naxis:
                    actor.axis = naxis
                    if obstruct:
                        actor._map.map2d._local_add_del(caxis, naxis, obstruct)
        except:
            traceback.print_exc()
            print('Actor out of bounds. {}'.format(self.actor.axis))

    def auto_change_direct(self, d):
        curr = self.actor.status['current']
        targ = None
        if 4 in d or 6 in d:
            if 4 in d: targ = self.actor.status['direction'].get('left')
            if 6 in d: targ = self.actor.status['direction'].get('right')
        else:
            if 2 in d: targ = self.actor.status['direction'].get('down')
            if 8 in d: targ = self.actor.status['direction'].get('up')
        if targ and curr != targ: self.actor.aload_image(targ)

    def move_angle(self, angle, speed=None):
        self.smooth_move([6], self.speed if speed is None else pygame.Vector2(speed, speed), angle)

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
        if self.tempx is None: self.tempx = self.actor.rect[0]
        if self.tempy is None: self.tempy = self.actor.rect[1]
        if abs(self.tempx - self.actor.rect.x) > 2: self.tempx = self.actor.rect.x
        if abs(self.tempy - self.actor.rect.y) > 2: self.tempy = self.actor.rect.y
        if self.actor.in_bounds:
            w, h = self.actor.theater.size
            _w = w - self.actor.rect.width
            _h = h - self.actor.rect.height
        self.tempx += speed.x
        self.actor.rect[0] = self.tempx
        if self.actor.in_entity:
            aw = self.collide()
            side = []
            if aw:
                for w in aw:
                    if speed.x > 0: self.actor.rect.x = w.rect.left - self.actor.rect.width; side.append((w, 'r'))
                    if speed.x < 0: self.actor.rect.x = w.rect.right;                        side.append((w, 'l'))
            if side:
                self.actor._abound(side)
            if self.actor.in_bounds:
                side = []
                if self.actor.rect.x < 0:  self.actor.rect.x = 0;  side.append((None, 'l'))
                if self.actor.rect.x > _w: self.actor.rect.x = _w; side.append((None, 'r'))
                if side:
                    self.actor._abound(side)
        self.tempy += speed.y
        self.actor.rect[1] = self.tempy
        if self.actor.in_entity:
            aw = self.collide()
            side = []
            if aw:
                for w in aw:
                    if speed.y > 0: self.actor.rect.y = w.rect.top - self.actor.rect.height; side.append((w, 'd'))
                    if speed.y < 0: self.actor.rect.y = w.rect.bottom;                       side.append((w, 'u'))
            if side:
                self.actor._abound(side)
            if self.actor.in_bounds:
                side = []
                if self.actor.rect.y < 0:  self.actor.rect.y = 0;  side.append((None, 'u'))
                if self.actor.rect.y > _h: self.actor.rect.y = _h; side.append((None, 'd'))
                if side:
                    self.actor._abound(side)

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
        self.actor = None
        self.hasclick = False

    def dnd(self, m, lr='left'): # 实现鼠标拖拽对象的功能
        # m 为鼠标的消息信息
        # m 如非 None，则为一个三元组：
        # m[0] 表示按键，数字0代表左键，数字2代表右键
        # m[1] 表示模式，数字0代表单击，数字2代表拖动
        # m[2] 表示两个点的坐标，m[2][0] 为按下鼠标时的坐标， m[2][1] 为松开鼠标时的坐标
        if m:
            if m and m[1] == 2:
                pos1 = self._loc_in_theater(m[2][0], self.actor.theater)
                if self.collidepoint(pos1):
                    self.hasclick = True
            if self.hasclick:
                pos2 = self._loc_in_theater(m[2][1], self.actor.theater)
                self.actor.local(self.actor.theater, pos2)
        else:
            self.hasclick = False

    def _loc_in_theater(self, pos, theater):
        rx, ry = pos
        ox, oy = theater.camera.camera[:2]
        return rx-ox, ry-oy

    def collidepoint(self, pos, theater=None):
        if theater:
            pos = self._loc_in_theater(pos, theater)
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
    SHOW_BODY = {}

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
                  in_collide = None,  # 需要自动添加进碰撞检测列表的对象
                  rate       = 0,     # 动态图循环的速率
                  offsets    = (0,0), # 图片的偏移位置
                  rotate     = 0,     # 默认图片旋转角
                  cam_follow = True,  # 镜头跟随，默认开启
                  debug      = False  # 是否开启单个 Actor 对象的 Debug 模式
            ):
        pygame.sprite.Sprite.__init__(self)

        # 后续这两行需要修改，因为角色的状态资源应该可以有多个，并且由于每个 Image 都要逆向绑定 Actor
        # 所以后续要考虑怎么更加合理的添加角色状态动画的处理
        self.img        = img
        self.rate       = rate
        self.rotate     = rotate
        self.showsize   = showsize # showsize 用于墙体检测，所以比较常用，尽量主动设置
        self.rectsize   = rectsize # 默认情况下直接使用 showsize 作为墙体检测
        self.masksize   = masksize # masksize 用于碰撞检测，使用默认的从图片中读取即可
        self.offsets    = offsets
        self.in_entity  = in_entity
        self.in_bounds  = in_bounds
        self.in_collide = in_collide
        self.in_control = in_control
        self.imager     = None
        self.image      = None
        self.mask       = None
        self._status    = None
        self.status     = {}
        self.status['current']   = None
        self.status['before']    = None
        self.status['default']   = self.aload_image(img)
        self.status['direction'] = {}

        self.axis       = None # 用于栅格类游戏，角色可以在 theater.map 中的函数处理运动，最短路径计算等
        self.obstruct   = None # 用于栅格类游戏，用于寻路算法，使用
        self._map       = None # 用于绑定 map

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
        self.mover      = self.regist(SmoothMover())
        self.clicker    = self.regist(Clicker())
        self.in_entitys = in_entitys if in_entitys is not None else ENTITYS_DEFAULT.copy()
        self.ticks      = None
        self.cam_follow = cam_follow
        self._tuning    = {}

        self._set_showpoint(showpoint)
        self.bug_check  = None
        self.has_bind   = False

        # hover 功能，让 Actor 带有鼠标移入移出单位时候的可配置函数的处理
        self.mouse_pos  = self.controller.get_pos()
        self.mouse_stat = self._get_mouse_stat()

    def _delay_bind(self):
        if not self.has_bind:
            if self.theater:
                self._bindbody()
            self.has_bind = True

    def _get_showpoint(self): return self.rect[:2]
    def _set_showpoint(self, value): 
        if value: self.rect[:2] = value
    showpoint = property(_get_showpoint, _set_showpoint)

    def _get_showsize(self): return self._showsize
    def _set_showsize(self, value):
        self._showsize = (int(round(value[0])), int(round(value[1]))) if value else value
        imager = getattr(self, 'imager', None)
        if imager:
            imager.orig_image = pygame.transform.scale(imager.orig_image, self._showsize)
    showsize = property(_get_showsize, _set_showsize)

    def _get_status(self): return self._status
    def _set_status(self, value): 
        if self._status is None:
            self._status = value
        else:
            raise Exception('Actor.status cannot be overwrite. pls use Actor.status[key] change inner data.')
    status = property(_get_status, _set_status)

    def aload_image(self, img):
        self.status['before'] = self.imager
        if not (img is None or isinstance(img, (str, tuple, list, pygame.Surface))):
            self.imager = img.imager if isinstance(img, Actor) else img
            if self.imager.active:
                self.imager.rects.idx = 0
        else: 
            self.imager = Image(img, showsize=self.showsize, rate=self.rate, 
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
            return pygame.Rect(rect)

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
            if self._contl_dly.update(ticks): self._acontrol(c, d, ticks)
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

        self._delay_bind()
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

        if len(list_sprite) == 1 and isinstance(list_sprite[0], (tuple, list)):
            list_sprite = list_sprite[0]
        scollide = pygame.sprite.spritecollide(self, self.theater.group, False, collide_mask)
        rcollide = []
        for sprite in list_sprite:
            if sprite in scollide:
                rcollide.append(sprite)
            if sprite in COLLIDE:
                extra = [i for i in sprite.SHOW_BODY[self.theater.artist.current] if i.alive()]
                rcollide.extend(pygame.sprite.spritecollide(self, extra, False, collide_mask))
        return rcollide

    def angle(self, sprite):
        sx, sy = self.rect.center
        tx, ty = sprite.rect.center
        return math.atan2((ty - sy), (tx - sx)) * 57.2958

    def kill(self):
        cur = self.theater.artist.current
        if self in self.RIGID_BODY[cur]: self.RIGID_BODY[cur].remove(self)
        if self in self.SHOW_BODY[cur]: self.SHOW_BODY[cur].remove(self)
        super().kill()

    def change_theater(self, theatername):
        self.theater.artist.change_theater(theatername)

    @staticmethod
    def mouse(mouse_info): pass
    def _amouse(self, m, ticks):
        if   self.mouse.__code__.co_argcount == 1: self.mouse(self)
        elif self.mouse.__code__.co_argcount == 2: self.mouse(self, m)
        elif self.mouse.__code__.co_argcount == 3: self.mouse(self, m, ticks)
        if m and m[1] == 0:
            if self.clicker.collidepoint(m[2][0], self.theater):
                self._aclick(m, self.theater)
            if self.clicker.collidepoint(m[2][0]):
                self._aabsclick(m)
    @staticmethod
    def click(): pass
    def _aclick(self, m, theater):
        # 真实坐标，用在游戏场景里面
        pos1 = self.clicker._loc_in_theater(m[2][0], theater)
        pos2 = self.clicker._loc_in_theater(m[2][1], theater)
        m = (m[0], m[1], (pos1, pos2))
        if   self.click.__code__.co_argcount == 0: self.click()
        elif self.click.__code__.co_argcount == 1: self.click(self)
        elif self.click.__code__.co_argcount == 2: self.click(self, m)
    @staticmethod
    def absclick(): pass
    def _aabsclick(self, m):
        # 绝对坐标，用在一些窗口菜单上面
        if   self.absclick.__code__.co_argcount == 0: self.absclick()
        elif self.absclick.__code__.co_argcount == 1: self.absclick(self)
        elif self.absclick.__code__.co_argcount == 2: self.absclick(self, m)
    def _get_mouse_stat(self, theater=None):
        dx, dy = self.mouse_pos
        dx = int(dx + self.rect[2]/2 - self.showsize[0]/2)
        dy = int(dy + self.rect[3]/2 - self.showsize[1]/2)
        return 'over' if self.clicker.collidepoint((dx, dy), theater) else 'out'
    @staticmethod
    def mouseover(self): pass
    def _amouseover(self):
        if   self.mouseover.__code__.co_argcount == 0: self.mouseover()
        elif self.mouseover.__code__.co_argcount == 1: self.mouseover(self)
        else:
            raise Exception('cos mouseover not in_control update loop. so this func only get "self" parameter.')
    @staticmethod
    def mouseout(self): pass
    def _amouseout(self):
        if   self.mouseout.__code__.co_argcount == 0: self.mouseout()
        elif self.mouseout.__code__.co_argcount == 1: self.mouseout(self)
        else:
            raise Exception('cos mouseout not in_control update loop. so this func only get "self" parameter.')
    def _hover_idle(self, ticks):
        pos = self.controller.get_pos()
        if self.mouse_pos != pos:
            self.mouse_pos = pos
            mstat = self._get_mouse_stat(self.theater)
            if mstat != self.mouse_stat:
                self.mouse_stat = mstat
                if mstat == 'over':
                    self._amouseover()
                    self._hoving(toggle=True)
                elif mstat == 'out':
                    self._amouseout()
                    self._hoving(toggle=False)
        self._hoving(update=True, ticks=ticks)
    def _hoving(self, toggle=None, update=None, ticks=None):
        pass
    @staticmethod
    def direction(direction_info): pass
    def _adirction(self, d, c, ticks):
        if   self.direction.__code__.co_argcount == 1: self.direction(self)
        elif self.direction.__code__.co_argcount == 2: self.direction(self, d)
        elif self.direction.__code__.co_argcount == 3: self.direction(self, d, c)
        elif self.direction.__code__.co_argcount == 4: self.direction(self, d, c, ticks) # 2d卷轴游戏可能需要别的键作为跳跃功能，所以需要处理更多消息
    @staticmethod
    def control(control_info): pass
    def _acontrol(self, c, d, ticks):
        if   self.control.__code__.co_argcount == 1: self.control(self)    
        elif self.control.__code__.co_argcount == 2: self.control(self, c)
        elif self.control.__code__.co_argcount == 3: self.control(self, c, d)
        elif self.control.__code__.co_argcount == 4: self.control(self, c, d, ticks)
    @staticmethod
    def idle(): pass
    def _aidle(self, ticks):
        self._hover_idle(ticks)
        if   self.idle.__code__.co_argcount == 0: self.idle()
        elif self.idle.__code__.co_argcount == 1: self.idle(self)
        elif self.idle.__code__.co_argcount == 2: self.idle(self, ticks)

    @staticmethod
    def bound(): pass
    def _abound(self, side):
        if   self.bound.__code__.co_argcount == 0: self.bound()
        elif self.bound.__code__.co_argcount == 1: self.bound(self)
        elif self.bound.__code__.co_argcount == 2: self.bound(self, side)

    def local(self, theater, point=None, offsets=(0,0)):
        if isinstance(theater, vgame.Theater):
            theater.regist(self)
        if isinstance(theater, Actor):
            theater.theater.regist(self)
        if point:
            rx,ry = point
            ox,oy = offsets
        else:
            rx,ry = theater.rect.center
            ox,oy = offsets
        self.rect.center = (rx+ox, ry+oy)
        self._bindbody()
        return self

    def follow(self, theater, fspeed=1, offsets=(0,0), padding=(0,0)):
        theater.follow(self, fspeed, offsets, padding)
        return self

    def _delay(self, time, delayer, ticks):
        try:
            # 这里的 delay 函数事实上是运行在 Actor.update 函数里面的"函数的内部"，
            # 调用的深度固定，所以用指定调用栈可以准确的用如下方式找到 ticks ，这样就避免了让开发者直接接触到 ticks 的处理
            if delayer not in self.delayers:
                self.delayers[delayer] = self.regist(Delayer(time))
            return self.delayers[delayer].update(ticks)
        except:
            raise Exception('delay function must work in (Actor.mouse, Actor.control, Actor.direction, Actor.idle).')

    def _repeat(self, judge, delayer):
        if delayer not in self.repeaters:
            self.repeaters[delayer] = False
        pjudge = self.repeaters[delayer]
        self.repeaters[delayer] = judge
        return bool(judge) != bool(pjudge)

    def _keyup(self, judge, delayer, keyup):
        if keyup:
            if delayer not in self.repeaters:
                self.repeaters[delayer] = False
            pjudge = self.repeaters[delayer]
            self.repeaters[delayer] = judge
            if bool(judge) != bool(pjudge) and not judge:
                keyup()

    def delay(self, judge, time=0, repeat=False, keyup=None, delayer=None, ticks=None):
        '''
        keyup   -> 你可以在 keyup 参数传入一个回调专门用于按键弹起时执行该函数
                   并且该参数同时作用于 repeat 的两种状态，让开发变得更加简洁。

        # 原本使用 inspect.stack 来获取函数调用栈的信息，不过这个函数每次都会获取全部的空间信息导致非常耗时
        # 现在直接使用 sys._getframe() 来获取，可以节约大量时间，现在你可以无需主动配置 delayer, ticks 这两个参数
        # 只要你能理解函数栈，你就能明白这里处理的绝妙性。
        delayer -> 标识延迟器的唯一标识符，用数字字符串标识均可
        ticks   -> 游戏循环体内唯一的 ticks 信息。参考 Actor.update 函数位置的传递。
        '''
        if delayer == None:
            frame = sys._getframe().f_back
            delayer = '{}:{}'.format(id(frame), frame.f_lineno) # (被调用函数所在函数空间的函数id and 被调用时delay函数所在的行数)
        if ticks is None:   ticks = sys._getframe().f_back.f_back.f_locals['ticks']
        if repeat or self._repeat(judge, delayer):
            self._keyup(judge, delayer+':keyup', keyup) # 用于钩住键盘松开瞬间，执行一个回调函数 keyup。
            return judge and self._delay(time, delayer, ticks)

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
            self._bindbody()
        if self.axis:
            # 清理/恢复栅格游戏类型中的阻值，如果 alive 则关闭
            self._bindmap(not alive)

    def _bindmap(self, open_close:bool):
        if open_close:
            self.theater.map.map2d._local_add(self.axis, self.obstruct)
        else:
            if self.obstruct == float('inf'):
                self.theater.map.map2d._local_set(self.axis, 0)
            else:
                self.theater.map.map2d._local_del(self.axis, self.obstruct)

    def _bindbody(self):
        cur = self.theater.artist.current
        if self.in_entity and self not in self.RIGID_BODY[cur]: self.RIGID_BODY[cur].append(self)
        if self.in_collide and self not in self.SHOW_BODY[cur]: self.SHOW_BODY[cur].append(self)

    def outbounds(self):
        # 返回超过边界的方向和长度，这样更方便控制边界
        ww, wh = self.theater.size
        aw, ah = self.showsize
        cx, cy = self.rect.center
        if cx-aw/2 > ww: return 'r', cx-aw/2-ww
        if cy-ah/2 > wh: return 'd', cy-ah/2-wh
        if cx+aw/2 < 0:  return 'l', -(cx+aw/2)
        if cy+ah/2 < 0:  return 'u', -(cy+ah/2)

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

    @property
    def draw(self):
        return vgame.draw(self)

    @property
    def menu(self):
        class _menu:
            def local(s, menu, axis):
                assert isinstance(menu, Menu), 'menu must be vgame.Menu object.'
                menu._gridlocal(self, axis)
                return self
        return _menu()

    @property
    def map(self):
        class _map:
            def local(s, map, axis, obstruct=0):
                assert isinstance(map, Map), 'map must be vgame.Map object.'
                self._map = map._map_local(self, axis, obstruct)
                return self
            def trace(s, actor_or_point):
                if self._map:
                    return self._map.trace(self, actor_or_point)
                else:
                    raise Exception('map is not init, pls use "Actor.map.local(map, axis)" bind map.')
            def area(s, max, min=1):
                if self._map:
                    return self._map.area(self, max, min)
                else:
                    raise Exception('map is not init, pls use "Actor.map.local(map, axis)" bind map.')
            def tracelimit(s, max, min=1):
                if self._map:
                    return self._map.tracelimit(self, max, min)
                else:
                    raise Exception('map is not init, pls use "Actor.map.local(map, axis)" bind map.')
            @property
            def graph(s):
                return self._map.map2d.graph
        return _map()










































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
    SHOW_BODY = {}
    def __init__(self, *a, player='p1', **kw):
        kw.setdefault('in_control', True)
        kw.setdefault('in_collide', True)
        super().__init__(*a, **kw)
class NPC(Actor):
    RIGID_BODY = {}
    SHOW_BODY = {}
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)

class Anime(Actor):
    RIGID_BODY = {}
    SHOW_BODY = {}
    def __init__(self, *a, **kw):
        kw.setdefault('in_entity', False)
        kw.setdefault('in_bounds', False)
        self._loopnumer = kw.pop('loop', -1)
        super().__init__(*a, **kw)
    def update(self,ticks):
        super().update(ticks)
        if self.imager.rects is not None:
            cycnumber = self.imager.rects.get_cycle_number()
            idxnumber = self.imager.rects.get_idx_number()
            if cycnumber == self._loopnumer:
                self.kill()
                self._aendanime(cycnumber, idxnumber)
    @staticmethod
    def endanime(): pass
    def _aendanime(self, cycnumber, idxnumber):
        if   self.endanime.__code__.co_argcount == 0: self.endanime()
        elif self.endanime.__code__.co_argcount == 1: self.endanime(self)
        elif self.endanime.__code__.co_argcount == 2: self.endanime(self, cycnumber)
        elif self.endanime.__code__.co_argcount == 3: self.endanime(self, cycnumber, idxnumber)

class Enemy(Actor):
    RIGID_BODY = {}
    SHOW_BODY = {}
    def __init__(self, *a, **kw):
        kw.setdefault('in_bounds', False)
        kw.setdefault('in_collide', True)
        super().__init__(*a, **kw)
class Bullet(Actor):
    RIGID_BODY = {}
    SHOW_BODY = {}
    def __init__(self, *a, **kw):
        kw.setdefault('in_entity', False)
        kw.setdefault('in_bounds', False)
        kw.setdefault('in_collide', True)
        kw.setdefault('in_entitys', []) # 默认情况只检测 ENTITYS_DEFAULT 内的物体，子弹类则无需实体检测
        super().__init__(*a, **kw)

class Wall(Actor):
    RIGID_BODY = {}
    SHOW_BODY = {}
    def __init__(self, *a, **kw):
        kw.setdefault('in_entitys', ENTITYS) # 墙体也要自动对其他类型的数据进行互斥，否则墙体运动时候不会与
        super().__init__(*a, **kw)

# 该处的背景类仅用于规范游戏的范围使用的
class Background(Actor):
    RIGID_BODY = {}
    SHOW_BODY = {}
    def __init__(self, *a, **kw):
        kw.setdefault('in_entity', False)
        kw.setdefault('in_entitys', [])
        kw.setdefault('cam_follow', True) # 背景需要镜头跟随的处理
        super().__init__(*a, **kw)

ENTITYS = [Player, NPC, Enemy, Wall]
ENTITYS_DEFAULT = [Wall]
COLLIDE = [Player, NPC, Enemy, Bullet]



































# 后来发现一个场景一个 sprite.group 可能不够，要更加方便的管理应该是 一个大类元素使用一个 sprite.group
# 因为这样分层管理起来会更加容易的实现前景，背景之类谁先谁后渲染顺序的处理，例如“菜单”必须要置顶于游戏之上
# 否则菜单就没有意义。
class _Grid(Actor):
    DEBUG = False
    RIGID_BODY = {}
    SHOW_BODY = {}

    def __init__(self, *a, **kw):
        kw.setdefault('in_entity', False)
        kw.setdefault('in_entitys', [])
        kw.setdefault('cam_follow', False)
        grid = kw.pop('grid', (1, 1))
        if not a:
            kw.setdefault('img', (70, 70, 70, 100))
        super().__init__(*a, **kw)
        self.group = pygame.sprite.Group()
        self.grid = grid
        gw, gh = self.grid
        sw, sh = self.showsize
        self.gridw = sw/gw
        self.gridh = sh/gh
        self.mapw  = gw
        self.maph  = gh
        self._debug_toggle = False

    def local(self, theater, point=None, offsets=(0,0)):
        if isinstance(theater, vgame.Theater):
            theater.regist_grid(self)
        if point:
            rx,ry = point
            ox,oy = offsets
        else:
            rx,ry = theater.rect.center
            ox,oy = offsets
        self.rect.center = (rx+ox, ry+oy)
        self._bindbody()
        self._debug_draw()
        return self

    @property
    def gridsize(self):
        return self.gridw, self.gridh

    def _gridlocal(self, actor, axis):
        center_map = self._get_gridcenter(self.theater, self.grid)
        cx, cy = center_map[tuple(axis)]
        rx, ry = actor.rectsize if actor.rectsize else actor.showsize
        actor.rect.x = int(cx-rx/2)
        actor.rect.y = int(cy-ry/2)
        actor.axis = axis
        self.group.add(actor)
        actor.theater = self.theater

    def _griddraw(self, image, grid):
        x, y, w, h = image.get_rect()
        xw, xh = grid
        gw, gh = w/xw, h/xh
        for ix in range(xw):
            x = int(gw*ix)
            pygame.draw.line(image, vgame.Artist.GRID_LINE_COLOR_MAP_DEBUG, (x, 0), (x, h))
        for iy in range(xh):
            y = int(gh*iy)
            pygame.draw.line(image, vgame.Artist.GRID_LINE_COLOR_MAP_DEBUG, (0, y), (w, y))
        return image

    def _get_gridcenter(self, theater, grid):
        ox, oy, w, h = self.rect
        ww, wh = theater.size
        xw, xh = grid
        gw, gh = w/xw, h/xh
        center_map = {}
        for ix in range(xw):
            x = gw*ix
            for iy in range(xh):
                y = gh*iy
                _x, _y = int(x+gw/2+ox), int(y+gh/2+oy)
                if _x <= ww and _y <= wh:
                    center_map[(ix, iy)] = _x, _y
        return center_map

    def _debug_draw(self):
        if self.DEBUG and not self._debug_toggle:
            self._debug_toggle = True
            img = self.aload_image(self.img)
            self.aload_image(self._griddraw(img.image, self.grid))

class Menu(_Grid):
    DEBUG = False
    RIGID_BODY = {}
    SHOW_BODY = {}
    # TODO 菜单需要实现一些方向键控制按钮的功能，以及绑定某些按键的功能
    # 以及呼出菜单后自动只接收某些函数功能，一般的 player 功能将会隐藏。

class Map(_Grid):
    DEBUG = False
    RIGID_BODY = {}
    SHOW_BODY = {}
    class Map2D:
        DEFAULT_OBSTRUCT = 1 # 默认阻值
        DEFAULT_GAP = 3
        def __init__(self, map, mapw, maph):
            self.map   = map
            self.gridw = map.gridw
            self.gridh = map.gridh
            self.mapw  = mapw
            self.maph  = maph
            self.world = self._create_map2ds()
            self.graph = self._create_graph()
            self.gap   = self.DEFAULT_GAP
        def _create_map2ds(self):
            d = {}
            d['_obs2d'] = self._create_obs2d()  # 存放默认阻值，均为 DEFAULT_OBSTRUCT
            d['obs2d']  = self._create_obs2d(0) # 地图单位阻值，初始均为 0
            return d
        def _create_obs2d(self, obstruct=None):
            w = []
            for i in range(self.maph):
                m = []
                for j in range(self.mapw):
                    m.append(Map.Map2D.DEFAULT_OBSTRUCT if obstruct is None else obstruct)
                w.append(m)
            return w
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
            if lx >= 0:        p[(lx, ly)] = self.world['_obs2d'][ly][lx] # Map.Map2D.DEFAULT_OBSTRUCT
            if rx < self.mapw: p[(rx, ry)] = self.world['_obs2d'][ry][rx] # Map.Map2D.DEFAULT_OBSTRUCT
            if uy >= 0:        p[(ux, uy)] = self.world['_obs2d'][uy][ux] # Map.Map2D.DEFAULT_OBSTRUCT
            if dy < self.maph: p[(dx, dy)] = self.world['_obs2d'][dy][dx] # Map.Map2D.DEFAULT_OBSTRUCT
            return p
        def _shortest_path(self, actor_a, actor_b):
            axis_a = getattr(actor_a, 'axis', actor_a) # axis or actor
            axis_b = getattr(actor_b, 'axis', actor_b)
            try:
                return shortest_path(self.graph, axis_a, axis_b)
            except Exception as e:
                print('dijkstra error:{}, the destination address cannot reach or exceed the boundary.'.format(e))
                return []
        def _area(self, actor, max, min):
            x, y = axis = getattr(actor, 'axis', actor) # axis or actor
            a = set()
            for i in range(max+1):
                for j in range(max+1):
                    if i+j >= min and i+j <= max:
                        _a = (x+i, y+j)
                        _b = (x+i, y-j)
                        _c = (x-i, y+j)
                        _d = (x-i, y-j)
                        if _a in self.graph: a.add(_a)
                        if _b in self.graph: a.add(_b)
                        if _c in self.graph: a.add(_c)
                        if _d in self.graph: a.add(_d)
            return a
        def _tracelimit(self, actor, max, min):
            ret = []
            for axis in self._area(actor, max, 1):
                trs = self._shortest_path(actor, axis)
                cos = self._trace_cost(trs)
                if cos >= min and cos <= max and trs:
                    ret.append(trs[-1])
            return ret
        def _trace_cost(self, trace):
            cost = 0
            for i in range(len(trace)-1):
                cost += self.graph[trace[i]][trace[i+1]]
            return cost
        def _local(self, actor, axis, obstruct): 
            actor.axis = axis # 让 actor 绑定一个坐标地址
            actor.obstruct = obstruct
            self._local_add(actor.axis, obstruct)
        def _local_set(self, axis, val): self.world['obs2d'][axis[1]][axis[0]]  = val; self._local_calc_graph(axis)
        def _local_del(self, axis, val): self.world['obs2d'][axis[1]][axis[0]] -= val; self._local_calc_graph(axis)
        def _local_add(self, axis, val): self.world['obs2d'][axis[1]][axis[0]] += val; self._local_calc_graph(axis)
        def _local_add_del(self, caxis, naxis, val):
            a = caxis[1] >= 0 and caxis[1] < self.maph and caxis[0] >= 0 and caxis[0] < self.mapw
            b = naxis[1] >= 0 and naxis[1] < self.maph and naxis[0] >= 0 and naxis[0] < self.mapw
            if a and b:
                self._local_del(caxis, val)
                self._local_add(naxis, val)
            else:
                if a: self._local_del(caxis, val)
                if b: self._local_add(naxis, val)
        def _local_calc_graph(self, axis):
            _val = self.world['_obs2d'][axis[1]][axis[0]] + self.world['obs2d'][axis[1]][axis[0]]
            for i in self.graph[axis]:
                if axis in self.graph[i]: self.graph[i][axis] = _val
        def _calc_center_by_rect(self, actor):
            ox, oy = self.map.rect[:2]
            _x, _y, w, h = actor.rect
            px, py = actor.axis
            tx = int(_x + w / 2) - ox
            ty = int(_y + h / 2) - oy
            ux = int(round((tx + self.gridw / 2) / self.gridw, 0) - 1)
            uy = int(round((ty + self.gridh / 2) / self.gridh, 0) - 1)
            return ux, uy
        def __str__(self):
            pks = []
            for i in self.world['obs2d']:
                pks.append(' '.join(['_'*self.gap if j == 0 else ('{:'+str(self.gap)+'}').format(j) for j in i]))
            return '\n'.join(pks)

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.map2d = Map.Map2D(self, self.mapw, self.maph)

    @property
    def gsize(self):
        return self.mapw, self.maph

    def _map_local(self, actor, axis, obstruct=0):
        self._gridlocal(actor, axis)
        self.map2d._local(actor, axis, obstruct)
        return self

    def trace(self, actor_a, actor_b):
        return self.map2d._shortest_path(actor_a, actor_b)

    def tracelimit(self, actor, max, min=1):
        return self.map2d._tracelimit(actor, max, min)

    def area(self, actor, max, min=1):
        return self.map2d._area(actor, max, min)

    def __str__(self):
        return 'map.gsize:{}\n{}'.format(self.gsize, str(self.map2d)) # 默认绘制阻力图



































class Button(Actor):
    RIGID_BODY = {}
    SHOW_BODY = {}

    def __init__(self, *a, **kw):
        kw.setdefault('in_entity', False)
        kw.setdefault('in_entitys', [])
        kw.setdefault('cam_follow', False) # 菜单一般都不需要镜头跟随的处理
        kw.setdefault('in_control', True)
        super().__init__(*a, **kw)
        self._init_hover_color()

    def _init_hover_color(self):
        class HoverImage(Actor):
            RIGID_BODY = {}
            SHOW_BODY = {}
            def __init__(self, *a, **kw):
                kw.setdefault('in_entity', False)
                kw.setdefault('in_entitys', [])
                kw.setdefault('cam_follow', False) # 背景需要镜头跟随的处理
                super().__init__(*a, **kw)
        colors = list(range(20, 200, 20))
        self._hover_lst = cycle(colors + colors[::-1])
        self._hover_col = (255, 255, 255)
        self._hover_aph = next(self._hover_lst)
        self._hover_dly = self.regist(Delayer(30))
        def func(image):
            bg = HoverImage((*self._hover_col,self._hover_aph), showsize=image.get_rect()[2:])
            image.blit(bg.image, bg.rect)
            del bg
            return image
        return func
    def _hoving(self, toggle=True, update=False, ticks=None):
        if update:
            if self._hover_dly.update(ticks):
                self._hover_aph = next(self._hover_lst)
        else:
            if toggle:
                self._tuning[0] = self._init_hover_color()
            else:
                if self._tuning:
                    del self._tuning[0]

