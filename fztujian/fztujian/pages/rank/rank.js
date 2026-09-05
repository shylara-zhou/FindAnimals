Page({
  data: {
    animals: [],
    loading: true
  },
  onLoad: function (options) {
    this.fetchRanking();
  },
  fetchRanking: function() {
    wx.request({
      url: 'https://wulara.top/api/animals/ranking/?sort_type=1', // 1=Hot (views)
      method: 'GET',
      success: res => {
        if (res.data.code === 200) {
          this.setData({
            animals: res.data.data,
            loading: false
          });
        }
      }
    });
  },
  viewDetail: function(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({
      url: '/pages/animal/detail?id=' + id
    })
  }
})