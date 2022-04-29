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

## 顺手记录一下学校干过的事

### 2022/4/29

- 修改页面:
  - 温度改为一天一次
- 个人评价（雾）
  - 广州不说是寄吧 但也不安全啊 怎么改回去了
  - 总之先保留三次体温填写功能, 靠报错进入单次填写

### 2022/3/25

- 修改页面：
  - 一天三次温度检测并要求填入日期
- 个人评价（雾）
  - tnnd 跟我玩阴的是吧 哈哈！我是百变温度怪！哗！吓死你！

### 2022/2/15

- 增加脚本判断:
  - 验证`navigator.webdriver`是否为 True
- 个人评价（雾）
  - 有趣，学到了新东西

## 感谢

- 来自我自身的高效且稳定的精神支持
- 作为死宅多余的空闲时间
- 各种文章
  - [selenium之 下拉选择框Select——huilan_same(CSDN)(2016-08-18 23:52:39)](https://blog.csdn.net/huilan_same/article/details/52246012)
  - [使用Python+selenium+aircv+numpy破解图片滑块验证码——WoY2020(CSDN)(2021-03-31 10:20:50)](https://blog.csdn.net/weixin_38179939/article/details/115307333)
  - [如何正确移除Selenium中的 window.navigator.webdriver(知乎)(编辑于 2021-07-14 13:42)](https://zhuanlan.zhihu.com/p/117506307)
  - [~~Google翻译~~](https://translate.google.cn/)
