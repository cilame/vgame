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
    # vgame.Theater.Camera.DEBUG = True

    # 资源加载
    i_bg0 = Image(bg0)
    i_ims = Image(ims, showsize=(40,40), rate=80)
    i_fsd = Image(fsd, showsize=(40,40), rate=60)
    i_fsu = Image(fsu, showsize=(40,40), rate=60)
    i_fsr = Image(fsr, showsize=(40,40), rate=60)
    i_fsl = Image(fsr, showsize=(40,40), rate=60, flip='x') # x水平翻转， y上下翻转，这里写入'xy' 则可以同时翻转
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
    theater_1.map.local(actor2, (3, 3), 1)


    actor4 = vgame.Enemy(i_fsl)
    theater_1.regist(actor4)
    theater_1.map.local(actor4, (12, 5), 2)

    # 第一排墙
    for i in range(0, 11):
        ac = vgame.Wall(showsize=(40, 40))
        theater_1.regist(ac)
        theater_1.map.local(ac, (5, i), 999) # map.local 的第三个参数为阻力
    # 第二排墙
    for i in range(5, 12):
        vgame.Wall(showsize=(40, 40)).map.local((8, i), float('inf'), theater_1) 
        # 这个 actor 有特殊的绑定了自身的 local 方法，是一种很 pythonic 的写作优化
        # 并且这个 local 函数如果你传入 theater ，那么函数内部还包含了 theater.regist 自动注册进场景
        # 所以这里非常简便，上面第一排墙初始化需要写三行固定顺序的代码，第二排墙初始化只需要一行就可以了
        # 注意 Player, NPC, Enemy, Wall 均继承于 Actor ，所以 Actor 能用的这些都能用
        # 所以在 Player 控制里面也能用同样的方式轻易调用转换

    actor2.map.local((13, 7), 1)
    # 按下J键自动寻路
    # 按下K键显示阻力图
    def _my_ctl(self, c):
        if c and c.get('p1')[0]:
            # trs = theater_1.map.trace(actor2, actor4) # 计算路径 actor2 到 actor4 的坐标路径
            # trs = theater_1.map.trace(actor2, (6, 6)) # 计算路径 actor2 到目标点的坐标路径
            # theater_1.map.move(actor2, trs[:-1], 3)

            # 与上面的方式同样的，但是更 pythonic 的方法，让 actor 内绑定自身去执行 theater 方法
            # self.map.local((13, 7), 1)
            trs = self.trace(actor4)
            self.map.move(trs[:-1], 3) # 速度为 0或者 inf则立即到达

        # 显示阻力图的功能
        global START
        if c and c.get('p1')[1] and not START: START = True; print(theater_1.map, end='\n\n')
        if not c: START = False
    START = False

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

