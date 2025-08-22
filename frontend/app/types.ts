// API Response Types
export interface AnalysisResult {
    score: number;
    components: ScoreComponents;
    keywords: KeywordAnalysis;
    semantic_matches: SemanticMatch[];
    suggestions: string[];
    latex_annotated?: string;
    limits: {
      file_bytes_max: number;
      tokens_trimmed: boolean;
    };
  }
  
  export interface ScoreComponents {
    recall: number;
    precision: number;
    semantic: number;
    context: number;
  }
  
  export interface KeywordAnalysis {
    found: string[];
    missing: string[];
    all_extracted_from_jd: string[];
    critical_missing: string[];
  }
  
  export interface SemanticMatch {
    jd: string;
    resume: string;
    similarity: number;
  }
  
  // UI State Types
  export interface FileUploadState {
    file: File | null;
    resumeText: string;
    isLatex: boolean;
  }
  
  // Component Props Types
  export interface ScoreDisplayProps {
    score: number;
    components: ScoreComponents;
  }
  
  export interface KeywordAnalysisProps {
    keywords: KeywordAnalysis;
  }
  
  export interface SuggestionsDisplayProps {
    suggestions: string[];
  }
  
  export interface SemanticMatchesProps {
    matches: SemanticMatch[];
  }
  
  export interface LaTeXDisplayProps {
    content: string;
  }
  
  // Utility Types
  export type AnalysisStatus = 'idle' | 'loading' | 'success' | 'error';
  
  export interface ApiError {
    detail: string;
    status?: number;
  }
  
  // Configuration Types
  export interface AppConfig {
    apiUrl: string;
    maxFileSize: number;
    supportedFileTypes: string[];
  }
  
  // Constants
  export const SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.tex'];
  export const MAX_FILE_SIZE = 4 * 1024 * 1024; // 4MB
  
  export const SCORE_RANGES = {
    EXCELLENT: 85,
    GOOD: 70,
    FAIR: 55,
    POOR: 0
  } as const;
  
  export type ScoreLevel = keyof typeof SCORE_RANGES;