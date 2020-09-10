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

    main = Initer(60)
    vgame.Actor.DEBUG = True # 调试模式

    # 资源加载
    i_bg0 = Image(bg0)
    i_ims = Image(ims, rate=80)
    i_fsd = Image(fsd, rate=60)
    i_fsu = Image(fsu, rate=60)
    i_fsr = Image(fsr, rate=60)
    i_fsl = Image(fsr, rate=60, flip='x')
    i_fra = Image(fra, rate=60)

    theater_1 = Theater('sea', i_bg0)
    actor2 = Actor(i_fsd, in_control=True)
    # actor2.mover.speed.x = 1.
    # actor2.mover.speed.y = 1.
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




    actor3 = vgame.Wall(i_ims)
    actor3.rect[0], actor3.rect[1] = 300, 300
    theater_1.regist(actor3)

    actor4 = vgame.Wall(i_fsl)
    actor4.rect[0], actor4.rect[1] = 400, 200
    theater_1.regist(actor4)
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

