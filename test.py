#from vgame import artist
import vgame.artist as artist
import vgame.theater as theater
import vgame.actor as actor
import vgame.initer as initer


if __name__ == "__main__":
    bg1 = 'test_data/sushiplate.jpg'
    bg2 = 'test_data/sea.jpg'
    cur = 'test_data/sprite_100x100_32.png'

    s = initer(120) # 第一个参数为全局帧率，默认60
    v1 = theater(bg1,'123') # theater必须要指定两个元素，背景图片地址，舞台名字（舞台切换用，键盘C键测试切换）
    actor1 = actor(cur,action='cursor')
    # 现在每个actor内部都会产生一个events对象来实现自身的功能，不过仍然可以通过外部注册的方式将外部events对象注入actor内部

    #e = events(cur)
    #actor1.regist(e)

    
    v1.regist(actor1)
    

    # 指定blocks之后会按照列行数量对图片切分，然后以每块大小默认为（30，30）进行缩放显示，支持地图缩放
    v2 = theater(bg2,'sea',blocks=(16,12))
    actor2 = actor(cur)
    actor3 = actor(cur,(3,3),'actor',100)

    v2.regist(actor2)
    v2.regist(actor3)

    s.regist(v1)
    s.regist(v2)
    print(actor1.theater)
    print(actor2.theater)
    print(actor3.theater)

    print(id(actor1))
    print(id(actor2))
    print(id(actor3))

    s.run()

