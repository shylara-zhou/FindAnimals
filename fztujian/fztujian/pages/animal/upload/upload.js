Page({
  data: {
    parks: [],
    selectedParkId: null,
    selectedParkName: '',
    form: {
      name: '',
      species: '',
      scientific_name: '',
      description: ''
    },
    photoPath: '',
    submitting: false,
    // 名称查重状态：'' | 'checking' | 'available' | 'duplicate' | 'warn'
    nameCheckStatus: '',
    nameCheckMsg: ''
  },
  onLoad() {
    this.fetchParks()
  },
  fetchParks() {
    wx.request({
      url: 'https://wulara.top/api/parks/',
      method: 'GET',
      success: res => {
        if (res.data && res.data.code === 200) {
          this.setData({ parks: res.data.data || [] })
        }
      }
    })
  },
  onParkChange(e) {
    const index = Number(e.detail.value)
    const park = this.data.parks[index]
    if (park) {
      this.setData({ selectedParkId: park.id, selectedParkName: park.name })
    }
  },
  // 名称专用input处理器：内容变更时清除之前的查重结果，避免误导
  onNameInput(e) {
    const value = e.detail.value
    this.setData({
      'form.name': value,
      nameCheckStatus: '',
      nameCheckMsg: ''
    })
  },
  onInput(e) {
    const key = e.currentTarget.dataset.key
    const value = e.detail.value
    this.setData({ [`form.${key}`]: value })
  },
  // 失焦查重（前端体验校验）
  onNameBlur() {
    const name = (this.data.form.name || '').trim()
    if (!name) return
    if (name.length < 2) return
    this._checkNameAndUpdateUI(name)
  },
  // 统一的查重+UI更新方法
  _checkNameAndUpdateUI(name) {
    this.setData({ nameCheckStatus: 'checking', nameCheckMsg: '' })
    return this._callCheckNameApi(name).then(result => {
      // 后端查重接口还没部署/404 → 降级提示warn
      if (result.notReady) {
        this.setData({
          nameCheckStatus: 'warn',
          nameCheckMsg: result.msg || '服务端查重接口暂未启用，提交时会再次校验名称是否重复'
        })
        return { duplicate: false, notReady: true }
      }
      if (result.duplicate) {
        let msg = result.msg || `「${name}」已经存在了，请换一个名字`
        if (result.park_name || result.discoverer) {
          const extras = []
          if (result.park_name) extras.push(`在${result.park_name}`)
          if (result.discoverer) extras.push(`由${result.discoverer}发现`)
          if (extras.length) msg += `（${extras.join('，')}）`
        }
        this.setData({ nameCheckStatus: 'duplicate', nameCheckMsg: msg })
        return { duplicate: true, msg }
      } else {
        this.setData({ nameCheckStatus: 'available', nameCheckMsg: '' })
        return { duplicate: false }
      }
    }).catch(() => {
      this.setData({
        nameCheckStatus: 'warn',
        nameCheckMsg: '服务端查重接口暂未启用，提交时会再次校验名称是否重复'
      })
      return { duplicate: false, notReady: true }
    })
  },
  // 调用查重接口（内部用），返回 {duplicate, notReady?, ...}
  _callCheckNameApi(name) {
    return new Promise((resolve) => {
      wx.request({
        url: 'https://wulara.top/api/animals/check_name/',
        method: 'GET',
        data: { name: name },
        success: res => {
          // 接口404/500/非200 → 视为还没部署查重接口
          if (res.statusCode !== 200) {
            resolve({ duplicate: false, notReady: true })
            return
          }
          const d = res.data
          // 标准 std({code, msg, data}) 格式
          if (d && typeof d === 'object' && d.code === 200 && d.data && typeof d.data === 'object') {
            resolve({ ...d.data, msg: d.msg })
          } else {
            // 返回格式不是我们的std契约，也降级为warn
            resolve({ duplicate: false, notReady: true })
          }
        },
        fail: () => resolve({ duplicate: false, notReady: true })
      })
    })
  },
  choosePhoto() {
    wx.chooseImage({
      count: 1,
      sizeType: ['compressed'],
      sourceType: ['album', 'camera'],
      success: res => {
        const path = (res.tempFilePaths || [])[0]
        if (path) this.setData({ photoPath: path })
      }
    })
  },

  // ============== 通用：从响应中抽取人能看懂的错误消息 ==============
  _extractErrorMessage(res, rawBody) {
    // Case 1: 我们的标准 {code, msg} 格式
    if (rawBody && typeof rawBody === 'object') {
      if (typeof rawBody.msg === 'string' && rawBody.msg) return rawBody.msg
      // DRF默认格式（全局异常处理器未转std时）
      if (typeof rawBody.detail === 'string' && rawBody.detail) return rawBody.detail
      // DRF serializers.ValidationError的字段级错误格式：{ field: [msg1, msg2] }
      // 例如 unique=True 冲突会是 { name: ["Animal with this name already exists." / "动物名称xx已存在"] }
      for (const k of Object.keys(rawBody)) {
        const v = rawBody[k]
        if (Array.isArray(v) && v.length && typeof v[0] === 'string') return v[0]
        if (typeof v === 'string' && v) return v
      }
      if (rawBody.error && typeof rawBody.error === 'string') return rawBody.error
      if (rawBody.message && typeof rawBody.message === 'string') return rawBody.message
    }
    // Case 2: 非JSON字符串，看看是否包含可识别错误
    if (typeof rawBody === 'string' && rawBody) {
      const trimmed = rawBody.trim()
      if (trimmed.length <= 200) return trimmed
    }
    // Case 3: 看HTTP状态码给通用信息
    if (res && res.statusCode === 400) return '提交内容有误，请检查填写内容'
    if (res && res.statusCode === 401) return '登录已过期，请重新登录'
    if (res && res.statusCode === 403) return '没有权限执行此操作'
    if (res && res.statusCode === 404) return '请求的接口不存在'
    if (res && res.statusCode >= 500) return '服务端处理出错，请稍后再试'
    return '上传失败'
  },

  // ============== 通用：判断消息是否属于"动物名称重复"类 ==============
  _isDuplicateNameError(msg) {
    if (!msg || typeof msg !== 'string') return false
    const m = msg.toLowerCase()
    // 中文提示
    if (msg.indexOf('已存在') >= 0) return true
    if (msg.indexOf('重名') >= 0) return true
    if (msg.indexOf('名字') >= 0 && (msg.indexOf('重复') >= 0 || msg.indexOf('占用') >= 0)) return true
    if (msg.indexOf('动物名称') >= 0) return true
    // 英文DRF默认提示
    if (m.indexOf('already exists') >= 0 && (m.indexOf('name') >= 0 || m.indexOf('animal') >= 0)) return true
    if (m.indexOf('unique') >= 0 && m.indexOf('name') >= 0) return true
    if (m.indexOf('duplicate') >= 0) return true
    return false
  },

  // ============== 显示重名专属弹窗（UI统一）==============
  _showDuplicateModal(msg) {
    this.setData({ nameCheckStatus: 'duplicate', nameCheckMsg: msg })
    wx.vibrateShort && wx.vibrateShort({ type: 'medium' })
    wx.showModal({
      title: '🚫 动物名字重复啦',
      content: msg + '\n\n换一个更有创意的名字吧～',
      showCancel: false,
      confirmText: '好的我改',
      confirmColor: '#16a34a'
    })
  },

  async submit() {
    if (this.data.submitting) return
    const token = wx.getStorageSync('token')
    const userId = wx.getStorageSync('user_id')
    if (!token || !userId) {
      wx.showToast({ title: '请先登录', icon: 'none' })
      return
    }

    const lastSubmitTime = wx.getStorageSync('last_submit_time_upload') || 0
    const now = Date.now()
    if (now - lastSubmitTime < 60000) {
      const remaining = Math.ceil((60000 - (now - lastSubmitTime)) / 1000)
      wx.showToast({ title: `请稍等 ${remaining} 秒再试`, icon: 'none' })
      return
    }

    const { name, species, scientific_name, description } = this.data.form
    const { selectedParkId } = this.data
    if (!name || !species || !selectedParkId) {
      wx.showToast({ title: '请填写名称、品种并选择公园', icon: 'none' })
      return
    }

    // 写入前服务端二次查重
    const trimmedName = name.trim()
    if (trimmedName.length >= 2) {
      const checkRes = await this._checkNameAndUpdateUI(trimmedName)
      if (checkRes.duplicate) {
        this._showDuplicateModal(checkRes.msg || '这个名字已经被别的小动物占用了')
        return
      }
      // 注意：notReady（查重接口未部署）不拦截提交，让后端写入校验兜底
    }

    this.setData({ submitting: true })
    const hasPhoto = !!this.data.photoPath

    // ========== 分支A：带照片上传（uploadFile） ==========
    if (hasPhoto) {
      wx.uploadFile({
        url: 'https://wulara.top/api/animals/',
        filePath: this.data.photoPath,
        name: 'photo',
        header: { 'Authorization': 'Token ' + token },
        formData: {
          name, species, scientific_name, description,
          park: selectedParkId,
          discoverer_id: userId,
          discovered_at: new Date().toISOString()
        },
        success: res => {
          // 1) 解析响应体
          let body = null
          try { body = JSON.parse(res.data) } catch (e) { body = res.data }
          // 2) 成功判定（std格式 code=200 + data.id）
          const isSuccess = body && typeof body === 'object' && body.code === 200 && body.data && body.data.id
          if (isSuccess) {
            wx.setStorageSync('last_submit_time_upload', Date.now())
            const id = body.data.id
            wx.showModal({
              title: '提交成功 🎉',
              content: '谢谢您的关心，丰富了福州动物图鉴！您真棒！您的信息已提交等待wulara审核，如果很急赶紧联系他，嘿嘿',
              showCancel: false,
              confirmText: '太棒了',
              success: () => wx.navigateTo({ url: '/pages/animal/detail?id=' + id })
            })
          } else {
            const msg = this._extractErrorMessage(res, body)
            if (this._isDuplicateNameError(msg)) {
              this._showDuplicateModal(msg)
            } else {
              // 非重名错误：把原始HTTP码和msg同时打出来，避免永远只显示"上传失败"
              const hint = res.statusCode ? `（${res.statusCode}）` : ''
              wx.showModal({
                title: '提交未成功' + hint,
                content: msg,
                showCancel: false,
                confirmText: '知道了',
                confirmColor: '#374151'
              })
            }
          }
        },
        fail: () => wx.showToast({ title: '网络错误', icon: 'none' }),
        complete: () => this.setData({ submitting: false })
      })
    }

    // ========== 分支B：纯文字提交（wx.request POST） ==========
    else {
      wx.request({
        url: 'https://wulara.top/api/animals/',
        method: 'POST',
        header: {
          'content-type': 'application/json',
          'Authorization': 'Token ' + token
        },
        data: {
          name, species, scientific_name, description,
          park: selectedParkId,
          discoverer_id: userId,
          discovered_at: new Date().toISOString()
        },
        success: res => {
          const body = res.data
          const isSuccess = body && typeof body === 'object' && body.code === 200 && body.data && body.data.id
          if (isSuccess) {
            wx.setStorageSync('last_submit_time_upload', Date.now())
            const id = body.data.id
            wx.showModal({
              title: '提交成功 🎉',
              content: '谢谢您的关心，丰富了福州动物图鉴！您真棒！您的信息已提交等待wulara审核，如果很急赶紧联系他，嘿嘿',
              showCancel: false,
              confirmText: '太棒了',
              success: () => wx.navigateTo({ url: '/pages/animal/detail?id=' + id })
            })
          } else {
            const msg = this._extractErrorMessage(res, body)
            if (this._isDuplicateNameError(msg)) {
              this._showDuplicateModal(msg)
            } else {
              const hint = res.statusCode ? `（HTTP ${res.statusCode}）` : ''
              wx.showModal({
                title: '提交未成功' + hint,
                content: msg,
                showCancel: false,
                confirmText: '知道了',
                confirmColor: '#374151'
              })
            }
          }
        },
        fail: () => wx.showToast({ title: '网络错误', icon: 'none' }),
        complete: () => this.setData({ submitting: false })
      })
    }
  }
})
