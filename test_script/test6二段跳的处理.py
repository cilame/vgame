# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)




import vgame
s = vgame.Initer(60)
t = vgame.Theater('main')

vgame.Actor.DEBUG = True

a = vgame.Actor(in_control=True)
b = vgame.Actor(showsize=(80,80))
c = vgame.Actor(showsize=(40,40)) 

wd = vgame.Wall(showsize=(600,10))
wu = vgame.Wall(showsize=(500,10))
wl = vgame.Wall(showsize=(10,300))
wr = vgame.Wall(showsize=(10,300))

# 经过测试
# 如果使用重力/惯性系统做移动的话，请尽量使用默认 fps。

# 示例：
# y重力系统，x摩擦系统

# 处理使用其他按键作为跳跃键
# 方法1：
# 在操作中函数内同时获取方向键和操作键的信息，然后用操作键消息覆盖上键的消息
# 因为 direction 也可以使用三个参数的函数覆盖，使用三个参数时候第三个为控制键的消息
# def direct_a(self, d, c):
#     q = d.get('p1')
#     p = c.get('p1')
#     if d and 8 in q: q.remove(8) # 先去除原本存在的上方向键传递的跳跃消息
#     if p and p[0]: # 使用控制功能键来做为跳跃的消息
#         if q is None: q = []
#         q.append(8)
#     self.physics.move2(q)
# a.direction = direct_a
# 方法2：
# 直接修改上键操作为J按键即可 a.controller.direction_keys_p1.up
# 方法2也会比较简单，或许也能扩展成其他没有设置过的按键都行
a.direction = lambda self,d: self.physics.move2(d.get('p1'))
a.controller.direction_keys_p1.up = vgame.K_j
a.physics.gravity.y = 3

# 这里封装了两个参数，是一个非常重要的游戏性，如果在外部单独处理起来非常麻烦的功能
# limit_highs 为一个限制跳跃的高度字典，key为跳跃方向的数字，value为限制高度的参数
# jump_times  为一个限制跳跃的次数字段，key为跳跃方向的数字，value为限制高度的参数
# 1 某个方向跳跃的最大高度，限制了高度，才是一个好的跳跃游戏
#  *注意，这个高度最好适当调整一些 y 方向上的加速度、重力、最大速度调整到最佳会方便游戏
a.physics.limit_highs = {8:80}
# 2 某个方向跳跃的最大次数，跳跃后直到落到地面才会重新更新次数
#  *注意，如果不设置这个参数，默认跳跃次数无限，类似游戏 flappy bird 的模式。
#   一般游戏设置 1 或 2 已经足够
a.physics.jump_times = {8:2}

# “重力系统” 和 “摩擦系统” 均能使用的参数
a.physics.speed_inc.x = 3 # 加速度           【整数小数均可，只能正数】
a.physics.speed_dec.x = 1 # 减速度（摩擦系统）【整数小数均可，只能正数】
a.physics.speed_max.x = 5 # 最大速度         【整数小数均可，只能正数】
a.physics.speed_max.y = 8
a.physics.speed_inc.y = 3

# 测试移动模块，
# physics.move 和 physics.move2 接收的参数为一个数字的列表
# 数字只能为 8,2,4,6 即为小键盘的键位方向 上下左右 的意思。
# 例如下面这个示例就是不断向左下方向移动的意思。
b.idle = lambda self,d: self.physics.move([4, 2])

a.rect[0:2] = 100, 100
b.rect[0:2] = 400, 200
c.rect[0:2] = 200, 200
t.regist(a)
t.regist(b)
t.regist(c)


wd.rect[0:2] = 100, 400
wu.rect[0:2] = 100, 10
wl.rect[0:2] = 600, 100
wr.rect[0:2] = 30, 100
t.regist(wd)
t.regist(wu)
t.regist(wl)
t.regist(wr)

s.regist(t) # 将场景 t 注入游戏
s.run()