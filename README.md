# 暨南大学学生健康系统自动打卡

用于自动完成[暨南大学健康打卡](https://stuhealth.jnu.edu.cn/#/login)所写的简单python  

如果你是因为搜索**网易易盾**、**滑条验证**等字眼进入的本仓库,那么可以直接拿`./src/yidun.py`去用(直接调用`yidun().crack()`即可):  

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
```
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

## 注意 / 须知

- 程序会自动识别windows或是linux系统, 并自动尝试寻找`/source/chromedriver.exe`或是`/source/chromedriver`
- 首次使用需要根据要求输入对应的当前所在地
  - 如果后续需要修改可以：
    - 打开`/source/config.json`修改内容(请确保你修改的内容正确)
    - 删除`/source/config.json`

- 有关体温：
  - 温度自动在 \[36.1,36.9\] 区间中生成, 可能存在上午36.1 中午36.9 晚上36.1的大幅度浮动情况
  - 按要求为早上为当天，午间以及晚上为昨天，如果有需要改请打开`/src/driver.py`修改101-103行的传入的布尔值一项(具体自己看函数注释)

- 本项目**仅**适用于已完成首次打卡的人(而本项目仅会填写当日体温当前所在地地址)
  
- 本项目**不保证**没有bug, 请注意是否打印了`提交成功`字样

- 你可能遇到的`正常`情况:
  - 停着没干事(可能在下载验证码图片/等待某些操作完成)，总之没有报错就是胜利！

- 本作者完全不知道代码在干嘛,会产生怎么样的后果。总而言之,祝你好运(笑)

## 为什么写此项目

- 无聊
- 你妈的 打卡算分！

## 它用来干什么?

- 进行暨南大学学生健康系统的自动打卡
- 将滑条验证的一部分单独抽出, 可用于其他地方的滑条验证
   
## 它是怎么做到的

- 模拟浏览器自动打卡: [Selenium](https://github.com/SeleniumHQ/selenium)
- 彩色日志: [loguru](https://github.com/Delgan/loguru)

~~强烈安利~~

## 更新(顺便记录爬虫攻防?)
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
