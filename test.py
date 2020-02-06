#from vgame import artist
from vgame import Initer, Theater, Actor

if __name__ == "__main__":
    bg1 = 'test_data/sushiplate.jpg'
    bg2 = 'test_data/sea.jpg'
    cur = 'test_data/sprite_100x100_32.png'

    # 测试时使用 c 键切换场景
    # 测试时使用 q 键删除对象

    main = Initer(60) # 第一个参数为全局秒帧率，默认60

    # 场景一
    theater_0 = Theater(bg1, '123') # theater 必须要指定两个元素，1背景图片资源地址，2舞台名字
    actor1 = Actor(cur, showsize=(40,40), in_control=True) # in_control 负责接收控制指令，目前控制指令只会打印相关的操作内容
    theater_0.regist(actor1) # 动作者注册进场景才能使用
    main.regist(theater_0) # 场景需要注册进初始对象才能使用

    # 场景二
    theater_1 = Theater(bg2, 'sea') # theater 必须要指定两个元素，1背景图片资源地址，2舞台名字
    actor2 = Actor(cur, showsize=(80,80), in_control=True)
    theater_1.regist(actor2)
    main.regist(theater_1)


    main.change_theater('sea') # 可以通过舞台名字进行场景的切换

    main.run() # 启动一切

