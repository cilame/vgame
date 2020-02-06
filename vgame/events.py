from itertools import cycle, product
from string import printable

import pygame
from pygame.locals import *

UP    = 8 # 固定值
DOWN  = 2 # 固定值
LEFT  = 4 # 固定值
RIGHT = 6 # 固定值

class Events:
    '''
    控制事件的对象，每个 Actor 都会生成一个属于他们自身的 Events 对象在类内部，
    可以通过 in_control 参数进行配置是否需要使用控制处理
    状态转化 # 战斗计算 # 血条显示之类 # 属性配置之类 # 子弹发射 # 我个人想到什么就扩展什么，各种功能...
    '''
    def __init__(self, event_rate=60, in_control=False):
        # 
        self.actor    = None
        self.rate     = event_rate  # 
        self.cur_tick = 0           # 总延时帧率部分的参数

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
        self.limit_len    = 3.   # 一个阈值，与鼠标按下松开时，两点坐标点距离有关

        # 用于键盘方向操作的参数
        self.direction_key_tick  = 0  # 后期发现只用 self._delay 函数，如果混合其他操作可能会出现灵敏丢失的情况
        self.direction_key_delay = 15 # 所以最后还是把键盘的操作延时也单独出来了
        self.un_oblique          = 0  # 如果没有斜角操作的话，处理斜角的操作滞粘操作参数

        # 用于键盘控制操作的参数
        self.control_key_tick  = 0
        self.control_key_delay = 15
        self.control_keys      = [pygame.K_j, pygame.K_k]

        # 用于实现栈效果式的更新函数
        self.update_stack = []

        # 直接通过 action参数实现对update函数的内置函数的配置
        if in_control:
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
        morse_info = self.general_mouse_key(ticks,model='a')         # 处理通常鼠标键，有两种模式，请看函数内的注释描述
        direc_info = self.general_direction_key(ticks,direct='wasd') # 处理通常方向键
        cntro_info = self.general_control_key(ticks)                 # 处理通常ab键的接收
        
        # # 简单打印操作接口返回的内容，后续会进行开发处理
        # if morse_info: print(self.actor, self.actor.rect, 'morse_info:', morse_info)
        # if direc_info: print(self.actor, self.actor.rect, 'direc_info:', direc_info)
        # if cntro_info: print(self.actor, self.actor.rect, 'cntro_info:', cntro_info)
        return morse_info, direc_info, cntro_info

    #===============#
    #               #
    #  操作功能捕捉  #
    #               #
    #===============#

    #==============#
    # 一般鼠标操作 #
    #==============#
    # 鼠标的操作有两个函数，分别表示两种处理方式
    # model=='a': 这种类型仅含单击和框选两种模式
    # model=='b': 这种类型包含单击、框选和长按三种模式
    # 该两个函数的返回参数均如下所示，仅在功能上是否返回3这点区别
    # 返回的参数为 按键id（0左键，1中键[不包含滚轮]，2右键），功能（1单击，2直接框选，3按住后再拖动），起点坐标，终点坐标
    # 非常建议使用 a 类，这种处理非常顺滑，
    def general_mouse_key(self,ticks,model='a'):
        # 这里的点击模式仅仅包含单击和框选两种处理方式
        rem = self._mouse_pressed() # rem 究竟是什么，详细请看 _mouse_pressed 函数注释。
        def model_a(rem):
            if rem and rem[0] in (0, 2):
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
        # 这里的点击模式包含单击、框选和长按拖动三种模式
        def model_b(rem):
            if rem and rem[0] in (0, 2):
                if self.cross_status == 0:
                    if rem[1] == 1:
                        # 随时检查长度和时间
                        if self._mouse_delay(ticks):
                            if self.cross_time:
                                if rem[4] < self.limit_len:
                                    self.cross_status = 3
                                if rem[4] >= self.limit_len:
                                    self.cross_status = 2
                            self.cross_time = True
                    if rem[1] == 2:
                        if rem[4] >= self.limit_len:
                            self.cross_status = 2
                        else:
                            self.cross_status = 1
                            self.cross_time = False
                # 1单击状态 # 就是鼠标单击
                if self.cross_status == 1:
                    self.cross_status = 0
                    return rem[0], self.cross_status, rem[2:4]
                # 2框选状态 # 鼠标快速框选某个区域
                if self.cross_status == 2:
                    if rem[1] == 2:
                        self.cross_status = 0
                        self.cross_time = False
                    else:
                        return rem[0], self.cross_status, rem[2:4]
                # 3地图状态 # 鼠标长按一点，然后拖动
                if self.cross_status == 3:
                    if rem[1] == 2:
                        self.cross_status = 0
                        self.cross_time = False
                    else:
                        return rem[0], self.cross_status, rem[2:4]
        if model == 'a': return model_a(rem)
        if model == 'b': return model_b(rem)
    def _mouse_delay(self,ticks):
        # 鼠标的延迟在这里更类似于一种等待，实现鼠标长按功能
        if ticks - self.mouse_tick > self.mouse_delay:
            self.mouse_tick = ticks
            return True
    def _mouse_pressed(self):
        # 【返回参数】：
        # 按键id（0左键，1中键[不包含滚轮]，2右键），按键状态（0无按，1按下，2松开瞬间），起点坐标，终点坐标，两坐标之间的长
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
                self.mouse_pos = pygame.mouse.get_pos() # 起始坐标
                self.mouse_toggle = False
            if mouse.count(1) != 1: # 按住左键同时又按住右键，这样不会存在松开的状态
                self.mouse_status = 2
            cur_pos = pygame.mouse.get_pos() # 鼠标松开的坐标点
            len_for_2point = ((self.mouse_pos[0]-cur_pos[0])**2 + (self.mouse_pos[1]-cur_pos[1])**2)**.5
            return self.mouse_id, 1 ,self.mouse_pos, cur_pos, len_for_2point
        # 鼠标松开的瞬间
        if self.mouse_status == 2:
            self.mouse_status = 0 # 松开后立马将状态转换成未按下的状态，让鼠标松开的操作仅返回一次
            self.mouse_toggle = True # 同时将鼠标单次记录开关打开
            cur_pos = pygame.mouse.get_pos() # 鼠标松开的坐标点
            len_for_2point = ((self.mouse_pos[0]-cur_pos[0])**2 + (self.mouse_pos[1]-cur_pos[1])**2)**.5
            # 按键id，按键状态，起止两个坐标点，两坐标之间的长度
            return self.mouse_id, 2, self.mouse_pos, cur_pos, len_for_2point

    #================#
    # 一般方向键操作 #
    #================#
    def general_direction_key(self,ticks,direct='wasd',oblique=True):
        rek = self._direction_key_pressed(direct) # 获取当前按键（或组合键）的方向，以小键盘八方向数字为准
        # 需要先判断rek再判断延迟才能防止出现灵敏丢失的情况
        if rek and self._direction_key_delay(ticks):
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
                if rek in [2,4,6,8]:
                    self.un_oblique = rek
                if rek == 7:
                    if self.un_oblique == 8: target.append(LEFT)
                    if self.un_oblique == 4: target.append(UP)
                if rek == 1:
                    if self.un_oblique == 2: target.append(LEFT)
                    if self.un_oblique == 4: target.append(DOWN)
                if rek == 9:
                    if self.un_oblique == 8: target.append(RIGHT)
                    if self.un_oblique == 6: target.append(UP)
                if rek == 3:
                    if self.un_oblique == 2: target.append(RIGHT)
                    if self.un_oblique == 6: target.append(DOWN)
            return target
    def _direction_key_delay(self,ticks):
        if ticks - self.direction_key_tick > self.direction_key_delay:
            self.direction_key_tick = ticks
            return True
    def _direction_key_pressed(self,direct='wasd'):
        key = pygame.key.get_pressed()
        ret = 0
        if direct == 'wasd':
            a = key[pygame.K_w]
            b = key[pygame.K_s]
            c = key[pygame.K_a]
            d = key[pygame.K_d]
        if direct == 'uldr':
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

    #================#
    # 一般控制键操作 #
    #================#
    def general_control_key(self,ticks):
        # 类似于一般手柄上面的AB键位的功能，简单的提供一些接口
        # 让某些键位注册后返回一些对于编写者来说更方便查调用的数据接口
        # 类似注册了键盘 jk 键位为 ab（手柄），按j、k键时候返回为a、b，之类的。ab会更好进行功能辨识
        rck = self._control_key_pressed() # 获取当前按键（或组合键）的方向，以小键盘八方向数字为准
        if rck and self._control_key_delay(ticks):
            return rck
    def _control_key_delay(self,ticks):
        if ticks - self.control_key_tick > self.control_key_delay:
            self.control_key_tick = ticks
            return True
    def _control_key_pressed(self):
        # 一些普通的键盘非方向键的按键返回，这里需要考虑的是一般游戏ab键的单按和连发的区分和识别
        # 所以可能需要和鼠标那样的方式去实现功能。方向键和ab键和鼠标都是需要各自的延迟参数(必须)
        # 动作类游戏不可能按住方向键ab键就不能使用，分开延迟就可以实现互不影响
        # 这里先实现分类，向上封装后再由上一层进行延迟封装，这里需要实现注册功能，因为wasd本身就是键盘上的按键，所以需要考虑
        # 这里默认只给予三种游戏选择键的处理（ab）（abxy）（abcxyz），就是说，self.control_keys 只接受长度为2、4、6的list参数。
        # 并且xyz分别为abc三个功能按键的连发，仅此而已。
        # 考虑一下多个按键同时按下的话怎么处理，
        key = pygame.key.get_pressed()
        v = [key[i] for i in self.control_keys]
        if any(v): return (len(self.control_keys),v)