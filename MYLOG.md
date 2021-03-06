主要的设计结构

```
# 用 Initer  类用于初始化，该类里面自动组装了一个 artist 类实例
# 用 Artist  类对所有资源进行存储调配（通常这个不需要主动实现，封装在 Initer 内部即可）
# 用 Theater 类生成舞台
# 用 Actor   类生成演员
# 用 Image   类加载资源，该资源会直接传入 Actor 实例中。
#
# 其中 Initer，Artist，Theater 里面都有一个regist函数
# 用于将下级资源进上级资源的方法，其中 Initer 和 Artist 的注册函数相等，就是为了方便而已
# 资源结构如下
# 
#        Artist
#        /     \
#   Theater1  ...
#    /    \
# Actor1  ...
#
# 演员（actor）对象注册进舞台
# 舞台（theater）对象注册进总的表演类
# 事件（events）默认每个actor对象默认自带一个，可以通过 in_control 参数配置是否会收到操作挂钩的信息
#       events 的实现就是这个框架比较功能性的核心扩展部分，主要用于实现与操作挂钩的一切内容
#
# 注册函数都包含一个反向关联的方法
# 这样的方式可以让所有的演员（actor）也能有结构的找到全局数据
# eg. 如果 actor_1 是一个演员对象，通过一般注册之后，那么他可以通过 actor_1.theater 找到当前剧场资源
# 也可以通过 actor_1.theater.artist 找到全局数据存储地方
```

20200205 放弃了之前的块状处理

```
放弃非常耦合的块状处理的方式，因为过去的块状处理对后续的扩展性非常不友好，以至于后续可能对开发的整体思路修改
也是为了让这个框架能够更加适配更多的游戏类型，

之前的游戏资源的分配结构将会保留，这是这个框架目前来说唯一的优点了。
后续可能需要扩充 actor 的多个表演功能的处理，因为需要不同演出的分支，
单位对象就应该处理好对自身全部的表演资源进行存储。以便保证后续的互动会更加方便。

TODO: 目前的鼠标操作非常的不丝滑，肯定是设计上出现了什么问题，
      并且，鼠标操作并非一定需要长按的处理的功能，长按拖动或许并没有那么的必要
      或许换个角度，直接右键按住实现那个有时候也可有可无的拖动功能也并非不可
      设计上一定要以操作丝滑为目标，否则就太膈应人了
TODO: 动作交互，原来考虑的时候有点傻逼，貌似是想通过 events 类来实现相关的功能
      因为是觉得子弹之类的和操作有强相关，所以应该绑定在 events 里面
      后来发现实际上，子弹的演出本来也属于演员的一种，所以就直接放在 actor 里面
      触发的方式可以在 actor 类里面实现，并且从这个角度延伸开去
      将子弹之类的内容或者演出以 actor 交互演出的类型直接放置在操作对象里面，
      这样的处理可能会更好一些，武器和角色也能更好的绑定或组合，是一个更方便的思路
      甚至可以考虑实现一些类似于对话框演出与角色绑定，这样对话框的资源和角色绑定
      更好的使用，这样一想，好处还挺多的。后续会考虑从这个角度对框架进行扩展。

或许是最近在家里闲得慌，所以才有了点时间来更新一下原来就稍微有点兴趣的框架了。
```

20200206 增加图片资源类，后续需要解耦一个 actor 只有一个资源类

```
鼠标的处理已经直接使用两种模式的处理，（单击反馈，框选反馈）
动作交互现在还在处理，因为动作交互需要考虑怎么处理单个对象，多个动作图的加载
所以现在刚处理完图片资源加载的初步解耦，后续还需要考虑两种表演模式的处理
    现在想的是，后续 actor 对象需要加载多个状态
    1 在执行某些操作时，或者触发了某些条件时需要转换自身的表演状态（切换不同的动态图显示），
    2 子弹类的处理，也就是需要在某些发射子弹的场景下，需要生成新的 actor 
      这个 actor 是区别于自身的一个额外的对象，后续可能还会消灭
    3 电脑的自动运动的处理，某些对象可能不需要接收操作，但是需要电脑让其自动运动
      所以需要单位的人工智能进行自动运动

现在的问题：
    需要增加 computer 类吗？负责让单位在闲置状态有自己的动作，或许可以在这里加上交互操作？
    怎样处理自身状态的切换，处理接收控制信号时候的操作
另外还有一些需要考虑的开发处理：
    怎么样才能让移动处理会更人性化，尽量不要直接对运动进行操作，今天尝试写测试的时候发现了
    运动函数还需要直接对像素和坐标进行操作，感觉就很难受，这一点上面感觉相比于纯的 pygame
    似乎并没有进化多少，所以想要更进一步的处理移动的方式
    运动如果需要考虑处理的话，我觉得很有可能需要实现对应类型场景下的 map
    （因为游戏类型的不同，不同类型的游戏运动处理肯定也不一样。）
    或许可以针对不同的游戏类型，进行不同 map 模板进行一定的封装，然后使用 actor 进行交互，
    快速实现移动的各种各样的功能。（非常靠后的开发或许还可以开发一定程度上的自动寻路？）
    横版卷轴（重力、速度、地板）、slg（块状移动、回合）、rpg...
总之下一次的开发，首先要做的就是素材的收集：
    收集好了素材，测试写起来也会更加顺手一些，进一步的开发效率也会更快。
```

20200212

```
修改 events 为 controller 。因为那个模块基本上也只会用来处理接收操作了。

素材的处理比想像中的要难上不少，目前能查到的方式是通过 shoebox 切分其他游戏的素材
然后通过多个图片加载的方式拼成动态展示的对象。为之增加了通过文件夹的方式加载动态图。
    目前加载的方式有
        1通过图片地址加载（加载成静图）
        2通过图片地址加载（加载成动图，如果图片格式为 xxx_123x123.png, 则会通过 123x123 的大小切分图片然后加载成动图）
        3通过图片路径加载（加载成动图，通过图片地址按顺序加载里面全部的图片地址成为游戏动态图）
        *4如果参数为数字颜色的元组例 (100,100,100,255) 的颜色生成大小为 60x60 的矩形色块
        *5如果参数为空，则使用颜色为 (255,255,255,255) 大小为 60x60 的矩形色块
    4，5方法为测试时候使用的调试
暂时先不要求加载方向的内容，现在比较紧急的需求是怎么才能实现物理效果，爬坡之类的
现在用测试的模式来调试，想看看能不能处理贴边移动。
先试试能不能想办法把 mask 的轮廓画出来。

目前实现的移动非常非常的简陋，没有任何的物理性质，仅仅是像素的加减处理，所以不够好。
现在的优势就是场景的转换以及操作的封装，电脑持续动作的封装。但是说是电脑，却没有智能。
因为现在没有考虑好怎么处理场景和处理与场景交互的物理性质。

后续还需要考虑更多，音乐的处理似乎也还很远的样子。如果 unity2d 的开发环境没有臃肿成那种鬼样子。
我应该不会来开发这个东西。我真是非常喜欢非常轻便、且接口不像是rpgmk封装得那么高的开发环境。

后续还要多想想场景的问题，碰撞检测貌似还不能很好的处理贴墙滑动。我暂时还没有别的方法，
没办法处理好斜坡上下的问题。太难了，尽量多找找有没有别的教程里面有接口吧。
```

20200213

```
现在稍微修改了一下控制方向的核心接口，因为发现了之前的一个BUG
当你想要在键盘上实现两个人一起玩游戏的话，方向键肯定需要判断，
之前没有对 2p 进行方向键的区分，导致接口在后续开发肯定会出现一些问题
并且如果想要用之前的代码强行处理成 2p 会导致 1p 运行时候 2p 完全无法运行
所以现在将核心代码修改了一下，现在已经可以同时控制 1p 和 2p 。
为什么我这里不开发更多p呢？ 因为键盘就那么大一点，两个人同时用一个键盘来玩已经很拥挤了。
并且主流的小游戏普遍最多是 2p 一起游戏，所以目前不考虑更多p玩家的处理。
```

20200214

```
可能需要考虑怎么处理刚体，因为要考虑到更加顺滑的移动
目前来看，简单的碰撞检测处理起靠墙移动有点不太方便，如果强行外部实现的话，代码一定会很臃肿
所以，我现在的想法就是，可能会在 Actor 里面增加一个刚体类实例的绑定，让每一个对象本身就含有
一些更加方便的蹭边的处理，并且后续可能还需要修改物体的移动方式

物体的移动方式使用简单的像素可能就很麻烦，说不定 Actor 还需要绑定一个物体属性
用控制速度的方式使其移动，方便让其受到重力影响之类。

今天简单的增加了 mask 边框线显示的 DEBUG 模式，发现之前的一个小 BUG 并解决，感觉很舒畅。
另外显示 mask 边框线的解决，对后续的处理有很大很大的帮助，后续会根据这个方向进行开发。

还有一点就是，这里不应该使用动图自动生成的边框线来处理物体的物理性质，
边框检测线用于处理碰撞，游戏中的子弹碰撞伤害一类的会比较有帮助，但是不适用于移动相关的内容
因为动图的边框线是变化的，你在靠墙/站在地面的时候突然变化了边框形状，
那么墙体，地面的处理就很困难，pygame 没有非常强大的物理处理功能，我也不想用其他第三方库实现
所以我对于一个角色的看法就是：一个角色的物理体积一定是很少变化且变化的状态是非常少的
这样对游戏的开发来说回比较方便。

今天重要的开发思路变化，将 “碰撞检测” 和 “物理性质” 的开发分开，
这样看来就需要两个 mask 来处理不同的内容的检测，之前没想清楚，现在才发觉一个 mask 是不够的。
    1 碰撞检测体积，用于检测碰撞伤害使用，这样会更加符合人对碰撞的直观感受
    2 物理检测体积，用于简化物体移动开发相关，简化刚体处理

晚上稍微简化了一下 idle 函数的处理，之后都不需要通过覆盖 Actor.computer.idle 实现持续监测了
现在直接用覆盖 Actor.idle 这个函数来实现持续监测的行为了，另外这里的处理也会有额外的好处。
    因为 idle 和 mouse、direction、control 在一个函数内做循环，所以后续方便扩展 idle 的功能，
    比如可以扩展 idle 的参数数量，让 idle 参数也能接收到当前的操作信息，举个实际开发的例子
        当你用一个 Actor 做墙的时候，如果需要让被检测的主角能够贴墙移动就要知道当前方向的操作
        知道方向的操作才能让对主角进行坐标的调整
    目前考虑的修改：用一个三个参数的函数去覆盖 idle ，那么就让第三个参数定为方向操作信息
        鼠标，控制键均可以此类推。
    不过暂时先不改，因为我想通过其他的方式来实现贴墙移动的操作，想要将这个物理性质封装进去
    能封装这个物理性质的话，后续对某些 2D 横版卷轴类游戏来说，开发就会变得简单很多。
```

20200215

```
增加了物理这个大类，后续非常多的运动处理都将会包装在这里面
修改物理量来处理操作和移动，并且操作移动里面封装了一部分的实体处理，已经能够实现平滑移动了
可以控制一个对象贴着另一个对象移动。

这是一个非常良好的开端，似乎很多东西都明朗起来了。等处理好了这些物理性质，后续会增加文档内容
物理性质目前仅仅有最简单的平滑移动，不过平滑移动中增加了实体与实体间的贴边移动。
我的希望是这个框架能够作为动作游戏引擎的存在，所以对于这类游戏，物理性的处理会很重要
另外，目前的平滑移动的检测碰撞的方式用的是 pygame.Rect.colliderect 所以只能处理方块的边界
后续会将 physics 内部的碰撞检测函数修改成别的，动作类的游戏如果上个斜坡都不行，就很不优雅。
可能还是需要增加一些额外的 mask，这样或许可能处理好斜坡的内容。目前没写出来所以不确定。
目前以物理性质的任务优先。

后续还会增加更多的游戏处理模式，就是为了更多的处理不同类型的游戏。
    1 卷轴动作        # 物理运动，惯性，重力，加速度，斜坡
    2 战旗游戏        # 网格地图需求，有障碍物的寻路，
    3 角色扮演        # 网格地图需求，有障碍物的寻路，
    4 即时战略        # 碰撞体积(估计非常难)，群策移动(估计非常非常难)，这种游戏最后考虑

目前需要做的事情：
    1 继续补完物理内容，处理重力，惯性，加速度
    2 后续增加对斜坡的处理内容，这方面尽量要做好，如果不行就算了
    3 做一些图片多状态加载，前面两个内容需要的时间可能会挺长的，这个到时候估计不一定按着计划走
      后续还需要考虑镜头处理

今天写了挺多了，暂时没什么思路，明天搞。
```

20200216

```
惯性摩擦方面的处理已经做好了！重力处理也做好了，目前来看，勉强还是能用的。
不过现在看来还有一些不太方便的地方就是在持续时间上面，如果在外部来处理的话感觉稍有点麻烦。
现在发现一些超级难受的东西。因为为了固定速率的问题，所以很多地方都有各自的延时器。

现在感觉貌似在跳跃上面有点不太顺滑，还有一个BUG，就是在 debug 模式下显示 rect 的框线没有显示
有些测试却能显示，现在就觉得稍微有点奇怪。
```

20200217

```
目前已经做好了单跳的处理，不过目前不够完善，(1)如果在跳跃过程中松手但还没到最高点，那么就会出现继续跳的情况。
为了处理这点，可能需要考虑按键状态切换的处理。这个对于多级跳的功能来说应该挺有用的，(2)所以后续会考虑处理多级跳，
因为这个功能对于2d游戏来说很流行。

(1) 问题已经解决。
(2) 问题已经解决。

多级跳这个功能终于设计好了接口放置在了代码内部，终于漂亮的实现好了多级跳的接口，想了整整一天。
为了多级跳，那么肯定就需要实现跳跃，跳跃就需要考虑起跳和坠落两种状态，最终也同样实现了另一个接口，跳跃的高度。
跳跃和多级跳的实现在这个框架里面比想象中要难好几倍，为了与核心移动处理同频，
你需要在两个函数中实现对流体信息的状态切换进行捕捉，在游戏的物理引擎核心中修改移动循环的处理。
真是非常非常的烦，真TM日了狗了，花了太长时间来解决这个问题了。

后面要处理的内容可能还是之前的那个 rect 线条不出现的 bug？不过实际上这个不用那么着急。

目前需要好好考虑的内容：
后续需要处理的功能大概就是斜边？实体碰撞的检测可能就要用 mask 来处理
之前用 rect 检测也不是不可以，但就是不适用与爬斜坡，我想用 mask 来试试，如果不行这块我就会放弃

还有就是镜头跟随的接口设置，希望会有更好的处理灵感。
```

20200219

```
放弃斜边处理，感觉对于这种方式的处理并不方便，因为核心模块即便是能检测不规则的碰撞，
也没办法处理各种问题，并且实现碰撞的方式比较麻烦。目前彻底放弃斜边的处理。

有些跳台游戏，跳台平面是有单面穿透的效果的。

简单写了一个效果，发觉一个场景里面有三四百个元素是完全OK的，所以放心写下去。
三四百个一直移动的物体已经能做非常多的事情了，今天感觉提不起劲来，暂停这个框架的开发。

后续的目标可能主要要处理的还是在怎么扩展状态的转换了，实际也是图片资源的切换
让主角显得有很多状态一样，站立不动/跳跃/跑步/冲刺/二段跳状态获取的接口

不过现在对于子弹的处理来说，还需要处理直线移动的处理，特别的用夹角向量移动啥的。
这个是非常有必要的。需要增加一个计算角度的函数了。然后用角度来进行移动，这样会好很多。
因为一般的子弹的行动轨迹都很单纯。如果非要用各种参数的物理量去模拟就会显得多此一举。

最近有点累了，可能会稍微搁一段时间，等想动了再动手。

1 对子弹的移动要有更加合理的接口，不能直接使用物理系统去处理
2 对于跳台方面，要有可从某个方向穿透的跳台。
3 要有额外的延迟接口，让某些操作能够更加舒适的延迟使用出来。
4 想一想冲刺的接口新增。
5 想好了上面的之后最后考虑一下怎么搞一个比较难的：一个更加平滑的镜头跟随。

休息。搞这个太伤身体了。音乐的处理貌似还很早的样子。我日。
```

20200225

```
虽然重力相关的跳跃稍微有点顿挫感，但是为了让对高度相关的处理更加的精准，所以目前接受了这样的处理
在开发中非常要注意的是，增加参数的配置检查，让使用者在配置参数时就能察觉到问题。
```

20200227

```
之前很多部分都需要修改，封装了几个基于 Actor 的类，是一种高层的封装，让不同属性的对象理解起来更加清晰
放弃之前全部都使用 Actor 对象的方式进行处理，考虑了一下，那样的处理稍微有点过度抽象了。
并且调整了一下互斥的处理方式，通过对 Actor 属性进行封装后，可以让不同属性的对象在实例化时候有特有属性的配置
互斥即为在移动过程中不会被穿透的意思。

目前的增加 五个分类，均为 Actor 对象的继承。
Player Enemy NPC Bullet Wall

其中最重要的几个点，默认初始化情况下：
0 Player 默认是 in_control=True 的状态，所以可以直接覆盖操作函数来接收操作信息
1 Player Enemy NPC 相互之间并不互斥
2 Player Enemy NPC 全部都与 Wall 互斥
3 Bullet 与全部都不互斥，所以可以穿透全部

其中也可以通过修改某些属性专门对某些类型进行互斥处理，或者对某个 Actor 进行互斥，比之前要方便很多。

另外修复了之前 DEBUG 模式不显示边框的BUG。总感觉重力系统相关设计哪里出现了一些问题。
但是就是不太清楚是什么问题。有种像是在水里面给游泳的感觉。

目前将两种移动的方式进行了一定的封装，后续使用接口的时候可能会更加方便一点。
```

20200228

```python
目前觉得物理处理写得有点失败，又臭又长，特别是在将跳跃处理和多段跳得功能集成在里面之后就复杂起来
而且移动起来貌似还有各种小问题，有点难受。真的有点越看越不顺眼。

为什么不爽主要就是因为 2020227 的顿挫感处理不妥当。在我的处理下感觉有点像是在水里游泳一样。
可能之后会增加额外的物理性质相关的类的处理，或者直接在现有的基础上直接修改。
现有的摩擦处理和重力处理写在一起感觉稍微有点不太舒服。暂时不管，先处理别的。

目前在处理镜头跟随的部分。
明天再好好考虑一下镜头相关的内容，因为镜头的处理还是稍微有点麻烦的。
有几个元素需要好好考虑
1 地图
2 镜头
3 游戏画面
4 内 padding
5 外 padding
游戏画面本质和镜头基本等同，但是稍微有些概念上面的区别，后续还要增加一些 DEBUG 模式
DEBUG 模式下的镜头处理也要好好整理一下。要尽量做到和 unity 那样有起码的全局的镜头检查功能。
后续可能要在 Initer 里面分类出 1 game_size 2 camera_size 两种。

目前已经开发一下 DEBUG 模式下在边框部分显示对象的类型，这样看上去也比较直观一点。

还需要开发在 DEBUG 模式下鼠标操作的相关功能。
明天再搞镜头，和 DEBUG 鼠标相关的处理。
```

20200330

```
对象拖拽在场景大于窗口的情况下会有BUG，后续考虑一下怎么处理好了。
现在开发的话可能会暂时放弃缓冲性的镜头跟随的处理。全局镜头检查的功能有点遥远，个人技术力有限。
后续也察觉到了，目前的跳跃功能集成进来虽然也还行，但是还是非常的不行，跳跃不够顺滑，
甚至有点失败。

先走一步是一步好了。不如先考虑实现一个游戏，后续再深度考虑这些问题。
不然一直都在引擎上面处理，不知道什么时候是个头啊。
```

20200907

```
今天感觉好安静呢，街道上也没有人

之前真实太怠惰了。今天的计划就是简单考虑处理好 map 相关的内容
map的处理：
    地图一律统一使用块处理方式，就类似 rpgmaker 那种，因为即便是你不需要单位遵守块的行动方式
    但是从初始化，从地图的构建的方便程度上来看，也是非常有必要的。
    之前还考虑是不是块处理仅仅当作一种模式来扩展，现在想想，块处理非常必要设置成默认模式。

后续估计还是要抛弃用图片名字配置切割加载动态图的方式，所有的考虑均使用一帧一图片的方式。
反思了一下之前的处理，感觉 pygame 不太适合做十分精细的动作游戏，因为在一些异常帧率出现的问题我暂时没法解决。
所以目前主要的方向应该还是会朝着一些经营养成的方式开始处理。

现在主要是要想办法调和两种移动方式，或者直接抽象成两种移动处理方式来实现也还行。
把名字再整理成更加有辨识度，直接分成两类即可？
```

20200909

```
栅格化界面元素，一方面规范了以后绘制地图，一方面给予了更容易实现的游戏性的提升
今天使用了别人写好的库来实现最短路径算法，后续想了想，确实有了栅格处理之后，路径算法才有实现的展开

目前需要解决的主要是一个在使用地图信息存储时的多图层存储方式的清晰化
一个地图存放数据的可以使用多个图层信息进行构建，目前生成两个，但仅用到一个图层对主要的对象进行阻值存储
函数需要写更清晰一些，今天太晚了，白天再好好修改好再处理。

单位显示的前后顺序，主角肯定一定要在最后渲染，也就是置顶渲染。这个小问题后续处理。

之后主要的处理有两个，单元游戏模式的移动，非单元游戏模式的兼容，希望能实现简单一种游戏场景
以游戏场景为框架，后续游戏实现起来也会更加方便一些。
```

20200910

```
处理方向上的自动状态变化，也就是你只要设定好走什么方向使用什么状态的动图，
当你用类里面的移动方法就会自动变化。所以会方便很多。

后续尝试将普通移动也就是非栅格化的单位绑定栅格，这样可以扩展更多的游戏开发面。
还有也差不多该准备菜单栏的开发相关内容了。

动态图现在还没有一个比较规范的处理，也是因为对于游戏而言现在的开发暂时还接触不到那些东西，
所以图片的加载方面还是不太严格，处理将就用的水平，后续再继续处理。

目前使得非栅格类的游戏单位在 SmoothMover 里面的移动自动绑定了阻挡系数图的修改。
这样就能更加动态的适应一些非强栅格类型游戏的自动寻路功能。

现在需要考虑的就是菜单的开发了。
    菜单的呼出，关闭。
    菜单出现后被盖住的那些就自动获取不到控制信息，直到菜单关闭。并且多个菜单是可以盖加的。
    菜单也是基本策略游戏中下达指令的重要联系，也是后续重要的开发方向。

现在回想一下貌似，物理系统也没有想象中那么好，后续也可能会进行一定程度的修改。
```

20200911

```
解决了寻路系统的一些小BUG。

菜单开发需要构思一下，准备开始处理了。
```

20200913

```
因为菜单方面对鼠标键盘的操作有更加细的粒度，所以花了点时间处理了一下一些操作的延迟器。先优化操作。
从开发的角度，不可能每一个时间片都接收控制信息，这样也很麻烦。所以先优化一下操作，后续再继续看菜单。

另外菜单方面也要对图片的加载有更加丰富的需求，所以也在图片加载方面进行一定程度的功能增强。
发现一个碰撞检测方面的问题。
1 通常使用 rect 的碰撞检测，适用于刚体 pygame.Rect.colliderect
2 通常使用 mask 的碰撞检测，适用于子弹碰撞检测， sprite.spritecollide <- sprite.collide_mask

现在遇到一个问题，就是我展示的图片加载后自动生成的 rect 是以图片为准的，也就是图片必然在 rect 内。
但是我想让我的图片超过刚体检测的范围，我想让实际的刚体微微小于图片，这样游戏性更强一些。
不会出现一些动态图用因为几个像素微微浮空在地面上移动。

发现直接修改 sprite 的 rect 不能直接用，因为图片终究是以 rect 的左上角作为坐标进行渲染的。
最后是发现在 screen.blit 的时候直接修改图片贴的位置就可以了。目前已经解决。
```

20200920

```
目前还在考虑怎么处理菜单相关的内容，因为这一块可能有一定程度上的操作考虑：是否打开菜单后，
上下左右键不会变成操作游戏内容移动的处理，这一块我觉得还是得尽量集成在功能里面会更好一些。

是否需要隔离操作很重要，因为可被操作的单位未必只有一个，直接交给使用框架的开发者来处理会麻烦很多。
最好在框架这一步就能够轻松做到与所有操作单位的操作隔离会更好。

另外现在发现了一些地图 grid 相关的问题。目前的地图栅格化貌似只能用于不可移动的地图处理，有点问题
这点问题很大，关系到后续扩展。另外还有一个问题就是要让移动更加方便一些。

还有一个就是要处理一下斜角移动的平滑性。这样游戏性看上也会更好一点点。
对于菜单栏后续肯定是需要更加有意思的，另外按钮的处理也应该提上日程了，毕竟很多游戏都需要按钮进行交互。
提到按钮的相关操作，必然绕不开鼠标相关功能的封装的。

所以：
1栅格化兼容区域地图显示等（大方向或许能增强地图的放大和缩小的功能）
2栅格化的移动应尽量方便一点，比如斜角的优化，虽然并不是那么重要
3最重要的就是按钮效果的实现，按钮效果绑定菜单板，菜单版的出现/消失动画的实现，对于点击的实现
4后续肯定要对鼠标操作进行优化，甚至是整个 controller.py 的大改。（鼠标框选的处理的按键松开需要增加一个类型进行处理）
 并且鼠标操作时候，可能需要一些 grid 定位相关的函数操作。
 同样，鼠标的操作也需要实现菜单和操作相关的隔离。这点也挺重要的。
```

20200922

```
考虑先把按钮实现，按钮相关的鼠标功能，还有与菜单绑定后的方向键操作的选则按钮相关的内容。
或许一般角色也需要这些按钮相关的操作，鼠标框选之类的功能也需要。

Menu 内部处理按钮绑定相关的功能，用于快速打开或关闭菜单以及菜单绑定的一些列组件。
Button 刚想了想，目前在犹豫是否真的需要抽象出这一个类出来，因为毕竟本身就是 Actor 的分身，分身已经有点多了。
```

20200927

```
目前图片的加载还是存在一定问题，一些动态图片在非规则化的状态变化时需要更精准的偏移而并不仅仅只是简单的居中处理。
比如有些图片实际上是以左下角作为加载后的状态，那么就不应该直接用非常普通的 offsets 来处理，因为这样不够通用。
这个 offsets 如果不能直接修改偏移，那么后续可能就会直接做用在图片上。

还有一些动画只会播放固定N个循环。所以这里也需要更多处理。

另外前面几天考虑的按钮相关的问题，现在暂时还没有时间考虑，尽量还是朝着能够看得到的成果的方向努力一下。
另外感觉 physics 非常鸡肋，后续很可能直接将这部分直接删除。
```

20200922

```
将 controler.py 中的默认延迟帧率调到最低，解决了高帧率下接收信号会出现间断的问题。
并且，后续要注意，尽量不要在 controler 内部实现延迟的处理，最好还是在 actor 里面，对各自的操作加上不同的延迟器。
```

20201005

```
后续应该将计算路径的处理分离开来，并且也不能直接的数字作为阻值，这样加减会混在一起，不方便计算。
路径的处理后续肯定会分离出一个更加可控的处理方案。因为需要考虑到不同单位可能对相同的物体有不同的阻值
所以处理的时候后续需要搞分离。

另外还需要处理 menu 更复杂一些的功能，处理文本列表，列表更加方便的处理。另外还需要考虑列表数量超过屏幕时的情况。
滚轮相关，以及处理选择框的问题。

找到一个系统自带的还算挺好的一个用于中文的字体
# 目前用新宋的 12大小字号的字体是最好的，如果需要不同大小，在此基础上缩放即可
# 注意 render 的第二个参数抗锯齿一定要关掉，否则渲染出的英文和数字的字体很憨批
dfont = font.SysFont('simsunnsimsun', 12)
ft = dfont.render('简体刘关张，繁體劉關張。abcd,13:32', False, (255,255,255))
w,h = ft.get_rect()[2:]
_ft = pygame.transform.scale(ft, (int(w*2), int(h*2))) # 示例：缩放为原尺寸的两倍大小

另外字体这边还需要考虑做换行的问题，还需要考虑固定长度，靠左/靠右的展示，这种处理便于表格数据的展示。
还有一种开发需求，就是拖拽调整位置，并且输出坐标信息，这样会非常方便对于 grid 的开发。
```

20201007

```
对于一些音效加载来说有时候会出现奇怪的问题，这里记录一下
这里很奇怪的是加载一些 mp3 音效的时候
    使用 pygame.mixer.music.load 加载音乐时候没有问题
    使用 pygame.mixer.Sound 却会出现 python.error: Unable to open file 的错误
    怀疑是一些处理音效的位数相关的问题，
直接使用 pygame.mixer.music.load 不好，因为这个处理的音乐只能同时有一个音乐播放
但是我这边需要的是能够同时加载多个音效的 pygame.mixer.Sound 的加载播放方式
所以那些 mp3 的音效音乐我只能通过其他 py 库转换成 wav 格式，至少目前转换后的音乐能使用了
转换代码如下：

# pip install pydub
import pydub
from pydub import AudioSegment
def mp3_to_wav(mp3_path, wav_path):
    s = AudioSegment.from_mp3(file=mp3_path)
    s.export(wav_path, format="wav")
```

20201008

```
Anime 对象存在动态(多张图片动画)时是存在问题的，因为会自动在一次循环之后自动调用 self.kill() 方法，
并调用该对象中的静态方法 endanime 原本该功能开发是由于飞机大战中的机体死亡时播放动画的需要，
现在考虑扩展可控循环次数，在每播放完一个轮回的时候，自动调用一个类似 endanime 的静态函数（方便后续覆盖）。
名字大概会时 loopanime？总之先看后续开发情况，如果后续开发游戏有需要就将该功能放进来即可。
```

20201009

```
优化 delay 函数性能。

发现了对于性能开销非常大的一个瓶颈，就是之前的 inspect 获取调用站空间来获取高层函数参数信息开销极大。
因为 inspect.stack() 调用时会获取当前的全部的调用栈的信息，导致非常消耗资源，所以换了另一种获取方式
使用 sys._getframe() 来获取就好了非常多，无需存储多余的栈信息，所以消耗非常小。

另外，不能使用 pygame.font.get_default_font() 作为默认加载的字体参数，因为获取到的默认字体不一定存在
这样就失去了作为默认字体的意义了。所以换了一个，现在一般情况下打包的游戏现在不太可能会出现字体加载的问题了。

后续还需要调整 menu 相关的控制处理，现在这个 menu 使用的定位函数有点乱。需要增加 DEBUG 模式下的快速调整处理。
另外 button 配合 menu 时还需要考虑：上下左右选择，默认选中，以及确认按键的处理调整和回调函数等。
这样的处理之后，menu 就显得要比原始版本的 Actor.local 函数要好很多了。


Theater 实例化时放弃主动设置 theater_name ，因为这个参数感觉一点主动设置的必要都没有，所以之后开发也越发简便。
```

20201015

```
解决了屏幕缩放的问题，不过是比较粗暴的直接根据外边框缩放，后面可能会考虑使用留黑边的等比缩放，
不过优先级并不需要那么高，现有的缩放已经够用。

感觉对于飞机类游戏可能还需要考虑更加省资源的碰撞优化，不然屏幕中出现百来个对象的时候就开始有点吃不消了。
所以后续得考虑一定程度得优化，主要得问题还是发生在碰撞检测实在是太多了。主要是用敌机进行碰撞检测，如果说，
在使用碰撞检测前使用数学方式快速消除掉一部分根本无需检测的内容，后续再进行检测，那么这样似乎会好非常多。
```

20201017

```
现在发现，将 grid 绑定了 Theater 进行开发的方式确实十分的傻逼，应该将这类型的也继承 Actor 来使用
这样才能更加方便的修改 grid 的边界和长宽，也能在某些程度上减轻 theater 功能的负担。

回头看了看，这么集成的代码属实傻逼，为啥没能早点想到这些？就不应该绑定舞台 Theater，并且在移动的过程中
Actor 还需要在内部从向上查找舞台进行处理，动态力修改的能力很菜，看了下，里面的代码约三百行。真是傻逼透了。
```

20201017

```
直接对 Map 重构，让其继承自 Actor，一定程度上减轻了 theater 的压力，将 Map 与 Theater 解耦
现在 Theater 初始化时也将不会默认自带一个 map 对象，map 解耦后可以进行一个地图多个阻力图的绑定
这样扩展了开发的效率。不过也删掉了不少不兼容的功能代码。

对于现在的地图而言，暂时还没有重新写出移动函数，需要耗费一点时间重新实现之前的功能。
增强了 delay 的功能，让其能够检测到按键弹起的瞬间，这样对地图移动的处理变得更加简单起来。
```

20201021

```
目前看来，似乎传递的消息第一个参数就应该是 self ，之前考虑欠缺了，以为为了便捷性可以用参数顺序一定程度化简写作……
不过现在看来如果在传递一个参数的时候不指向 self 那么后续对于一般的 python 开发者来说，可能就会出现一些语法疑惑。
并且，这个 self 在一定程度上也是非常重要，并不应该在顺序上出现疑惑。或许之前的开发对于新手展示可能用起来可以，
但是对于熟悉了框架的人来说，后续开发需要更加清晰的逻辑。

所以后续统一将可以被覆盖的函数本身所接收的第一个参数设置为对象本身 self。
```

20201024

```
将 mouseover/mouseout 的回调移入 Actor 对象中，让所有的 Actor 对象都能享受该功能
另外将光标移入按钮上闪烁的功能作为接口配置继承下去，让 Button 负责闪烁功能的实现，当然也能配置更多的效果
这样，Button 就主要负责配置效果即可。
```

20201029

```
解决之前的一个BUG，实际上是我自己对游戏边界的理解出现了一定偏差。现在的平滑移动方面更好一些了。
并且平滑移动使用了更高精度的平滑，不会因为一些 Rect 实例化时强转类型导致精度丢失。
增强点击功能，让点击在场景与窗口不统一时也能准确定位。增强一下拖拽的功能，让拖拽能够满足更大场景的需求。
```

20201101

```
终于把关于镜头跟随的 padding 处理好了，现在就是其他的问题了。
```

20201104

```
镜头的 padding 在移动的时候的速度上存在一定问题，后续修改。这里有点麻烦，实际上目前默认的 padding=(0,0) 已经够用。
另外在窗口移动速度设置到最大的1时候，需要考虑最大的移动速度，免得跑得太快。

另外还得好好想一想一个更好用的状态转移的方法。
```