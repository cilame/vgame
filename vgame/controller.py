from itertools import cycle, product
from string import printable

import pygame
from pygame.locals import *

import vgame

UP    = 8 # 固定值
DOWN  = 2 # 固定值
LEFT  = 4 # 固定值
RIGHT = 6 # 固定值

class Direction:
    def __init__(self, up, down, left, right):
        self.up    = up
        self.down  = down
        self.left  = left
        self.right = right

class Controller:
    '''
    控制事件的对象，每个 Actor 都会生成一个属于他们自身的 Controller 对象在类内部，
    '''
    roll = 0
    def __init__(self):
        self.actor = None

        # 因为之后设计的所有按键操作都将会“放弃”通过 pygame.event.get() 获取事件的方式来获取控制
        # 因为 pygame.event.get() 多次在不同地方使用的时候，会出现各种问题（测试结论）。
        # 这无疑是对单击事件是非常灾难性的。灵敏度丢失不可接受， 所以这里一律使用 pygame.key.get_pressed() 来实现功能，
        # 这里通过延迟来实现按键执行的速率，避免任意需要延迟的操作漂移。
        # 这个地方为通用延时，和鼠标延时（鼠标延时类似于一种等待）还是有一些不太一样的。

        # 用于鼠标操作的参数（一般只有在鼠标按下时候会更新，所以不用担心资源浪费问题）
        self.mouse_id     = None # in (0,1,2) 0代表左键，2代表右键，1代表中键
        self.mouse_pos    = None
        self.mouse_status = 0    # 按键状态（0无按，1按下，2松开瞬间）
        self.mouse_toggle = True
        self.mouse_tick   = 0
        self.mouse_delay  = 300  # 鼠标按下多久不动后转变成地图拖拽模式
        self.cross_time   = False
        self.cross_status = 0    # 判断状态（0判断，1单击，2框选，3地图拖拽）
        self.limit_len    = 5.   # 一个阈值，与鼠标按下松开时，两点坐标点距离有关

        # 用于键盘方向操作的参数，目前可支持2p（由于处理方向键的延迟处理有点特殊，所以需要这样处理）
        self.direction_key_tick_p1  = 0 # 后期发现只用 self._delay 函数，如果混合其他操作可能会出现灵敏丢失的情况
        self.direction_key_delay_p1 = 1 # 所以最后还是把键盘的操作延时也单独出来了，不过后续发现最好还是在 actor 内实现延迟会更好
        self.direction_keys_p1      = Direction(*[pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d])
        self.un_oblique_p1          = 0  # 如果没有斜角操作的话，处理斜角的操作滞粘操作参数
        self.direction_key_tick_p2  = 0
        self.direction_key_delay_p2 = 1
        self.direction_keys_p2      = Direction(*[pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT])
        self.un_oblique_p2          = 0

        # 用于键盘控制操作的参数
        self.control_key_tick_p1  = 0
        self.control_key_delay_p1 = 1
        self.control_keys_p1      = [pygame.K_j, pygame.K_k]
        self.control_key_tick_p2  = 0
        self.control_key_delay_p2 = 1
        self.control_keys_p2      = [pygame.K_KP1, pygame.K_KP2] # 小键盘数字键

        # 用于实现栈效果式的更新函数
        self.update_stack = []

        # 直接通过 action参数实现对update函数的内置函数的配置
        self.update_stack.append(self.update_select_cursor)

    def update(self,ticks):
        # 这里的处理暂时没有特别的必要，但是一个操作捕捉的栈空间或许后续可以扩充功能
        # 用于覆盖某些之前的功能，或者说，
        if self.update_stack:
            return self.update_stack[-1](ticks)
        else:
            return None, None, None

    def update_select_cursor(self,ticks):
        # 光标类主要是用于可以被控制所操作的对象，该类对象可以通过下面的函数来对操作进行挂钩
        # 后续可以开发部分功能用于该处与外部通信，让外部自定义的函数能够使用下面挂钩到的接口
        morse_info = self.general_mouse_key(ticks)     # 处理通常鼠标键，有两种模式，请看函数内的注释描述
        direc_info = self.general_direction_key(ticks) # 处理通常方向键
        cntro_info = self.general_control_key(ticks)   # 处理通常ab键的接收
        return morse_info, direc_info, cntro_info

    #===============#
    #               #
    #  操作功能捕捉  #
    #               #
    #===============#

    @staticmethod
    def get_pos():
        x, y = pygame.mouse.get_pos()
        artist = vgame.Artist.ARTIST
        if not artist:
            return x, y
        if artist.equalscale:
            ow, oh = artist.screen_rect[2:]
            tw, th = artist.screen_neor[2:]
            fx, fy = artist.screen_offx, artist.screen_offy
            if fx:    rx, ry = int((x-fx)/th*oh), int(y/th*oh)
            elif fy:  rx, ry = int(x/tw*ow), int((y-fy)/tw*ow)
            else:     rx, ry = int(x/tw*ow), int(y/th*oh)
        else:
            ow, oh = artist.screen_rect[2:]
            tw, th = artist.screen_neor[2:]
            rx, ry = int(x/tw*ow), int(y/th*oh)
        return rx, ry

    #==============#
    # 一般鼠标操作 #
    #==============#
    # 返回的参数为 按键id（0左键，1滚轮，2右键），功能（0单击，2拖动，4滚轮前滚，5滚轮后滚），起点坐标，终点坐标
    # 注意，滚轮有滚动操作和按下操作两种，
    def general_mouse_key(self,ticks):
        if self.roll:
            cur_pos = self.get_pos()
            return (1, self.roll, (cur_pos, cur_pos))
        rem = self._mouse_pressed() 
        # rem 究竟是什么，详细请看 _mouse_pressed 函数注释。
        # 注意：general_mouse_key 函数返回的参数 和 _mouse_pressed 看上去有点像，但实际上不一样。
        # 这里的点击模式仅仅包含单击和框选两种处理方式
        if rem and rem[0] in (0, 1, 2):
            if self.cross_status == 0:
                if rem[1] == 1:
                    if rem[4] >= self.limit_len:
                        self.cross_status = 2
                if rem[1] == 2:
                    if rem[4] >= self.limit_len:
                        self.cross_status = 2
                    else:
                        self.cross_status = 1
            # 1单击状态 # 就是鼠标单击
            if self.cross_status == 1:
                self.cross_status = 0
                return rem[0], self.cross_status, rem[2:4]
            # 2框选状态 # 鼠标快速框选某个区域
            if self.cross_status == 2:
                if rem[1] == 2:
                    self.cross_status = 0
                else:
                    return rem[0], self.cross_status, rem[2:4]
    def _mouse_delay(self,ticks):
        # 鼠标的延迟在这里更类似于一种等待，实现鼠标长按功能
        if ticks - self.mouse_tick > self.mouse_delay:
            self.mouse_tick = ticks
            return True
    def _mouse_pressed(self):
        # 【返回参数】：
        # 按键id（0左键，1中键[包含滚轮]，2右键），按键状态（0无按，1按下，2松开瞬间），起点坐标，终点坐标，两坐标之间的长
        # 虽然包含滚轮消息，但是由于 pygame 一定缺陷，滚轮消息在 Initer 里面的主循环内实现。
        mouse = pygame.mouse.get_pressed()
        # 鼠标未被按下
        if self.mouse_status == 0:
            if mouse.count(1) == 1:
                # 这里需要扩展滚轮操作吗？（暂时没有硬需求，不考虑）
                self.mouse_id = mouse.index(1)
                self.mouse_status = 1
        # 鼠标按下的处理
        if self.mouse_status == 1:
            if self.mouse_toggle:
                self.mouse_pos = self.get_pos() # 起始坐标
                self.mouse_toggle = False
            if mouse.count(1) != 1: # 按住左键同时又按住右键，这样不会存在松开的状态
                self.mouse_status = 2
            cur_pos = self.get_pos() # 鼠标松开的坐标点
            len_for_2point = ((self.mouse_pos[0]-cur_pos[0])**2 + (self.mouse_pos[1]-cur_pos[1])**2)**.5
            return self.mouse_id, 1 ,self.mouse_pos, cur_pos, len_for_2point
        # 鼠标松开的瞬间
        if self.mouse_status == 2:
            self.mouse_status = 0 # 松开后立马将状态转换成未按下的状态，让鼠标松开的操作仅返回一次
            self.mouse_toggle = True # 同时将鼠标单次记录开关打开
            cur_pos = self.get_pos() # 鼠标松开的坐标点
            len_for_2point = ((self.mouse_pos[0]-cur_pos[0])**2 + (self.mouse_pos[1]-cur_pos[1])**2)**.5
            # 按键id，按键状态，起止两个坐标点，两坐标之间的长度
            return self.mouse_id, 2, self.mouse_pos, cur_pos, len_for_2point

    #================#
    # 一般方向键操作 #
    #================#
    def general_direction_key(self,ticks,oblique=True):
        cp1, cp2 = self._direction_key_pressed() # 获取当前按键（或组合键）的方向，以小键盘八方向数字为准
        d = {}
        p, rek = cp1
        if rek and self._direction_key_delay_p1(ticks): # 需要先判断rek再判断延迟才能防止出现灵敏丢失的情况
            target = self._direction_ret_p1(rek, oblique); d[p] = target
        p, rek = cp2
        if rek and self._direction_key_delay_p2(ticks):
            target = self._direction_ret_p2(rek, oblique); d[p] = target
        return d
    def _direction_key_delay_p1(self,ticks):
        if ticks - self.direction_key_tick_p1 > self.direction_key_delay_p1:
            self.direction_key_tick_p1 = ticks
            return True
    def _direction_key_delay_p2(self,ticks):
        if ticks - self.direction_key_tick_p2 > self.direction_key_delay_p2:
            self.direction_key_tick_p2 = ticks
            return True
    def _direction_ret_p1(self, rek, oblique): return self._direction_ret(self.un_oblique_p1, rek, oblique)
    def _direction_ret_p2(self, rek, oblique): return self._direction_ret(self.un_oblique_p2, rek, oblique)
    def _direction_ret(self, p, rek, oblique):
        target = []
        if rek == 4: target.append(LEFT)
        if rek == 6: target.append(RIGHT)
        if rek == 8: target.append(UP)
        if rek == 2: target.append(DOWN)
        if oblique:
            # 允许有斜角的处理方法（默认允许斜角处理）# 这样处理不会出现对顶的可能性，注意
            if rek == 7: target.append(LEFT),  target.append(UP)
            if rek == 1: target.append(LEFT),  target.append(DOWN)
            if rek == 9: target.append(RIGHT), target.append(UP)
            if rek == 3: target.append(RIGHT), target.append(DOWN)
        else:
            # 只允许正方向键[只有上下左右]的处理方法（最优解是根据后一个按下的正方向键[只有上下左右]来实现）
            # 不过这个借口目前基本上不暴露出去，基本不会被用到，只为提供给后面考虑是否使用这里作为扩展。
            if rek in [2,4,6,8]:
                p = rek
            if rek == 7:
                if p == 8: target.append(LEFT)
                if p == 4: target.append(UP)
            if rek == 1:
                if p == 2: target.append(LEFT)
                if p == 4: target.append(DOWN)
            if rek == 9:
                if p == 8: target.append(RIGHT)
                if p == 6: target.append(UP)
            if rek == 3:
                if p == 2: target.append(RIGHT)
                if p == 6: target.append(DOWN)
        return target
    def _direction_key_pressed_p1(self, key):
        ret = 0
        p = 'p1'
        a = key[self.direction_keys_p1.up]
        b = key[self.direction_keys_p1.down]
        c = key[self.direction_keys_p1.left]
        d = key[self.direction_keys_p1.right]
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
        return p, ret
    def _direction_key_pressed_p2(self, key):
        ret = 0
        p = 'p2'
        a = key[self.direction_keys_p2.up]
        b = key[self.direction_keys_p2.down]
        c = key[self.direction_keys_p2.left]
        d = key[self.direction_keys_p2.right]
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
        return p, ret
    def _direction_key_pressed_p0(self, key):
        p = 'p0'
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
        return p, ret
    def _direction_key_pressed(self):
        key = pygame.key.get_pressed()
        # 目前将放弃小键盘数字的方向处理，
        # 因为有些两人共用一个键盘的2p游戏，小键盘可能用于功能键
        # 所以现在默认将放弃对这个部分的处理。
        # cp0 = self._direction_key_pressed_p0(key) # 小键盘数字
        cp1 = self._direction_key_pressed_p1(key) # wasd
        cp2 = self._direction_key_pressed_p2(key) # 小键盘箭头
        return cp1, cp2
        

    #================#
    # 一般控制键操作 #
    #================#
    def general_control_key(self,ticks):
        rck1, rck2 = self._control_key_pressed()
        d = {}
        p, rck = rck1
        if rck and self._control_key_delay_p1(ticks):
            d[p] = rck
        p, rck = rck2
        if rck and self._control_key_delay_p2(ticks):
            d[p] = rck
        return d
    def _control_key_delay_p1(self,ticks):
        if ticks - self.control_key_tick_p1 > self.control_key_delay_p2:
            self.control_key_tick_p1 = ticks
            return True
    def _control_key_delay_p2(self,ticks):
        if ticks - self.control_key_tick_p2 > self.control_key_delay_p2:
            self.control_key_tick_p2 = ticks
            return True
    def _control_key_pressed(self):
        key = pygame.key.get_pressed()
        p1 = [key[i] for i in self.control_keys_p1]
        p2 = [key[i] for i in self.control_keys_p2]
        p1 = p1 if any(p1) else []
        p2 = p2 if any(p2) else []
        return ('p1', p1), ('p2', p2)