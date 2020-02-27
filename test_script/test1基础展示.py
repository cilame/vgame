# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame
from vgame import Initer, Theater, Actor, Image

if __name__ == "__main__":
    bg1 = '../test_data/sushiplate.jpg'
    bg2 = '../test_data/sea.jpg'
    cur = '../test_data/sprite_100x100.png'
    som = '../test_data/niu_56x85.png'

    ims = '../test_data/e1' # 文件夹也可以通过 Image 对象进行加载
    fsd = '../test_data/fish/down'
    fsu = '../test_data/fish/up'
    fsr = '../test_data/fish/right'
    fra = '../test_data/fish/right_attck1'

    # 测试时使用 TAB 键切按一定的顺序换场景 # 该功能仅为测试用

    main = Initer(120) # 核心类负责游戏的启动，必须在最前面，否则连资源加载都做不到，
    # 第一个参数为全局秒帧率，默认60

    vgame.Actor.DEBUG = True

    # 资源加载 # 动图和非动图均可，动图需要
    i_bg1 = Image(bg1)
    i_bg2 = Image(bg2)
    i_cur = Image(cur, showsize=(50,50), rate=60) # 动图需要填写速率，否则会很鬼畜
    i_som = Image(som, showsize=(80,80), rate=60)
    i_ims = Image(ims, rate=60)
    i_fsd = Image(fsd, rate=60)
    i_fsu = Image(fsu, rate=60)
    i_fsr = Image(fsr, rate=60)
    i_fra = Image(fra, rate=60)

    # 场景一
    theater_0 = Theater('sky', i_bg1) # theater(舞台) 必须要指定两个元素，1背景图片资源，2舞台名字
    actor1 = Actor(i_cur, in_control=True) # in_control 负责接收控制指令，目前控制指令只会打印相关的操作内容
    theater_0.regist(actor1) # actor(演员) 需要注册进场景才能使用
    actor1.direction = lambda info: print('morse_info', info) if info else None # 方向键操作的回调 hook
    actor1.mouse     = lambda info: print('direc_info', info) if info else None # 鼠标键操作的回调 hook
    actor1.control   = lambda info: print('cntro_info', info) if info else None # 功能键操作的回调 hook
    main.regist(theater_0) # threater(舞台) 需要注册进初始对象才能使用

    # 场景二
    theater_1 = Theater('sea', i_bg2) # theater(舞台) 必须要指定两个元素，1背景图片资源，2舞台名字
    actor2 = Actor(i_fra, in_control=True)
    actor3 = Actor(i_fsd)
    actor4 = Actor(i_fsr)
    actor2.rect[0], actor2.rect[1] = 100, 100
    actor3.rect[0], actor3.rect[1] = 300, 300
    actor4.rect[0], actor4.rect[1] = 400, 200
    theater_1.regist(actor2)
    theater_1.regist(actor3)
    theater_1.regist(actor4)
    main.regist(theater_1)

    main.change_theater('sea') # 可以通过舞台名字直接进行场景切换

    # 一个简单的角色的控制处理的模板
    # 这里的处理可以很方便的使用默认的操作消息，通过修改默认处理消息的函数就能利用这些操作消息
    # 下面就是鼠标、方向键、功能键的操作消息的处理，不修改则默认打印消息内容
    # 1修改 actor2 的方向键的挂钩操作处理 # 用小键盘的方向数字描述上下左右
    def my_direction(m):
        d = 5
        for i in m.get('p1') or []:
            if i == 8: actor2.rect[1] = actor2.rect[1] - d
            if i == 2: actor2.rect[1] = actor2.rect[1] + d
            if i == 4: actor2.rect[0] = actor2.rect[0] - d
            if i == 6: actor2.rect[0] = actor2.rect[0] + d
    # 2修改 actor2 鼠标处理，下面的功能是用鼠标拖动角色对象
    minfo1 = None
    minfo2 = None
    def my_mouse(m):
        global minfo1, minfo2
        if m and m[1] == 2:
            x,y,w,h = actor2.rect
            sx,sy = m[2][0]
            ex,ey = m[2][1]
            minfo1,minfo2 = ((sx,sy),(x, y, w, h)) if minfo1 != (sx,sy) else (minfo1,minfo2)
            if ( (sx >= minfo2[0] and sx <= minfo2[0] + minfo2[2]) and 
                 (sy >= minfo2[1] and sy <= minfo2[1] + minfo2[3]) ):
                dx,dy = minfo1[0] - minfo2[0], minfo1[1] - minfo2[1]
                actor2.rect[0] = ex - dx
                actor2.rect[1] = ey - dy
    # 3修改需要的控制键，默认使用的key是 jk
    actor2.controller.control_keys_p1 = [vgame.K_j, vgame.K_k, vgame.K_l]
    def my_control(c):
        if c:
            j,k,l = c.get('p1')
            if any(c.get('p1')):
                print('------control------')
                if j: print('j')
                if k: print('k')
                if l: print('l'); actor2.kill() # 测试按下l键删除自身(需要先在控制键列表里面增加键位)
    def idle():
        # 可以通过这样实现碰撞检测，collide 函数的参数可以传递无限的 actor 对象
        # 返回的结果是与 actor2 碰撞的 actor 列表，可以同时有多个碰撞
        # 碰撞检测一定要写在这里，因为这里的函数会一直执行，
        # 而如果你把检测碰撞写在操作函数中，那么碰撞检测只会在接收到操作的时候才会执行
        r = actor2.collide(actor3, actor4)
        for i in r: i.kill() 
    actor2.direction = my_direction
    actor2.mouse = my_mouse
    actor2.control = my_control
    actor2.idle = idle
    # actor2.rect        # 可以用 rect    参数获取当前对象的坐标和大小
    # actor2.kill()      # 可以用 kill    函数来删除掉这个对象
    # actor2.collide(*a) # 可以用 collide 函数来获取与 actor2 碰撞的其他 actor 对象

    main.run() # 启动一切

