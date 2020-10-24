# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)





import vgame
# vgame.DEBUG = True
vgame.Menu.DEBUG = True
vgame.Map.DEBUG = True

vgame.Initer()

main = vgame.Theater((0,0,0)).draw.rect((255,255,255), 5, 3)
menu = vgame.Menu(grid=(9,9), showsize=(main.size[0]-50,200-50)).local(main, offsets=(0,140))
player = vgame.Player(showsize=(40,20)).menu.local(menu, (1,1))

maps = vgame.Map(grid=(9,9), showsize=(main.size[0]-200,200-50)).local(main, offsets=(0,-140))
vgame.Enemy(showsize=(30, 10)).map.local(maps, (3, 3), 2)
vgame.Enemy(showsize=(30, 10)).map.local(maps, (3, 4), 2)
vgame.Enemy(showsize=(30, 10)).map.local(maps, (3, 5), 2)
enemy = vgame.Enemy(showsize=(30, 10)).map.local(maps, (8, 8), 2)
player = vgame.Player(showsize=(30, 15)).map.local(maps, (4, 5), 1)


def ctl(self, c):
    if self.delay(c and c.get('p1')[0]):
        print(maps)
        print(self.map.trace(enemy))

        self.status['trace'] = self.status.get('trace') or []
        for i in self.status['trace']:
            i.kill()
        for i in self.map.tracelimit(4):
            t = vgame.Anime((255,0,0,100), showsize=maps.gridsize).map.local(maps, i)
            self.status['trace'].append(t)

        print(maps)
        self.rotate += 20

player.direction = lambda self, d:self.mover.move(d.get('p1'))
player.control = ctl