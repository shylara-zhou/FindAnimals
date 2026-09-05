Page({
  data: {
    parkId: null,
    parkName: '',
    parkCover: '',
    animals: [],
    loading: true,
    keyword: ''
  },
  onLoad: function(options) {
    const parkId = options.park_id || null;
    const parkName = options.park_name || '';
    const parkCover = options.park_cover ? decodeURIComponent(options.park_cover) : '';
    this.setData({ parkId, parkName, parkCover });
    this.fetchAnimals();
  },
  fetchAnimals: function() {
    const { parkId } = this.data;
    if (!parkId) {
      this.setData({ loading: false });
      return;
    }
    wx.request({
      url: 'https://wulara.top/api/animals/by_park/?park_id=' + parkId,
      method: 'GET',
      success: res => {
        if (res.data.code === 200) {
          this.setData({ animals: res.data.data, loading: false })
        }
      },
      fail: () => this.setData({ loading: false })
    })
  },
  onKeywordInput: function(e) {
    this.setData({ keyword: e.detail.value })
  },
  doSearch: function() {
    const { keyword, parkId } = this.data;
    const kw = keyword && keyword.trim();
    if (!kw) {
      wx.showToast({ title: '请输入关键词', icon: 'none' })
      return;
    }
    const qs = `keyword=${encodeURIComponent(kw)}${parkId ? '&park_id=' + parkId : ''}`
    wx.request({
      url: 'https://wulara.top/api/animals/search/?' + qs,
      method: 'GET',
      success: res => {
        if (res.data.code === 200) {
          this.setData({ animals: res.data.data })
        }
      }
    })
  },
  viewDetail: function(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/animal/detail?id=' + id })
  }
})