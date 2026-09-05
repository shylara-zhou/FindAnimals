Page({
  data: {
    userInfo: {}
  },
  onLoad() {
    this.refreshUserInfo()
  },
  onShow() {
    this.refreshUserInfo()
  },
  refreshUserInfo() {
    const token = wx.getStorageSync('token')
    const stored = wx.getStorageSync('userInfo') || {}
    if (token && stored.nickName) {
      this.setData({ userInfo: stored })
    } else {
      this.setData({ userInfo: {} })
    }
  },
  goUpload() {
    wx.navigateTo({ url: '/pages/animal/upload/upload' })
  },
  goMyUploads() {
    wx.navigateTo({ url: '/pages/mine/my_uploads/my_uploads' })
  },
  goAbout() {
    wx.navigateTo({ url: '/pages/mine/about/about' })
  },
  logout() {
    wx.showModal({
      title: '确认退出',
      content: '确定要退出登录吗？',
      success: (res) => {
        if (res.confirm) {
          const token = wx.getStorageSync('token')
          this.setData({ userInfo: {} })
          if (token) {
            wx.request({
              url: 'https://wulara.top/api/logout/',
              method: 'POST',
              header: {
                'content-type': 'application/json',
                'Authorization': `Token ${token}`
              },
              complete: () => {
                wx.removeStorageSync('token')
                wx.removeStorageSync('user_id')
                wx.removeStorageSync('userInfo')
                const app = getApp()
                app.globalData.userInfo = {}
                wx.switchTab({
                  url: '/pages/home/home'
                })
              }
            })
          } else {
            wx.removeStorageSync('userInfo')
            const app = getApp()
            app.globalData.userInfo = {}
            wx.switchTab({
              url: '/pages/home/home'
            })
          }
        }
      }
    })
  }
})