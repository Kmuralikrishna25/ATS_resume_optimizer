export interface KeywordAnalysis {
  present_keywords: string[]
  missing_keywords: string[]
  suggested_keywords: string[]
}

export interface SectionScore {
  score: number
  feedback: string
}

export interface AnalysisResult {
  ats_score: number
  keyword_analysis: KeywordAnalysis
  format_suggestions: string[]
  section_analysis: Record<string, SectionScore>
  overall_feedback: string
  optimized_resume: string
}
