#from vgame import artist
from vgame import Initer, Theater, Actor, Image

if __name__ == "__main__":
    bg1 = 'test_data/sushiplate.jpg'
    bg2 = 'test_data/sea.jpg'
    cur = 'test_data/sprite_100x100.png'
    som = 'test_data/some_56x85.png'

    # 测试时使用 c 键切换场景 # 该功能仅为测试用

    main = Initer(60) # 核心类负责游戏的启动，必须在最前面，否则连资源加载都做不到，
    # 第一个参数为全局秒帧率，默认60

    # 资源加载 # 动图和非动图
    i_bg1 = Image(bg1, showsize=(40,40))
    i_bg2 = Image(bg2, showsize=(40,40))
    i_cur = Image(cur, showsize=(40,40), rate=60) # 动图需要填写速率，否则会很鬼畜
    i_som = Image(som, showsize=(80,80), rate=60) # 动图需要填写速率，否则会很鬼畜

    # 场景一
    theater_0 = Theater(i_bg1, '123') # theater(舞台) 必须要指定两个元素，1背景图片资源，2舞台名字
    actor1 = Actor(i_cur, in_control=True) # in_control 负责接收控制指令，目前控制指令只会打印相关的操作内容
    theater_0.regist(actor1) # actor(演员) 需要注册进场景才能使用
    main.regist(theater_0) # threater(舞台) 需要注册进初始对象才能使用

    # 场景二
    theater_1 = Theater(i_bg2, 'sea') # theater(舞台) 必须要指定两个元素，1背景图片资源，2舞台名字
    actor2 = Actor(i_som, in_control=True)
    theater_1.regist(actor2)
    main.regist(theater_1)

    # 修改actor2的上下左右的操作处理
    def my_direction(m):
        d = 3
        for i in m:
            if i == 8: actor2.rect[1] -= d
            if i == 2: actor2.rect[1] += d
            if i == 4: actor2.rect[0] -= d
            if i == 6: actor2.rect[0] += d
    actor2.direction = my_direction

    main.change_theater('sea') # 可以通过舞台名字直接进行场景切换

    main.run() # 启动一切

