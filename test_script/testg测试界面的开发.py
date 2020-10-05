# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame
from vgame import Initer, Theater, Actor, Image, Menu

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
    theater_1.map.local(actor2, (7, 9), 1)


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
        vgame.Wall(showsize=(40, 40)).map.local(theater_1, (8, i), float('inf'))
        # 这个 actor 有特殊的绑定了自身的 local 方法，是一种很 pythonic 的写作优化
        # 并且这个 local 函数如果你传入 theater ，那么函数内部还包含了 theater.regist 自动注册进场景
        # 所以这里非常简便，上面第一排墙初始化需要写三行固定顺序的代码，第二排墙初始化只需要一行就可以了
        # 注意 Player, NPC, Enemy, Wall 均继承于 Actor ，所以 Actor 能用的这些都能用
        # 所以在 Player 控制里面也能用同样的方式轻易调用转换

    # 按下J键自动寻路
    # 按下K键显示阻力图
    def _my_ctl(self, c):
        if self.delay(c and c.get('p1')[0], delayer='A'):
            self.map.move(self.map.trace(actor4)[:-1], 10) # 速度小于 0或者 inf则报错，需要即刻到达的处理请直接使用 local 函数

        # # 显示阻力图的功能
        # if c and c.get('p1')[1]:
        #     # delay 的默认值是 150(毫秒), 这个值比较适合一般人的操作延迟
        #     # 另外这个延迟判断函数一定要写在接收到控制信息后再使用，否则有可能在按下的瞬间无效（虽然长按时间隔仍旧一样，但是非常影响操作体验）。
        #     # 还有另一种更pythonic 的写法就是用 delay 方法
        #     if self.delay():
        #         print(theater_1.map, end='\n\n')

        # 显示阻力图的功能，和上面注释部分相同功能
        if self.delay(c and c.get('p1')[1], delayer='B', time=0, repeat=False):
            print(theater_1.map, end='\n\n')

            m.toggle() # 元素显示或隐藏


        # 另外这个 delay 函数使用的都是 Actor 内部自带的一个延迟器，所以
        # 如果你想在一个Actor里面使用多个延迟器则只需要在这两个函数里面多设置一个延迟器 delayer 的名字，而且是一定要设置，否则就会有奇怪的问题
        # Actor会根据名字自动创建延迟器并使用它
        # 另外对于一些功能而言需要连发，将 repeat 设置成True即可按照time(毫秒)参数进行连发设置，而默认情况下时并不连发的

    def _my_move(self, d):
        dr = d.get('p1')
        if dr:
            self.mover.move(dr)
    actor2.control = _my_ctl
    actor2.direction = _my_move


    m = Menu(showsize=(80,80))
    theater_1.regist_menu(m)

    # print(main.size/2)


    main.regist(theater_1)
    main.run() # 启动一切

