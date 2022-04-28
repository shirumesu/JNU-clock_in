# 暨南大学学生健康系统自动打卡

用于自动完成[暨南大学健康打卡](https://stuhealth.jnu.edu.cn/#/login)所写的简单python  

如果你是因为搜索**网易易盾**、**滑条验证**等字眼进入的本仓库,那么可以直接拿`./src/yidun.py`去用(直接调用`yidun().crack()`即可):

![Alt](https://repobeats.axiom.co/api/embed/09ffb6e78e635d8995b20234a93eaecea6b1481c.svg "Repobeats analytics image")

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

3. 在根目录创建文件夹`/source/`用于存放chromedriver
此时你的项目结构应该如下:

    ```shell
    JNU-CLOCK_IN
    │  .gitattributes
    │  .gitignore
    │  LICENSE
    │  main.py
    │  README.md
    │  requirements.txt
    │      
    ├─source
    │      chromedriver.exe
    │      
    └─src
           config.py
           driver.py
           yidun.py
    ```

4. 下载对应版本的[Chromedriver](https://chromedriver.chromium.org/)并解压放在`/source/`下
   1. 请确保你安装了[谷歌浏览器(Chrome)](https://www.google.com/intl/zh-CN/chrome/)

5. **关闭系统代理(重要)**然后启动`main.py`
   1. 强烈推荐在命令行(偷偷安利 [Windows Terminal](https://github.com/microsoft/terminal) )中使用`python ./main.py`启动
   2. 这样结束可以保留窗口以及输出 防止报错直接跳出去了什么都看不到

6. 提供了不同的启动参数, 重置设定、重置当前所在地设定等,有需要请使用`python ./main.py --help`查看

## 注意 / 须知

- 程序会自动识别windows或是linux系统, 并自动尝试寻找`/source/chromedriver.exe`或是`/source/chromedriver`
- 首次使用需要根据要求输入对应的当前所在地
  - 如果后续需要修改可以：
    - `python main.py --reset` 或
    - 打开`/source/config.json`修改内容(请确保你修改的内容正确)

- 有关体温：
  - 温度自动在 \[36.1,36.9\] 区间中生成, 可能存在上午36.1 中午36.9 晚上36.1的大幅度浮动情况
  - 按要求为早上为当天，午间以及晚上为昨天，如果有需要改请打开`/src/driver.py`修改101-103行的传入的布尔值一项(具体自己看函数注释)

- 本项目**仅**适用于已完成首次打卡的人(而本项目仅会填写当日体温当前所在地地址)

- 本作者完全不知道代码在干嘛,会产生怎么样的后果。总而言之,祝你好运(笑)

## 为什么写此项目

- 你妈的 打卡算分！

## 更新(顺便记录爬虫攻防?)

### 2022/4/12

- 说明:
  - 考虑到返校时需要更换当前所在地详细地址, 因此专门增加，提供更好的使用体验，并加入自动更新检查，提醒更新
- 新增:
  - 启动参数`--help`
    - 启动参数一览及说明
  - 启动参数`--reset-living`
    - 保留邮件、账号密码设定，单独重置当前所在地
  - 新增**当前所在地详细地址**以及**近14天经过城市**的数据
    - 会要求用户输入并以后会自动填入
  - 自动检查更新功能
    - 因为直连github 速度可能稍慢

### 2022/4/7

- 说明:
  - 考虑到有用户并非每天启动而是使用linux等服务器后台挂着, 因此新增每天打卡后推送至邮件
- 新增:
  - 邮件推送功能

### 2022/3/25

- 说明:
  - tnnd 跟我玩阴的是吧 一天三次温度检测 哈哈！我是百变温度怪！哗！吓死你！
- 新增:
  - 首次使用会自动询问账号密码以及当前所在地
- 移除:
  - 需要手动修改输入config.json
  - 可选的输入当日体温, 现在强制为随机填写
- 优化:
  - 重写, 将 yidun 以及 config 单独拿出来了

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
