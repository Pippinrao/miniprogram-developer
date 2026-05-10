# wx.request 网络请求

来源: https://developers.weixin.qq.com/miniprogram/dev/api/network/request/wx.request.html

## wx.request(Object object)
发起 HTTPS 网络请求。

### 参数
| 属性 | 类型 | 默认值 | 必填 | 说明 |
|------|------|--------|------|------|
| url | string | | 是 | 开发者服务器接口地址 |
| data | string/object/ArrayBuffer | | 否 | 请求的参数 |
| header | Object | | 否 | 设置请求的 header |
| method | string | GET | 否 | HTTP 请求方法：GET/POST/PUT/DELETE/OPTIONS/HEAD/TRACE/CONNECT |
| dataType | string | json | 否 | 返回的数据格式：json（返回的数据为 JSON）/其他（不对返回内容进行处理） |
| responseType | string | text | 否 | 响应的数据类型：text/arraybuffer |
| timeout | number | 60000 | 否 | 超时时间，单位毫秒 |
| success | function | | 否 | 接口调用成功的回调函数 |
| fail | function | | 否 | 接口调用失败的回调函数 |
| complete | function | | 否 | 接口调用结束的回调函数 |

### success 返回参数
| 参数 | 类型 | 说明 |
|------|------|------|
| data | string/Object/ArrayBuffer | 服务器返回的数据 |
| statusCode | number | HTTP 状态码 |
| header | Object | 响应头 |
| cookies | Array.<string> | 返回的 cookies |

### 示例代码
```javascript
wx.request({
  url: 'https://api.example.com/data',
  method: 'POST',
  data: { key: 'value' },
  header: { 'content-type': 'application/json' },
  success(res) {
    console.log('状态码:', res.statusCode)
    console.log('响应数据:', res.data)
  },
  fail(err) {
    console.error('请求失败:', err)
  }
})
```

### 注意
- 需要在小程序管理后台配置 request 合法域名
- 最大并发限制：10 个（wx.request、wx.uploadFile、wx.downloadFile 的总和）
- 默认超时时间和最大超时时间都是 60s
