
import React from 'react';
import { LoadingSpinner } from './icons/LoadingSpinner';

export const SubmitButton = ({ isLoading }) => {
  return (
    <button
      type="submit"
      disabled={isLoading}
      className="w-full flex items-center justify-center p-3 font-semibold text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-indigo-500 disabled:bg-indigo-500/50 disabled:cursor-wait transition-all duration-200 transform active:scale-95"
    >
      {isLoading ? (
        <>
          <LoadingSpinner className="w-5 h-5 mr-2" />
          <span>Asking AI...</span>
        </>
      ) : (
        'Submit'
      )}
    </button>
  );
};
