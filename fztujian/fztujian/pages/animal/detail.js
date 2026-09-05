Page({
  data: {
    id: null,
    animal: {},
    animalTimeDisplay: '',
    comments: [],
    commentText: '',
    commentImage: '',
    commentPage: 1,
    commentTotalPages: 1,
    commentTotal: 0,
    loadingComments: false,
    refreshing: false
  },
  onLoad: function(options) {
    const { id } = options || {};
    if (!id) {
      wx.showToast({ title: '缺少ID', icon: 'none' });
      return;
    }
    this.setData({ id, commentPage: 1 });
    this.fetchDetail();
    this.fetchComments();
  },
  fetchDetail: function() {
    const id = this.data.id;
    wx.request({
      url: 'https://wulara.top/api/animals/' + id + '/',
      method: 'GET',
      success: res => {
        if (res.data.code === 200) {
          const animal = res.data.data
          // 上传/发现时间显示（优先发现时间，其次创建时间）
          const timeStr = animal.discovered_at || animal.created_at || ''
          this.setData({
            animal,
            animalTimeDisplay: timeStr ? this.formatTime(timeStr) : ''
          })
        }
      }
    })
  },
  fetchComments: function(pageArg) {
    const id = this.data.id;
    const token = wx.getStorageSync('token')
    const headers = token ? { 'Authorization': 'Token ' + token } : {}
    const page = Number(pageArg || this.data.commentPage || 1)
    this.setData({ loadingComments: true })
    wx.request({
      url: 'https://wulara.top/api/comments/?animal=' + id + '&page=' + page,
      method: 'GET',
      header: headers,
      success: res => {
        if (res.statusCode === 401) {
          wx.showToast({ title: '请先登录后查看评论', icon: 'none' })
          this.setData({ loadingComments: false })
          return
        }
        if (res.data && res.data.code === 200) {
          const list = (res.data.data || []).map(item => ({
            ...item,
            created_at_display: this.formatTime(item.created_at)
          }))
          const pagination = res.data.pagination || {}
          const nextData = page === 1 ? list : (this.data.comments || []).concat(list)
          this.setData({
            comments: nextData,
            commentPage: pagination.page || page || 1,
            commentTotalPages: pagination.total_pages || 1,
            commentTotal: pagination.total || nextData.length,
            loadingComments: false
          })
        }
      },
      fail: () => {
        this.setData({ loadingComments: false })
        wx.showToast({ title: '评论加载失败', icon: 'none' })
      },
      complete: () => {
        if (this.data.refreshing) {
          wx.stopPullDownRefresh()
          this.setData({ refreshing: false })
        }
      }
    })
  },
  formatTime: function(isoStr) {
    if (!isoStr) return ''
    const d = new Date(isoStr)
    const Y = d.getFullYear()
    const M = String(d.getMonth() + 1).padStart(2, '0')
    const D = String(d.getDate()).padStart(2, '0')
    const h = String(d.getHours()).padStart(2, '0')
    const m = String(d.getMinutes()).padStart(2, '0')
    return `${Y}-${M}-${D} ${h}:${m}`
  },
  onCommentInput: function(e) {
    this.setData({ commentText: e.detail.value })
  },
  // 选择评论配图
  chooseCommentImage: function() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: res => {
        const path = (res.tempFilePaths || [])[0]
        if (path) this.setData({ commentImage: path })
      }
    })
  },
  removeCommentImage: function() {
    this.setData({ commentImage: '' })
  },
  // 预览已选的本地图片
  previewCommentImage: function() {
    if (!this.data.commentImage) return
    wx.previewImage({ urls: [this.data.commentImage] })
  },
  // 预览评论里的图片（网络图）
  previewCommentPhoto: function(e) {
    const url = e.currentTarget.dataset.url
    if (url) wx.previewImage({ urls: [url] })
  },
  sendComment: function() {
    const token = wx.getStorageSync('token')
    const userId = wx.getStorageSync('user_id')
    if (!token || !userId) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }

    // Client-side rate limit: 1 minute
    const lastSubmitTime = wx.getStorageSync('last_submit_time_comment') || 0
    const now = Date.now()
    if (now - lastSubmitTime < 60000) {
      const remaining = Math.ceil((60000 - (now - lastSubmitTime)) / 1000)
      wx.showToast({ title: `请稍等 ${remaining} 秒再试`, icon: 'none' })
      return
    }

    const content = (this.data.commentText || '').trim()
    const hasImage = !!this.data.commentImage
    if (!content && !hasImage) {
      wx.showToast({ title: '说点什么或配张图吧', icon: 'none' })
      return
    }

    // —— 分支A：带图片的评论，走 multipart 上传，图片需审核 ——
    if (hasImage) {
      wx.showLoading({ title: '提交中...', mask: true })
      wx.uploadFile({
        url: 'https://wulara.top/api/comments/',
        filePath: this.data.commentImage,
        name: 'photo',
        header: { 'Authorization': 'Token ' + token },
        formData: {
          animal: String(this.data.id),
          user_id: String(userId),
          content: content
        },
        success: res => {
          wx.hideLoading()
          let body = null
          try { body = JSON.parse(res.data) } catch (e) { body = res.data }
          if (body && body.code === 200) {
            wx.setStorageSync('last_submit_time_comment', Date.now())
            this.setData({ commentText: '', commentImage: '', commentPage: 1, comments: [] })
            // 图片评论需要审核：明确告知用户
            const pending = body.data && body.data.photo_audit_status === 'pending'
            wx.showModal({
              title: pending ? '提交成功 🎉' : '发布成功',
              content: pending
                ? '您的图片评论已提交，等待wulara审核通过后就会显示出来，谢谢您的分享！'
                : '评论发布成功',
              showCancel: false,
              confirmText: '知道了',
              confirmColor: '#16a34a'
            })
            this.fetchComments(1)
          } else {
            const msg = (body && (body.msg || body.detail)) || '图片评论发布失败'
            wx.showToast({ title: String(msg).slice(0, 30), icon: 'none' })
          }
        },
        fail: () => {
          wx.hideLoading()
          wx.showToast({ title: '网络错误', icon: 'none' })
        }
      })
      return
    }

    // —— 分支B：纯文字评论 ——
    wx.request({
      url: 'https://wulara.top/api/comments/',
      method: 'POST',
      header: {
        'content-type': 'application/json',
        'Authorization': 'Token ' + token
      },
      data: {
        animal: Number(this.data.id),
        user_id: userId,
        content
      },
      success: res => {
        if (res.data && res.data.code === 200) {
          wx.setStorageSync('last_submit_time_comment', Date.now())
          wx.showToast({ title: '已发布', icon: 'success' })
          this.setData({ commentText: '', commentPage: 1, comments: [] })
          this.fetchComments(1)
        } else {
          wx.showToast({ title: res.data.msg || '发布失败', icon: 'none' })
        }
      },
      fail: () => wx.showToast({ title: '网络错误', icon: 'none' })
    })
  },
  loadMoreComments: function() {
    if (this.data.loadingComments) return
    const { commentPage, commentTotalPages, commentTotal } = this.data
    if (!commentTotal || Number(commentTotal) === 0) {
      wx.showToast({ title: '暂无评论', icon: 'none' })
      return
    }
    if (Number(commentPage) >= Number(commentTotalPages)) {
      wx.showToast({ title: '已到底', icon: 'none' })
      return
    }
    const nextPage = Number(commentPage) + 1
    this.setData({ commentPage: nextPage })
    this.fetchComments(nextPage)
  },
  onReachBottom: function() {
    this.loadMoreComments()
  },
  onPullDownRefresh: function() {
    this.setData({
      refreshing: true,
      commentPage: 1,
      comments: [],
      commentTotalPages: 1,
      commentTotal: 0
    })
    this.fetchComments(1)
  }
})