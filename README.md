# pyfileconf

## 简介
pyfileconf可以使用文件配置多服务器下的supervisor等服务

项目里常用supervisor管理daemon服务，但是多台机器管理起来就比较困难了。为了统一管理，使用统一的文件配置方式就比较方便的。

服务开启后，会监控配置文件变化，如果文件变化则相应启动或关闭surpervisor下的项目。另外每分钟会检测服务，保证状态一致。

## 说明

~~~
python pyfileconf.py file_path
~~~

## 配置
* is_client  默认值 true，如果true，在每台服务器都需要部署本项目，好处是减少网络流量。如果false，只需在一台机器部署即可，但是需要能够访问每台机器
* supervisor_authorize supervisor用户名和密码
* supervisor_port supervisor端口
* servers 服务器，详见example.json

## 感谢
本项目里使用了第三方模块：
* apscheduler
* pyinotify