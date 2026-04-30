import { useState, useRef, DragEvent, ChangeEvent } from 'react'

interface UploadSectionProps {
  onAnalyze: (file: File, jobDescription?: string) => void
  loading: boolean
}

export function UploadSection({ onAnalyze, loading }: UploadSectionProps) {
  const [file, setFile] = useState<File | null>(null)
  const [jobDescription, setJobDescription] = useState('')
  const [isDragging, setIsDragging] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(false)
    const dropped = e.dataTransfer.files[0]
    if (dropped) setFile(dropped)
  }

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0])
  }

  const handleClick = () => inputRef.current?.click()

  const handleAnalyze = () => {
    if (file) onAnalyze(file, jobDescription || undefined)
  }

  return (
    <div className="upload-section">
      <textarea
        className="job-description-input"
        placeholder="Paste job description here (optional)..."
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
      />

      <div
        className={`file-drop-zone ${isDragging ? 'active' : ''} ${file ? 'has-file' : ''}`}
        onDrop={handleDrop}
        onDragOver={(e) => e.preventDefault()}
        onDragEnter={() => setIsDragging(true)}
        onDragLeave={() => setIsDragging(false)}
        onClick={handleClick}
      >
        {file ? (
          <p>Selected: <strong>{file.name}</strong></p>
        ) : (
          <p>Drag & drop your resume here, or click to browse</p>
        )}
        <input
          ref={inputRef}
          type="file"
          accept=".pdf,.docx,.doc"
          onChange={handleFileChange}
          hidden
        />
      </div>

      <button
        className="analyze-btn"
        onClick={handleAnalyze}
        disabled={!file || loading}
      >
        {loading ? 'Analyzing...' : 'Analyze Resume'}
      </button>
    </div>
  )
}
