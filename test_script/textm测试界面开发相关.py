# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)





import vgame
# vgame.DEBUG = True
# vgame.Menu.DEBUG = True

vgame.Initer()

main = vgame.Theater('main', (0,0,0)).draw.rect((255,255,255), 5, 3)
btn = vgame.Button(vgame.Text('开始游戏', (255,255,255))).local(main, offsets=(0, -15))
btn = vgame.Button(vgame.Text('保存游戏', (255,255,255))).local(main, offsets=(0, 15))

