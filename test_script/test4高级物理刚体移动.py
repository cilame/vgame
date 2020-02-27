# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)




import vgame
s = vgame.Initer(60)
t = vgame.Theater('main') # 按 ESC 关闭，按 TAB 切换场景(如果只有一个场景就切换不了)

vgame.Actor.DEBUG = True # 让全部的 Actor 对象都显示 mask 的边框线

a = vgame.Actor(in_control=True,showsize=(50,100))
b = vgame.Actor(in_control=True,showsize=(10,10))
c = vgame.Actor(showsize=(20,20))

# 使用物理性质来进行移动，这样的话会自动对其他的物理对象进行平滑
# 代码量极大的简化了，并且如果你不想使用这样来移动，那么你也能使用最原始的 Actor对象的像素加减来实现。
# 在参数d中，用 p1 获取wasd方向键消息，p2 获取小箭头方向键消息，直接传递给 physics 即可使用
# *非常注意，覆盖 Actor.direction 函数的对象一定在初始化的时候设置了 in_control=True，否则报错
a.direction = lambda self,d: self.physics.move(d.get('p1')) 
b.direction = lambda self,d: self.physics.move(d.get('p2'))

a.in_entitys = [b, c] # AB相互互斥，因为 AB 均可移动所以需要考虑这些。
b.in_entitys = [a, c] # C 不会移动，所以无需给C一个额外绑定

a.rect[0:2] = 100, 100
b.rect[0:2] = 400, 200
c.rect[0:2] = 350, 180
t.regist(a)
t.regist(b)
t.regist(c)

s.regist(t) # 将场景 t 注入游戏
s.run()