/**
 * 语音服务工具类
 * 提供 Web Speech API 的封装，支持语音识别（STT）和语音合成（TTS）
 */

class SpeechService {
  constructor() {
    this.recognition = null
    this.synthesis = window.speechSynthesis
    this.isSupported = this.checkSupport()
  }

  /**
   * 检查浏览器是否支持语音功能
   */
  checkSupport() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const SpeechSynthesis = window.speechSynthesis

    return {
      recognition: !!SpeechRecognition,
      synthesis: !!SpeechSynthesis
    }
  }

  /**
   * 初始化语音识别
   * @param {Object} options - 配置选项
   * @param {string} options.lang - 语言设置，默认 'zh-CN'
   * @param {boolean} options.continuous - 是否连续识别，默认 false
   * @param {boolean} options.interimResults - 是否返回临时结果，默认 true
   * @returns {Promise<SpeechRecognition>}
   */
  initRecognition(options = {}) {
    if (!this.isSupported.recognition) {
      throw new Error('浏览器不支持语音识别功能')
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    this.recognition = new SpeechRecognition()

    // 配置参数
    this.recognition.lang = options.lang || 'zh-CN'
    this.recognition.continuous = options.continuous !== undefined ? options.continuous : false
    this.recognition.interimResults = options.interimResults !== undefined ? options.interimResults : true
    this.recognition.maxAlternatives = 1

    return Promise.resolve(this.recognition)
  }

  /**
   * 开始语音识别
   * @param {Object} callbacks - 回调函数
   * @param {Function} callbacks.onResult - 识别结果回调
   * @param {Function} callbacks.onInterim - 临时结果回调
   * @param {Function} callbacks.onStart - 开始识别回调
   * @param {Function} callbacks.onEnd - 结束识别回调
   * @param {Function} callbacks.onError - 错误回调
   */
  startRecognition(callbacks = {}) {
    if (!this.recognition) {
      this.initRecognition()
    }

    this.recognition.onstart = () => {
      console.log('语音识别已启动')
      callbacks.onStart?.()
    }

    this.recognition.onresult = (event) => {
      const result = event.results[event.results.length - 1]
      const transcript = result[0].transcript

      if (result.isFinal) {
        console.log('最终识别结果:', transcript)
        callbacks.onResult?.(transcript)
      } else {
        console.log('临时识别结果:', transcript)
        callbacks.onInterim?.(transcript)
      }
    }

    this.recognition.onerror = (event) => {
      console.error('语音识别错误:', event.error)
      callbacks.onError?.(event.error)
    }

    this.recognition.onend = () => {
      console.log('语音识别已结束')
      callbacks.onEnd?.()
    }

    try {
      this.recognition.start()
    } catch (error) {
      console.error('启动语音识别失败:', error)
      callbacks.onError?.(error)
    }
  }

  /**
   * 停止语音识别
   */
  stopRecognition() {
    if (this.recognition) {
      try {
        this.recognition.stop()
        console.log('语音识别已停止')
      } catch (error) {
        console.error('停止语音识别失败:', error)
      }
    }
  }

  /**
   * 语音合成（文字转语音）
   * @param {string} text - 要朗读的文本
   * @param {Object} options - 配置选项
   * @param {string} options.lang - 语言设置，默认 'zh-CN'
   * @param {number} options.rate - 语速，默认 1（0.1-10）
   * @param {number} options.pitch - 音调，默认 1（0-2）
   * @param {number} options.volume - 音量，默认 1（0-1）
   * @returns {Promise<SpeechSynthesisUtterance>}
   */
  speak(text, options = {}) {
    if (!this.isSupported.synthesis) {
      throw new Error('浏览器不支持语音合成功能')
    }

    // 停止当前正在播放的语音
    this.stopSpeaking()

    const utterance = new SpeechSynthesisUtterance(text)

    // 配置参数
    utterance.lang = options.lang || 'zh-CN'
    utterance.rate = options.rate || 1
    utterance.pitch = options.pitch || 1
    utterance.volume = options.volume !== undefined ? options.volume : 1

    // 尝试获取中文语音
    const voices = this.synthesis.getVoices()
    const chineseVoice = voices.find(voice => voice.lang.includes('zh'))
    if (chineseVoice) {
      utterance.voice = chineseVoice
    }

    return new Promise((resolve, reject) => {
      utterance.onstart = () => {
        console.log('开始播放语音:', text)
      }

      utterance.onend = () => {
        console.log('语音播放完成')
        resolve(utterance)
      }

      utterance.onerror = (event) => {
        console.error('语音合成错误:', event.error)
        reject(new Error(event.error))
      }

      this.synthesis.speak(utterance)
    })
  }

  /**
   * 停止语音合成
   */
  stopSpeaking() {
    if (this.synthesis) {
      this.synthesis.cancel()
      console.log('语音播放已停止')
    }
  }

  /**
   * 暂停语音播放
   */
  pauseSpeaking() {
    if (this.synthesis) {
      this.synthesis.pause()
      console.log('语音播放已暂停')
    }
  }

  /**
   * 恢复语音播放
   */
  resumeSpeaking() {
    if (this.synthesis) {
      this.synthesis.resume()
      console.log('语音播放已恢复')
    }
  }

  /**
   * 获取可用的语音列表
   * @returns {SpeechSynthesisVoice[]}
   */
  getVoices() {
    if (!this.isSupported.synthesis) {
      return []
    }
    return this.synthesis.getVoices()
  }

  /**
   * 释放资源
   */
  destroy() {
    this.stopRecognition()
    this.stopSpeaking()
    this.recognition = null
  }
}

// 导出单例
export const speechService = new SpeechService()
export default speechService