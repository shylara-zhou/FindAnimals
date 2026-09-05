// index.js

Page({
  data: {
    motto: 'Hello World',
    userInfo: { nickName: '', avatarUrl: '' },
    hasUserInfo: false,
    loginType: 'quick',
    logging: false,
    showWelcomeLetter: false
  },
  bindViewTap() {
    wx.navigateTo({
      url: '../logs/logs'
    })
  },
  switchLoginType(e) {
    this.setData({
      loginType: e.currentTarget.dataset.type
    })
  },
  onChooseAvatar(e) {
    const avatarUrl = e.detail.avatarUrl
    if (!avatarUrl) {
      return
    }
    this.setData({
      'userInfo.avatarUrl': avatarUrl
    })
  },
  onNicknameInput(e) {
    const nickName = e.detail.value
    this.setData({
      'userInfo.nickName': nickName,
      hasUserInfo: !!nickName
    })
  },
  quickLogin() {
    if (!this.data.userInfo.nickName) {
      wx.showToast({
        title: '请输入昵称',
        icon: 'none'
      })
      return
    }
    wx.request({
      url: 'https://wulara.top/wx_login/',
      method: "GET",
      header:{
        "content-type": "application/x-www-form-urlencoded"
      },
      data: {
        mname: this.data.userInfo.nickName,
      },
      success: res => {
        console.log(res)
        if (res.statusCode == 200 && res.data.code === 200) {
          if (res.data.data && res.data.data.token) {
              wx.setStorageSync('token', res.data.data.token)
              if (res.data.data.user_id) {
                wx.setStorageSync('user_id', res.data.data.user_id)
              }
              const userInfo = {
                nickName: this.data.userInfo.nickName,
                avatarUrl: this.data.userInfo.avatarUrl
              }
              wx.setStorageSync('userInfo', userInfo)
              const app = getApp()
              app.globalData.userInfo = userInfo
              // 新用户首次注册：先展示致读者的一封信；老用户直接进入首页
              if (res.data.data.is_new_user) {
                this.setData({ showWelcomeLetter: true })
              } else {
                wx.showToast({
                    title: '登录成功',
                    icon: 'success',
                    duration: 1500,
                    success: () => {
                      setTimeout(() => {
                          wx.switchTab({
                              url: '../home/home'
                          })
                      }, 1500)
                    }
                })
              }
          }
        } else {
            wx.showToast({
                title: '登录失败: ' + (res.data.msg || '未知错误'),
                icon: 'none'
            })
        }
      },
      fail: err => {
          console.error("Request failed", err)
          wx.showToast({
              title: '网络请求失败',
              icon: 'none'
          })
      }
    })
  },
  wxLogin() {
    if (!this.data.userInfo.nickName) {
      wx.showToast({
        title: '请输入昵称',
        icon: 'none'
      })
      return
    }
    if (this.data.logging) return
    this.setData({ logging: true })

    wx.login({
      success: (res) => {
        if (res.code) {
          this.doWxLogin(res.code)
        } else {
          this.setData({ logging: false })
          wx.showToast({
            title: '登录失败：' + res.errMsg,
            icon: 'none'
          })
        }
      },
      fail: (err) => {
        this.setData({ logging: false })
        console.error('wx.login fail', err)
        wx.showToast({
          title: '微信登录失败',
          icon: 'none'
        })
      }
    })
  },
  doWxLogin(code) {
    wx.request({
      url: 'https://wulara.top/wx/login/',
      method: 'POST',
      header: {
        'content-type': 'application/json'
      },
      data: {
        code: code,
        nickname: this.data.userInfo.nickName
      },
      success: res => {
        this.setData({ logging: false })
        console.log(res)
        if (res.statusCode == 200 && res.data.code === 200) {
          if (res.data.data && res.data.data.token) {
            wx.setStorageSync('token', res.data.data.token)
            if (res.data.data.user_id) {
              wx.setStorageSync('user_id', res.data.data.user_id)
            }
            const userInfo = {
              nickName: res.data.data.nickname || '微信用户',
              avatarUrl: this.data.userInfo.avatarUrl
            }
            wx.setStorageSync('userInfo', userInfo)
            const app = getApp()
            app.globalData.userInfo = userInfo

            // 新用户首次注册：先展示致读者的一封信；老用户直接进入首页
            if (res.data.data.is_new_user) {
              this.setData({ showWelcomeLetter: true })
            } else {
              wx.showToast({
                title: '登录成功',
                icon: 'success',
                duration: 1500,
                success: () => {
                  setTimeout(() => {
                    wx.switchTab({
                      url: '../home/home'
                    })
                  }, 1500)
                }
              })
            }
          }
        } else {
          wx.showToast({
            title: '登录失败: ' + (res.data.msg || '未知错误'),
            icon: 'none'
          })
        }
      },
      fail: err => {
        this.setData({ logging: false })
        console.error("Request failed", err)
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        })
      }
    })
  },
  
  onLoad() {
    const token = wx.getStorageSync('token')
    const storedUserInfo = wx.getStorageSync('userInfo')
    if (token) {
      const app = getApp()
      if (storedUserInfo) {
        app.globalData.userInfo = storedUserInfo
      }
      wx.switchTab({
        url: '../home/home'
      })
      return
    }
    if (storedUserInfo) {
      this.setData({
        userInfo: storedUserInfo,
        hasUserInfo: !!storedUserInfo.nickName
      })
    }
  },
  // 关闭致读者的一封信，进入首页
  closeWelcomeLetter() {
    this.setData({ showWelcomeLetter: false })
    wx.showToast({ title: '注册成功', icon: 'success', duration: 1000 })
    setTimeout(() => {
      wx.switchTab({ url: '../home/home' })
    }, 1000)
  },
  goBack() {
    wx.navigateBack({
      delta: 1,
      fail: () => {
        wx.switchTab({
          url: '../home/home'
        })
      }
    })
  }
})