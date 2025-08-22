"use client";

import React, { useState, useCallback, useRef } from "react";
import { CloudArrowUpIcon, DocumentTextIcon, SparklesIcon } from "@heroicons/react/24/outline";
import { AnalysisResult, FileUploadState } from "@/types";
import ScoreDisplay from "@/components/ScoreDisplay";
import KeywordAnalysis from "@/components/KeywordAnalysis";
import SuggestionsDisplay from "@/components/SuggestionsDisplay";
import SemanticMatches from "@/components/SemanticMatches";
import LatexDisplay from "@/components/LatexDisplay"; // match the actual filename
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function HomePage() {
  // State management
  const [fileState, setFileState] = useState<FileUploadState>({
    file: null,
    resumeText: '',
    isLatex: false
  });
  const [jobDescription, setJobDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // File upload handlers
  const handleFileChange = useCallback((file: File) => {
    setFileState(prev => ({
      ...prev,
      file,
      resumeText: '' // Clear text when file is selected
    }));
    setError(null);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      const file = files[0];
      if (file.type === 'application/pdf' || 
          file.name.endsWith('.docx') || 
          file.name.endsWith('.tex') ||
          file.type.includes('pdf') ||
          file.type.includes('word')) {
        handleFileChange(file);
      } else {
        setError('Please upload a PDF, DOCX, or LaTeX file');
      }
    }
  }, [handleFileChange]);

  // Analysis submission
  const handleAnalyze = async () => {
    if (!jobDescription.trim()) {
      setError('Please enter a job description');
      return;
    }

    if (!fileState.file && !fileState.resumeText.trim()) {
      setError('Please upload a resume file or enter resume text');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('job_description', jobDescription.trim());
      
      if (fileState.file) {
        formData.append('file', fileState.file);
      } else if (fileState.resumeText.trim()) {
        formData.append('resume_text', fileState.resumeText.trim());
      }
      
      if (fileState.isLatex) {
        formData.append('is_latex', 'true');
      }

      const response = await fetch(`${API_URL}/analyze`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `Analysis failed: ${response.status}`);
      }

      const data: AnalysisResult = await response.json();
      setResult(data);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Analysis failed. Please try again.';
      setError(errorMessage);
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Clear all data
  const handleClear = () => {
    setFileState({ file: null, resumeText: '', isLatex: false });
    setJobDescription('');
    setResult(null);
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <header className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <SparklesIcon className="w-8 h-8 text-blue-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              Resume-Analytica
            </h1>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            AI-powered resume analysis that provides explainable match scores and actionable improvement suggestions
          </p>
        </header>

        <div className="grid lg:grid-cols-2 gap-8 mb-8">
          {/* Resume Upload Section */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <DocumentTextIcon className="w-5 h-5 text-blue-600" />
              Your Resume
            </h2>

            {/* File Upload Area */}
            <div
              className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                dragActive
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-gray-400'
              }`}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <CloudArrowUpIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600 mb-2">
                Drag & drop your resume here, or{' '}
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="text-blue-600 hover:text-blue-700 underline"
                >
                  browse files
                </button>
              </p>
              <p className="text-sm text-gray-500">Supports PDF, DOCX, and LaTeX files (max 4MB)</p>
              
              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.tex"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) handleFileChange(file);
                }}
                className="hidden"
              />
            </div>

            {/* File Info */}
            {fileState.file && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg flex items-center justify-between">
                <span className="text-sm text-blue-700">
                  📄 {fileState.file.name} ({(fileState.file.size / 1024 / 1024).toFixed(1)} MB)
                </span>
                <button
                  onClick={() => setFileState(prev => ({ ...prev, file: null }))}
                  className="text-red-600 hover:text-red-700 text-sm"
                >
                  Remove
                </button>
              </div>
            )}

            {/* Text Input Alternative */}
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Or paste your resume text here:
              </label>
              <textarea
                value={fileState.resumeText}
                onChange={(e) => setFileState(prev => ({ ...prev, resumeText: e.target.value }))}
                placeholder="Paste your resume content here..."
                className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                disabled={!!fileState.file}
              />
            </div>

            {/* LaTeX Checkbox */}
            <label className="flex items-center gap-2 mt-3 text-sm">
              <input
                type="checkbox"
                checked={fileState.isLatex}
                onChange={(e) => setFileState(prev => ({ ...prev, isLatex: e.target.checked }))}
                className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              This is LaTeX format (enables inline suggestions)
            </label>
          </div>

          {/* Job Description Section */}
          <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
            <h2 className="text-xl font-semibold mb-4">Job Description</h2>
            <textarea
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
              placeholder="Paste the complete job description here. Include requirements, responsibilities, and preferred qualifications for the most accurate analysis..."
              className="w-full h-64 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
            <p className="text-sm text-gray-500 mt-2">
              💡 Tip: Include the complete job posting for better keyword and semantic analysis
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 justify-center mb-8">
          <button
            onClick={handleAnalyze}
            disabled={loading || (!fileState.file && !fileState.resumeText.trim()) || !jobDescription.trim()}
            className="px-8 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-semibold 
                     hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed
                     transform hover:scale-105 transition-all duration-200 shadow-lg"
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Analyzing...
              </span>
            ) : (
              'Analyze Resume'
            )}
          </button>
          
          <button
            onClick={handleClear}
            className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-semibold hover:bg-gray-300 
                     transition-colors duration-200"
          >
            Clear All
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">❌ {error}</p>
          </div>
        )}

        {/* Results Display */}
        {result && (
          <div className="space-y-8">
            {/* Score Overview */}
            <ScoreDisplay score={result.score} components={result.components} />

            {/* Analysis Details */}
            <div className="grid lg:grid-cols-2 gap-8">
              <KeywordAnalysis keywords={result.keywords} />
              <SuggestionsDisplay suggestions={result.suggestions} />
            </div>

            {/* Semantic Matches */}
            {result.semantic_matches && result.semantic_matches.length > 0 && (
              <SemanticMatches matches={result.semantic_matches} />
            )}

            {/* LaTeX Display */}
            {result.latex_annotated && (
              <LaTeXDisplay content={result.latex_annotated} />
            )}
          </div>
        )}
      </div>
    </main>
  );
}