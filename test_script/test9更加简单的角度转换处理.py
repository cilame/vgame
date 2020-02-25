# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)





# 对于一些子弹的功能来说，直接使用平滑的移动，使用角度处理即可
# 完全没有必要对一些子弹加上各种物理量来处理，子弹的移动就用最简单的处理方式即可。
import vgame

s = vgame.Initer()
t = vgame.Theater('main')

p1 = vgame.Player(showpoint=(100, 100))
p2 = vgame.Player((255,0,0),showpoint=(100, 200))
b = vgame.Wall(showsize=(500, 20),showpoint=(100, 400))
c = vgame.Wall(showsize=(20, 20),showpoint=(400, 100))


def create_bullet(self):
    bullet = vgame.Bullet(showsize=(6,6))
    bullet.rect[:2] = self.rect.center
    curr_angle = self.angle(c)
    def bullet_move(self):
        self.physics.move_angle(curr_angle)
    bullet.idle = bullet_move
    self.theater.regist(bullet)

def control_a(self, cc):
    if cc and cc.get('p1'):
        if cc.get('p1')[1]:
            create_bullet(self)

def direction_a(self, d):
    self.physics.move2(d.get('p1'))

p1.control = control_a
p1.direction = direction_a
p1.controller.direction_keys_p1.up = vgame.K_j
p1.physics.limit_highs = {8:120}
p1.physics.jump_times = {8:2}
p1.physics.gravity.y = 3

def direction_p2(self, d):
    self.physics.move2(d.get('p2'))
p2.direction = direction_p2
p2.physics.gravity.y = 3


t.regist(p1, p2, b, c)
s.regist(t)
s.run()