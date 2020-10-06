# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)




import random
import vgame

# vgame.DEBUG = True
# vgame.Map.DEBUG = True

init = vgame.Initer()
main = vgame.Theater('main')


player = vgame.Player(showsize=(80,100)).map.local(main, (10, 13))
score = 0
txt = vgame.Text(str(score), textcolor=(255,0,0), textscale=2)
label = vgame.Enemy(txt).map.local(main, (17, 0), )


bullets = []
def enemycreater(self):
    if self.delay(True, time=1000, repeat=True):
        x = random.randint(4,16)
        e = vgame.Enemy((0,255,5), showsize=(32,32), in_bounds=False).map.local(main, (x, 0))
        def idle(self):
            global score, bullets
            self.mover.move([2], 1)
            if self.collide(player):
                player.kill()
            bts = self.collide(*bullets)
            if bts:
                for i in bts:
                    i.kill()
                    self.kill()
                    score += 1
                    label.text = score
        e.idle = idle
        main.regist(e)

label.idle = enemycreater

def direct(self, d):
    if d:
        self.mover.move(d.get('p1'))

def ctl(self, c):
    if self.delay(c and c.get('p1'),repeat=True,time=0):
        def idle(self):
            self.mover.move([8], 7)
            if self.rect.x < 0:
                self.kill()
        b = vgame.Bullet(showsize=(10, 10), showpoint=self.rect.center, in_bounds=False)
        b.idle = idle
        bullets.append(b)
        main.regist(b)

player.direction = direct
player.control = ctl
