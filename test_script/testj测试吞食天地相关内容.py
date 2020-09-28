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

init = vgame.Initer()
main = vgame.Theater('main', gridsize=(32, 32))






print(main.gridsize)
gy = '../test_data/fc吞食天地素材/行走图/关羽.png'
vgame.Image(gy)
imake = vgame.ImageMaker(gy)
s = imake.gridcut((32, 32))
p = []
for i in range(int(len(s)/4)):
    v = s[i*4:(i+1)*4]
    p.append(v)

playerimg_u = vgame.Image(p[3], rate=200, showsize=(32,32))
playerimg_d = vgame.Image(p[0], rate=200, showsize=(32,32))
playerimg_r = vgame.Image(p[2], rate=200, showsize=(32,32))
playerimg_l = vgame.Image(p[1], rate=200, showsize=(32,32))
player = vgame.Player(playerimg_d, rectsize=(32, 32)).map.local((1,1), 10, main)
player.status['direction']['up']    = playerimg_u
player.status['direction']['down']  = playerimg_d
player.status['direction']['right'] = playerimg_r
player.status['direction']['left']  = playerimg_l

def direct(self, d):
    if d: self.map.direct(d.get('p1'), 7)
player.direction = direct

atk = '../test_data/fc吞食天地素材/战斗_头像图/攻击图1.png'
imake = vgame.ImageMaker(atk)
s = imake.gridcut((192, 192))
playerimg_a_right = vgame.Image(s[8:10], rate=200, showsize=(192,192), offsets=(-80,80))
playerimg_a_left  = vgame.Image(s[8:10], rate=200, showsize=(192,192), offsets=(80,80), flip='x')
player.status['direction']['atkr'] = playerimg_a_right
player.status['direction']['atkl'] = playerimg_a_left
def ctl(self, c):
    if self.delay(c and c.get('p1')[0], delayer='A'):
        self.aload_image(self.status['direction']['atkr'])
    if self.delay(c and c.get('p1')[1], delayer='B'):
        self.aload_image(self.status['direction']['atkl'])

player.control = ctl


init.run()
