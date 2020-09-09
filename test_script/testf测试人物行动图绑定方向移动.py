# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame
from vgame import Initer, Theater, Actor, Image

if __name__ == "__main__":
    bg0 = '../test_data/sea.jpg'
    ims = '../test_data/e1'
    fsd = '../test_data/fish/down'
    fsu = '../test_data/fish/up'
    fsr = '../test_data/fish/right'
    fra = '../test_data/fish/right_attck1'

    main = Initer()
    vgame.DEBUG = True # 调试模式
    # vgame.Theater.Map.DEBUG = True # 打开地图栅格调试
    # vgame.Theater.Camera.DEBUG = True

    # 资源加载
    i_bg0 = Image(bg0)
    i_ims = Image(ims, showsize=(40,40), rate=80)
    i_fsd = Image(fsd, showsize=(40,40), rate=60)
    i_fsu = Image(fsu, showsize=(40,40), rate=60)
    i_fsr = Image(fsr, showsize=(40,40), rate=60)
    i_fsl = Image(fsr, showsize=(40,40), rate=60, flip='x')
    i_fra = Image(fra, showsize=(40,40), rate=60)

    theater_1 = Theater('sea', i_bg0, gridsize=(40, 40))
    actor2 = vgame.Player(i_fsd)
    actor2.status['direction'] = { 
        'up':    i_fsu,
        'down':  i_fsd,
        'right': i_fsr,
        'left':  i_fsl,
    }
    theater_1.regist(actor2)
    theater_1.map.local(actor2, (3, 3))


    actor4 = vgame.Enemy(i_fsl)
    theater_1.regist(actor4)
    theater_1.map.local(actor4, (12, 6))

    for i in range(0, 10):
        ac = vgame.Wall(showsize=(40, 40))
        theater_1.regist(ac)
        theater_1.map.local(ac, (5, i), float('inf')) # map.local 的第三个参数为阻力
    for i in range(5, 12):
        ac = vgame.Wall(showsize=(40, 40))
        theater_1.regist(ac)
        theater_1.map.local(ac, (8, i), float('inf'))

    # 按下J键自动寻路
    def _my_ctl(self, c):
        if c and c.get('p1')[0]:
            trs = theater_1.map.trace(self, actor4) # 计算路径 actor2 到 actor4 的坐标
            theater_1.map.move(self, trs, 3)

    print(actor2.axis)
    print(actor4.axis)
    def _my_move(self, d):
        dr = d.get('p1')
        if dr:
            self.mover.move(dr)
    actor2.control = _my_ctl
    actor2.direction = _my_move

    main.regist(theater_1)
    main.run() # 启动一切

