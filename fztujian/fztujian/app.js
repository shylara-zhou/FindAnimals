// app.js
App({
  onLaunch() {
    const logs = wx.getStorageSync('logs') || []
    logs.unshift(Date.now())
    wx.setStorageSync('logs', logs)

    const token = wx.getStorageSync('token')
    const userInfo = wx.getStorageSync('userInfo')
    if (userInfo) {
      this.globalData.userInfo = userInfo
    }
    if (token) {
      this.globalData.token = token
    }
  },
  globalData: {
    userInfo: null,
    token: null
  }
})
