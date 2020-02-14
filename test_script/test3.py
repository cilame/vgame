# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)




import vgame
s = vgame.Initer()
t = vgame.Theater('main') # 按 ESC 关闭，按 TAB 切换场景(如果只有一个场景就切换不了)

vgame.Actor.DEBUG = True # 让全部的 Actor 对象都显示 mask 的边框线

a = vgame.Actor(in_control=True,showsize=(50,100))
b = vgame.Actor(in_control=True)

def direct_a(self, m):
    for i in m.get('p1') or []:
        if i == 8: self.rect[1] = max(self.rect[1] - 7, 0)
        if i == 2: self.rect[1] = min(self.rect[1] + 7, s.size[1] - self.rect[3])
        if i == 4: self.rect[0] = max(self.rect[0] - 7, 0)
        if i == 6: self.rect[0] = min(self.rect[0] + 7, s.size[0] - self.rect[2])
a.direction = direct_a

def collide_b(self):
    r = self.collide(a)
    if r:
        print(r)
b.idle = collide_b
a.rect[0:2] = 100, 100
b.rect[0:2] = 400, 200
t.regist(a)
t.regist(b)


s.regist(t) # 将场景 t 注入游戏
s.run()