import { useState } from 'react'
import { AnalysisResult } from '../types'
import { downloadResume } from '../api/client'

interface ResultsDisplayProps {
  result: AnalysisResult
}

export function ResultsDisplay({ result }: ResultsDisplayProps) {
  const [activeTab, setActiveTab] = useState(0)
  const [expandedSection, setExpandedSection] = useState<string | null>(null)
  const tabs = ['Keywords', 'Format', 'Sections', 'Optimized']

  const scoreClass = result.ats_score >= 80 ? 'good' : result.ats_score >= 60 ? 'warning' : 'error'

  const handleDownload = async (format: 'docx' | 'pdf' | 'txt') => {
    try {
      await downloadResume(result.optimized_resume, format)
    } catch {
      alert(`Failed to download ${format.toUpperCase()}`)
    }
  }

  return (
    <div className="results-section">
      <div className="metrics">
        <div className={`metric-card ${scoreClass}`}>
          <div className="score">{result.ats_score}/100</div>
          <div className="label">ATS Score</div>
        </div>
        <div className="metric-card">
          <div className="score">{result.keyword_analysis.present_keywords.length}</div>
          <div className="label">Keywords Found</div>
        </div>
        <div className="metric-card">
          <div className="score">{result.keyword_analysis.missing_keywords.length}</div>
          <div className="label">Missing Keywords</div>
        </div>
      </div>

      <div className="tabs">
        {tabs.map((tab, i) => (
          <button
            key={tab}
            className={`tab ${activeTab === i ? 'active' : ''}`}
            onClick={() => setActiveTab(i)}
          >
            {tab}
          </button>
        ))}
      </div>

      <div className="tab-content">
        {activeTab === 0 && <KeywordTab keyword={result.keyword_analysis} />}
        {activeTab === 1 && <FormatTab suggestions={result.format_suggestions} />}
        {activeTab === 2 && <SectionsTab sections={result.section_analysis} expanded={expandedSection} setExpanded={setExpandedSection} />}
        {activeTab === 3 && <OptimizedTab resume={result.optimized_resume} onDownload={handleDownload} />}
      </div>

      <div className="overall-feedback">
        <strong>Overall Feedback:</strong> {result.overall_feedback}
      </div>
    </div>
  )
}

function KeywordTab({ keyword }: { keyword: AnalysisResult['keyword_analysis'] }) {
  return (
    <div className="keyword-grid">
      <div className="keyword-list present">
        <h3>Present Keywords</h3>
        <ul>{keyword.present_keywords.map((k) => <li key={k}>{k}</li>)}</ul>
      </div>
      <div className="keyword-list missing">
        <h3>Missing Keywords</h3>
        <ul>{keyword.missing_keywords.map((k) => <li key={k}>{k}</li>)}</ul>
      </div>
      {keyword.suggested_keywords.length > 0 && (
        <div className="keyword-list suggested" style={{ gridColumn: '1 / -1' }}>
          <h3>Suggested Keywords</h3>
          <ul>{keyword.suggested_keywords.map((k) => <li key={k}>{k}</li>)}</ul>
        </div>
      )}
    </div>
  )
}

function FormatTab({ suggestions }: { suggestions: string[] }) {
  return (
    <div className="format-suggestions">
      <ul>{suggestions.map((s, i) => <li key={i}>{s}</li>)}</ul>
    </div>
  )
}

function SectionsTab({ sections, expanded, setExpanded }: {
  sections: Record<string, { score: number; feedback: string }>
  expanded: string | null
  setExpanded: (name: string | null) => void
}) {
  return (
    <div>
      {Object.entries(sections).map(([name, info]) => (
        <div key={name} className={`section-item ${expanded === name ? 'expanded' : ''}`}>
          <div className="section-header" onClick={() => setExpanded(expanded === name ? null : name)}>
            <span>{name.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())}</span>
            <span className="section-score">{info.score}/100</span>
          </div>
          <div className="section-feedback">{info.feedback}</div>
        </div>
      ))}
    </div>
  )
}

function OptimizedTab({ resume, onDownload }: {
  resume: string
  onDownload: (format: 'docx' | 'pdf' | 'txt') => void
}) {
  return (
    <div>
      <textarea className="optimized-text" value={resume} readOnly />
      <div className="download-section">
        <button className="download-btn" onClick={() => onDownload('docx')}>DOCX</button>
        <button className="download-btn" onClick={() => onDownload('pdf')}>PDF</button>
        <button className="download-btn" onClick={() => onDownload('txt')}>TXT</button>
      </div>
    </div>
  )
}
