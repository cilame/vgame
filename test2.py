import vgame
s = vgame.Initer() # 参数 ticks帧数(默认60), title标题名(默认vgame), 分辨率 size(默认640x480)

# Actor 对象的第一个参数可以是 None/tuple/vgame.Image 三种类型
# 当是一个表示颜色的3/4个数字的元组 tuple （如果是四个数字，则第四个数字代表了透明度通道）类型时
#          会生成一个矩形方块，默认大小为 60x60 
# 当是 None 时候就代表表示颜色的4数字元组 (255,255,255,255) 情况下默认大小为 60x60 白色矩形。
# 当是一个 vgame.Image 对象时，showsize 可以在该 Image 对象实例化的时候传入，并且 Actor 中的 showsize 将无效

# 创建场景，第二个参数可以是背景图，也可以不写，不写展示默认的蓝色背景
t = vgame.Theater('main') # 按键 ESC 关闭

# 增加三个角色，其中a设置 in_control为True 后就能够通过修改 a.direction 函数来接收方向功能sssssssssss
a = vgame.Actor(in_control=True,showsize=(50,100))
b = vgame.Actor() # 一个参数都不添加默认为一个白色色块大小为60x60，(255,255,255,255), (60,60)
c = vgame.Actor((255,0,0),showsize=(150,100))

# a 的操作
def direct_a(m):
    for i in m:
        if i == 8: a.rect[1] = max(a.rect[1] - 7, 0)
        if i == 2: a.rect[1] = min(a.rect[1] + 7, s.size[1] - a.rect[3])
        if i == 4: a.rect[0] = max(a.rect[0] - 7, 0)
        if i == 6: a.rect[0] = min(a.rect[0] + 7, s.size[0] - a.rect[2])
a.direction = direct_a

def collide_b():
    r = a.collide(b, c)
    for i in r: i.kill()
def collide_c():
    r = a.collide(b, c)
    for i in r: i.kill()
    c.rect[0] -= 1
    c.rect[1] -= 1
    if c.rect[0] <= 0 or c.rect[1] <= 0:
        c.kill()
b.computer.idle = collide_b
c.computer.idle = collide_c


a.rect[0:2] = 100, 100 # 不写则默认 0,0
b.rect[0:2] = 200, 400 # 修改角色起始坐标
c.rect[0:2] = 400, 200 # 修改角色起始坐标
t.regist(a) # 将角色 a 注入场景
t.regist(b) # 将角色 b 注入场景
t.regist(c) # 将角色 c 注入场景

p = vgame.Theater('pause') # 可以用 TAB 测试切换场景

s.regist(t) # 将场景 t 注入游戏
s.regist(p) # 将场景 p 注入游戏
s.run()