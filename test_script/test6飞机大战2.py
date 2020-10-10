# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame
import random

# vgame.DEBUG = True
# vgame.Map.DEBUG = True
path = '../test_data/fjdz/image'

vgame.Initer(size=(240, 430))
main = vgame.Theater(path+'/background.png')
pause = vgame.Theater(path+'/background.png')
death = vgame.Theater(path+'/background.png')
unpause = vgame.Button(vgame.Text('暂停')).local(pause, pause.background.rect.center)
restart = vgame.Button(vgame.Text('重开')).local(death, death.background.rect.center)

unpause.click = lambda: vgame.change_theater(main)
unpause.control = lambda self, c:unpause.click() if self.delay(c and c.get('p1')[1]) else None

def _restart():
    for i in main.Enemy: 
        i.kill()
        if i.status['bgbar']:i.status['bgbar'].kill()
        if i.status['hpbar']:i.status['hpbar'].kill()
    for i in main.Bullet: i.kill()
    label.text = 0
    vgame.change_theater(main)
    player.toggle(True)
    player.local(main, (120,400))
restart.click = _restart
restart.control = lambda self, c: _restart() if self.delay(c and c.get('p1')[1]) else None

bg_music = vgame.Music('../test_data/fjdz/music/game_music.wav', .2).play(-1)
bullet_player = vgame.Music('../test_data/fjdz/music/bullet.wav', .2)
enemy0_dplayer = vgame.Music('../test_data/fjdz/music/enemy0_down.wav', .3)

player_imgs = [
    path+'/hero1.png',
    path+'/hero2.png',
]
player = vgame.Player(player_imgs, rate=200, showsize=(50, 62)).local(main, (120,400))
player.direction = lambda self, d: self.mover.move(d.get('p1'), 6)
def control(self, c):
    if self.delay(c and c.get('p1')[0], time=100, repeat=True): create_bullet()
    if self.delay(c and c.get('p1')[1]): vgame.change_theater(pause)
player.control = control

enemy0_dead = [path+'/enemy0_down1.png',path+'/enemy0_down2.png',path+'/enemy0_down3.png',path+'/enemy0_down4.png',]
enemy1_dead = [path+'/enemy1_down1.png',path+'/enemy1_down2.png',path+'/enemy1_down3.png',path+'/enemy1_down4.png',]
enemy2_dead = [path+'/enemy1_down1.png',path+'/enemy1_down2.png',path+'/enemy1_down3.png',path+'/enemy1_down4.png',]
hero_blowup = [path+'/hero_blowup_n1.png',path+'/hero_blowup_n2.png',path+'/hero_blowup_n3.png',path+'/hero_blowup_n4.png',]
def enemy_creater(self):
    if self.delay(True, time=100, repeat=True):
        if random.randint(0, 10) <= 6:
            x, y, speed, enemysize, enemy_dead, score = random.randint(15, 220), 30, random.randint(2, 4), (25,20), enemy0_dead, 100
            enemy = vgame.Enemy(path+'/enemy0.png', showsize=enemysize).local(main, (x, y))
            enemy.status['hp'] = 3
            enemy.status['maxhp'] = 3
            enemy.status['bgbar'] = vgame.Anime((0,0,0), showsize=(enemy.showsize[0], 3)).local(main, (x, y-15))
            enemy.status['hpbar'] = vgame.Anime((0,255,0), showsize=(enemy.showsize[0], 3)).local(main, (x, y-15))
        elif random.randint(0, 10) <= 8:
            x, y, speed, enemysize, enemy_dead, score = random.randint(15, 220), 30, random.randint(2, 3), (35,45), enemy1_dead, 300
            enemy = vgame.Enemy(path+'/enemy1.png', showsize=enemysize).local(main, (x, y))
            enemy.status['hp'] = 7
            enemy.status['maxhp'] = 7
            enemy.status['bgbar'] = vgame.Anime((0,0,0), showsize=(enemy.showsize[0], 3)).local(main, (x, y-25))
            enemy.status['hpbar'] = vgame.Anime((0,255,0), showsize=(enemy.showsize[0], 3)).local(main, (x, y-25))
        elif random.randint(0, 10) <= 10:
            x, y, speed, enemysize, enemy_dead, score = random.randint(15, 220), 30, random.randint(1, 2), (60,100), enemy1_dead, 800
            enemy = vgame.Enemy(path+'/enemy2.png', showsize=enemysize).local(main, (x, y))
            enemy.status['hp'] = 25
            enemy.status['maxhp'] = 25
            enemy.status['bgbar'] = vgame.Anime((0,0,0), showsize=(enemy.showsize[0], 3)).local(enemy, offsets=(0,-60))
            enemy.status['hpbar'] = vgame.Anime((0,255,0), showsize=(enemy.showsize[0], 3)).local(enemy, offsets=(0,-60))
        else:
            return
        def idle(self):
            self.mover.move([2], speed)
            self.status['hpbar'].mover.move([2], speed)
            self.status['bgbar'].mover.move([2], speed)
            if self.outbounds():
                self.status['hpbar'].kill()
                self.status['bgbar'].kill()
                self.kill()
            v = self.collide(vgame.Bullet)
            if v:
                v[0].kill()
                self.status['hp'] -= 2
                if self.status['hp'] <= 0:
                    self.kill()
                    self.status['hpbar'].kill()
                    self.status['bgbar'].kill()
                    label.text += score
                    vgame.Anime(enemy_dead, rate=50, showsize=enemysize).local(main, self.rect.center)
                    enemy0_dplayer.play()
                else:
                    if self.status['hpbar']: 
                        barlen = int(self.status['hp']*self.showsize[0]/self.status['maxhp'])
                        color = (0,255,0) if barlen/self.showsize[0] > 0.3 else (255,0,0)
                        self.status['hpbar'].imager = vgame.Image(color, showsize=(barlen, 3))
            v = self.collide(vgame.Player)
            if v:
                self.status['hpbar'].kill()
                self.status['bgbar'].kill()
                v[0].kill(); self.kill()
                anime = vgame.Anime(hero_blowup, rate=50, showsize=(50, 62)).local(main, v[0].rect.center)
                anime.endanime = lambda: vgame.change_theater(death) # 死亡动画播放完后执行的函数
        enemy.idle = idle
        enemy.in_entity = False

label = vgame.Button(vgame.Text(0, textside='r', textwidth=150, textcolor=(255,0,0), textformat='分数:{:>3d}', textscale=2)).local(main, (160,15))
label.idle = enemy_creater

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
    def three(): one(-15,-15) or one(0) or one(15,15)
    def five(): one(-20,-20) or one(-10,-10) or one(0,0) or one(10,10) or one(20,20)
    # one(0) # 单发
    five()