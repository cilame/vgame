# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame

vgame.DEBUG = True
# vgame.Player.DEBUG = True
vgame.Map.DEBUG = True

# hywz = '../test_data/hywz/hywz.gif'
hywz = '../test_data/hywz/2.png'

init = vgame.Initer()
imake = vgame.ImageMaker(hywz)
s = imake.gridcut((64, 64))
p = []
for i in range(int(len(s)/3)):
    v = s[i*3:(i+1)*3]
    p.append(v)

main = vgame.Theater('main', gridsize=(64, 64))
playerimg_u = vgame.Image(p[1], rate=200, showsize=(120,120))
playerimg_r = vgame.Image(p[2], rate=200, showsize=(120,120))
playerimg_d = vgame.Image(p[3], rate=200, showsize=(120,120))
playerimg_l = vgame.Image(p[4], rate=200, showsize=(120,120))

player = vgame.Player(playerimg_d, rectsize=(64, 64))
player.status['direction'] = { 
    'up':    playerimg_u,
    'down':  playerimg_d,
    'right': playerimg_r,
    'left':  playerimg_l,
}
main.regist(player)
def direct(self, d):
    if d: 
        self.mover.move(d.get('p1'))

def ctl(self, c):
    if self.delay(c and c.get('p1')[0], time=150, delayer='A'):
        trs = self.map.trace((8, 6))
        self.map.move(trs, 10)
        print(trs)

    if self.delay(c and c.get('p1')[1], time=150, delayer='B'):
        print(self.map, end='\n\n')

enemy = vgame.Enemy(playerimg_d, rectsize=(64, 64))
enemy.map.local((8,6), 3, main)


player.direction = direct
player.control = ctl
player.map.local((1,1), 10)

for i in range(0, 5): vgame.Wall(showsize=(64, 64)).map.local((3, i), float('inf'), main) 
for i in range(3, 7): vgame.Wall(showsize=(64, 64)).map.local((6, i), float('inf'), main) 

init.run()