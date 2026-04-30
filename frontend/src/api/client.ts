import axios from 'axios'
import { AnalysisResult } from '../types'

const api = axios.create({
  baseURL: '/api',
})

export const analyzeResume = async (
  file: File,
  jobDescription?: string
): Promise<AnalysisResult> => {
  const formData = new FormData()
  formData.append('file', file)
  if (jobDescription) {
    formData.append('job_description', jobDescription)
  }

  const response = await api.post<AnalysisResult>('/analyze', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export const downloadResume = async (
  content: string,
  format: 'docx' | 'pdf' | 'txt'
): Promise<void> => {
  const formData = new FormData()
  formData.append('content', content)

  const response = await api.post(`/download/${format}`, formData, {
    responseType: 'blob',
  })

  const url = window.URL.createObjectURL(new Blob([response.data]))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', `optimized_resume.${format}`)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}
