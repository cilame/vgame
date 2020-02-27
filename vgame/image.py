import os, re, time
import traceback
from itertools import cycle, product

import pygame

class Image:
    '''
    用于单个图片资源的加载，可以是动图，不过现在实现暂时还是不够好
    因为动图的加载模式有时候很不一样，会有细微的位置需要调整
    '''
    def __init__(self, img=None, showsize=None, rate=0):
        # 一些默认配置，用于图片动画的刷新率，可以通过图片名字进行配置
        self.showsize   = showsize # 该参数仅用于对象
        self.rate       = rate # 不同的单位可以使用不同的速率
        self.actor      = None
        self.active     = None # 会在加载图片的时候根据图片类型自动设置
        self.src_image  = None
        self.cur_tick   = 0
        self.rects      = None # 后续用于动图
        self.image      = self.load_img(img)
        self.mask       = pygame.mask.from_surface(self.image)



    def load_img(self,img):
        try:
            if img is None:
                image = pygame.Surface((60, 60)).convert_alpha()
                image.fill((255,255,255,255))
            elif isinstance(img, (tuple, list)):
                image = pygame.Surface((60, 60)).convert_alpha()
                image.fill(img)
            elif isinstance(img, str) and os.path.isdir(img):
                imgfs, imgfv = {}, []
                for idx, imgf in enumerate(sorted(os.listdir(img))):
                    v = tuple(map(int, re.findall(r'\d+', imgf)))
                    v = v if v else idx
                    imgfs[v] = imgf
                    imgfv.append(v)
                func = lambda i:pygame.image.load(os.path.join(img,i)).convert_alpha()
                all_rects = [func(imgfs[i]) for i in sorted(imgfv)]
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
        except:
            print("无法加载图片.",img)
            print(traceback.format_exc())
            image = None
        return image

    def update_image(self, ticks):
        if self.active and self._time_update(ticks):
            self.image = self.src_image.subsurface(next(self.rects)) if self.src_image else next(self.rects)
            if self.showsize: 
                self.image = pygame.transform.scale(self.image, self.showsize)
            self.mask  = pygame.mask.from_surface(self.image)
        self._delay_bind_debug()

    def _time_update(self, ticks):
        if ticks - self.cur_tick > self.rate:
            self.cur_tick = ticks
            return True

    def _delay_bind_debug(self):
        # 显示 mask 边框线，让边框检测处理起来更加的直观
        if self.actor and (self.actor.debug or self.actor.DEBUG):
            x, y, w, h = self.actor.rect
            pygame.draw.polygon(self.image, self.actor.DEBUG_RECT_LINE_CORLOR, self.mask.outline(), 1)
            pygame.draw.polygon(self.image, self.actor.DEBUG_MASK_LINE_CORLOR, [(0,0),(w-1,0),(w-1,h-1),(0,h-1)], 1)