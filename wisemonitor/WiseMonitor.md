## 1. 概述
### 1.1 产品功能
**WiseMonitor**是集成基础设施、虚拟化平台、云平台监控报警为一体的监控系统。

对于基础设施支持以下监控功能：

+ 检测主机是否在线
+ 检测主机上运行的服务
+ 主机和服务监控报警
+ 主机和服务性能数据展示
+ 使用插件自定义服务检测
+ 网络设备监控
+ 网络设备流量展示
+ 主机和服务的报警信息通过WEB、SMS方式的实时通知

对于虚拟化平台，支持以下监控功能：

+ XenServer Master/Slaver架构监控
+ XenServer主机详细信息
+ XenServer虚拟机监控
+ XenServer虚拟机CPU Usage、磁盘IO、网卡IO性能数据展示
+ XenServer主机和虚拟机的VNC控制台的访问和回放
+ XenServer报警信息通过WEB、SMS方式的实时通知用户

对于云平台支持支持以下监控功能：

+ CloudStack Zone的列表和详情
+ CloudStack资源使用率展示

### 1.2 面向的用户

**WiseMonitor**面向运营IAAS公有云、私有云的用户，为运维团队提供详细全面的云平台纵深监控。

### 1.3 典型客户
+ 在河南洛阳大学科技园的云平台部署中，**WiseMonitor**监控平台运行稳定，监控效果突出及时 ，获得运维团队的好评。

+ 在山东滕州公安系统政务云平台部署升级中，**WiseMonitor**监控平台替代原有的监控平台，将基础设施、虚拟化平台、云平台的监控集成在一个平台中，实现统一访问。

+ 在[浦软汇智公有云]的运营中，公司的运维团队一致认为**WiseMonitor**超过了原有的Zabbix监控。

[浦软汇智公有云]: http://www.wiseonline.com.cn


## 2. 架构

### 2.1 架构图
<img src="http://127.0.0.1:9999/file/6af7229981a32b8b2910e9b8ef79c2df" width="70%" />

### 2.2 开发语言

**WiseMonitor**混合使用了`Python`、`C`、`Golang`开发。

`Python`代码占`85%`，`C`代码占`10%`，`Golang`代码占`5%`。

### 2.3 模块架构

模块**A**基于**Tornado**实现，提供以下功能：

+ 供用户通过浏览器访问
+ 基于Tornado的IOLoop的异步客户端，包括：MongoDB、RabbitMQ、CloudStack。
+ 在Tornado的IOLoop的驱动下，以异步的方式实现Nagios的报警信息(通过RabbitMQ发送)、CloudStack API访问、Nagios和XenServer的报警信息存储到MongoDB
+ 运行在独立线程中的XenServer告警信息实时获取
+ 告警信息通过长轮询(Comet)技术实现WEB页面中实时通知

模块**B**基于**Gevent**实现，提供以下功能：

+ 提供用户通过支持HTML5 Canvas功能的浏览器访问XenServer主机、虚拟机的**VNC控制台**
+ 记录用户每次访问VNC控制台的数据，将数据通过TCP协议发送到**C**模块保存

模块**C**使用**Golang**语言实现，提供以下功能:

+ 监听在TCP 23457端口，将**B**模块发送来的VNC数据记录成文件
+ 提供HTTP JSON API接口，供用户列出、删除VNC记录文件
+ 使用WebSocket服务器，接受用户浏览器通过WebSocket协议获取VNC记录的数据，并在浏览器端回放

模块**D**本质为使用**C**语言开发的动态共享库，加载到Nagios主进程中，提供以下功能：

+ 注册Nagios的事件回调，监听以下事件：创建、删除主机、服务；主机、服务告警；主机、服务产生性能数据；
+ 将监听到的事件，发送到RabbitMQ服务器，提供给其他模块通过RabbitMQ客户端访问
+ 将监听到的事件，保存到MongoDB中，提供给其他模块访问


## 3. 产品截图
### 3.1 基础设施监控
#### 3.1.1 服务器列表
<img src="http://127.0.0.1:9999/file/e660248549a2341711b07ff8a24ee0ef" height="70%">
#### 3.1.2 添加服务器
<img src="http://127.0.0.1:9999/file/62ac784b24482445b3a0558982415dd9" height="70%">
#### 3.1.3 服务器性能报表
<img src="http://127.0.0.1:9999/file/820cdba297fa57bfc2a6e22074792889" height="70%">
#### 3.1.4 服务列表
<img src="http://127.0.0.1:9999/file/25758792ebd97ee49c6f5eef983a4bac" height="70%">
#### 3.1.5 服务性能报表
<img src="http://127.0.0.1:9999/file/52caea4f05968fb3d01db8c13c86627d" height="70%">
#### 3.1.6 添加网络流量监控服务
<img src="http://127.0.0.1:9999/file/050dd527bbb27231a9ed392a76c3577b" height="70%">
#### 3.1.7 网络流量报表
<img src="" height="70%">

### 3.2 虚拟化监控
#### 3.2.1 XenServer主机列表
<img src="http://127.0.0.1:9999/file/a76c69799c741ecd8008a1231a97f132" height="70%">
#### 3.2.2 XenServer详细信息
<img src="http://127.0.0.1:9999/file/5a311c0d3c9dc9166d8b13a2d1dbcecb" height="70%">
#### 3.2.4 XenServer VNC控制台
<img src="http://127.0.0.1:9999/file/c42a86791c1860a38020d5c74591e296" height="70%">
#### 3.2.4 XenServer VNC控制台回放列表
<img src="http://127.0.0.1:9999/file/9ce615c7fbd09070a4b8f57c3e07d9da" height="70%">
#### 3.2.4 XenServer VNC控制台回放
<img src="http://127.0.0.1:9999/file/1fd867e51763aeb50d9a51cc9987c95d" height="70%">
#### 3.2.5 XenServer虚拟机列表
<img src="http://127.0.0.1:9999/file/8b10b8de56126bc97bb2eea6ebcbaad2" height="70%">
#### 3.2.6 XenServer虚拟机性能报表
<img src="" height="70%">
#### 3.2.7 XenServer虚拟机报警设置
<img src="http://127.0.0.1:9999/file/f717c8a998ca577601df83887045059f" height="70%">
#### 3.2.8 XenServer虚拟机VNC控制台
<img src="http://127.0.0.1:9999/file/95e6005bdf9dc98fa604469b9dc2f5e6" height="70%">
#### 3.2.8 XenServer虚拟机VNC控制台回放列表
<img src="http://127.0.0.1:9999/file/55e63aacf792ddf9c800e0d2f40d083a" height="70%">
#### 3.2.8 XenServer虚拟机VNC控制台回放
<img src="http://127.0.0.1:9999/file/7cd8a9aff1d3aad8ff908d2cd9b9f13e" height="70%">

### 3.3 云平台监控
#### 3.3.1 CloudStack Zone列表
#### 3.3.2 CloudStack Zone的资源使用率
#### 3.3.3 CloudStack Zone的详细信息

### 3.4 报警
#### 3.4.5 物理设备报警
#### 3.4.6 XenServer报警

### 4. 视频演示
