# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)




import vgame
s = vgame.Initer(60)
t = vgame.Theater() # 按 ESC 关闭，按 TAB 切换场景(如果只有一个场景就切换不了)

vgame.Actor.DEBUG = True # 让全部的 Actor 对象都显示 mask 的边框线

a = vgame.Actor(in_control=True,showsize=(50,100))
b = vgame.Actor(showsize=(10,10))
c = vgame.Actor(showsize=(20,20))

walls = []
walls.append(b)
walls.append(c)
speed = 7

# 平滑移动(墙体检测，贴边移动)
# 这是一个比较硬核的平滑移动处理，后面将使用 Actor.physics 来实现平滑移动的处理
# 那样将会大幅度简化代码量，让人能够更好的远离操作处理与运动处理的绑定。
def direct_a(self, d):
    for i in d.get('p1') or []:
        print(d)
        if i == 6: self.rect[0] = min(self.rect[0] + speed, s.size[0] - self.rect[2])
        if i == 4: self.rect[0] = max(self.rect[0] - speed, 0)
        aw = self.collide(*walls)
        if aw:
            for w in aw:
                if 6 in d.get('p1'): self.rect.x = w.rect.left - self.rect.width
                if 4 in d.get('p1'): self.rect.x = w.rect.right
        if i == 2: self.rect[1] = min(self.rect[1] + speed, s.size[1] - self.rect[3])
        if i == 8: self.rect[1] = max(self.rect[1] - speed, 0)
        aw = self.collide(*walls)
        if aw:
            for w in aw:
                if 2 in d.get('p1'): self.rect.y = w.rect.top - self.rect.height
                if 8 in d.get('p1'): self.rect.y = w.rect.bottom
a.direction = direct_a

a.rect[0:2] = 100, 100
b.rect[0:2] = 400, 200
c.rect[0:2] = 350, 180
t.regist(a)
t.regist(b)
t.regist(c)

s.regist(t) # 将场景 t 注入游戏
s.run()