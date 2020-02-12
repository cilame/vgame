想要开发一个基于 pygame 的游戏框架。

后续会使用该框架开发一般类型的小游戏，根据开发过程的需求增加框架的功能，让框架鲁棒性更强。

- ##### 游戏框架的安装

```bash
pip3 install vgame
```

- ##### 一个简单的开始

```python
import vgame
s = vgame.Initer() # 该处重要的参数 fps(帧/秒,默认60),title(标题,默认vgame),size(屏幕分辨率,默认640x480)
s.run()
```

- ##### 如何在游戏画面里面增加场景？增加一个可以移动的对象，以下代码不需要任何图片资源，直接就能运行

```python
import vgame
s = vgame.Initer()

t = vgame.Theater('main') # 先生成一个舞台，舞台需要指定一个名字
a = vgame.Actor(in_control=True, showsize=(40,90)) # 生成一个角色，in_control 设置为True可以让角色接收控制信息

# 游戏的背景核心就是 Theater(舞台)
#     Theater 对象的第二个参数是一个图像资源的对象 vgame.Image 对象。不填则为空背景，背景底色 (0,0,100)
# 游戏的表演核心就是 Actor(演员)
#     Actor 对象的第一个参数 img 可以是 None/tuple/vgame.Image 三种类型
#       当是表示颜色的3/4个数字的元组，则生成一个该颜色的矩形方块，默认大小 60x60（第4个数字为透明度）
#       当是 None 时候就代表表示颜色的4数字元组 (255,255,255,255) 情况下默认大小 60x60 的白色矩形。
#       当是 vgame.Image 对象时，showsize 可以在该 Image 对象实例化的时候传入，并且 Actor 中的 showsize 将无效

def direction_a(m):
    # m 为接收 wasd 执行信号的参数，是一个最大两个数字的列表，是按下的方向的列表
    # 最多同时按下两个相邻的方向，如果按下超过2个方向，则 m 为空
    # 如果同时按下“左右”或同时按下“上下”则 m 也为空
    # 之所以是 8,2,4,6 的数字代表了方向，请看小键盘的数字键位即可明白。
    print(m) # 你可以打印看看
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
# 那就是你不用直接接触到键盘控制的部分，就不用写各种判断是不是 wasd 按键，而且这里的处理
# 控制按键的最爽的地方就是你不用怕调整帧率会影响到执行的速度，因为哪怕你调整帧率到 200，信号速度都一样
# （除非你把帧率调整太低，否则，direction_a 函数执行的速度是固定的。这点非常爽。）
# 后续的样例代码还有鼠标和控制键的处理方式，也很类似，以及一些非常方便的碰撞判断，请往后看。
```

- ##### 实现对游戏角色的拖动、实现控制键的设置，代码很简单，如下。

```python
import vgame
s = vgame.Initer()

t = vgame.Theater('main') # 先生成一个舞台，舞台需要指定一个名字
a = vgame.Actor(in_control=True, showsize=(40,90))

# 设置鼠标拖拽对象的函数
# 这里硬编码了只能修改全局的Actor对象a，后面我会告诉你怎么让函数自动绑定被设置的对象，现在先就这样
def my_mouse(m):
    global minfo1, minfo2
    try:
        minfo1
    except:
        minfo1,minfo2 = None,None
    if m[1] == 2:
        x,y,w,h = a.rect
        sx,sy = m[2][0]
        ex,ey = m[2][1]
        minfo1,minfo2 = ((sx,sy),(x, y, w, h)) if minfo1 != (sx,sy) else (minfo1,minfo2)
        if ( (sx >= minfo2[0] and sx <= minfo2[0] + minfo2[2]) and 
             (sy >= minfo2[1] and sy <= minfo2[0] + minfo2[3]) ):
            dx,dy = minfo1[0] - minfo2[0], minfo1[1] - minfo2[1]
            a.rect[0] = ex - dx
            a.rect[1] = ey - dy
a.mouse = my_mouse # 覆盖默认的鼠标操作的函数(这里的对象a必须在实例化时设置 in_control 为 True)
# 设置新的接收控制键位，默认键位是 j,k
a.controller.control_keys = [vgame.K_j, vgame.K_k, vgame.K_l]
def my_control(c):
    j,k,l = c[1]
    print('------control------')
    if j: print('j')
    if k: print('k')
    if l: print('l'); a.kill() # 测试按下l键删除自身(需要先在控制键列表里面增加键位)
actor2.control = my_control

t.regist(a) # 将角色注入舞台t
s.regist(t) # 将舞台注入游戏s
s.run() # 开始游戏
```

- ##### 碰撞检测、场景切换

```python
import vgame
s = vgame.Initer() # 按键 ESC 关闭，TAB 测试切换场景

t = vgame.Theater('main')
a = vgame.Actor(in_control=True,showsize=(50,100))
b = vgame.Actor((255,0,0),showsize=(150,200))

# a 的操作
def direct_a(m):
    for i in m:
        if i == 8: a.rect[1] = max(a.rect[1] - 7, 0)
        if i == 2: a.rect[1] = min(a.rect[1] + 7, s.size[1] - a.rect[3])
        if i == 4: a.rect[0] = max(a.rect[0] - 7, 0)
        if i == 6: a.rect[0] = min(a.rect[0] + 7, s.size[0] - a.rect[2])
a.direction = direct_a
# 将 b 设置一个一直执行的操作
def collide_b():
    r = a.collide(b) # actor 对象的 collide 函数可以接收任意个 actor 对象参数
    # 这里返回的结果 r 为collide函数参数内与 a 碰撞的 actor 对象的列表
    for i in r: i.kill() # 这里让对象 b 碰撞到 a 后自动消失
    b.rect[0] -= 1
    b.rect[1] -= 1
    if b.rect[0] <= 0 or b.rect[1] <= 0: # 对象靠近左/上的游戏边框自动消失
        b.kill()
b.computer.idle = collide_b

a.rect[0:2] = 100, 100 # 不写则默认 0,0
b.rect[0:2] = 400, 200 # 修改角色起始坐标
t.regist(a) # 将角色 a 注入场景t
t.regist(b) # 将角色 b 注入场景t

# 生成第二个场景
# 可以用 TAB 测试切换场景，切换场景时，仅当前的场景会更新操作
p = vgame.Theater('pause')

s.regist(t) # 将场景 t 注入游戏
s.regist(p) # 将场景 p 注入游戏
s.run()

# 注意，尽量不要把碰撞检测放在 操作函数里面，
# 因为那样主角只有在接收到操作的时候才会有函数执行，所以面对像是朝着主角飞过来的子弹
# 处理的时候，如果主角不动，即便是碰撞了，也不会触发到碰撞的操作，
# 所以，请将碰撞检测都写在 computer.idle 里面
# 另外，从开发的角度上，最好将碰撞检测放在非操作对象的 computer.idle 的函数里面
# 因为后续如果处理子弹的时候有非常非常多类型的子弹，这时候调整起来就很麻烦，代码臃肿
# 当然，你如果程序没有太多复杂开发的需求，写在主角操作对象的 computer.idle 里面也行
# 因为每一个 Actor 对象都会绑定一个 computer 对象。用就是了。
```

- ##### 加载图片资源（下面的代码需要你添加一些图片资源才能执行成功）

```python
import vgame
s = vgame.Initer()

# vgame.Image 比一般的资源加载要稍微强大一些可以将 png 加载成动态资源图
# 当第一个参数，路径参数有不同类型的时候有可能加载成不同类型的图片
#     当是一个表示颜色的3/4个数字的元组 tuple （如果是四个数字，则第四个数字代表了透明度通道）类型时
#         会生成一个矩形方块，默认大小为 60x60 
#     当是 None 时候就代表表示颜色的4数字元组 (255,255,255,255) 情况下默认大小为 60x60 白色矩形。
#     当是一个“图片文件地址”，就直接加载成 pygame 的图片数据，
#     当是一个“图片文件地址”，并且图片文件的命名是 xxx_123x123.png 时(正则处理为r'_(\d+)x(\d+)\.')，
#         图片会按照 123x123 的大小切割图片，从左到右从上往下的切割图来生成动图，有时有点用。
#     当是一个“图片文件夹”，则会将文件夹内的图片按顺序排序，自动加载成动态图
#     以上处理均会自动自动进行 mask 处理，方便 actor 对象使用碰撞检测。

bg = '' # 这里填你本地的图片的地址，随便网上保存一张即可
ac = '' # 这里填你本地的图片的地址，随便网上保存一张即可

v_bg = vgame.Image(bg, showsize=(640,480)) # 加载背景图片资源
v_ac = vgame.Image(ac, showsize=(60,60)) # 这里请尽量主动设置 showsize

t = vgame.Theater('main', v_bg)
a = vgame.Actor(v_ac)
def direct_a(m):
    for i in m:
        if i == 8: a.rect[1] = max(a.rect[1] - 7, 0)
        if i == 2: a.rect[1] = min(a.rect[1] + 7, s.size[1] - a.rect[3])
        if i == 4: a.rect[0] = max(a.rect[0] - 7, 0)
        if i == 6: a.rect[0] = min(a.rect[0] + 7, s.size[0] - a.rect[2])
a.direction = direct_a
t.regist(a) # 将角色 a 注入场景t

s.regist(t) # 将场景 t 注入游戏
s.run()
```