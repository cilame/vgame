# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame
vgame.Initer()
main = vgame.Theater()

a = vgame.Player().local(main, (100,100))
b = vgame.Wall(showsize=(300,100)).local(main, (200,200))

def move_d(self, d):
    # self 代表了被覆盖了 direction 函数的对象本身，即为 Player 实例。
    # 这个实例有一个 mover 方法，可以将获取到的操作信息直接用 mover.move 函数接收
    # 这样能直接移动，如果需要修改各个方向的加速度分量，
    # p1:WASD  p2:上下左右键 # 这个 get('p1') 消息实际上是一个数字的列表
    # 这个列表长度最大为2，从小键盘上看到的 8264 方向即作为方向表示，比英文更加直观
    # 这里的消息 d 也是经过处理了的，同时按下超过三个方向键这里的消息就会返回空。
    # 同时按下左右，或者同时按下上下均返回空消息。所以这些接收的消息必然是八方向其中的一个。
    # 放心使用即可。
    self.mover.move(d.get('p1'), 13)

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

a.direction = move_d
a.bound = lambda self, b:print(b)