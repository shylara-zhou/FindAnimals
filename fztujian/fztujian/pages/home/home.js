Page({
  data: {
    parks: [],
    loading: true,
    searchKeyword: '',
    searchResults: [],
    isLoggedIn: false,
    userInfo: {}
  },
  onLoad: function (options) {
    this.checkLoginStatus();
    this.fetchParks();
  },
  onShow: function() {
    this.checkLoginStatus();
  },
  checkLoginStatus: function() {
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo') || {};
    this.setData({
      isLoggedIn: !!token,
      userInfo: userInfo
    });
  },
  goLogin: function() {
    wx.navigateTo({
      url: '/pages/index/index'
    });
  },
  goMine: function() {
    wx.switchTab({
      url: '/pages/mine/mine'
    });
  },
  fetchParks: function() {
    wx.request({
      url: 'https://wulara.top/api/parks/',
      method: 'GET',
      success: res => {
        if (res.data.code === 200) {
          this.setData({ parks: (res.data.data || []), loading: false });
        }
      }
    });
  },
  viewAnimals: function(e) {
      const parkId = e.currentTarget.dataset.id;
      const parkName = e.currentTarget.dataset.name;
      const parkCover = e.currentTarget.dataset.cover || '';
      wx.navigateTo({
          url: '/pages/home/animals/animals?park_id=' + parkId + '&park_name=' + parkName + '&park_cover=' + encodeURIComponent(parkCover)
      })
  },
  onSearchInput: function(e) {
    this.setData({ searchKeyword: e.detail.value })
  },
  doGlobalSearch: function() {
    const keyword = this.data.searchKeyword && this.data.searchKeyword.trim();
    if (!keyword) {
      wx.showToast({ title: '请输入关键词', icon: 'none' })
      return;
    }
    wx.request({
      url: 'https://wulara.top/api/animals/search/?keyword=' + encodeURIComponent(keyword),
      method: 'GET',
      success: res => {
        if (res.data.code === 200) {
          this.setData({ searchResults: res.data.data })
        }
      }
    })
  },
  viewDetail: function(e) {
    const id = e.currentTarget.dataset.id;
    wx.navigateTo({ url: '/pages/animal/detail?id=' + id })
  }
})