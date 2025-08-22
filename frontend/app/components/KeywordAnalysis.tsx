import React, { useState } from 'react';
import { KeywordAnalysisProps } from '../types';
import { CheckCircleIcon, XCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const KeywordAnalysis: React.FC<KeywordAnalysisProps> = ({ keywords }) => {
  const [showAllFound, setShowAllFound] = useState(false);
  const [showAllMissing, setShowAllMissing] = useState(false);

  const displayLimit = 8;
  const foundToShow = showAllFound ? keywords.found : keywords.found.slice(0, displayLimit);
  const missingToShow = showAllMissing ? keywords.missing : keywords.missing.slice(0, displayLimit);

  const KeywordBadge: React.FC<{ keyword: string; type: 'found' | 'missing' | 'critical' }> = ({ 
    keyword, 
    type 
  }) => {
    const baseClasses = "inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium transition-colors";
    
    const typeClasses = {
      found: "bg-green-100 text-green-800 border border-green-200",
      missing: "bg-gray-100 text-gray-700 border border-gray-200",
      critical: "bg-red-100 text-red-800 border border-red-200"
    };

    const icon = {
      found: <CheckCircleIcon className="w-3 h-3" />,
      missing: <XCircleIcon className="w-3 h-3" />,
      critical: <ExclamationTriangleIcon className="w-3 h-3" />
    };

    return (
      <span className={`${baseClasses} ${typeClasses[type]}`}>
        {icon[type]}
        {keyword}
      </span>
    );
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
      <h3 className="text-xl font-semibold mb-6 text-gray-800">Keyword Analysis</h3>
      
      {/* Overview Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6 text-center">
        <div className="bg-green-50 rounded-lg p-3">
          <div className="text-2xl font-bold text-green-600">{keywords.found.length}</div>
          <div className="text-sm text-green-700">Found</div>
        </div>
        <div className="bg-red-50 rounded-lg p-3">
          <div className="text-2xl font-bold text-red-600">{keywords.critical_missing.length}</div>
          <div className="text-sm text-red-700">Critical Missing</div>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-2xl font-bold text-gray-600">{keywords.missing.length}</div>
          <div className="text-sm text-gray-700">Total Missing</div>
        </div>
      </div>

      {/* Found Keywords */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-semibold text-gray-800 flex items-center gap-2">
            <CheckCircleIcon className="w-5 h-5 text-green-600" />
            Keywords Found ({keywords.found.length})
          </h4>
          {keywords.found.length > displayLimit && (
            <button
              onClick={() => setShowAllFound(!showAllFound)}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              {showAllFound ? 'Show less' : `Show all ${keywords.found.length}`}
            </button>
          )}
        </div>
        
        {foundToShow.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {foundToShow.map((keyword, index) => (
              <KeywordBadge key={index} keyword={keyword} type="found" />
            ))}
          </div>
        ) : (
          <p className="text-gray-500 italic">No matching keywords found</p>
        )}
      </div>

      {/* Critical Missing Keywords */}
      {keywords.critical_missing.length > 0 && (
        <div className="mb-6">
          <h4 className="font-semibold text-red-700 mb-3 flex items-center gap-2">
            <ExclamationTriangleIcon className="w-5 h-5 text-red-600" />
            Critical Missing Keywords ({keywords.critical_missing.length})
          </h4>
          <div className="flex flex-wrap gap-2 mb-2">
            {keywords.critical_missing.map((keyword, index) => (
              <KeywordBadge key={index} keyword={keyword} type="critical" />
            ))}
          </div>
          <p className="text-sm text-red-600 bg-red-50 rounded-lg p-2">
            💡 These keywords appear frequently in the job description. Consider incorporating them into your resume.
          </p>
        </div>
      )}

      {/* All Missing Keywords */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-semibold text-gray-800 flex items-center gap-2">
            <XCircleIcon className="w-5 h-5 text-gray-600" />
            Missing Keywords ({keywords.missing.length})
          </h4>
          {keywords.missing.length > displayLimit && (
            <button
              onClick={() => setShowAllMissing(!showAllMissing)}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              {showAllMissing ? 'Show less' : `Show all ${keywords.missing.length}`}
            </button>
          )}
        </div>
        
        {missingToShow.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {missingToShow.map((keyword, index) => (
              <KeywordBadge key={index} keyword={keyword} type="missing" />
            ))}
          </div>
        ) : (
          <p className="text-gray-500 italic">All keywords found!</p>
        )}
        
        {keywords.missing.length > 0 && (
          <p className="text-sm text-gray-600 mt-3 bg-blue-50 rounded-lg p-3">
            💡 <strong>Tip:</strong> Prioritize critical missing keywords first. Look for natural ways to incorporate 
            2-3 of these into your existing experience descriptions or skills section.
          </p>
        )}
      </div>

      {/* Coverage Summary */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="text-sm text-gray-600">
          <strong>Coverage Summary:</strong> {keywords.found.length} of {keywords.all_extracted_from_jd.length} job requirements keywords found
          ({((keywords.found.length / Math.max(1, keywords.all_extracted_from_jd.length)) * 100).toFixed(1)}%)
        </div>
      </div>
    </div>
  );
};

export default KeywordAnalysis;