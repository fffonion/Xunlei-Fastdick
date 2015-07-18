迅雷快鸟
===
一个可以运行在路由器的迅雷快鸟(diǎo)客户端

# 快速入门
* 同目录下新建 __swjsq.account.txt__，填入`用户名,密码`，如`ahaha,123456`，并保存
* python ./swjsq.py &

# 使用方法
以小米路由为例

* 开启SSH
* 安装Python
* 将项目文件通过winscp拷贝到路由临时文件夹，同目录下新建 __swjsq.account.txt__，填入`用户名,密码`，如`ahaha,123456`，并保存
* 进入目录，`$ python ./swjsq.py`
* 安装生成的swjsq_0.0.1_all.ipk，安装后，路由 /tmp/bin 目录将有 swjsq 文件
* 将swjsq移到/data/usr/bin,测试运行一次看能否提速，然后加入到PATH：
     1.`export PATH=$PATH:/data/usr/bin`
     2.`echo 'export PATH=$PATH:/data/usr/bin' >> /etc/profile`
* 设置自启动
     `vi /etc/init.d/usb_deploy_init_script.sh`
	 找到以下两行：
	 1.`rm -rf /tmp/xiaomi_router`
     2.`mkdir -p /tmp/xiaomi_router`
     在下面加入一行命令`/data/usr/swjsq`
* 重启，稍等几分钟，ssh到路由，使用ps命令查看swjsq是否正常启动，提速是否成功。

# 说明
* Python版本可以为2.x或3.x(但是Python3.x没有支持生成ipk包，所以会报一个错（因为作者比较懒
* 如果路由器硬件限制无法安装Python，也可以在PC上运行脚本，登陆成功后会生成`swjsq_wget.sh`以及一个ipk包，将生成的ipk安装进路由器即可
* 如果路由器配置较高，也可以直接用`python ./swjsq.py &`的方式加速，同理修改设置自启动脚本
* 明文存储的密码将会在第一次登陆成功后保存为数字ID和密码的MD5，明文文件将会删除
* 会员权限及月加速流量等详见[这里](http://swjsq.xunlei.com)
* 自带[这里抄的](https://github.com/mengskysama/XunLeiCrystalMinesMakeDie/blob/master/run.py)纯python实现RSA加密，可选安装pycrypto加快(首次)运算速度

# TODO
* session过期时间
* web前端

