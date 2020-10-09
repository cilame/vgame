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
    vgame.Theater.Map.DEBUG = True # 打开地图栅格调试

    # 资源加载
    i_bg0 = Image(bg0)
    i_ims = Image(ims, showsize=(40,40), rate=80)
    i_fsd = Image(fsd, showsize=(30,30), rate=60)
    i_fsu = Image(fsu, showsize=(30,30), rate=60)
    i_fsr = Image(fsr, showsize=(30,30), rate=60)
    i_fsl = Image(fsr, showsize=(30,30), rate=60, flip='x')
    i_fra = Image(fra, showsize=(30,30), rate=60)

    theater_1 = Theater(i_bg0)
    actor2 = vgame.Player(i_fsd)
    actor2.mover.speed.x = 4.
    actor2.mover.speed.y = 4.
    actor2.status['dirct'] = {
        'u': i_fsu,
        'd': i_fsd,
        'r': i_fsr,
        'l': i_fsl,
        'a': i_fra,
        'dict': {
            0: i_fsd,
            1: None,
        },
    }
    actor2.rect[0], actor2.rect[1] = 100, 100
    theater_1.regist(actor2)
    # theater_1.camera.follow = actor2 # 
    theater_1.map.local(actor2, (3, 3))




    actor3 = vgame.Wall(i_ims)
    theater_1.regist(actor3)
    theater_1.map.local(actor3, (9, 9))

    actor4 = vgame.Enemy(i_fsl)
    theater_1.regist(actor4)
    theater_1.map.local(actor4, (12, 6))
    main.regist(theater_1)

    def _my_move(self, d):
        dr = d.get('p1')
        if dr:
            if 4 in dr or 6 in dr:
                if 4 in dr: self.status['dirct']['dict'][0] = self.status['dirct']['l']
                if 6 in dr: self.status['dirct']['dict'][0] = self.status['dirct']['r']
            else:
                if 2 in dr: self.status['dirct']['dict'][0] = self.status['dirct']['d']
                if 8 in dr: self.status['dirct']['dict'][0] = self.status['dirct']['u']
            self.mover.move(dr)

    def _my_ctl(self, c):
        ct = c.get('p1')
        close = False
        if ct:
            if ct[0]:
                if not self.status['dirct']['dict'][1]:
                    self.status['dirct']['dict'][1] = self.status['dirct']['a']
            else: close = True
        else: close = True
        if close:
            if self.status['dirct']['dict'][1]: self.status['dirct']['dict'][1] = None

    def _my_idle(self):
        if self.status['dirct']['dict'][1]:
            self.aload_image(self.status['dirct']['dict'][1])
        elif self.status['dirct']['dict'][0]:
            self.aload_image(self.status['dirct']['dict'][0])

    actor2.direction = _my_move
    actor2.control = _my_ctl
    actor2.idle = _my_idle

    main.run() # 启动一切

