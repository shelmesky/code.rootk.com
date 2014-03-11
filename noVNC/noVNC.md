### 介绍

通俗的说：

[noVNC]提供一种在网页上通过html5的Canvas，访问机器上vncserver提供的vnc服务，需要做tcp到websocket的转化，才能在html5中显示出来。
网页就是一个客户端，类似与vncviewer。但直接访问的不是VNCServer，而是noVNC服务器，它提供了VNC协议到WebSocket之间的转换。

[noVNC]: https://github.com/kanaka/noVNC

通过下图可能看得更清楚一些：


可以很清楚的看到，noVNC服务器是在将VNC协议的数据打包到WebSocket协议中，发送给浏览器。
并将从浏览器WebSocket连接中读取到的数据发送给VNC服务器。可以说，noVNC服务器是一个VNC代理，在浏览器和VNC服务器之间架起了一个桥梁。

### 问题

但是noVNC并不是完美的，它还存在以下问题：

+ 基于进程的并发，每个在独立的进程中被处理
+ 对后端VNC服务器的连接只包装了OpenStack
+ 自带的对VNC数据的记录和回放比较原始，容易产生性能问题

### 问题解决

#### 解决方案

+ 将基于进程的并发改为基于轻量Greenlet的并发，使用Gevent支持，提高并发性能
+ 增加对XenServer虚拟机VNC控制台的连接
+ 将VNC数据的记录通过TCP协议发送到远端服务器记录，并增加数据管理
+ 将VNC数据的回放通过远端服务器提供

#### 架构图

#### 屏幕截图

##### XenServer Linux虚拟机VNC控制台

##### XenServer Windows虚拟机VNC控制台

##### XenServer 虚拟机VNC记录文件

##### XenServer 虚拟机VNC回放和暂停


