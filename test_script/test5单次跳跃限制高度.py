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
a = vgame.Actor(i_fra,in_control=True)
b = vgame.Actor(showsize=(510,10))
c = vgame.Actor(showsize=(80,80))
d = vgame.Actor(showsize=(40,40)) 
# 如果不想让某些块处理实体碰撞，实例化时候设置 in_entity 为 False，自动去除实体检测

# 使用物理性质进行移动，将会自动对其他实体对象实现实体碰撞，并能极大简化代码

# 1 简单物理性质的移动 self.physics.move
# 2 高级物理性质的移动 self.physics.move2
# 两者的使用方式是一模一样的，下面用从方向消息中获取 'p1' 来获取 wasd 方向键消息
# a.direction = lambda self,d: self.physics.move(d.get('p1')) 
# a.direction = lambda self,d: self.physics.move2(d.get('p1'))

# 简单物理移动：
# 如果只想用到自动碰撞检测，平滑移动，不想用重力，摩擦，之类的复杂功能
# 那么你只要使用 physics.move 来实现移动即可
# 而且可以使用 physics.speed.x 和 physics.speed.y 来修改这种平滑移动的速度

# 高级物理移动：
# 高级物理移动的原理是改变x/y速度的分量。物体会在 speed 影响下移动一定的距离。
# 速度会自动在“摩擦函数”或者“碰撞其他实体”墙壁的时候自动归零。
# 1重力系统，2摩擦系统，这两个系统互斥，在 x/y 方向各有分量
# 一个 Actor 对象如果设置了 in_entity，则默认自带一个高级物理环境
# 默认情况 x/y 方向均为摩擦系统。
# 如何设置重力系统？
# 当 x 方向设置了 physics.gravity.x 为非零整数或浮点数，则 x 方向自动转换成重力系统
# 当 y 方向设置了 physics.gravity.y 为非零整数或浮点数，则 y 方向自动转换成重力系统
# 重力系统和摩擦系统不一样
# 重力系统一直会对重力系统的方向的速度进行变化，除非你给了一个其他速度的分量
# 一般带有跳跃的游戏中，y 方向一般都为重力系统，而 x 方向都为摩擦系统
# 所以如果想要主角拥有重力影响，则直接设置 physics.gravity.y 为一个很小的整数即可




# 示例：
# 简单物理系统
# a.direction = lambda self,d: self.physics.move(d.get('p1'))
# a.physics.smooth_speed.x = 20 # 用 smooth_speed 参数来修改平滑移动的速度
# a.physics.smooth_speed.y = 20

# 示例：
# y重力系统，x摩擦系统
a.direction = lambda self,d: self.physics.move2(d.get('p1')) # p1:wasd键方向消息
a.physics.limit_highs = {8:80}
a.physics.gravity.y = 2.5  # 修改 gravity.y 即在 y 方向上增加重力常量【参数可正可负】
# “重力系统” 和 “摩擦系统” 均能使用的参数，摩擦系统需要的参数
a.physics.speed_inc.x = 2  # 加速度             【只能正数，整数小数均可】
a.physics.speed_dec.x = 1  # 减速度（类似于摩擦）【只能正数，整数小数均可】
a.physics.speed_max.x = 5  # 最大速度           【只能正数，整数小数均可】
a.physics.speed_inc.y = 2.5
a.physics.speed_max.y = 8
# 额外描述：
# physics.move2 函数的第二个参数为执行时间


# 测试移动模块，
# physics.move 和 physics.move2 接收的参数为一个数字的列表
# 数字只能为 8,2,4,6 即为小键盘的键位方向 上下左右 的意思。
# 例如下面这个示例就是不断向左下方向移动的意思。
c.idle = lambda self,d: self.physics.move([4, 2]) 

a.rect[0:2] = 100, 100
b.rect[0:2] = 100, 400
c.rect[0:2] = 400, 200
d.rect[0:2] = 200, 200
t.regist(a)
t.regist(b)
t.regist(c)
t.regist(d)

s.regist(t) # 将场景 t 注入游戏
s.run()