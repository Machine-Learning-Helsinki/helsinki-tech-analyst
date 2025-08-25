
import React from 'react';
import { LoadingSpinner } from './icons/LoadingSpinner';
import { ErrorIcon } from './icons/ErrorIcon';

export const AnswerDisplay = ({ isLoading, error, answer }) => {
  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="flex flex-col items-center justify-center text-gray-400">
          <LoadingSpinner className="w-8 h-8 mb-2 animate-spin" />
          <p className="font-medium">Thinking...</p>
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex flex-col items-center p-4 bg-red-900/50 border border-red-700 rounded-lg">
          <ErrorIcon className="w-8 h-8 mb-2 text-red-400" />
          <p className="font-semibold text-red-300">An Error Occurred</p>
          <p className="text-sm text-red-400 mt-1 text-center">{error}</p>
        </div>
      );
    }

    if (answer) {
      return (
        <div>
          <h3 className="text-lg font-semibold text-gray-200 mb-2">Answer:</h3>
          <div className="p-4 bg-gray-900/70 border border-gray-700 rounded-lg prose prose-invert max-w-none prose-p:text-gray-300">
            <p>{answer}</p>
          </div>
        </div>
      );
    }

    return (
      <div className="text-center text-gray-500">
        <p>Your answer will appear here.</p>
      </div>
    );
  };

  return (
    <div className="min-h-[120px] p-4 bg-gray-800 border border-dashed border-gray-600 rounded-lg flex items-center justify-center transition-all duration-300">
      {renderContent()}
    </div>
  );
};
