import React from 'react';
import { ScoreDisplayProps, SCORE_RANGES } from '../types';

const ScoreDisplay: React.FC<ScoreDisplayProps> = ({ score, components }) => {
  const getScoreColor = (score: number): string => {
    if (score >= SCORE_RANGES.EXCELLENT) return 'text-green-600';
    if (score >= SCORE_RANGES.GOOD) return 'text-blue-600';
    if (score >= SCORE_RANGES.FAIR) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreLabel = (score: number): string => {
    if (score >= SCORE_RANGES.EXCELLENT) return 'Excellent Match';
    if (score >= SCORE_RANGES.GOOD) return 'Good Match';
    if (score >= SCORE_RANGES.FAIR) return 'Fair Match';
    return 'Needs Improvement';
  };

  const getComponentBar = (value: number, label: string, weight: string) => (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span className="font-medium text-gray-700">{label}</span>
        <span className="text-gray-500">
          {(value * 100).toFixed(0)}% ({weight})
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className={`h-2 rounded-full transition-all duration-500 ${
            value >= 0.8
              ? 'bg-green-500'
              : value >= 0.6
              ? 'bg-blue-500'
              : value >= 0.4
              ? 'bg-yellow-500'
              : 'bg-red-500'
          }`}
          style={{ width: `${value * 100}%` }}
        />
      </div>
    </div>
  );

  return (
    <div className="bg-white rounded-2xl shadow-lg p-8 border border-gray-100">
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-2">Match Score</h2>
        <div className="flex items-center justify-center gap-4 mb-4">
          <div className={`text-6xl font-bold ${getScoreColor(score)}`}>
            {score}%
          </div>
          <div className="text-left">
            <div className={`text-lg font-semibold ${getScoreColor(score)}`}>
              {getScoreLabel(score)}
            </div>
            <div className="text-gray-500 text-sm">
              Based on multi-factor analysis
            </div>
          </div>
        </div>
        
        {/* Score interpretation */}
        <div className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3 max-w-md mx-auto">
          {score >= SCORE_RANGES.EXCELLENT && (
            "🎉 Outstanding alignment! Your resume strongly matches this role."
          )}
          {score >= SCORE_RANGES.GOOD && score < SCORE_RANGES.EXCELLENT && (
            "✅ Strong match! A few tweaks could make your resume even better."
          )}
          {score >= SCORE_RANGES.FAIR && score < SCORE_RANGES.GOOD && (
            "⚠️ Moderate alignment. Consider incorporating more relevant keywords and experiences."
          )}
          {score < SCORE_RANGES.FAIR && (
            "🔧 Significant improvements needed. Focus on the missing keywords and suggestions below."
          )}
        </div>
      </div>

      <div className="space-y-6">
        <h3 className="text-lg font-semibold text-gray-800 text-center mb-4">
          Score Breakdown
        </h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-4">
            {getComponentBar(components.recall, 'Keyword Coverage', '40%')}
            {getComponentBar(components.precision, 'Keyword Precision', '15%')}
          </div>
          <div className="space-y-4">
            {getComponentBar(components.semantic, 'Semantic Alignment', '35%')}
            {getComponentBar(components.context, 'Context Bonus', '10%')}
          </div>
        </div>

        {/* Component explanations */}
        <div className="grid md:grid-cols-2 gap-4 mt-6 text-xs text-gray-600">
          <div className="space-y-2">
            <div>
              <strong>Keyword Coverage:</strong> Percentage of job description keywords found in your resume
            </div>
            <div>
              <strong>Keyword Precision:</strong> How specific your keywords are to this role (prevents stuffing)
            </div>
          </div>
          <div className="space-y-2">
            <div>
              <strong>Semantic Alignment:</strong> How well your experience descriptions match the job requirements conceptually
            </div>
            <div>
              <strong>Context Bonus:</strong> Seniority level fit and industry domain alignment
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScoreDisplay;