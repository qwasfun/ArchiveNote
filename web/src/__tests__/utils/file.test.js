import { describe, it, expect } from 'vitest'
import {
  isImage,
  isVideo,
  isAudio,
  isPdf,
  isText,
  getFileIcon,
  getFileTypeColor,
} from '@/utils/file'

describe('isImage', () => {
  it('识别 image/* 类型', () => {
    expect(isImage('image/png')).toBe(true)
    expect(isImage('image/jpeg')).toBe(true)
    expect(isImage('image/gif')).toBe(true)
  })

  it('非图片类型返回 false', () => {
    expect(isImage('video/mp4')).toBe(false)
    expect(isImage('text/plain')).toBe(false)
  })

  it('undefined 返回 false', () => {
    expect(isImage(undefined)).toBe(false)
  })
})

describe('isVideo', () => {
  it('识别 video/* 类型', () => {
    expect(isVideo('video/mp4')).toBe(true)
    expect(isVideo('video/webm')).toBe(true)
  })

  it('非视频类型返回 false', () => {
    expect(isVideo('image/png')).toBe(false)
  })
})

describe('isAudio', () => {
  it('识别 audio/* 类型', () => {
    expect(isAudio('audio/mpeg')).toBe(true)
    expect(isAudio('audio/wav')).toBe(true)
  })
})

describe('isPdf', () => {
  it('识别 application/pdf', () => {
    expect(isPdf('application/pdf')).toBe(true)
  })

  it('其他类型返回 false', () => {
    expect(isPdf('application/json')).toBe(false)
  })
})

describe('isText', () => {
  it('识别 text/* 类型', () => {
    expect(isText('text/plain')).toBe(true)
    expect(isText('text/html')).toBe(true)
    expect(isText('text/css')).toBe(true)
  })

  it('识别代码相关 application 类型', () => {
    expect(isText('application/json')).toBe(true)
    expect(isText('application/javascript')).toBe(true)
    expect(isText('application/xml')).toBe(true)
  })

  it('非文本类型返回 false', () => {
    expect(isText('image/png')).toBe(false)
    expect(isText('video/mp4')).toBe(false)
  })
})

describe('getFileIcon', () => {
  it('图片返回图片图标', () => {
    expect(getFileIcon('image/png')).toBe('🖼️')
  })

  it('视频返回视频图标', () => {
    expect(getFileIcon('video/mp4')).toBe('🎥')
  })

  it('PDF 返回文档图标', () => {
    expect(getFileIcon('application/pdf')).toBe('📄')
  })

  it('音频返回音乐图标', () => {
    expect(getFileIcon('audio/mpeg')).toBe('🎵')
  })

  it('压缩包返回压缩图标', () => {
    expect(getFileIcon('application/zip')).toBe('🗜️')
  })

  it('未知类型返回默认图标', () => {
    expect(getFileIcon('application/octet-stream')).toBe('📁')
  })
})

describe('getFileTypeColor', () => {
  it('图片返回绿色样式', () => {
    expect(getFileTypeColor('image/jpeg')).toContain('green')
  })

  it('视频返回蓝色样式', () => {
    expect(getFileTypeColor('video/mp4')).toContain('blue')
  })

  it('PDF 返回红色样式', () => {
    expect(getFileTypeColor('application/pdf')).toContain('red')
  })

  it('音频返回紫色样式', () => {
    expect(getFileTypeColor('audio/mpeg')).toContain('purple')
  })

  it('未知类型返回灰色样式', () => {
    expect(getFileTypeColor('application/octet-stream')).toContain('gray')
  })
})
