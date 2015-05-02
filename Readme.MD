迅雷快鸟
===
一个可以运行在路由器的迅雷快鸟(diǎo)客户端

# 怎么play
* 买买买 http://pay.vip.xunlei.com/baijin.html
* $ git clone git@github.com:fffonion/Xunlei-FastDick.git && cd Xunlei-FastDick
* 新建 __swjsq.account.txt__，填入`用户名,密码`，如`ahaha,123456`，并保存
* Python 2.x or Python3.x
* $ nohup python ./swjsq.py &

# 说明
* 明文存储的密码将会在第一次登陆成功后保存为数字ID和密码的MD5，明文文件将会删除
* 需要迅雷白金会员或普通会员VIP6及以上，不能使用子账号
* 自带[这里抄的](https://github.com/mengskysama/XunLeiCrystalMinesMakeDie/blob/master/run.py)纯python实现RSA加密，可选安装pycrypto加快(首次)运算速度

# TODO
* session过期时间
*　lua版
*　wget版

