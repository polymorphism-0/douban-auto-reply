# douban-auto-reply
豆瓣自动回复机器人

### 通过豆瓣的API获得小组最新的发帖并自动回复
* 豆瓣没有直接公开API，所以需要利用豆瓣app使用的接口，并且在手机上抓包获得credentials
* 手机抓包的方法请根据自己的系统自行搜索
  * 抓登陆包（POST /service/auth2/token HTTP/1.1），找到client_secret
  * 抓刷新小组首页时的包，找到headers和设备信息
* 相比爬虫豆瓣网页版并回复的优势：没有验证码，并且利用的是豆瓣现成的API接口


### 使用方法
* 安装requirements：pip3 install -r requirements.txt
* 抓包，在config.py里填入需要设置的值
* 启动IP代理池：python3 IPProxyPool/IPProxy.py （需要一直在后台运行）
* 运行主程序：python3 autoreply.py


### 项目结构
* IPProxyPool/: 为了避免引发反爬虫机制，需要经常换IP。直接用的这个IP代理池的代码：https://github.com/qiyeboy/IPProxyPool
* util/： wrappers for logger and IP proxy（logger的代码来源：https://github.com/echoTheLiar/DoubanAuto）
* config.py: 配置信息
* autoreply.py：主程序，每隔一段时间刷新小组首页，并且回复0回复的帖子


### Tips:
* 关爱豆瓣服务器，不要过于频繁地发送请求
* 使用一个绑定了手机的老号作为回帖机器人的账号，新号被封禁的几率更大

