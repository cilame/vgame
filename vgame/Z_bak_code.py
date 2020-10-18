# Map 整改需要废弃代码的备份，部分功能重新实现将会参考一定原实现的代码




class Map(_GridMap):
    '''
    用于处理栅格类型游戏的方式，不过如果不需要单位强制栅格化
    那么这里的处理也可以简单的当作一种更加规范的单位初始化/地图绘制的方式
    '''

    DEBUG = False

    class Map2D:

        DEFAULT_OBSTRUCT = 1 # 默认阻值
        DEFAULT_GAP = 3

        def __init__(self, mapw, maph):
            '''
            地图存储，主要使用 world 调用资源，使用 graph 进行路径计算
            当物体移动的时候需要考虑物体移动的状态
            '''
            self.mapw  = mapw
            self.maph  = maph
            self.world = self._create_map2ds()
            self.graph = self._create_graph()
            self.gap   = self.DEFAULT_GAP
        def _create_map2ds(self):
            d = {}
            d['_obs2d'] = self._create_obs2d()  # 存放默认阻值，均为 DEFAULT_OBSTRUCT
            d['obs2d']  = self._create_obs2d(0) # 地图单位阻值，初始均为 0
            d['_']      = self._create_obs2d()  # 此处尚未用到，在这里写入仅为说明可以在此处进行扩展性开发。
            return d
        def _create_obs2d(self, obstruct=None):
            return [[Map.Map2D.DEFAULT_OBSTRUCT if obstruct is None else obstruct for j in range(self.mapw)] for i in range(self.maph)]
        def _create_graph(self):
            d = {}
            for i in range(self.mapw):
                for j in range(self.maph):
                    d[(i, j)] = self._init_point(i, j)
            return d
        def _init_point(self, x, y):
            p = {}
            lx, ly = x-1, y # l
            rx, ry = x+1, y # r
            ux, uy = x, y-1 # u
            dx, dy = x, y+1 # d
            if lx >= 0:        p[(lx, ly)] = self.world['_obs2d'][ly][lx] # Map.Map2D.DEFAULT_OBSTRUCT
            if rx < self.mapw: p[(rx, ry)] = self.world['_obs2d'][ry][rx] # Map.Map2D.DEFAULT_OBSTRUCT
            if uy >= 0:        p[(ux, uy)] = self.world['_obs2d'][uy][ux] # Map.Map2D.DEFAULT_OBSTRUCT
            if dy < self.maph: p[(dx, dy)] = self.world['_obs2d'][dy][dx] # Map.Map2D.DEFAULT_OBSTRUCT
            return p
        def _shortest_path(self, actor_a, actor_b):
            # axis or actor
            axis_a = getattr(actor_a, 'axis', actor_a)
            axis_b = getattr(actor_b, 'axis', actor_b)
            try:
                return shortest_path(self.graph, axis_a, axis_b)
            except Exception as e:
                print('dijkstra error:{}, the destination address cannot reach or exceed the boundary.'.format(e))
                return []
        def _local(self, actor, axis, obstruct): 
            if actor.axis:
                self._local_add_del(actor.axis, axis, obstruct)
                actor.axis = axis
            else:
                actor.axis = axis # 让 actor 绑定一个坐标地址
                actor.obstruct = obstruct
                self._local_set(actor.axis, obstruct)
        def _local_set(self, axis, val): self.world['obs2d'][axis[1]][axis[0]]  = val; self._local_calc_graph(axis)
        def _local_del(self, axis, val): self.world['obs2d'][axis[1]][axis[0]] -= val; self._local_calc_graph(axis)
        def _local_add(self, axis, val): self.world['obs2d'][axis[1]][axis[0]] += val; self._local_calc_graph(axis)
        def _local_add_del(self, caxis, naxis, val):
            a = caxis[1] >= 0 and caxis[1] < self.maph and caxis[0] >= 0 and caxis[0] < self.mapw
            b = naxis[1] >= 0 and naxis[1] < self.maph and naxis[0] >= 0 and naxis[0] < self.mapw
            if a and b:
                self._local_del(caxis, val)
                self._local_add(naxis, val)
            else:
                if a: self._local_del(caxis, val)
                if b: self._local_add(naxis, val)
        def _local_calc_graph(self, axis):
            _val = self.world['_obs2d'][axis[1]][axis[0]] + self.world['obs2d'][axis[1]][axis[0]]
            for i in self.graph[axis]:
                if axis in self.graph[i]: self.graph[i][axis] = _val
        def __str__(self):
            pks = []
            for i in self.world['obs2d']:
                pks.append(' '.join(['_'*self.gap if j == 0 else ('{:'+str(self.gap)+'}').format(j) for j in i]))
            return '\n'.join(pks)

    def __init__(self, gw, gh, sw, sh):
        self.theater = None
        self.gridw   = gw
        self.gridh   = gh
        self.screenw = sw
        self.screenh = sh
        self.mapw    = int(sw/gw)
        self.maph    = int(sh/gh)
        self.map2d   = Map.Map2D(self.mapw, self.maph)

    @property
    def size(self):
        return self.mapw, self.maph

    def local(self, actor, axis, obstruct=0):
        if not actor._toggle['gridmove_start']:
            actor._toggle['gridmove_start'] = True
            self._local(actor, axis, obstruct)
            actor._toggle['gridmove_start'] = False

    def _local(self, actor, axis, obstruct):
        # 这里处理某些精灵的定位，换算出真实坐标然后定位到目标位置
        _x, _y, w, h = actor.rect
        px, py = axis
        rx = self.gridw * px + self.gridw / 2 - w / 2
        ry = self.gridh * py + self.gridh / 2 - h / 2
        actor.rect.x = rx
        actor.rect.y = ry
        self.map2d._local(actor, axis, obstruct)

    def move(self, actor, trace, speed=4.):
        # 处理部分“平滑移动”以及部分“状态转移”以及部分“操作延时”以及最重要的“坐标记录”
        # 操作延时：即让处于正在移动中的角色暂时不再接收控制信息
        # 坐标记录：即让路径算法能够快速算出最短路
        if not trace: return       # trace 为空列表则可能寻路函数出现异常
        if len(trace) == 0: return # trace 起点和终点是同一个，则不执行移动
        if len(trace) == 1: 
            trace.append(trace[0])
            # return # trace 起点和终点是同一个，则不执行移动
        if speed <= 0 or speed == float('inf'):
            raise Exception('speed error. {}'.format(speed))
        chain = self._get_move_chain(actor, trace, speed)
        self._run_move_chain(actor, chain)

    def direct(self, actor, side, speed=4.):
        x, y = actor.axis
        w, h = self.mapw-1, self.maph-1
        if isinstance(side, int):
            if side == 8: y -= 1; y = 0 if y < 0 else y
            if side == 2: y += 1; y = h if y > h else y
            if side == 4: x -= 1; x = 0 if x < 0 else x
            if side == 6: x += 1; x = w if x > w else x
        elif isinstance(side, list):
            if 8 in side: y -= 1; y = 0 if y < 0 else y
            if 2 in side: y += 1; y = h if y > h else y
            if 4 in side: x -= 1; x = 0 if x < 0 else x
            if 6 in side: x += 1; x = w if x > w else x
        curr = actor.axis
        targ = (x, y)
        self.move(actor, [curr, targ], speed=speed)
        return actor

    def _run_move_chain(self, actor, chain):
        if not actor._toggle['gridmove_start']:
            actor._toggle['gridmove_start'] = True
            chain.append(self._gridmove_stop_toggle(actor))
            actor._chain['gridmove'].extend(chain)

    def _get_move_chain(self, actor, trace, speed):
        chain = []
        _x, _y, w, h = actor.rect
        tracep = []
        trace2 = []
        startx = 0
        for idx, (curr_pxpy, new_pxpy) in enumerate(zip(trace[:-1], trace[1:])):
            (cpx, cpy), (npx, npy) = curr_pxpy, new_pxpy
            cx = int(self.gridw * cpx + self.gridw / 2 - w / 2)
            cy = int(self.gridh * cpy + self.gridh / 2 - h / 2)
            nx = int(self.gridw * npx + self.gridw / 2 - w / 2)
            ny = int(self.gridh * npy + self.gridh / 2 - h / 2)
            dr = self._judge_direct((cpx, cpy), (npx, npy))
            if idx == 0:
                # 这里的处理是为了一些单位原本不是强制栅格的单位更加平滑的适应自动寻路处理的方式
                if abs(cx - _x) > 2 or abs(cy - _y) > 2:
                    npx, npy = trace[1]
                    x2 = int(self.gridw * npx + self.gridw / 2 - w / 2)
                    y2 = int(self.gridh * npy + self.gridh / 2 - h / 2)
                    t1len = ((_x-x2)**2 + (_y-y2)**2)**0.5
                    t2len = ((cx-x2)**2 + (cy-y2)**2)**0.5
                    if t1len <= t2len:
                        startx = 1
                        startr = [(_x, _y), (x2, y2), curr_pxpy, (npx, npy), dr]
                    if t1len > t2len:
                        startx = 0
                        startr = [(_x, _y), (cx, cy), curr_pxpy, (npx, npy), dr]
                    if len(trace) > 2:
                        npx, npy = trace[2]
                        x3 = int(self.gridw * npx + self.gridw / 2 - w / 2)
                        y3 = int(self.gridh * npy + self.gridh / 2 - h / 2)
                        t3len = ((_x-x3)**2 + (_y-y3)**2)**0.5
                        t4len = ((x2-x3)**2 + (y2-y3)**2)**0.5
                        if t3len < t2len:
                            startx = 2
                            startr = [(_x, _y), (x3, y3), curr_pxpy, (npx, npy), dr]
                    if startr:
                        tracep.append(startr)
            trace2.append([(cx, cy), (nx, ny), curr_pxpy, new_pxpy, dr])

        for (cx, cy), (nx, ny), (cpx, cpy), (npx, npy), dr in tracep:
            chain.append(self._change_direct(actor, dr))
            chain.extend(actor.mover.gridmove(actor, (cx, cy), (nx, ny), speed))

        for idx, ((cx, cy), (nx, ny), (cpx, cpy), (npx, npy), dr) in enumerate(trace2):
            # 这里处理角色方向自动改变，让人在使用的时候只需要配置好方向资源，自动变化
            # 当你在 actor.status['direction'] 里面配置好变化方向的自己的状态
            # 直接计算移动后的结果，这里可能需要一个快照功能，用于计算临时的结果
            if idx >= startx:
                chain.append(self._change_direct(actor, dr))
                chain.extend(actor.mover.gridmove(actor, (cx, cy), (nx, ny), speed))
            chain.append(self._change_obstruct(actor, (cpx, cpy), (npx, npy)))
        return chain

    def trace(self, actor_a, actor_b):
        return self.map2d._shortest_path(actor_a, actor_b)

    def _change_obstruct(self, actor, caxis, naxis):
        def func(actor, caxis, naxis):
            if caxis != naxis:
                self.map2d._local_add_del(caxis, naxis, actor.obstruct)
                actor.axis = naxis
        return [func, (actor, caxis, naxis,), True]

    def _gridmove_stop_toggle(self, actor):
        def func(actor):
            if actor._toggle['gridmove_start']:
                actor._toggle['gridmove_start'] = False
        return [func, (actor,), True]

    def _change_direct(self, actor, dr):
        def func(actor, dr):
            drname = None
            curr = actor.status['current']
            if dr == 2: drname = 'down'
            if dr == 8: drname = 'up'
            if dr == 4: drname = 'left'
            if dr == 6: drname = 'right'
            targ = actor.status['direction'].get(drname)
            if targ and curr != targ: actor.aload_image(targ)
        return [func, (actor, dr,), True]

    def _calc_center_by_rect(self, actor):
        # 计算对象的像素中心点与哪个栅格最近，用于一些非强栅格类型的游戏处理上面
        _x, _y, w, h = actor.rect
        px, py = actor.axis
        tx = int(_x + w / 2)
        ty = int(_y + h / 2)
        ux = int(round((tx + self.gridw / 2) / self.gridw, 0) - 1)
        uy = int(round((ty + self.gridh / 2) / self.gridh, 0) - 1)
        return ux, uy

    def _judge_direct(self, axis_a, axis_b):
        # 判断是否为相邻的某个方向，用数字表示 [1-9]
        # 如果该方向并不存在，则返回 0
        # b位于a的那个方向
        xa, ya = axis_a
        xb, yb = axis_b
        if xb-xa == 1:
            if yb-ya ==  1: return 3
            if yb == ya   : return 6
            if yb-ya == -1: return 9
        if xb == xa:
            if yb-ya ==  1: return 2
            if yb == ya   : return 5
            if yb-ya == -1: return 8
        if xb-xa == -1:
            if yb-ya ==  1: return 1
            if yb == ya   : return 4
            if yb-ya == -1: return 7
        return 0

    def _draw_debug_grid(self, image):
        # 用于对背景栅格的调试，绘制显示栅格以及坐标信息
        if vgame.DEBUG or Map.DEBUG:
            x, y, w, h = image.get_rect()
            x = 0
            while x < w:
                x += self.gridw
                pygame.draw.line(image, vgame.Artist.GRID_LINE_COLOR_MAP_DEBUG, (x, 0), (x, h))
            y = 0
            while y < h:
                y += self.gridh
                pygame.draw.line(image, vgame.Artist.GRID_LINE_COLOR_MAP_DEBUG, (0, y), (w, y))
            xys = []
            x = 0
            _x = 0
            while x < w:
                y = 0
                _y = 0
                while y < h:
                    xys.append((x,y,_x,_y))
                    y += self.gridh
                    _y += 1
                x += self.gridw
                _x += 1
            for x,y,_x,_y in xys:
                ft = vgame.Image.dfont.render(str((_x,_y)), 1, (255,255,255), (50,50,50))
                image.blit(ft, (x+1,y+1,*ft.get_rect()[2:]))

    def __str__(self):
        return 'map.size:{}\n{}'.format(self.size, str(self.map2d)) # 默认绘制阻力图












    def init_by_ratio(self, theater, grid=None, side=None, ratio=(1, 1), offsets=(0, 0)):
        '''
        # 后续发现这个函数并没有想象中那么好用，直接统一使用 Actor 的 local 会更舒服一些。
        # 这里的 init_by_ratio 这个函数后续可能会抛弃，因为对于开发者来说学习成本很高。且功能不方便。
        grid    --> 用于划分格子，后续用格子坐标来整理/展示图文。
        ratio   --> 如果 ratio 只有一个数字，则 side 所用的方向均使用这个比例，两个数字则分别为宽/高比例
        side    --> udlr:up,down,left,right，只能用最大两个(合法角落)字母，即为不能同时上下，不能同时左右
        offsets --> 初始化整块图片时的坐标偏移，和 ratio 一样以宽/高比例做偏移。
        '''
        theater.regist_menu(self)
        if isinstance(ratio, (int, float)): kw = kh = ratio
        if isinstance(ratio, (tuple, list)): kw, kh = ratio
        if isinstance(offsets, (int, float)): kx = ky = offsets
        if isinstance(offsets, (tuple, list)): kx, ky = offsets
        side = 'd' if side is None else side
        ta = 'd' in side or 'u' in side
        tb = 'r' in side or 'l' in side
        if ta and tb: self.rect.h, self.rect.w = theater.size[1]*kh, theater.size[0]*kw
        else:
            if ta: self.rect.h, self.rect.w = theater.size[1]*kh, theater.size[0]
            if tb: self.rect.w, self.rect.h = theater.size[0]*kw, theater.size[1]
        w, h = theater.size
        if 'd' in side: self.rect.y = h - self.rect.h
        if 'r' in side: self.rect.x = w - self.rect.w
        self.rect.x += theater.size[0] * kx
        self.rect.y += theater.size[1] * ky
        self.showsize = int(self.rect.w), int(self.rect.h)
        self.grid    = grid    if grid    else self.grid
        self.theater = theater if theater else self.theater
        self._debug_draw()
        return self













    # @property
    # def map(self):
    #     class _map:
    #         def move(s, trace, speed=4.):
    #             self.theater.map.move(self, trace, speed)
    #         def local(s, theater, axis, obstruct=0):
    #             if theater:
    #                 theater.regist(self)
    #                 theater.map.local(self, axis, obstruct)
    #             else:
    #                 try:
    #                     self.theater.map.local(self, axis, obstruct)
    #                 except AttributeError as e:
    #                     if 'map' in str(e) and 'NoneType' in str(e):
    #                         raise Exception('pls use theater.regist to register the object in theater, '
    #                                         'or use the third parameter of map.local to register automatically.')
    #             return self
    #         def trace(s, actor_or_point):
    #             return self.theater.map.trace(self, actor_or_point)
    #         def direct(s, side, speed=4.):
    #             return self.theater.map.direct(self, side, speed)
    #         def __str__(s):
    #             return str(self.theater.map)
    #     return _map()