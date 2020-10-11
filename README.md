想要开发一个基于 pygame 的游戏框架。

后续会使用该框架开发一般类型的小游戏，根据开发过程的需求增加框架的功能，让框架鲁棒性更强。

- ##### 该框架相比于 pygame 有哪些改进

```
1 控制和移动相关的内容大幅度简化
2 简化了碰撞检测，并且增加一些可供开关的 DEBUG 模式，让你快速检查全部角色或单个角色的碰撞边框线
3 增加一些角色内循环，这些循环和控制的内容一样，速率恒定，不受帧率影响
4 抽象出了舞台的概念，基于这个概念，你能做的事情有很多，快速暂停，商店场景切换，地图切换，各种各样。
5 已经初步处理了物体的刚体碰撞。 总之就是很简单也很好用。

尚在开发
    目前版本非常早期，所以很多接口暂时还有商榷的部分
    有可能有些接口过一段时间直接废弃，所以不建议从现在就开始学习该框架
    除非你的水平能够达到直接阅读框架代码的水平，否则：
    不建议从现在就开始使用该框架！！！
    不建议从现在就开始使用该框架！！！
    不建议从现在就开始使用该框架！！！
```

- #### 游戏框架的安装

```bash
pip3 install vgame
```

- #### 一个简单的开始

```python
import vgame
vgame.Initer() # 该处重要的参数 fps(帧/秒,默认60),title(标题,默认vgame),size(屏幕分辨率,默认640x480)
```

- #### 在屏幕里面放一个方块，并且用键盘的 WASD 操作它

```python
import vgame
vgame.Initer()
main = vgame.Theater() # 生成一个游戏场景

player = vgame.Player().local(main) # 生成一个玩家，放到 main 场景的中心
player.direction = lambda self,d: self.mover.move(d.get('p1'))
```

- #### 上面一块代码的带有注释的描述，额外说明自动实体检测的功能

```python
import vgame
vgame.Initer()
main = vgame.Theater() # 生成一个游戏场景

player = vgame.Player().local(main) # 生成一个玩家，放到 main 场景的中心
wall = vgame.Wall(showsize=(300,100)).local(main, point=(400,400)) # 以point为wall的中心将wall放到指定中心位置上

def move_d(self, d):
    # self 代表了被覆盖了 direction 函数的对象本身，即为 Player 实例。
    # 这个实例有一个 mover 方法，可以将获取到的操作信息直接用 mover.move 函数接收
    # 这样能直接移动，如果需要修改各个方向的加速度分量，
    # 用 mover.speed.x 修改 x 方向每次接收信息移动的像素，y 方向同理。
    # p1:WASD  p2:上下左右键 # 这个 get('p1') 消息实际上是一个数字的列表
    # 这个列表长度最大为2，从小键盘上看到的 8264 方向即作为方向表示，比英文更加直观
    # 这里的消息 d 也是经过处理了的，同时按下超过三个方向键这里的消息就会返回空。
    # 同时按下左右，或者同时按下上下均返回空消息。所以这些接收的消息必然是八方向其中的一个。
    # 放心使用即可。
    self.mover.move(d.get('p1'))

    # 实际上 Player 实例本身就是一个更加强大的 Sprite 类，所以自身也拥有 rect 属性
    # 你也可以通过直接修改 rect 的 x，y 来修改该对象的坐标来实现移动
    # 例如下面的代码能实现相同的效果
    # m = 5
    # for i in d.get('p1') or []:
    #     if i == 8: self.rect[1] = self.rect[1] - m
    #     if i == 2: self.rect[1] = self.rect[1] + m
    #     if i == 4: self.rect[0] = self.rect[0] - m
    #     if i == 6: self.rect[0] = self.rect[0] + m

    # 虽然上面两处代码的效果是一样的，但是还是非常推荐使用第一种来实现移动，
    # 使用 mover 来实现移动有两个好处
    # 1 代码简洁，你也不用直接接触方向的处理
    # 2 自动实现实体检测，这是最最重要的一种附加功能
    # 这样可以非常方便的实现一个简单的互斥效果
    # 如果感兴趣，你可以简单的注释掉上面的移动代码，使用下面的移动代码试试效果

player.direction = move_d

# 你也可以不必在这里设置速度，直接在 mover.move 函数的第二个参数里面设置速度会更加直观
# 而且那样调整速度会更加符合开发对速度的理解
player.mover.speed.x = 10 # 默认为 5
player.mover.speed.y = 4 # 默认为 5

# player 是默认带有实体检测，也就是说碰到墙之后就走不过去
# 另外这里给了一个回调函数 bound 用于覆盖，这样当你控制的对象在 mover.move 移动的时候
# 碰到了实体过不去时，就会回调这个函数，用于显示你是用了 player 的哪一个边碰到了哪个实体
player.bound = lambda side: print(side)
```