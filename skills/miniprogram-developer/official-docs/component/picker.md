# picker 选择器

来源: https://developers.weixin.qq.com/miniprogram/dev/component/picker.html

## picker
从底部弹起的滚动选择器。

### 属性
| 属性 | 类型 | 默认值 | 必填 | 说明 |
|------|------|--------|------|------|
| mode | string | selector | 否 | 选择器类型：selector（普通选择器）、multiSelector（多列选择器）、time（时间选择器）、date（日期选择器）、region（省市区选择器） |
| disabled | boolean | false | 否 | 是否禁用 |
| bindchange | eventhandle | | 否 | value 改变时触发 change 事件，event.detail = {value} |
| bindcancel | eventhandle | | 否 | 取消选择时触发 |

### mode = selector（普通选择器）
| 属性 | 类型 | 说明 |
|------|------|------|
| range | array/object array | mode为selector或multiSelector时有效 |
| range-key | string | 当range是一个Object Array时，通过range-key来指定Object中key的值作为选择器显示内容 |
| value | number | 表示选择了range中的第几个（下标从0开始） |

### mode = date（日期选择器）
| 属性 | 类型 | 说明 |
|------|------|------|
| value | string | 表示选中的日期，格式为"YYYY-MM-DD" |
| start | string | 表示有效日期范围的开始 |
| end | string | 表示有效日期范围的结束 |
| fields | string | 有效值 year/month/day |

### 示例代码
```html
<picker mode="date" value="{{date}}" start="2020-01-01" end="2030-12-31" bindchange="bindDateChange">
  <view>当前选择: {{date}}</view>
</picker>
```

```js
Page({
  data: { date: '2026-01-01' },
  bindDateChange(e) { this.setData({ date: e.detail.value }) }
})
```
