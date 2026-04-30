import { useState } from 'react'
import { UploadSection } from './components/UploadSection'
import { ResultsDisplay } from './components/ResultsDisplay'
import { AnalysisResult } from './types'

function App() {
  const [result, setResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleAnalyze = async (file: File, jobDescription?: string) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const { analyzeResume } = await import('./api/client')
      const data = await analyzeResume(file, jobDescription)
      setResult(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Analysis failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>ATS Resume Optimizer</h1>
        <p>Upload your resume and get AI-powered optimization suggestions</p>
      </header>

      {error && <div className="error-msg">{error}</div>}

      <UploadSection onAnalyze={handleAnalyze} loading={loading} />

      {loading && (
        <div className="loading">
          <p>Analyzing your resume with AI...</p>
        </div>
      )}

      {result && <ResultsDisplay result={result} />}
    </div>
  )
}

export default App
