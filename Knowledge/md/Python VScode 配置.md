## [Python VScode 配置](https://www.runoob.com/python3/python-vscode-setup.html)

[index](目录.md)

---
Python VScode 配置
================

在上一章节中我们已经安装了 Python 的环境，本章节我们将介绍 Python VScode 的配置。

准备工作：

* 安装 VS Code
* 安装 VS Code Python 扩展
* 安装 Python 3

### 安装 VS Code

VSCode（全称：Visual Studio Code）是一款由微软开发且跨平台的免费源代码编辑器，VSCode 开发环境非常简单易用。

VSCode 安装也很简单，打开官网
<https://code.visualstudio.com/>
，下载软件包，一步步安装即可，安装过程注意安装路径设置、环境变量默认自动添加到系统中，勾选以下所有选项：

![](https://www.runoob.com/wp-content/uploads/2021/08/RM04TZb.png)

VSCode 完整安装教程参考：
<https://www.runoob.com/vscode/vscode-tutorial.html>

接着我们安装
Python
扩展：

![](https://www.runoob.com/wp-content/uploads/2021/08/de824f4aad280b93a3c54a5a088c81ca.png)

---

创建一个 Python 代码文件
----------------

打开 VScode，然后点击新建文件：

![](https://www.runoob.com/wp-content/uploads/2021/08/vscode-py-1.jpeg)

点击选择语言：

![](https://www.runoob.com/wp-content/uploads/2021/08/vscode-py-2.jpg)

在搜索框输入 Python，选中 Python 选项：

![](https://www.runoob.com/wp-content/uploads/2021/08/vscode-py-3.jpg)

输入代码：

```
print("Runoob")
```

右击鼠标，选择在交互式窗口运行文件，
**如果有提示需要安装扩展，直接点安装即可(没有安装会一直显示在连接 Python 内核)：**

![](https://www.runoob.com/wp-content/uploads/2021/08/vscode-py-4.jpeg)

另外，我们也可以打开一个已存在的文件或目录（文件夹），比如我们打开一个 runoob-test，你也可以自己创建一个：

![](https://www.runoob.com/wp-content/uploads/2021/08/326906F8-C20B-4D76-AC86-FED6544B3DB5.jpeg)

然后我们创建一个 test.py 文件，点击下面新建文件图标，输入文件名 test.py：

![](https://www.runoob.com/wp-content/uploads/2021/08/86278531-3C46-4E05-BBE9-3E76CE82722A.jpg)

**注：**
runoob-test 里面包含了一个
.vscode
文件夹，是一些配置信息，可以先不用管。

在 test.py 输入以下代码：

```
print("Runoob")
```

点击右上角绿色图标，即可运行：

![](https://www.runoob.com/wp-content/uploads/2021/08/438AF06B-6E02-42F0-9062-53337E8E90AD.jpg)

可以右击文件，选择"在终端中运行 Python 文件"：

![](https://www.runoob.com/wp-content/uploads/2021/08/16743E52-BE92-424B-AE7B-F9F602A44462.jpeg)

当然也可以在代码窗口上右击鼠标，选择"在终端中运行 Python 文件"。