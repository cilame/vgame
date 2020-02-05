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
    def __init__(self, event_rate=0, in_control=False):
        # 
        self.actor    = None
        self.rate     = event_rate  # 
        self.cur_tick = 0           # 总延时帧率部分的参数

        # 用于鼠标操作的参数（一般只有在鼠标按下时候会更新，所以不用担心资源浪费问题）
        self.mouse_id     = None # in (0,1,2) 0代表左键，2代表右键，1代表中键
        self.mouse_pos    = None
        self.mouse_status = 0    # 按键状态（0无按，1按下，2松开瞬间）
        self.mouse_toggle = True
        self.mouse_tick   = 0
        self.mouse_delay  = 300  # 鼠标按下多久不动后转变成地图拖拽模式 # 关于延迟的动态配置后期再做，这里先硬编码
        self.cross_time   = False
        self.cross_status = 0    # 判断状态（0判断，1单击，2框选，3地图拖拽）
        self.limit_len    = 3.   # 一个阈值，与鼠标按下松开时，两点坐标点距离有关

        # 用于键盘方向操作的参数
        self.direction_key_tick   = 0    # 后期发现只用 self._delay 函数，如果混合其他操作可能会出现灵敏丢失的情况
        self.direction_key_delay  = 100  # 所以最后还是把键盘的操作延时也单独出来了 # 关于延迟的动态配置后期再做，这里先硬编码
        self.un_oblique           = 0    # 如果没有斜角操作的话，处理斜角的操作滞粘操作参数

        # 用于键盘控制操作的参数
        self.control_key_tick     = 0
        self.control_key_delay    = 100
        self.control_keys = [pygame.K_j,pygame.K_k]


        # 用于实现栈效果式的更新函数
        self.update_stack = []

        # 直接通过 action参数实现对update函数的内置函数的配置
        if in_control:
            self.update_stack.append(self.update_select_cursor)

    def update(self,ticks):
        # 戏大部分功能是一种开关式的处理，就是开启之后必要会考虑的关闭，
        # 所以实际上，这里的处理如果是使用栈来实现的话，那些功能叠加的时候也能通过简单的pop-
        # 来回到上层的功能，这样的设计一般在这里都是找栈最上层的函数进行更新，不过栈在这里独立出来之后
        # 就可以更容易扩展出多场景捕捉功能的叠加。
        if self.update_stack:
            self.update_stack[-1](ticks)




    def _delay(self,ticks,rate):
        # 核心延迟函数，保证接收命令的帧率，防止操作灵敏度过高
        # 不过其他的操作不能直接用这个来实现延迟，因为直接用 self._delay 控制不好调整不同操作的接收频率。
        
        # 因为之后设计的所有按键操作都将会“放弃”通过 pygame.event.get() 获取事件的方式来获取控制
        # 因为 pygame.event.get() 多次在不同地方使用的时候，会出现各种问题（测试结论）。
        # 这无疑是对单击事件是非常灾难性的。灵敏度丢失不可接受， 所以这里一律使用 pygame.key.get_pressed() 来实现功能，
        # 这里通过延迟来实现按键执行的速率，避免任意需要延迟的操作漂移。
        # 这个地方为通用延时，和鼠标延时（鼠标延时类似于一种等待）还是有一些不太一样的。
        if ticks - self.cur_tick > rate:
            self.cur_tick = ticks
            return True

    def update_select_cursor(self,ticks):
        # 光标类主要是用于可以被控制所操作的对象，该类对象可以通过下面的函数来对操作进行挂钩
        # 后续可以开发部分功能用于该处与外部通信，让外部自定义的函数能够使用下面挂钩到的接口

        if self._delay(ticks,self.rate):
            direc_info = self.general_direction_key(ticks,wasd=True) # 处理通常方向键
            morse_info = self.general_mouse_model_a(ticks)           # 处理通常鼠标键
            
            # 简单打印操作接口返回的内容，后续会进行开发处理
            if morse_info:
                print(self.actor, morse_info)
            if direc_info:
                print(self.actor, direc_info)








    #===============#
    #               #
    #  操作功能捕捉  #
    #               #
    #===============#

    #==============#
    # 一般鼠标操作 #
    #==============#
    def general_mouse_model_a(self,ticks):
        # 这里的点击模式包含了类似地图抓取拖动的功能
        # 返回的参数为 按键id（0左键，1中键[不包含滚轮]，2右键），功能（1单击，2直接框选，3按住后再拖动），起点坐标，终点坐标
        # 当然如果没有 “按住后再拖动” 的功能需求，直接判断返回结果的第一个参数是否在 2，3 里面即可。
        rem = self._mouse_pressed() # rem 究竟是什么，详细请看 _mouse_pressed 函数注释。
        if rem and rem[0] in (0, 2):
            if self.cross_status == 0:
                if rem[1] == 1:
                    # 随时检查长度和时间
                    if self._mouse_delay(ticks,self.mouse_delay):
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
                return rem[0], 1, rem[2:4]
            # 2框选状态 # 鼠标快速框选某个区域
            if self.cross_status == 2:
                if rem[1] == 2:
                    self.cross_status = 0
                    self.cross_time = False
                else:
                    return rem[0], 2, rem[2:4]
            # 3地图状态 # 鼠标长按一点，然后拖动
            if self.cross_status == 3:
                if rem[1] == 2:
                    self.cross_status = 0
                    self.cross_time = False
                else:
                    return rem[0], 3, rem[2:4]
    def _mouse_delay(self,ticks,rate):
        # 鼠标的延迟在这里更类似于一种等待，实现鼠标长按功能
        if ticks - self.mouse_tick > rate:
            self.mouse_tick = ticks
            return True
    def _mouse_pressed(self):
        # 鼠标的话需要考虑几个状态
        # 1 左键单击（持续按，不超过一个很微小的时间，然后松开）
        # 2 左键持续（持续按，超过一个很微小的时间）
        # 3 右键同理
        # 4 右键同理
        # 5 复选模式（可能需要返回一个界面区域的rect交给后续处理，返回值也要考虑
        # ...
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
    def general_direction_key(self,ticks,wasd=False,oblique=True):
        rek = self._direction_key_pressed(wasd) # 获取当前按键（或组合键）的方向，以小键盘八方向数字为准
        # 需要先判断rek再判断延迟才能防止出现灵敏丢失的情况
        if rek and self._direction_key_delay(ticks,self.direction_key_delay):
            target = []
            if rek == 4: target.append(LEFT)
            if rek == 6: target.append(RIGHT)
            if rek == 8: target.append(UP)
            if rek == 2: target.append(DOWN)
            if oblique:
                # 允许有斜角的处理方法（默认允许斜角处理）# 这样处理不会出现对顶的可能性，注意
                if rek == 7: target.append(LEFT), target.append(UP)
                if rek == 1: target.append(LEFT), target.append(DOWN)
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
    def _direction_key_delay(self,ticks,rate):
        if ticks - self.direction_key_tick > rate:
            self.direction_key_tick = ticks
            return True
    def _direction_key_pressed(self,wasd=False):
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

    #================#
    # 一般控制键操作 #
    #================#
    def general_control_key(self,ticks):
        # 类似于一般手柄上面的AB键位的功能，简单的提供一些接口
        # 让某些键位注册后返回一些对于编写者来说更方便查调用的数据接口
        # 类似注册了键盘 jk 键位为 ab（手柄），按j、k键时候返回为a、b，之类的。ab会更好进行功能辨识
        pass
    def _control_key_pressed(self):
        # 一些普通的键盘非方向键的按键返回，这里需要考虑的是一般游戏ab键的单按和连发的区分和识别
        # 所以可能需要和鼠标那样的方式去实现功能。方向键和ab键和鼠标都是需要各自的延迟参数(必须)
        # 动作类游戏不可能按住方向键ab键就不能使用，分开延迟就可以实现互不影响
        # 这里先实现分类，向上封装后再由上一层进行延迟封装，这里需要实现注册功能，因为wasd本身就是键盘上的按键，所以需要考虑
        # 这里默认只给予三种游戏选择键的处理（ab）（abxy）（abcxyz），就是说，self.control_keys 只接受长度为2、4、6的list参数。
        # 并且xyz分别为abc三个功能按键的连发，仅此而已。
        # 考虑一下多个按键同时按下的话怎么处理，
        key = pygame.key.get_pressed()
        if len(self.control_keys) == 2:
            a,b = self.control_keys
            a = key[a]
            b = key[b]
            v = [a,b]
            if any(v): return (2,v)
        if len(self.control_keys) == 4:
            a,b,x,y = self.control_keys
            a = key[a]
            b = key[b]
            x = key[x]
            y = key[y]
            v = [a,b,x,y]
            if any(v): return (4,v)
        if len(self.control_keys) == 6:
            a,b,c,x,y,z = self.control_keys
            a = key[a]
            b = key[b]
            c = key[c]
            x = key[x]
            y = key[y]
            z = key[z]
            v = [a,b,c,x,y,z]
            if any(v): return (6,v)