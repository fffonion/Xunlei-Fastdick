迅雷快鸟
===
一个可以运行在路由器的迅雷快鸟(diǎo)客户端

# 快速入门
* 同目录下新建 __swjsq.account.txt__，填入`用户名,密码`，如`ahaha,123456`（英文逗号），并保存
* python ./swjsq.py &

# 详细使用方法

### 能安装Python的路由器

以小米路由为例

* 开启SSH
* 安装Python
* 将[swjsq.py](https://github.com/fffonion/Xunlei-Fastdick/raw/master/swjsq.py)通过[WinSCP](https://winscp.net/eng/download.php)拷贝到路由`/data/usr/bin/swjsq`，同目录下新建 __swjsq.account.txt__，填入`用户名,密码`，如`ahaha,123456`（英文逗号），并保存
* 使用SSH进入目录`/data/usr/bin/swjsq`，运行`$ python ./swjsq.py`
* 测试运行一次看能否提速，提示`Upgrade done: Down xxM, Up xxM`即表示成功
* 设置自启动
     `vi /etc/rc.local`
	 在exit0语句之前加上：
     `nohup python /data/usr/bin/swjsq.py >/dev/null 2>&1 &`
* 重启，稍等几分钟，ssh到路由，使用ps命令查看swjsq是否正常启动，提速是否成功。
* 升级路由器固件后，需要重新设置自启动，swjsq一般不需要重新设置，请注意备份swjsq文件。

### 无法安装Python的路由器

适用于硬件条件有限无法在路由器上安装Python的用户

* 在路由器上安装支持https的wget或curl
* 在PC上安装Python，2.x或3.x版本均可
* 下载[swjsq.py](https://github.com/fffonion/Xunlei-Fastdick/raw/master/swjsq.py)，同目录下新建 __swjsq.account.txt__，填入`用户名,密码`，如`ahaha,123456`（英文逗号），并保存
* 在命令提示符中进入刚才下载的目录，然后运行`python swjsq.py`
* 提示`Upgrade done: Down xxM, Up %xxM`即表示成功登陆成功
* 安装生成的`swjsq_0.0.1_all.ipk`，安装后，路由`/bin`目录将有 __swjsq__文件
* 如果对路由器`/bin`目录的修改重启后会丢失，请使用[WinSCP](https://winscp.net/eng/download.php)手动将前一步中PC上生成的`swjsq_wget.sh`拷贝到路由器上不会丢失的目录，如`/data/usr/bin`，并更名为`swjsq`
* 设置自启动
     `vi /etc/rc.local`
     在exit0语句之前加上：
     `nohup /bin/swjsq >/dev/null 2>&1 &`
     前一步中如果手动拷贝了`swjsq_wget.sh`，此处应改为：
     `nohup /data/usr/bin/swjsq >/dev/null 2>&1 &`
* 重启，稍等几分钟，ssh到路由，使用ps命令查看swjsq是否正常启动，提速是否成功。
* 升级路由器固件后，需要重新设置自启动，swjsq一般不需要重新设置，请注意备份swjsq文件。

# Docker

* 下载最新 docker image

```
docker pull flier/xunlei-fastdick
```

* 指定环境变量作为启动参数

```
docker run -d --name=xunlei-fastdick --restart=unless-stopped -e XUNLEI_UID=<uid> -e XUNLEI_PASSWD=<uid> flier/xunlei-fastdick
```

# 说明
* 生成的`swjsq_wget.sh`和`swjsq_0.0.1_all.ipk`包含了账户信息，请不要共享给他人使用
* 明文存储的密码将会在第一次登陆成功后保存为数字ID和密码的MD5，明文文件将会删除。如果需要更换账号，只需新建一个 __swjsq.account.txt__，并重新运行python脚本
* 如果修改或更新了python脚本，下次运行时将重新生成ipk包和`swjsq_wget.sh`，请重新安装ipk或拷贝`swjsq_wget.sh`到路由器
* 会员权限及月加速流量等详见[这里](http://swjsq.xunlei.com)
* 自带[这里抄的](https://github.com/mengskysama/XunLeiCrystalMinesMakeDie/blob/master/run.py)纯python实现RSA加密，可选安装pycrypto加快(首次)运算速度

# TODO
* session过期时间
* web前端
