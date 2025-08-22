import React from "react";
import { SuggestionsDisplayProps } from "../types";

const SuggestionsDisplay: React.FC<SuggestionsDisplayProps> = ({ suggestions }) => (
  <div className="bg-white rounded-2xl shadow-lg p-6 border border-gray-100">
    <h3 className="text-xl font-semibold mb-4">AI Suggestions</h3>
    {suggestions?.length ? (
      <ul className="list-disc pl-6 space-y-2 text-sm">
        {suggestions.map((s, i) => <li key={i}>{s}</li>)}
      </ul>
    ) : (
      <p className="text-gray-500 italic">No suggestions available.</p>
    )}
  </div>
);
export default SuggestionsDisplay;
