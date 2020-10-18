# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame
from vgame import Initer, Theater, Actor, Image

bg0 = '../test_data/sea.jpg'
ims = '../test_data/e1'
fsd = '../test_data/fish/down'
fsu = '../test_data/fish/up'
fsr = '../test_data/fish/right'
fra = '../test_data/fish/right_attck1'

Initer()
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

main = Theater(i_bg0)
player = vgame.Player(i_fsd)
player.status['direction'] = { 
    'up':    i_fsu,
    'down':  i_fsd,
    'right': i_fsr,
    'left':  i_fsl,
}
player.local(main)
player.direction = lambda self, d: self.mover.move(d.get('p1'))