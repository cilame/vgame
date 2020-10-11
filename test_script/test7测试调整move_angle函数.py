# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame
vgame.DEBUG = True

path = '../test_data/fjdz/image'

vgame.Initer()
main = vgame.Theater(path+'/background.png')
player_imgs = [
    path+'/hero1.png',
    path+'/hero2.png',
]
player = vgame.Player(player_imgs, rate=200, showsize=(50, 62)).local(main, (120,400))
player.direction = lambda self, d: self.mover.move(d.get('p1'), 6)
def control(self, c):
    if self.delay(c and c.get('p1')[0], time=50, repeat=True): create_bullet()
    if self.delay(c and c.get('p1')[1], time=50, repeat=True): 
        for idx, i in enumerate(main.Bullet):
            print(idx, i)
            i.rect[:2] = 100,100
player.control = control



bullet_player = vgame.Music('../test_data/fjdz/music/bullet.wav', .2)
def create_bullet():
    x, y = player.rect.center
    def one(dx, ag=0, dy=0):
        bullet = vgame.Bullet(path+'/bullet1.png', showsize=(4, 10)).local(main, (x+dx, y-15))
        def idle(self):
            if self.outbounds():
                self.kill()
            self.mover.move_angle(ag-90, 10)
        bullet.idle = idle
        bullet_player.play()
    def two(): one(-10) or one(10)
    def three(): one(-15,-45) or one(0) or one(15,45)
    def five(): one(-20,-20) or one(-10,-10) or one(0,0) or one(10,10) or one(20,20)
    # one(0) # 单发
    three()
    # five()