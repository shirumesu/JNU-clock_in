# 暨南大学学生健康系统自动打卡

用于自动完成[暨南大学健康打卡](https://stuhealth.jnu.edu.cn/#/login)所写的简单python  

如果你是因为搜索`网易易盾`、`滑条验证`等字眼进入的本仓库,那么你可以看看下面的内容:  
实际上由于暨南大学健康打卡中滑条验证使用的网易易盾, 本项目代码也提供了简单的接口和类进行滑条验证的破解(当然代码需要自己扒, 祝好运)
```python3
# 具体参数传入请到时候参照注释
cs = CrackSlider() # 创建一个网易易盾破解类并启动selenium的chromdriver无头浏览器
cs.crack() # 保存图片->计算->滑条验证一连串
cs.Slider_Success() # ->bool :是否成功通过滑条验证
cs.reflash_temp() # 点击刷新滑条验证图片
```

## 使用本项目

1. 进入任一文件夹内,`Shift+右键`选择`在此处打开PowerShell窗口`
   
2. 克隆本项目
   
    ```git
    git clone https://github.com/LYshiying/jnu-stu-health-clock-in
    ```
    然后安装依赖
    ```pip
    pip install -r requirements.txt
    或使用墙内清华代理源:
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    ```

3. 在根目录创建文件夹`/source/`以及`/images/`用于存放chromedriver以及临时图片
此时你的项目结构应该如下:
```
JNU-CLOCK_IN/
    │  config_simple.json
    │  LICENSE
    │  main.py
    │  README.md
    │  requirements.txt
    │
    ├─images/
    │
    └─source/
```

4. 安装**谷歌浏览器**以及**Chromedriver**并放在`/source/`下

5. 将`config_simple.json`改为`config.json`并用记事本打开根据说明编辑

    编辑示例:
    ```Json
    {
        "user_name": "20991512350", // 此处为学号, 你登录的用户名
        "passwd": "12345678", // 此处为密码
        "temperture": "", // 温度,可填可不填(不填自动生成由36.2~36.9的温度)
        "province": "广东省", // 需要自己去下拉框看,打出对应文本即可,必须每个字对上
        "city": "广州市",
        "district": "番禺区" // 如香港这种没有district的,请输入`请选择`如下:
        // "district": "请选择"
    }
    ```

6. **关闭系统代理**(或是进入main.py为`cs = CrackSlider()`指定proxy-server)，双击打开`main.py`，然后欣赏滑条验证无限尝试吧（逃
   1. 可以使用`python3 main.py --chrome-path /path/to/chromedriver`来指定chrome路径

7. 对于windows和linux用户的差距就在`main.py`中的chromedriver，windows为chromedriver.exe，linux为chromedriver，根据需求自改就行了

## 注意

- 本项目仅适用于`已完成首次打卡`的人(信息会自动记录,其后打卡会自动填入,而本项目仅填写了动态变更需要填写的地方如体温,地址)
  
- 本项目**不保证**没有bug, 请注意是否出现了打卡成功的页面, 并且请留意python窗口的输出
  - 2022/2/15: 已经基本重构结束, 代码相对完善, 理论不会再出现问题(当然欢迎提交issue)
    - 因为我看github频率取决于我摸不摸鱼, 一直没有留意到有两个issue非常抱歉

- 你可能遇到的`正常`情况:
  - 一直失败(除非次数实在多的出奇,否则可能只是单纯运气不好……)
    - 如果多的出奇, 可能是打卡网站采取了新的风控政策, 会尽可能及时更改
  - 停着没干事(可能在下载验证码图片/等待某些操作完成)

- 抱歉，我太懒了，这确实并非是一个完善的项目，仅限于 **能跑** 总之在我电脑上能跑
  - 2022/2/15: 哈哈, 爷写完辣！

- 本作者完全不知道代码在干嘛,会产生怎么样的后果。总而言之,祝你好运(笑)

## 为什么写此项目

- 无聊
   
## ~~适用人群~~

- 已进行过`首次打卡`的人
- 无聊想搞点新东西的人
- 想学学`selenium`的人(~~这有最简单的代码~~)

## 它用来干什么?

- 进行暨南大学学生健康系统的自动打卡
- 目前可在`配置后`实现自动输入体温,地址,点击以上信息真实按钮并提交
   
## 它是怎么做到的

- 模拟浏览器自动打卡: [Selenium](https://github.com/SeleniumHQ/selenium)
- 分析滑条验证: [aircv](https://github.com/NetEaseGame/aircv)
- 彩色日志: [loguru](https://github.com/Delgan/loguru)

~~强烈安利以上三款~~

## TODO
如果该打卡系统未来会保持使用（2021/9/26编辑:?还要打卡一年?cnm!), 将进行更好的优化  
`以下TODO的前提为上面一行`

~~将playwright替换为selenium,使用pyinstaller打包为exe(2021/9/6编辑:你在说个寄吧 selenium打包不一样很难)~~
- [ ] 询问更多信息,实现第一次就可以直接自动填入所有项
- [x] 不再需要用户使用F12获取地区value, 而是通过询问的方式(2021-9-26编辑:不用填数字id而是文字了,算是搞定了吧（

## 更新(顺便记录爬虫攻防?)
### 2022/2/15
  - 说明:
    - 由于网站加入对webdriver的验证导致失效, 因此代码大规模重构
  - 新增
    - 现在失败次数过多会自动点击重试了
  - 优化
    - 代码结构
    - 滑条验证准确度
    - 更多的日志提醒
## 感谢

- 来自我自身的高效且稳定的精神支持
- 作为死宅多余的空闲时间
- 各种文章
  - [selenium之 下拉选择框Select——huilan_same(CSDN)(2016-08-18 23:52:39)](https://blog.csdn.net/huilan_same/article/details/52246012)
  - [使用Python+selenium+aircv+numpy破解图片滑块验证码——WoY2020(CSDN)(2021-03-31 10:20:50)](https://blog.csdn.net/weixin_38179939/article/details/115307333)
  - [如何正确移除Selenium中的 window.navigator.webdriver(知乎)(编辑于 2021-07-14 13:42)](https://zhuanlan.zhihu.com/p/117506307)
  - [~~Google翻译~~](https://translate.google.cn/)
