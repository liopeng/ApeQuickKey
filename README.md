# 猿快键-2.0

[TOC]

## 软件介绍

- 软件主要功能写完了，包括快捷键**快速打开控制台/资源管理器**，**禁用按键/快捷键/鼠标**<img style="width:30px;" src="./assets/025087d4b31c8701e8cafb8c307f9e2f0708ff7b.png" alt="img" />。

- 支持**开机自启，解压即可使用**。
- 主要是给**程序员**使用的。
- 界面是使用pyside6写的，控制键盘和鼠标用到了Python和C/C++。
- 因为是没事瞎写的，所以界面比较垃圾<img style="width:30px;" src="./assets/025087d4b31c8701e8cafb8c307f9e2f0708ff7b.png" alt="img" />。



### 技术介绍

- **虚拟键码**
  - [windows系统官方键码链接](https://learn.microsoft.com/zh-cn/windows/win32/inputdev/virtual-key-codes)
  - [虚拟键码表/104键键盘键码表](https://blog.csdn.net/m0_74389553/article/details/144358199?fromshare=blogdetail&sharetype=blogdetail&sharerId=144358199&sharerefer=PC&sharesource=m0_74389553&sharefrom=from_link)
- **C/C++ windows系统下禁用按键/快捷键/鼠标**
  - [C/C++ windows系统下禁用按键/快捷键/鼠标](https://blog.csdn.net/m0_74389553/article/details/144369659?fromshare=blogdetail&sharetype=blogdetail&sharerId=144369659&sharerefer=PC&sharesource=m0_74389553&sharefrom=from_link)

- **python监控按键/快捷键/鼠标**
  - [python监控按键/快捷键/鼠标](https://blog.csdn.net/m0_74389553/article/details/144476696?fromshare=blogdetail&sharetype=blogdetail&sharerId=144476696&sharerefer=PC&sharesource=m0_74389553&sharefrom=from_link)



### 功能介绍

#### 快捷键快速打开控制台/资源管理器

- **快捷键**可以设置为**键盘按键/快捷键/鼠标前进键/鼠标后退键**

![image-20241215185851549](./assets/image-20241215185851549.png)

- **禁止其他应用使用已录制的快捷键**会使你在上面勾选的快捷键**只能被本程序使用**

![image-20241215185952615](./assets/image-20241215185952615.png)



- 可以设置**控制台/资源管理器**打开的**默认路径**，使用快捷键会从**打开到设置的路径**

![image-20241215190141186](./assets/image-20241215190141186.png)

- 如果你想打开**控制台/资源管理器**到**当前打开的资源管理器的路径**，可以**勾选下面按钮**

![image-20241215190333136](./assets/image-20241215190333136.png)



#### 禁用按键/快捷键/鼠标

##### 下面的操作请谨慎使用，尤其是设置开机自启动情况下！！！

- 点击**添加快捷键**就会在左边添加一个快捷键的输入框

![image-20241215190822590](./assets/image-20241215190822590.png)

- 勾选**左侧按钮**则表示**开启这个快捷键**（前提是开启本功能）
- **点击快捷键框**就可以**录入快捷键**
- 点击**右侧删除按钮**可以**删除快捷键**

![image-20241215190942044](./assets/image-20241215190942044.png)

- **勾选启用此功能**并**保存重启**才会**开启功能**

![image-20241215191204547](./assets/image-20241215191204547.png)

- 禁用鼠标，没什么讲的，看图即可

![image-20241215190606065](./assets/image-20241215190606065.png)
