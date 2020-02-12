想要开发一个基于 pygame 的游戏框架。

后续会使用该框架开发一般类型的小游戏，根据开发过程的需求增加框架的功能，让框架鲁棒性更强。

目前可以通过 pip 进行下载

```bash
pip3 install vgame
```

一个简单的开始

```python
import vgame
s = vgame.Initer() # 该处对象的实例化时候，重要的参数有 fps（帧/秒,默认60）,title（标题,默认vgame）,size（屏幕分辨率,默认640x480）
s.run()
```

如何在游戏画面里面增加场景？增加一个可以移动的对象，以下代码不需要任何图片资源，直接就能运行

```python
import vgame
s = vgame.Initer()

t = vgame.Theater('main') # 先生成一个舞台，舞台需要指定一个名字
a = vgame.Actor(in_control=True, showsize=(40,90)) # 生成一个角色，in_control 设置为True可以让角色接收控制信息

# 游戏的背景核心就是 Theater(舞台)
#     Theater 对象的第二个参数可以是一个图像的地址
# 游戏的表演和兴就是 Actor(演员)
#     Actor 对象的第一个参数 img 可以是 None/tuple/vgame.Image 三种类型
#         当参数 img 是一个表示颜色的3/4个数字的元组，则生成一个该颜色的矩形方块，默认大小 60x60（第4个数字为透明度）
#         当参数 img 是 None 时候就代表表示颜色的4数字元组 (255,255,255,255) 情况下默认大小 60x60 的白色矩形。
#         当参数 img 是一个 vgame.Image 对象时，showsize 可以在该 Image 对象实例化的时候传入，并且 Actor 中的 showsize 将无效

def direction_a(m):
    # m 为接收 wasd 执行信号的参数，是一个最大两个数字的列表，是按下的方向的列表
    # 最多同时按下两个相邻的方向，如果按下超过2个方向，则 m 为空
    # 如果同时按下“左右”或同时按下“上下”则 m 也为空
    # 之所以是 8,2,4,6 的数字代表了方向，请看小键盘的数字键位即可明白。
    for i in m:
        if i == 8: a.rect[1] = max(a.rect[1] - 7, 0)
        if i == 2: a.rect[1] = min(a.rect[1] + 7, s.size[1] - a.rect[3])
        if i == 4: a.rect[0] = max(a.rect[0] - 7, 0)
        if i == 6: a.rect[0] = min(a.rect[0] + 7, s.size[0] - a.rect[2])
a.direction = direction_a # 将移动的函数覆盖默认的函数(这里的对象a必须在实例化时设置 in_control 为 True)

t.regist(a) # 将角色注入舞台t
s.regist(t) # 将舞台注入游戏s
s.run() # 开始游戏

# 有没有发现，上面的代码里面比起纯 pygame 有一个非常舒适的地方，
# 那就是你不用直接接触到键盘控制的部分，就不用写各种判断是不是 wasd 按键，而且
# 控制按键的最爽的地方就是你不用怕调整帧率会影像到执行的速度，因为哪怕你调整帧率到 200，信号速度都一样
# （除非你把帧率调整太低，否则，direction_a 函数执行的速度是固定的。这点非常爽。）
# 后续还有鼠标和控制键的处理方式，也很类似，以及一些非常方便的碰撞判断，请往后看。
```


