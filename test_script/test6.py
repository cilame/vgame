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

i_fra = vgame.Image('../test_data/fish/right_attck1', rate=60)
a = vgame.Actor(in_control=True)
b = vgame.Actor(showsize=(80,80))
c = vgame.Actor(showsize=(40,40)) 

wd = vgame.Actor(showsize=(300,10))
wu = vgame.Actor(showsize=(300,10))
wl = vgame.Actor(showsize=(10,300))
wr = vgame.Actor(showsize=(10,300))

# 经过测试
# 如果使用重力/惯性系统做移动的话，请尽量使用默认 fps。

# 示例：
# y重力系统，x摩擦系统
# effect_highs 为一个限制跳跃的高度字典，key为跳跃方向的数字，value为限制高度的参数
a.direction = lambda self,d: self.physics.move2(d.get('p1'))
a.physics.gravity.y = 3
a.physics.effect_highs = {8:80}
# a.physics.gravity.x = -2.5

# “重力系统” 和 “摩擦系统” 均能使用的参数
a.physics.speed_inc.x = 3  # 加速度             【只能正数，整数小数均可】
a.physics.speed_dec.x = 5  # 减速度（类似于摩擦）【只能正数，整数小数均可】
a.physics.speed_max.x = 5  # 最大速度           【只能正数，整数小数均可】
a.physics.speed_max.y = 8

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