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

main = vgame.Theater((0,0,0)).draw.rect((255,255,255), 5, 3)
btn1 = vgame.Button(vgame.Text('一号场景', (255,255,255))).local(main, offsets=(0, -15))
btn1.click = lambda: vgame.change_theater(main2)

main2 = vgame.Theater((0,0,0)).draw.rect((255,255,255), 5, 3)
btn2 = vgame.Button(vgame.Text('二号场景', (255,255,255))).local(main2, offsets=(0, -15))
btn2.click = lambda: vgame.change_theater(main)