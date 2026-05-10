# form 表单

来源: https://developers.weixin.qq.com/miniprogram/dev/component/form.html

## form
表单组件。将组件内的用户输入的 switch input checkbox slider radio picker 提交。

### 属性
| 属性 | 类型 | 默认值 | 必填 | 说明 |
|------|------|--------|------|------|
| report-submit | boolean | false | 否 | 是否返回 formId 用于发送模板消息 |
| report-submit-timeout | number | 0 | 否 | 等待一段时间（毫秒数）以确认 formId 是否生效 |
| bindsubmit | eventhandle | | 否 | 携带 form 中的数据触发 submit 事件，event.detail = {value: {'name': 'value'}, formId: ''} |
| bindreset | eventhandle | | 否 | 表单重置时会触发 reset 事件 |

### 示例代码
```html
<form bindsubmit="formSubmit" bindreset="formReset">
  <view class="section">
    <input name="input" placeholder="请输入内容" />
  </view>
  <button form-type="submit">提交</button>
  <button form-type="reset">重置</button>
</form>
```

```js
Page({
  formSubmit(e) {
    console.log('form发生了submit事件，携带数据为：', e.detail.value)
  },
  formReset() {
    console.log('form发生了reset事件')
  }
})
```

### 注意
- button 的 form-type 属性用于控制表单内 button 的行为：submit（提交表单）/ reset（重置表单）
- 当点击 form 表单中 form-type 为 submit 的 button 组件时，会将表单组件中的 value 值进行提交
