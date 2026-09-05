Page({
  data: {
    list: []
  },
  onShow() {
    this.fetchMyUploads()
  },
  formatStatus(status) {
    const map = { pending: '待审核', approved: '已通过', rejected: '已拒绝' }
    return map[status] || status
  },
  fetchMyUploads() {
    const token = wx.getStorageSync('token')
    if (!token) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }
    wx.request({
      url: 'https://wulara.top/api/my/animals/',
      method: 'GET',
      header: { 'Authorization': 'Token ' + token },
      success: res => {
        if (res.data && res.data.code === 200) {
          const list = (res.data.data || []).map(item => ({
            ...item,
            created_at_display: this.formatTime(item.created_at)
          }))
          this.setData({ list })
        }
      }
    })
  },
  formatTime(isoStr) {
    if (!isoStr) return ''
    const d = new Date(isoStr)
    if (isNaN(d.getTime())) return ''
    const Y = d.getFullYear()
    const M = String(d.getMonth() + 1).padStart(2, '0')
    const D = String(d.getDate()).padStart(2, '0')
    const h = String(d.getHours()).padStart(2, '0')
    const m = String(d.getMinutes()).padStart(2, '0')
    return `${Y}-${M}-${D} ${h}:${m}`
  },
  viewDetail(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({ url: '/pages/animal/detail?id=' + id })
  }
})