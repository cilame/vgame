import vgame
# vgame.DEBUG = True
# vgame.Camera.DEBUG = True

pathA = '../test_data/人物状态测试数据'
Attack      = vgame.ImageMaker(pathA + '/spr_ArcherAttack_strip_NoBkg.png')
Attack      = Attack.gridcut((Attack.size[0]/14, 128))
Dash        = vgame.ImageMaker(pathA + '/spr_ArcherDash_strip_NoBkg.png')
Dash        = Dash.gridcut((Dash.size[0]/14, 128))
Death       = vgame.ImageMaker(pathA + '/spr_ArcherDeath_strip_NoBkg.png')
Death       = Death.gridcut((Death.size[0]/24, 128))
Idle        = vgame.ImageMaker(pathA + '/spr_ArcherIdle_strip_NoBkg.png')
Idle        = Idle.gridcut((Idle.size[0]/8, 128))
JumpAndFall = vgame.ImageMaker(pathA + '/spr_ArcherJumpAndFall_strip_NoBkg.png')
JumpAndFall = JumpAndFall.gridcut((JumpAndFall.size[0]/12, 128))
Melee       = vgame.ImageMaker(pathA + '/spr_ArcherMelee_strip_NoBkg.png')
Melee       = Melee.gridcut((Melee.size[0]/28, 128))
Run         = vgame.ImageMaker(pathA + '/spr_ArcherRun_strip_NoBkg.png')
Run         = Run.gridcut((Run.size[0]/8, 128))

vgame.Initer()
main = vgame.Theater(size=(980,640))
show_Attack      = vgame.Anime(Attack,     rectsize=(30,40), rate=60, offsets=(-30,-5)).local(main, offsets=(100,-200))
show_Dash        = vgame.Anime(Dash,       rectsize=(30,40), rate=60, offsets=(0,-5)).local(main, offsets=(100,-150))
show_Death       = vgame.Anime(Death,      rectsize=(30,40), rate=60, offsets=(0,-5)).local(main, offsets=(100,-100))
show_Idle        = vgame.Anime(Idle,       rectsize=(30,40), rate=60, offsets=(0,-5)).local(main, offsets=(100,-50))
show_JumpAndFall = vgame.Anime(JumpAndFall,rectsize=(30,40), rate=60, offsets=(0,-5)).local(main, offsets=(100,0))
show_Melee       = vgame.Anime(Melee,      rectsize=(30,40), rate=60, offsets=(0,-5)).local(main, offsets=(100,50))
show_Run         = vgame.Anime(Run,        rectsize=(30,40), rate=60, offsets=(0,-5)).local(main, offsets=(100,100))

Idle_r = vgame.Image(Idle, rate=60, offsets=(0,-5))
Idle_l = vgame.Image(Idle, rate=60, offsets=(0,-5), flip='x')
player = vgame.Player(Idle_r, rectsize=(30,40)).local(main).follow(main, .1)
player.status['direction']['right'] = Idle_r
player.status['direction']['left'] = Idle_l

def direct(self, d):
    self.mover.move(d.get('p1'), 10)

def ctl(self, c):
    if self.delay(c and c.get('p1')[0], time=100):
        self.aload_image(show_Attack.imager)
    if self.delay(c and c.get('p1')[1], time=100):
        self.aload_image(show_Melee.imager)

player.direction = direct
player.control = ctl
player.mouse = lambda self,m: self.clicker.dnd(m)

