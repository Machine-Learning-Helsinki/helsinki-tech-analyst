
import React from 'react';

export const TextInput = (props) => {
  return (
    <textarea
      {...props}
      rows={3}
      className="w-full p-3 bg-gray-900 border border-gray-600 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-all duration-200 text-gray-200 placeholder-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
    />
  );
};
