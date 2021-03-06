import os, re, time
import types
import traceback
from itertools import product

class cycle:
    def __init__(self, items):
        self.items = items
        self.len = len(self.items)
        self.idx = 0
    def __next__(self):
        nx = self.items[self.idx % self.len]
        self.idx += 1
        return nx
    def __iter__(self):
        return self
    def get_cycle_number(self):
        return int(self.idx / self.len)
    def get_idx_number(self):
        return self.idx % self.len





import pygame
import pygame.font as font

class ImageMaker:
    def __init__(self, imgpath):
        self.imgpath = imgpath
        self.surface = pygame.image.load(imgpath)

    def gridcut(self, size=None):
        sw, sh = self.size
        gw, gh = size
        grid = []
        for j in range(int(sh/gh)):
            for i in range(int(sw/gw)):
                rect = (i*gw, j*gh, gw, gh)
                grid.append(self.getrect(rect))
        return grid

    def getrect(self, rect):
        return self.surface.subsurface(rect)

    @property
    def size(self):
        return self.surface.get_rect()[-2:]
    

class Image:
    '''
    用于单个图片资源的加载，可以是动图，不过现在实现暂时还是不够好
    因为动图的加载模式有时候很不一样，会有细微的位置需要调整
    '''

    dfont = None
    vgame = None

    def __init__(self, img=None, showsize=None, rate=0, flip=None, masksize=None, offsets=(0,0)):
        # 一些默认配置，用于图片动画的刷新率，可以通过图片名字进行配置
        self.showsize   = showsize # 该参数仅用于对象
        self.rate       = rate     # 不同的单位可以使用不同的速率
        self.offsets    = offsets  # 图片展示与真实的rect的偏移
        self.actor      = None
        self.active     = None # 会在加载图片的时候根据图片类型自动设置
        self.src_image  = None
        self.cur_tick   = 0
        self.rects      = None # 后续用于动图
        self.rotate     = 20
        self.flip       = flip
        if self.flip:
            self.flipx  = 'x' in flip or 'X' in flip
            self.flipy  = 'y' in flip or 'Y' in flip
        self.orig_image = self.load_img(img)
        self.image      = self.orig_image.copy()

        self.masksize   = masksize # mask 主要用于处理碰撞检测
        self.mask       = self._mk_mask()

        # Image.dfont 只能在游戏初始化之后才能初始化，否则报错。
        if not Image.dfont:
            if "papyrus" in pygame.font.get_fonts():
                Image.dfont = font.SysFont("papyrus", 8)
            else:
                Image.dfont = font.SysFont(pygame.font.get_fonts()[0], 15)
            Image.vgame = __import__('vgame')

    def _get_size(self):
        return self.image.get_rect()[2:]

    size = property(_get_size)

    def load_img(self,img):
        try:
            if not img:
                image = pygame.Surface((60, 60)).convert_alpha()
                image.fill((255,255,255,255))
            elif isinstance(img, (tuple, list)) and isinstance(img[0], int):
                image = pygame.Surface((60, 60)).convert_alpha()
                # image = pygame.transform.flip(image, self.flipx, self.flipy)
                image.fill(img)
            elif isinstance(img, (tuple, list)) and isinstance(img[0], pygame.Surface):
                self.active    = True
                self.src_image = None
                self.cur_tick  = 0
                self.rects     = cycle([pygame.transform.flip(image, self.flipx, self.flipy) if self.flip else image for image in img])
                image = next(self.rects)
            elif isinstance(img, (tuple, list)) and isinstance(img[0], str):
                def _load_img(i):
                    image = pygame.image.load(i).convert_alpha()
                    if self.flip: image = pygame.transform.flip(image, self.flipx, self.flipy)
                    return image
                self.active    = True
                self.src_image = None
                self.cur_tick  = 0
                self.rects     = cycle([_load_img(i) for i in img])
                image = next(self.rects)
            elif isinstance(img, str) and os.path.isdir(img):
                imgfs, imgfv = {}, []
                for idx, imgf in enumerate(sorted(os.listdir(img))):
                    v = tuple(map(int, re.findall(r'\d+', imgf)))
                    v = v if v else idx
                    imgfs[v] = imgf
                    imgfv.append(v)
                def _load_img(i):
                    image = pygame.image.load(os.path.join(img,i)).convert_alpha()
                    if self.flip: image = pygame.transform.flip(image, self.flipx, self.flipy)
                    return image
                all_rects = [_load_img(imgfs[i]) for i in sorted(imgfv)]
                self.active    = True
                self.src_image = None
                self.cur_tick  = 0
                self.rects     = cycle(all_rects)
                image = next(self.rects)
            elif isinstance(img, str) and os.path.isfile(img):
                image = pygame.image.load(img).convert_alpha()
                move = re.findall(r'_(\d+)x(\d+)\.', img.lower()) # 根据图片的命名自动切割图片，生成动图
                if move:
                    move        = list(map(int,move[0]))
                    src_h,src_w = image.get_height(),image.get_width()
                    pro_h,pro_w = move[:2]
                    nraws,ncols = int(src_h/pro_h),int(src_w/pro_w)
                    mfunc       = lambda i:(i[0]*pro_w, i[1]*pro_h, pro_w, pro_h)
                    all_rects   = list(map(mfunc,product(range(ncols),range(nraws))))
                    self.active    = True
                    self.src_image = image
                    self.cur_tick  = 0
                    self.rects     = cycle(all_rects)
                    image = self.src_image.subsurface(next(self.rects))
            elif isinstance(img, pygame.Surface):
                image = img
            if self.showsize:
                image = pygame.transform.scale(image, self.showsize)
            # print(self.flip)
            # if self.flip:
            #     print(self.flipx, self.flipy)
            #     image = pygame.transform.flip(image, self.flipx, self.flipy)
            return image
        except:
            raise Exception("无法加载图片. {}\n{}".format(img, traceback.format_exc()))

    def update_image(self, ticks):
        if self.active and self._time_update(ticks):
            self.orig_image = self.src_image.subsurface(next(self.rects)) if self.src_image else next(self.rects)
            if self.showsize: 
                self.orig_image = pygame.transform.scale(self.orig_image, self.showsize)
            self.image = self._rotate(self.orig_image.copy())
            self.mask  = self._mk_mask()
        else:
            self.image = self._rotate(self.orig_image.copy()) # 该处用于处理按钮闪烁相关的操作
        self._delay_bind_debug()

    def _rotate(self, image):
        if self.actor and self.actor.rotate:
            if self.actor.rectsize:
                # 暂时还没能解决该处与框架主动设置 rectsize 时候旋转定位相适配。
                raise Exception('rotate parameter cannot be used if rectsize parameter is set.')
            rotated = pygame.transform.rotate(image, -self.actor.rotate) # 统一使用逆时针旋转做正角
            self.actor.rect = rotated.get_rect(center=self.actor.rect.center)
            return rotated
        else:
            return image.copy()

    def _mk_mask(self):
        if self.masksize:
            if not getattr(self, 'mskdefault', None):
                self.mskdefault = pygame.mask.Mask(self.masksize)
                self.mskdefault.fill()
                mask = self.mskdefault
            else:
                mask = self.mskdefault
        else:
            mask = pygame.mask.from_surface(self.image)
        return mask

    def _time_update(self, ticks):
        if ticks - self.cur_tick > self.rate:
            self.cur_tick = ticks
            return True

    def _delay_bind_debug(self):
        # 显示 mask 边框线，让边框检测处理起来更加的直观
        if self.actor and (self.actor.debug or self.actor.DEBUG or Image.vgame.DEBUG):
            ft = self.dfont.render(self.actor.__class__.__name__, 1, (0, 0, 0), (200, 200, 200))
            # 原始图片文字描述
            self.image.blit(ft, ft.get_rect())
            # 原始图片边框
            (x, y), (w, h) = self.actor.rect.topleft, self.actor.showsize or self.actor.image.get_rect()[-2:]
            pygame.draw.polygon(self.image, self.actor.DEBUG_REALIMAGE_CORLOR, [(0,0),(w-1,0),(w-1,h-1),(0,h-1)], 1)
            # 真实边框处理的文字描述
            # x, y, w, h = ft.get_rect()
            # self.image.blit(ft, (x+ox, y+oy, w, h))
            # 真实碰撞边框
            ox, oy = self.actor.getoffset()
            x, y, w, h = self.actor.rect
            p1 = ox+0,   oy+0
            p2 = ox+w-1, oy+0 
            p3 = ox+w-1, oy+h-1
            p4 = ox+0,   oy+h-1
            pygame.draw.polygon(self.image, self.actor.DEBUG_RECT_LINE_CORLOR, [p1,p2,p3,p4], 1)
            # 碰撞检测边框线条绘制
            outline = self.mask.outline() # 透明图片outline 为空，如为空下面的函数直接执行会报错
            if self.masksize:
                dx, dy = self._get_mask_dxy()
                outline = [(_x+dx, _y+dy) for _x, _y in outline]
            if len(outline) > 1:
                pygame.draw.polygon(self.image, self.actor.DEBUG_MASK_LINE_CORLOR, outline, 1)

    def _get_mask_dxy(self):
        if not getattr(self, 'maskdx', None):
            x, y, w, h = self.actor.rect
            xx = int(x + self.masksize[0]/2 - self.showsize[0]/2)
            yy = int(y + self.masksize[1]/2 - self.showsize[1]/2)
            self.maskdx = x-xx
            self.maskdy = y-yy
        return self.maskdx, self.maskdy


class Text(Image):
    dfont = None
    def __init__(self, text=None, textcolor=(255,0,0), textscale=2, textwidth=None, textside=None, textformat='{}'):
        if not Text.dfont:
            Text.dfont  = font.SysFont('simsunnsimsun', 12)
            Text.vgame  = __import__('vgame')
        self.has_start  = False
        self.text       = text
        self.textcolor  = textcolor
        self.textscale  = textscale
        self.textside   = textside
        self.textwidth  = textwidth
        self.textformat = textformat
        img = self.render(self.text, self.textcolor, self.textscale).convert_alpha()
        img = self.shift(img, textside, textwidth)
        super().__init__(img=img)
        self.has_start = True

    def shift(self, img, textside, textwidth):
        if textwidth:
            w,h = img.get_rect()[2:]
            _temp = pygame.Surface((textwidth,h)).convert_alpha()
            _temp.fill((0,0,0,0))
            x,y,w,h = img.get_rect()
            if textside == 'r': 
                _temp.blit(img, (textwidth-w,y,w,h))
            else:
                _temp.blit(img, (x,y,w,h))
            img = _temp
        return img

    def render(self, text, textcolor, textscale):
        text = self.textformat(text) if isinstance(self.textformat, types.FunctionType) else self.textformat.format(text)
        ft   = self.dfont.render(text, False, textcolor)
        w,h  = ft.get_rect()[2:]
        ft   = pygame.transform.scale(ft, (int(w*textscale), int(h*textscale))) # 示例：缩放为原尺寸的两倍大小
        return ft

    def _get_text(self): return self._text
    def _set_text(self, value): self._text = value; self._flash()
    text = property(_get_text, _set_text)
    def _get_textcolor(self): return self._textcolor
    def _set_textcolor(self, value): self._textcolor = value; self._flash()
    textcolor = property(_get_textcolor, _set_textcolor)
    def _get_textscale(self): return self._textscale
    def _set_textscale(self, value): self._textscale = value; self._flash()
    textscale = property(_get_textscale, _set_textscale)
    def _get_textside(self): return self._textside
    def _set_textside(self, value): self._textside = value; self._flash()
    textside = property(_get_textside, _set_textside)
    def _get_textformat(self): return self._textformat
    def _set_textformat(self, value): self._textformat = value; self._flash()
    textformat = property(_get_textformat, _set_textformat)
    def _flash(self):
        if self.has_start:
            img = self.render(self.text, self.textcolor, self.textscale).convert_alpha()
            img = self.shift(img, self.textside, self.textwidth)
            self.orig_image = img