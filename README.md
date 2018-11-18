迅雷快鸟
===
一个可以运行在路由器的迅雷快鸟(diǎo)和上行提速客户端

在提交issue前，请先阅读[须知](https://github.com/fffonion/Xunlei-Fastdick/blob/master/CONTRIBUTING.md)

# 快速入门
* 同目录下新建 __swjsq.account.txt__，填入`用户名,密码`，如`ahaha,123456`（英文逗号），并保存
* python ./swjsq.py &

# 详细使用方法

### 能安装Python的路由器

以小米路由为例

1. 开启SSH
2. 安装Python (OpenWRT用户可以安装完整的`python`包，或者安装`python-light`, `python-codecs`和`python-openssl`三个包
3. 将[swjsq.py](https://github.com/fffonion/Xunlei-Fastdick/raw/master/swjsq.py)通过[WinSCP](https://winscp.net/eng/download.php)拷贝到路由`/data/usr/bin/swjsq`，同目录下新建 __swjsq.account.txt__，填入`用户名,密码`，如`ahaha,123456`（英文逗号），并保存
4. 使用SSH进入目录`/data/usr/bin/swjsq`，运行`$ python ./swjsq.py`
5. 测试运行一次看能否提速，提示`Upgrade done: down xxM, up xxM`即表示成功。如果只开启了快鸟会员，则只显示`down xxM`；如果只开启了上行提速会员，则只显示`up xxM`。
6. 设置自启动
     SSH运行`vi /etc/rc.local` 或者进入LuCI的`本地启动脚本`界面：
	 在exit0语句之前加上：
     `nohup python /data/usr/bin/swjsq/swjsq.py >/dev/null 2>&1 &`
7. 重启，稍等几分钟，ssh到路由，使用ps命令查看swjsq是否正常启动，提速是否成功。
8. 升级路由器固件后，需要重新设置自启动，swjsq一般不需要重新设置，请注意备份swjsq文件。

### 无法安装Python的路由器

适用于硬件条件有限无法在路由器上安装Python的用户

1. 在路由器上安装支持https的wget或curl
2. 在PC上安装Python，2.x或3.x版本均可
3. 下载[swjsq.py](https://github.com/fffonion/Xunlei-Fastdick/raw/master/swjsq.py)，同目录下新建 __swjsq.account.txt__，填入`用户名,密码`，如`ahaha,123456`（英文逗号），并保存
4. 在PC的命令提示符中进入刚才下载的目录，然后运行`python swjsq.py`
5. 提示`Upgrade done: down xxM, up %xxM`即表示成功登陆成功。如果只开启了快鸟会员，则只显示`down xxM`；如果只开启了上行提速会员，则只显示`up xxM`。
6. 安装生成的`swjsq_0.0.1_all.ipk`，安装后，路由`/bin`目录将有 __swjsq__ 文件；进入第8步
7. 如果对路由器`/bin`目录的修改重启后会丢失，请使用[WinSCP](https://winscp.net/eng/download.php)手动将前一步中PC上生成的`swjsq_wget.sh`拷贝到路由器上不会丢失的目录，如`/data/usr/bin`，并更名为`swjsq`；进入第9步
8. 设置自启动，在路由器的`启动项`界面将`swjsq`设置为**已启用**；进入第10步
9. 手动修改启动项：
     SSH运行`vi /etc/rc.local`或者进入LuCI的`本地启动脚本`界面：
     在exit0语句之前加上：
     `nohup /bin/swjsq >/dev/null 2>&1 &`
     前一步中如果手动拷贝了`swjsq_wget.sh`，此处应改为：
     `nohup /data/usr/bin/swjsq >/dev/null 2>&1 &`
    进入第10步
10. 重启，稍等几分钟，ssh到路由，使用ps命令查看swjsq是否正常启动，或者在路由器`系统进程`界面查找是否存在`{swjsq} /bin/ash /bin/swjsq`进程；检查提速是否成功。
11. 升级路由器固件后，需要重新设置自启动，swjsq一般不需要重新设置，请注意备份swjsq文件。

# Docker

**下载最新 docker镜像**

```
$ docker pull fffonion/xunlei-fastdick
```

群晖用户可以直接从`套件`->`Docker`->`注册表`中搜索`xunlei-fastdick`并下载；如果拉取失败，可以登录SSH后运行上述命令。


或者使用DaoCloud镜像

```
$ docker pull daocloud.io/fffonion/xunlei-fastdick
```

**指定环境变量作为启动参数**

```
$ docker run -d --name=xunlei-fastdick --restart=unless-stopped -e XUNLEI_UID=<uid> -e XUNLEI_PASSWD=<uid> fffonion/xunlei-fastdick
```

如果上一步使用了DaoCloud镜像

```
$ docker run -d --name=xunlei-fastdick --restart=unless-stopped -e XUNLEI_UID=<uid> -e XUNLEI_PASSWD=<uid> daocloud.io/fffonion/xunlei-fastdick
```

## 编译基于arm32v7内核的镜像(例如运行在树莓派上)

**编译**
```
$ docker build -f Dockerfile.arm32v7 -t yourname/xunlei-fastdick .
```

**运行**
```
$ docker run -d \
    --name=xunlei-fastdick \
    --restart=unless-stopped \
    -e XUNLEI_UID=<uid> \
    -e XUNLEI_PASSWD=<uid> \ 
    yourname/xunlei-fastdick
```

# 说明
* 生成的`swjsq_wget.sh`和`swjsq_0.0.1_all.ipk`包含了账户信息，请不要共享给他人使用
* 程序会查询快鸟和上行提速的到期时间，并自动选择是否开启快鸟提速和上行提速功能
* 第一次登陆成功后，用户名和密码会明文保存在`.swjsq.session`文件中。如果需要更换账号，只需新建一个 __swjsq.account.txt__，并重新运行python脚本
* 如果修改或更新了python脚本，下次运行时将重新生成ipk包和`swjsq_wget.sh`，请重新安装ipk或拷贝`swjsq_wget.sh`到路由器
* 会员权限及月加速流量等详见[这里](http://swjsq.xunlei.com)
* 自带[这里抄的](https://github.com/mengskysama/XunLeiCrystalMinesMakeDie/blob/master/run.py)纯python实现RSA加密，可选安装pycrypto加快(首次)运算速度

# 同类产品
- [mengskysama/yikuuuuu](https://github.com/mengskysama/yikuuuuu)
