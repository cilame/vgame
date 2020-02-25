# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)





import vgame
import random
import time
s = vgame.Initer()
t = vgame.Theater('main')
f = vgame.font.SysFont("simhei", 15)
bullets = []
def direct_a(self, d): self.physics.move(d.get('p1'))
d = {}
d['starttime'] = time.time()
currtime = lambda:time.time() - d['starttime']
currlens = lambda:len(bullets)
n = vgame.Actor(f.render('游戏时间:{:.5f}'.format(currtime()), 3, (255,255,255)), in_entity=False)
l = vgame.Actor(f.render('当前数量:{}'.format(currlens()), 3, (255,255,255)), in_entity=False)
n.rect.x, n.rect.y, l.rect.x, l.rect.y = 200, 0, 200, 18
a = vgame.Actor(showsize=(20,20),in_control=True)
a.direction = direct_a
a.physics.smooth_speed[:2] = 3,3
a.rect[:2] = 310, 230
def create_enemy(self):
    if len(bullets) >= 80: return
    bullet = vgame.Actor(showsize=(6,6), in_entity=False)
    v = random.choice(('x','y'))
    if v == 'x': x, y = random.random()*640, random.choice([-10, 480])
    else:        y, x = random.random()*480, random.choice([-10, 640])
    bullet.rect[:2] = x, y
    x = 6 if (bullet.rect.x - a.rect.x) < 0 else 4
    y = 2 if (bullet.rect.y - a.rect.y) < 0 else 8
    bullet.physics.smooth_speed.x = random.choice([-4,-3,-2,-1,1,2,3,4])*.5
    bullet.physics.smooth_speed.y = random.choice([-4,-3,-2,-1,1,2,3,4])*.5
    target = [x, y]
    def bullet_shut(self):
        if ( self.rect.x < -30 or self.rect.x > 660 or self.rect.y < -20 or self.rect.y > 500):
            self.kill()
            if self in bullets: bullets.remove(self)
        self.physics.move(target)
    bullet.idle = bullet_shut
    bullets.append(bullet)
    t.regist(bullet)
    n.imager.image = n.imager.load_img(f.render('游戏时间:{:.5f}'.format(currtime()), 3, (255,255,255)))
    l.imager.image = l.imager.load_img(f.render('当前数量:{}'.format(currlens()), 3, (255,255,255)))
    if a.collide(*bullets):
        m.imager.image = m.imager.load_img(f.render('游戏结束(按J重新开始游戏)', 3, (255,255,255)))
        s.change_theater('end')
a.idle = create_enemy
m = vgame.Actor(f.render('游戏结束(按J重新开始游戏)', 3, (255,255,255)), in_entity=False, in_control=True)
def restart(self, option):
    global bullets
    if option.get('control') and option.get('control').get('p1')[0]:
        for i in bullets: i.kill()
        bullets = []
        d['starttime'] = time.time()
        s.change_theater('main')
m.idle = restart
m.rect[0:2] = 250, 200
e = vgame.Theater('end')

t.regist(a, n, l)
e.regist(m, n, l)
s.regist(t, e)
s.run()