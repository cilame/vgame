想要开发一个基于 pygame 的游戏框架。

后续会使用该框架开发一般类型的小游戏，根据开发过程的需求增加框架的功能，让框架鲁棒性更强。

- ##### 该框架相比于 pygame 有哪些改进

```
1 控制相关的内容大幅度简化，并且将帧率考虑进去，你修改了帧率不会影响控制响应的频率
    你不需要关心帧率的影响，速度固定有一定好处，如何使用这些操作信息绑定角色下面有示例，非常简单
    控制处理包含了：方向键处理、鼠标的单击和框选、控制键
2 简化了碰撞检测，并且增加一些可供开关的 DEBUG 模式，让你快速检查全部角色或单个角色的碰撞边框线
3 增加一些角色内循环，这些循环和控制的内容一样，速率恒定，不受帧率影响
4 抽象出了舞台的概念，让一个场景做一个场景的事情，让场景切换变得超级简单
    基于这个概念，你能做的事情有很多，快速暂停，商店场景切换，地图切换，各种各样。

尚在开发的部分
     1 物体的简单实体物理性质
     2 角色的动态图加载不太方便，因为一些素材大小位置不一样，切分后的图片需要考虑相对位置的问题
     3 角色的动态图转换有点不太方便，还没有封装得更好
    对于动态图的内容现在暂时没有考虑更多，因为这块相比于移动相关的物理性质重要性稍差
    现在重点开发第一条内容，因为这个是 2D 横版卷轴类游戏的核心内容，为了兼容这个游戏分类，必须处理
```

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

t = vgame.Theater('main') # 先生成一个舞台，舞台需要指定一个名字(这里可以传入背景图，为演示方便这里先不传)
a = vgame.Actor(in_control=True, showsize=(40,90)) # 生成一个角色，in_control 设置为True可以让角色接收控制信息

# 游戏的背景核心就是 Theater(舞台)
#     Theater 对象的第二个参数是一个图像资源的对象 vgame.Image 对象。不填则为空背景，背景底色 (0,0,100)
# 游戏的表演核心就是 Actor(演员)
#     Actor 对象的第一个参数 img 可以是 None/tuple/vgame.Image 三种类型
#       当是表示颜色的3/4个数字的元组，则生成一个该颜色的矩形方块，默认大小 60x60（第4个数字为透明度）
#       当是 None 时候就代表表示颜色的4数字元组 (255,255,255,255) 情况下默认大小 60x60 的白色矩形。
#       当是 vgame.Image 对象时，showsize 可以在该 Image 对象实例化的时候传入，并且 Actor 中的 showsize 将无效

def direction_a(m):
    # m 为接收方向键的执行信号的参数，是一个最大有两个 key 的字典
    # 如果存在 key 并且是字符串 p1，则代表收到了键盘 wasd 的方向键操作
    # 如果存在 key 并且是字符串 p2，则代表收到了小键盘箭头的方向键操作
    # p1 和 p2 可以同时存在
    # 字典对应的 value ，是一个最大两个数字的列表，是按下的方向的列表
    # 最多同时按下两个相邻的方向，如果按下超过2个方向，则 m 为空
    # 如果同时按下“左右”或同时按下“上下”则 m 也为空
    # 之所以是 8,2,4,6 的数字代表了方向，请看小键盘的数字键位即可明白。
    print(m) # 你可以打印看看，这个参数在执行到wasd方向键/箭头方向键的时候究竟是什么
    for i in m.get('p1') or []:
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
    # m 为一个元组
    # 第一个参数为鼠标键位，0是左键，2是右键
    # 第二个参数为模式，0是单击模式，2是框选模式
    # 第三个参数为 “鼠标按下坐标” 和 “鼠标松开坐标” 的两个点的元组，
    # eg. (0, 0, ((384, 200), (384, 200))) # 这样的参数就代表了一个左键单击操作
    global minfo1, minfo2
    try:
        minfo1
    except:
        minfo1,minfo2 = None,None
    if m: print(m) # 打印看看这个参数是什么在单击，框选时候两者的参数都有什么区别
    if m and m[1] == 2:
        x,y,w,h = a.rect
        sx,sy = m[2][0]
        ex,ey = m[2][1]
        minfo1,minfo2 = ((sx,sy),(x, y, w, h)) if minfo1 != (sx,sy) else (minfo1,minfo2)
        if ( (sx >= minfo2[0] and sx <= minfo2[0] + minfo2[2]) and 
             (sy >= minfo2[1] and sy <= minfo2[1] + minfo2[3]) ):
            dx,dy = minfo1[0] - minfo2[0], minfo1[1] - minfo2[1]
            a.rect[0] = ex - dx
            a.rect[1] = ey - dy
a.mouse = my_mouse # 覆盖默认的鼠标操作的函数(这里的对象a必须在实例化时设置 in_control 为 True)
# 设置新的接收控制键位，默认键位是 j,k
a.controller.control_keys = [vgame.K_j, vgame.K_k, vgame.K_l]
def my_control(c):
    if c:
        j,k,l = c[1]
        print('------control------')
        if j: print('j')
        if k: print('k')
        if l: print('l'); a.kill() # 测试按下l键删除自身(需要先在控制键列表里面增加键位)
a.control = my_control

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
    for i in m.get('p1') or []:
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
b.idle = collide_b # 让要一直执行的函数覆盖这里，帧率不会影响这里执行频率

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
# 所以，请将碰撞检测都写在覆盖 “Actor对象的idle函数” 的函数里面
# 另外，从开发的角度上，最好将碰撞检测放在非操作对象的 idle 的函数里面
# 因为后续如果处理子弹的时候有非常非常多类型的子弹，各种子弹类型的判断都写在主角里面，代码会臃肿
# 所以，最好的开发就应该将伤害相关的处理绑定在子弹 Actor 里面，这样主角 Actor 的代码就简化很多
# 当然，你如果程序没有太多复杂开发的需求，写在主角操作对象的 idle 里面也行
# 因为每一个 Actor 对象都会绑定一个 computer 对象。用就完事儿了。
```

- ##### 加载图片资源（下面的代码需要你添加一些图片资源才能执行成功）

下面生成两个固定像素大小的方块，一个可以用wasd控制，一个可以用方向键控制，两者相撞则两者都会消失

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


# vgame.Actor.DEBUG 可以让全部的 Actor 对象显示其 mask 的边框线
# 如果你的控制对象的素材是一个带有透明度通道的 png 图片，
# 那么这个边框线的显示对开发来说就很有用了，碰撞检测就是依照这个 Mask 边框线来的
# 如果你只想某一个 Actor 对象显示 mask，那么就不能用 vgame.Actor.DEBUG
# 那么你只需要在 Actor 实例化的时候传入一个 debug=True 的参数即可。
vgame.Actor.DEBUG = True 

bg = './bg.jpg' # 这里填你本地的图片的地址，随便网上保存一张即可
a1 = './a1.png' # 尽量找一张带有透明度通道的角色图片，这样可以看到 debug 模式下的 mask 边框线的用处
a2 = './a2.png' # 

v_bg = vgame.Image(bg, showsize=(640,480)) # 加载背景图片资源
v_a1 = vgame.Image(a1, showsize=(50,50)) # 这里请尽量主动设置 showsize
v_a2 = vgame.Image(a2, showsize=(50,50)) # 这里请尽量主动设置 showsize

t = vgame.Theater('main', v_bg)
a = vgame.Actor(v_a1, in_control=True)
b = vgame.Actor(v_a2, in_control=True)
def direct_a(m):
    for i in m.get('p1') or []:
        if i == 8: a.rect[1] = max(a.rect[1] - 7, 0)
        if i == 2: a.rect[1] = min(a.rect[1] + 7, s.size[1] - a.rect[3])
        if i == 4: a.rect[0] = max(a.rect[0] - 7, 0)
        if i == 6: a.rect[0] = min(a.rect[0] + 7, s.size[0] - a.rect[2])
a.direction = direct_a
def direct_b(self, m):
    # 如果用于覆盖的 direction 的函数有两个参数，则第一个参数就是接受控制的 Actor 对象
    # 注意：
    #     Actor 对象中，可以覆盖的函数可以用一个参数的函数覆盖，也可以用两个参数的函数来覆盖
    #     Actor.mouse，Actor.control，Actor.direction 都是可以这样处理
    #     当是一个参数的函数时，那个参数就是操作信息
    #     当是两个参数的函数时，第一个参数就是被覆盖的 Actor 对象本身，第二个为操作信息
    #     本来我是考虑必须为两个参数的函数，不过后来想想，如果必须传入 self 的话
    #     那么对于某些新手来说，可能会稍微有点不太懂 self 是啥东西，且代码会稍微有点不简洁
    #     不过对于熟练 python 的人来说，他们很容易就能发现在 pygame 开发中这个参数的重要性
    #     所以为了兼顾简洁和功能性，这里就兼容了两种方式，一开始还以为实现会很难，结果却意外的简单
    for i in m.get('p2') or []:
        if i == 8: self.rect[1] = max(self.rect[1] - 7, 0)
        if i == 2: self.rect[1] = min(self.rect[1] + 7, s.size[1] - self.rect[3])
        if i == 4: self.rect[0] = max(self.rect[0] - 7, 0)
        if i == 6: self.rect[0] = min(self.rect[0] + 7, s.size[0] - self.rect[2])
b.direction = direct_b
b.rect[:2] = 400,400

def collide_ab(self):
    # Actor.idle 可以被无参数的函数覆盖，也可以被仅有一个参数的函数覆盖
    # 如果是有一个参数的函数，那么这个参数就一定是被覆盖的 Actor 对象本身
    r = self.collide(a)
    if r:
        self.kill()
        for i in r:
            i.kill()
b.idle = collide_ab
t.regist(a) # 将角色 a 注入场景t
t.regist(b) # 将角色 b 注入场景t

# 这里生成两个可以操作的对象，一个用 wasd 来控制移动，另一个用箭头方向键来控制移动
# 两个方块如果相互碰撞，则两者都消失

s.regist(t) # 将场景 t 注入游戏
s.run()
```

- ##### 墙体检测，让物体自动检测其他实体，大幅简化移动的代码，能实现斜方向的贴墙移动

```python
import vgame
s = vgame.Initer()
t = vgame.Theater('main')

vgame.Actor.DEBUG = True

a = vgame.Actor(in_control=True,showsize=(50,100))
b = vgame.Actor(showsize=(510,10))
c = vgame.Actor(showsize=(80,80))
d = vgame.Actor(showsize=(40,40),in_physics=False) 
# 如果不想让某些块实体物理属性，实例化时候设置 in_physics=False，自动去除墙体检测

# 使用物理性质来进行移动，自动对其他实体对象实现实体碰撞，并能极大简化代码
a.direction = lambda self,d: self.physics.move(d.get('p1')) 

# physics.move 这种移动会检测其他实体，或停止或切边移动，直接修改坐标则无法处理碰撞
# 后续接口可能修改，因为目前还在初版，修改会很多。
c.idle = lambda self,d: self.physics.move([4, 2]) # 不断向左下移动

a.rect[0:2] = 100, 100
b.rect[0:2] = 10, 400
c.rect[0:2] = 400, 200
d.rect[0:2] = 200, 200
t.regist(a)
t.regist(b)
t.regist(c)
t.regist(d)

s.regist(t) # 将场景 t 注入游戏
s.run()
```

- ##### 更加有趣的物理移动，带有重力，惯性，摩擦，加速度之类的特性，具体请看下面的代码

```python
import vgame
s = vgame.Initer(60)
t = vgame.Theater('main')

a = vgame.Actor(in_control=True,showsize=(50,100))
b = vgame.Actor(showsize=(510,10))
c = vgame.Actor(showsize=(80,80))
d = vgame.Actor(showsize=(40,40),in_physics=False) 
# 如果不想让某些块处理实体碰撞，实例化时候设置 in_physics 为 False，自动去除实体检测
# 使用物理性质进行移动，将会自动对其他实体对象实现实体碰撞，并能极大简化代码

# 1 简单物理移动：
# 接口：self.physics.move
# 如果只想用到自动碰撞检测，平滑移动，不想用重力，摩擦，之类的复杂功能
# 那么你只要使用 physics.move 来实现移动即可
# 而且可以使用 physics.speed.x 和 physics.speed.y 来修改这种平滑移动的速度
# 2 高级物理移动：
# 接口：self.physics.move2
# 高级物理移动的原理是改变x/y速度的分量。物体会在 speed 影响下移动一定的距离。
# 速度会自动在“摩擦函数”或者“碰撞其他实体”墙壁的时候自动归零。
# 1重力系统，2摩擦系统，这两个系统互斥，在 x/y 方向各有分量
# 一个 Actor 对象如果设置了 in_physics，则默认自带一个高级物理环境
# 默认情况 x/y 方向均为摩擦系统。
# 如何设置重力系统？
# 当 x 方向设置了 physics.gravity.x 为非零整数或浮点数，则 x 方向自动转换成重力系统
# 当 y 方向设置了 physics.gravity.y 为非零整数或浮点数，则 y 方向自动转换成重力系统
# 重力系统和摩擦系统不一样
# 重力系统一直会对重力系统的方向的速度进行变化，除非你给了一个其他速度的分量
# 一般带有跳跃的游戏中，y 方向一般都为重力系统，而 x 方向都为摩擦系统
# 所以如果想要主角拥有重力影响，则直接设置 physics.gravity.y 为一个很小的整数即可

# 示例：
# 简单物理系统
# a.direction = lambda self,d: self.physics.move(d.get('p1'))
# a.physics.smooth_speed.x = 20 # 用 smooth_speed 参数来修改平滑移动的速度
# a.physics.smooth_speed.y = 20

# 示例：
# y重力系统，x摩擦系统 # physics.move2 有第二个参数 effect_highs，限制某个方向跳跃的高度
a.direction = lambda self,d: self.physics.move2(d.get('p1'), effect_highs={8:80}) # p1:wasd键方向消息
a.physics.gravity.y = 3.5   # 修改 gravity.y 即在 y 方向上增加重力常量【参数可正可负】
# “重力系统” 和 “摩擦系统” 均能使用的参数，摩擦系统需要的参数
a.physics.speed_inc.x = 3  # 加速度             【只能正数，整数小数均可】
a.physics.speed_dec.x = 1  # 减速度（类似于摩擦）【只能正数，整数小数均可】
a.physics.speed_max.x = 13 # 最大速度           【只能正数，整数小数均可】

# 测试移动模块，
# physics.move 和 physics.move2 接收的参数为一个数字的列表
# 数字只能为 8,2,4,6 即为小键盘的键位方向 上下左右 的意思。
# 例如下面这个示例就是不断向左下方向移动的意思。
c.idle = lambda self,d: self.physics.move([4, 2]) 

a.rect[0:2] = 100, 100
b.rect[0:2] = 100, 400
c.rect[0:2] = 400, 200
d.rect[0:2] = 200, 200
t.regist(a)
t.regist(b)
t.regist(c)
t.regist(d)

s.regist(t) # 将场景 t 注入游戏
s.run()
```