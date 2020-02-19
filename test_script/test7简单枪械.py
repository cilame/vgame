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
a.rect[0:2] = 100, 100
b.rect[0:2] = 400, 200
c.rect[0:2] = 200, 200
t.regist(a, b, c)

font = vgame.font.SysFont("simhei", 15)
hp = 1000
boss = vgame.Actor(font.render('boss HP: {:>4}'.format(hp), 3, (255,255,255)), in_physics=False)
operate = vgame.Actor(font.render('操作说明：A(左)D(右)J(跳跃/二段跳)K(发射子弹)L(切换枪械)', 3, (255,255,255)), in_physics=False)
guninfo = vgame.Actor(font.render('当前枪械:pistol', 3, (255,255,255)), in_physics=False)
boss.rect[0:2] = 150, 150
operate.rect[0:2] = 100, 100
guninfo.rect[0:2] = 100, 80
t.regist(boss, operate, guninfo)

import random
# 创建子弹，并对子弹的运行进行编辑
def create_bullet(self,speed_inc_x,speed_inc_y,speed_max_x,speed_max_y,target_y):
    bullet = vgame.Actor(showsize=(6,6), in_physics=False)
    bullet.rect[:2] = self.rect.center
    bullet.physics.speed_inc.x = speed_inc_x
    bullet.physics.speed_max.x = speed_max_x
    bullet.physics.speed_inc.y = speed_inc_y
    bullet.physics.speed_max.y = speed_max_y
    def bullet_move(self):
        global hp
        # 子弹碰撞到墙自动消失
        for i in self.collide(*walls): self.kill() 
        # 子弹碰撞到大方块也会消失不过让大方块进行颜色的随机变化
        # 这里的处理仅供演示，后续会有更加方便的角色状态转移的处理
        for i in self.collide(b):
            i.imager.image = i.imager.load_img([random.randint(0,255) for i in range(3)])
            hp -= 1
            boss.imager.image = boss.imager.load_img(font.render('boss HP: {:>4}'.format(hp), 3, (255,255,255)))
            i.physics.smooth_speed.x = 1
            i.physics.move([6])
            if hp <= 0: i.kill()
            self.kill() 
        # 子弹超过边界自动消失
        if self.rect.x > self.theater.artist.screen.get_rect().width: self.kill()
        target = [6, target_y]
        self.physics.move2(target)
    bullet.idle = bullet_move
    self.theater.regist(bullet)
class Delayer:
    def __init__(self, delay=60):
        self.delay = delay # 子弹速度的控制
        self.tick = 0
    def delaying(self, ticks):
        if ticks - self.tick > self.delay:
            self.tick = ticks
            return True
class Weapon:
    def __init__(self, delay, speed_inc_x, speed_inc_y, speed_max_x, speed_max_y, times):
        self.dly = Delayer(delay)
        self.inc_x, self.inc_y, self.max_x, self.max_y = speed_inc_x, speed_inc_y, speed_max_x, speed_max_y
        self.times = times
    def create_random_bullet(self, actor):
        if self.dly.delaying(actor.ticks):
            for i in range(self.times):
                create_bullet(actor, self.inc_x, self.inc_y, self.max_x, self.max_y*random.random(), random.choice([8,2]))
# 测试一下生成枪械
pistol = Weapon(150,3,1,15,1,1)
fan    = Weapon(200,2,2,8,5,7)
gatlin = Weapon(15,2,.05,8,5,1)

from itertools import cycle
guns = [pistol,fan,gatlin]
gunsn = ['pistol','fan','gatlin']
_guns = cycle(guns)

# 默认枪械
gun = pistol
dly = Delayer(200) # 换枪键的响应延迟
def direct_a(self, d, c):
    global gun
    q = d.get('p1')
    if d and 8 in q: q.remove(8) # 去除 w 键的跳跃消息，改用下面的 J 键响应
    if c and c[1][0]: q = [] if q is None else q; q.append(8) # J 键跳跃
    if c and c[1][1]: gun.create_random_bullet(self) # K 键射出子弹
    if c and c[1][2]: # L 键切枪
        if dly.delaying(self.ticks):
            gun = next(_guns)
            guninfo.imager.image = guninfo.imager.load_img(font.render('当前枪械:{}'.format(gunsn[guns.index(gun)]), 3, (255,255,255)))
    self.physics.move2(q)
# 操作系统的初始化
a.direction = direct_a
a.controller.control_keys = [vgame.K_j, vgame.K_k, vgame.K_l]

# 主角的物理系统初始化
a.physics.gravity.y = 5 # y方向设置后自动变成重力系统（可以有负数）
a.physics.limit_highs = {8:80} # 起跳后的最大高度（80像素）
a.physics.jump_times = {8:2}   # 没有落到地面前最大跳跃次数（二段跳）
a.physics.speed_inc.x = 4 # 加速度
a.physics.speed_dec.x = 2 # 减速度，这里仅影响x方向，因为y方向用了重力系统，这个参数只影响摩擦系统（摩擦）
a.physics.speed_max.x = 6 # x方向的最大速度
a.physics.speed_max.y = 8 # y方向的最大速度

def check_a_is_dead(self):
    if self.rect.y > self.theater.artist.screen.get_rect().height:
        self.kill()
        self.theater.artist.change_theater('end')
a.idle = check_a_is_dead
b.idle = lambda self,d: self.physics.move2([2])

# 墙体
wd = vgame.Actor(showsize=(600,10))
wu = vgame.Actor(showsize=(500,10))
wl = vgame.Actor(showsize=(10,300))
wr = vgame.Actor(showsize=(10,300))
wd.rect[0:2] = 100, 400
wu.rect[0:2] = 100, 10
wl.rect[0:2] = 600, 100
wr.rect[0:2] = 30, 100
walls = [wd,wu,wl,wr]
t.regist(*walls)

e = vgame.Theater('end')
end = vgame.Actor(font.render('游戏结束', 3, (255,255,255)), in_physics=False)
end.rect[0:2] = 300, 200
e.regist(end)

s.regist(t) # 将场景 t 注入游戏
s.regist(e) # 注册游戏结束画面
s.run()