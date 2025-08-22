import React, { useState } from 'react';
import { SemanticMatchesProps } from '../types';
import { MagnifyingGlassIcon, ArrowsRightLeftIcon } from '@heroicons/react/24/outline';

const SemanticMatches: React.FC<SemanticMatchesProps> = ({ matches }) => {
  const [showAll, setShowAll] = useState(false);
  const [filterThreshold, setFilterThreshold] = useState(0.6);

  const displayLimit = 6;
  const filteredMatches = matches.filter(match => match.similarity >= filterThreshold);
  const matchesToShow = showAll ? filteredMatches : filteredMatches.slice(0, displayLimit);

  const getSimilarityColor = (similarity: number): string => {
    if (similarity >= 0.8) return 'text-green-600 bg-green-100';
    if (similarity >= 0.7) return 'text-blue-600 bg-blue-100';
    if (similarity >= 0.6) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  const getSimilarityLabel = (similarity: number): string => {
    if (similarity >= 0.8) return 'Strong';
    if (similarity >= 0.7) return 'Good';
    if (similarity >= 0.6) return 'Moderate';
    return 'Weak';
  };

  const truncateText = (text: string, maxLength: number = 120): string => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  if (!matches || matches.length === 0) {
    return (
      <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
        <h3 className="text-xl font-semibold mb-4 text-gray-800 flex items-center gap-2">
          <MagnifyingGlassIcon className="w-5 h-5 text-blue-600" />
          Semantic Matches
        </h3>
        <div className="text-center py-8">
          <MagnifyingGlassIcon className="w-12 h-12 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500">No semantic matches found</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-800 flex items-center gap-2">
          <MagnifyingGlassIcon className="w-5 h-5 text-blue-600" />
          Semantic Matches ({filteredMatches.length})
        </h3>
        
        {/* Filter controls */}
        <div className="flex items-center gap-3">
          <select
            value={filterThreshold}
            onChange={(e) => setFilterThreshold(Number(e.target.value))}
            className="text-sm border border-gray-300 rounded px-2 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value={0.5}>Show all (≥50%)</option>
            <option value={0.6}>Moderate+ (≥60%)</option>
            <option value={0.7}>Good+ (≥70%)</option>
            <option value={0.8}>Strong+ (≥80%)</option>
          </select>
          
          {filteredMatches.length > displayLimit && (
            <button
              onClick={() => setShowAll(!showAll)}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              {showAll ? 'Show less' : `Show all ${filteredMatches.length}`}
            </button>
          )}
        </div>
      </div>

      {/* Matches overview */}
      <div className="grid grid-cols-4 gap-2 mb-6 text-center">
        {[
          { label: 'Strong (≥80%)', count: matches.filter(m => m.similarity >= 0.8).length, color: 'text-green-600' },
          { label: 'Good (≥70%)', count: matches.filter(m => m.similarity >= 0.7 && m.similarity < 0.8).length, color: 'text-blue-600' },
          { label: 'Moderate (≥60%)', count: matches.filter(m => m.similarity >= 0.6 && m.similarity < 0.7).length, color: 'text-yellow-600' },
          { label: 'Weak (<60%)', count: matches.filter(m => m.similarity < 0.6).length, color: 'text-red-600' }
        ].map((stat, index) => (
          <div key={index} className="bg-gray-50 rounded-lg p-2">
            <div className={`text-lg font-bold ${stat.color}`}>{stat.count}</div>
            <div className="text-xs text-gray-600">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Match cards */}
      <div className="space-y-4">
        {matchesToShow.map((match, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow duration-200"
          >
            {/* Similarity score header */}
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSimilarityColor(match.similarity)}`}>
                  {getSimilarityLabel(match.similarity)} Match
                </span>
                <span className="text-sm text-gray-500">
                  {(match.similarity * 100).toFixed(1)}% similarity
                </span>
              </div>
              <ArrowsRightLeftIcon className="w-4 h-4 text-gray-400" />
            </div>

            {/* Content comparison */}
            <div className="grid md:grid-cols-2 gap-4">
              {/* Job Description side */}
              <div className="space-y-2">
                <div className="text-sm font-medium text-blue-700 flex items-center gap-1">
                  📋 Job Description
                </div>
                <div className="text-sm text-gray-800 bg-blue-50 rounded p-3 leading-relaxed">
                  "{truncateText(match.jd)}"
                </div>
              </div>

              {/* Resume side */}
              <div className="space-y-2">
                <div className="text-sm font-medium text-green-700 flex items-center gap-1">
                  📄 Your Resume
                </div>
                <div className="text-sm text-gray-800 bg-green-50 rounded p-3 leading-relaxed">
                  "{truncateText(match.resume)}"
                </div>
              </div>
            </div>

            {/* Improvement hint for lower scores */}
            {match.similarity < 0.7 && (
              <div className="mt-3 text-xs text-gray-600 bg-yellow-50 rounded p-2 border-l-4 border-yellow-400">
                💡 <strong>Improvement tip:</strong> Consider using similar terminology or adding more specific details 
                to strengthen this connection.
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Info box */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <h4 className="font-semibold text-blue-800 mb-2">🔍 Understanding Semantic Matches</h4>
        <p className="text-sm text-blue-700">
          These matches show how well your resume content aligns with job requirements conceptually, 
          beyond just keyword matching. Higher similarity scores indicate stronger conceptual alignment 
          between your experience and the role's needs.
        </p>
      </div>

      {filteredMatches.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p>No matches found with similarity ≥ {(filterThreshold * 100)}%</p>
          <p className="text-sm mt-2">Try lowering the filter threshold to see more results.</p>
        </div>
      )}
    </div>
  );
};

export default SemanticMatches;