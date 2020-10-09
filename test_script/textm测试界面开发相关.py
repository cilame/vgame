# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)





import vgame
vgame.DEBUG = True
vgame.Menu.DEBUG = True

vgame.Initer()

main = vgame.Theater('main', (0,0,0)).draw.rect((255,255,255), 5, 3)
# main.background.draw.rect((255,255,255), 5, 3)


# draw.rect((255,255,255), 3, 2)
print(main)

menu = vgame.Menu((100,100,100)).init(main, grid=(9,9))
btn = vgame.Button(vgame.Text('开始游戏', (255,255,255)))

menu.local()
