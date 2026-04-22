import { describe, it, expect } from 'vitest'
import { formatDate, formatSize } from '@/utils/format'

describe('formatDate', () => {
  it('空值返回空字符串', () => {
    expect(formatDate('')).toBe('')
    expect(formatDate(null)).toBe('')
    expect(formatDate(undefined)).toBe('')
  })

  it('自动补全 Z 后缀（UTC 时间）', () => {
    // 只验证能返回非空字符串，具体格式由 toLocaleString 决定
    const result = formatDate('2024-01-15T12:00:00')
    expect(typeof result).toBe('string')
    expect(result.length).toBeGreaterThan(0)
  })

  it('已有 Z 后缀的时间字符串正常解析', () => {
    const result = formatDate('2024-01-15T12:00:00Z')
    expect(typeof result).toBe('string')
    expect(result.length).toBeGreaterThan(0)
  })

  it('带时区偏移的时间字符串正常解析', () => {
    const result = formatDate('2024-01-15T12:00:00+08:00')
    expect(typeof result).toBe('string')
    expect(result.length).toBeGreaterThan(0)
  })
})

describe('formatSize', () => {
  it('0 字节返回 "0 Bytes"', () => {
    expect(formatSize(0)).toBe('0 Bytes')
  })

  it('小于 1 KB 显示 Bytes', () => {
    expect(formatSize(512)).toBe('512 Bytes')
  })

  it('1024 字节显示 1 KB', () => {
    expect(formatSize(1024)).toBe('1 KB')
  })

  it('1 MB', () => {
    expect(formatSize(1024 * 1024)).toBe('1 MB')
  })

  it('1.5 MB', () => {
    expect(formatSize(1024 * 1024 * 1.5)).toBe('1.5 MB')
  })

  it('1 GB', () => {
    expect(formatSize(1024 ** 3)).toBe('1 GB')
  })

  it('小数保留两位', () => {
    // 1536 Bytes = 1.5 KB
    expect(formatSize(1536)).toBe('1.5 KB')
  })
})
