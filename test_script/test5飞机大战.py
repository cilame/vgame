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
main = vgame.Theater()


player = vgame.Player(showsize=(80,100)).local(main, offsets=(0, 180))
score = 0
txt = vgame.Text(str(score), textcolor=(255,0,0), textscale=2)
label = vgame.Enemy(txt).local(main, (100, 100), )


bullets = []
def enemycreater(self):
    if self.delay(True, time=100, repeat=True):
        x = random.randint(40,600)
        e = vgame.Enemy((0,255,5), showsize=(32,32), in_bounds=False).local(main, (x, 0))
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
            if self.outbounds():
                self.kill()
        e.idle = idle
        main.regist(e)

label.idle = enemycreater

def direct(self, d):
    if d:
        self.mover.move(d.get('p1'), 20)

def ctl(self, c):
    if self.delay(c and c.get('p1'),repeat=True,time=0):
        def idle(self):
            self.mover.move([8], 7)
            if self.outbounds():
                self.kill()
        b = vgame.Bullet(showsize=(10, 10), showpoint=self.rect.center, in_bounds=False)
        b.idle = idle
        bullets.append(b)
        main.regist(b)

player.direction = direct
player.control = ctl
