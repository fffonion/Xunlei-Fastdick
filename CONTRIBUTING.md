# 提交issue

如果你要报告一个问题，请同时注明：

- 所使用的版本 (Python/Shell)
- 运行的系统环境及版本 (操作系统，Python版本等)
- 包含错误信息的日志
- 产生错误的操作步骤
- (可选) 运营商所在地，如：上海电信


# 提示“您的帐号存在异常,请登录安全中心确认”的排查方法

1. 登陆迅雷下载客户端、迅雷快鸟客户端是否需要验证码？如果是且长期出现，请向迅雷客服反映。
2. 是否频繁多次启动脚本？无论Python还是shell脚本每次打开均会登陆一次迅雷，如果频繁操作很可能被误判。请停止使用脚本12小时后再试。
3. 是否使用了旧版本的脚本？错误信息中若存在`'protocolVersion': 101`，则说明您使用了旧版本的脚本，请[下载新版](https://github.com/fffonion/Xunlei-Fastdick/raw/master/swjsq.py)
4. 参考[这个issue](https://github.com/fffonion/Xunlei-Fastdick/issues/97#issuecomment-313318849)，是否使用了类似的固件或者启动脚本
5. 如果以上均为否，请提交issue或至[博客](https://yooooo.us/2015/xunlei-fastdick-router#comments)留言
