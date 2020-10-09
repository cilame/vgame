# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame
# vgame.DEBUG = True
# vgame.Map.DEBUG = True



s = vgame.Initer()
main = vgame.Theater()

labeler = vgame.Player(vgame.Text('J键修改数字', (255,0,0), 2, textwidth=300, textside='r')).map.local(main, (0, 0))
player = vgame.Player(vgame.Text('0', (255,0,0), 2, textwidth=150, textside='r')).map.local(main, (10,10))

nums = {'v': 0}
def ctl(self, c):
    if self.delay(c and c.get('p1')[0]):
        nums['v'] += 1
        player.text = nums['v']
        labeler.text = '开始点击'

player.control = ctl


# s.run()