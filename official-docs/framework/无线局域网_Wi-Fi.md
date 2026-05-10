# 无线局域网 (Wi-Fi)

来源: https://developers.weixin.qq.com/miniprogram/dev/framework/device/wifi.html

#
无线局域网 (Wi-Fi)
在小程序中支持搜索周边的 Wi-Fi 设备，同时可以针对指定设备，传入密码发起连接。
该系列接口为系统原生能力，如需查看「微信连 Wi-Fi」能力及配置跳转小程序，请参考
文档
。
#
1. 连接指定 Wi-Fi 设备
如果知道 Wi-Fi 设备名称和密码，并确认设备在附近，可以直接在小程序中连接指定 Wi-Fi。
接口调用时序为：
startWifi
: 初始化 Wi-Fi 模块
connectWifi
: 连接 Wi-Fi（iOS 需 11 及以上版本支持）
onWifiConnected
: 连接上 Wi-Fi 的事件回调
#
2. 连接周边 Wi-Fi 设备
小程序可以通过扫描附近的 Wi-Fi 设备，让用户选择某个设备进行连接。
由于系统限制，不同平台下接口调用时序有所差异：
Android
startWifi
: 初始化 Wi-Fi 模块
getWifiList
: 请求获取周边 Wi-Fi 列表
onGetWifiList
: 获取到 Wi-Fi 列表数据事件
connectWifi
: 连接 Wi-Fi
onWifiConnected
: 连接上 Wi-Fi 的事件回调
iOS
startWifi
: 初始化 Wi-Fi 模块
getWifiList
: 请求获取周边 Wi-Fi 列表。本接口会跳转到系统设置中的微信设置页，需引导用户进入「无线局域网」设置页，手动连接设备。（iOS 11.0 及 11.1 版本因系统问题失效）
onGetWifiList
: 获取到 Wi-Fi 列表数据事件
setWifiList
: 设置 Wi-Fi 列表 中 AP 的相关信息，辅助用户进行连接
onWifiConnected
: 连接上 Wi-Fi 的事件回调
#
3. Wi-Fi 网络下的设备通信
通过
wx.getConnectedWifi
可以获取当前系统连接 Wi-Fi 信息，在确认当前连接是设备 Wi-Fi 后（手机与设备处于同一局域网），便可以使用相关接口与设备进行通信。
使用
wx.startLocalServiceDiscovery
等一系列 mDNS API ，可以获取局域网内提供 mDNS 服务的设备 IP 。然后通过
wx.request
/
wx.connectSocket
并传入格式为
`${IP}:${PORT}/${PATH}`
的 url 参数，就可以进行本地 HTTP / WebSocket 通信。详细文档参考「
局域网通信
」。
开发者根据具体设备的情况，在知道与设备通信的 ip address 和 port 之后，使用
TCPSocket.connect
或
UDPSocket.connect
就能与设备进行 TCP 或 UDP 通信。详细文档参考「
TCP 通信
」与「
UDP 通信
」。
#
4. 注意事项
Android 系统 6.0 以上版本，在没有打开定位开关的时候会导致设备不能正常获取周边的 Wi-Fi 信息。
Wi-Fi 相关接口暂不可用
wx.canIUse
接口判断。