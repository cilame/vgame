# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)




import vgame
vgame.DEBUG = True
# vgame.Map.DEBUG = True

vgame.Initer()
main = vgame.Theater(size=(960, 720))
maps = vgame.Map(grid=(20,15), showsize=main.size).local(main)
label = vgame.Anime(vgame.Text('wasd控制,j跳跃k冲刺')).local(main)

player = vgame.Player((255,0,0), showsize=maps.gridsize).map.local(maps, (0, 14))

# 窗口大小由 Initer 配置
# 游戏内窗大小由 Theater 配置（如不配置默认随窗口大小）
player.follow(main, 20)

def direct(self, d):
    d = d.get('p1')
    if self.status['dash_toggle']:
        pass
    else:
        if d and 6 in d: self.status['speedx'] = 10
        if d and 4 in d: self.status['speedx'] = -10

def ctl(self, c, d):
    A = c and c.get('p1')[0]
    B = c and c.get('p1')[1]
    if self.delay(A):
        if self.status['jump_number']:
            self.status['jump_number'] -= 1
            self.status['speedy'] = 15
    if self.delay(B):
        if self.status['dash_number']:
            if d and d.get('p1'):
                self.status['dash_number'] -= 1
                self.status['dash_toggle'] = True
                x = y = 0
                if 8 in d.get('p1'): y = 32
                if 2 in d.get('p1'): y = -32
                if 6 in d.get('p1'): x = 32
                if 4 in d.get('p1'): x = -32
                self.status['dash_speedx'] = x
                self.status['dash_speedy'] = y
                self.status['speedx'] = 0
                self.status['speedy'] = 0

def idle(self):
    if self.status['dash_toggle']:
        self.mover.move([8], self.status['dash_speedy'])
        self.mover.move([6], self.status['dash_speedx'])
        if self.status['dash_speedy'] > 0: self.status['dash_speedy'] -= 4
        if self.status['dash_speedy'] < 0: self.status['dash_speedy'] += 4
        if self.status['dash_speedx'] > 0: self.status['dash_speedx'] -= 4
        if self.status['dash_speedx'] < 0: self.status['dash_speedx'] += 4
        if self.status['dash_speedx'] == 0 and self.status['dash_speedy'] == 0:
            self.status['dash_toggle'] = False
    else:
        self.mover.move([8], self.status['speedy'])
        self.mover.move([6], self.status['speedx'])
        if self.status['speedy'] > -9: self.status['speedy'] -= 1
        if self.status['speedy'] < -9: self.status['speedy'] = -9
        if self.status['speedx'] > 0: self.status['speedx'] -= 1
        if self.status['speedx'] < 0: self.status['speedx'] += 1

def bound(self, b):
    if b and b[0][1] == 'd': self.status['jump_number'] = self.status['jump_number_def']
    if b and b[0][1] == 'd': self.status['dash_number'] = self.status['dash_number_def']

player.direction = direct
player.control = ctl
player.status['speedx'] = 0
player.status['speedy'] = -9
player.status['jump_number'] = player.status['jump_number_def'] = 2 # 跳跃次数
player.status['dash_number'] = player.status['dash_number_def'] = 2 # 冲刺次数
player.status['dash_toggle'] = False
player.status['dash_speedx'] = 0
player.status['dash_speedy'] = 0
player.idle = idle
player.bound = bound
