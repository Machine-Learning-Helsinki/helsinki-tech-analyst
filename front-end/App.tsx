
import React, { useState, useCallback } from 'react';
import { TextInput } from './components/TextInput';
import { SubmitButton } from './components/SubmitButton';
import { AnswerDisplay } from './components/AnswerDisplay';
import { Header } from './components/Header';
import { GithubIcon } from './components/icons/GithubIcon';

// Assume the FastAPI backend is running on this URL
const API_URL = process.env.VITE_API_URL // 'http://127.0.0.1:8000';

const App = () => {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = useCallback(async (event) => {
    event.preventDefault();
    if (!question.trim() || isLoading) {
      return;
    }
    console.log(API_URL)

    setIsLoading(true);
    setError(null);
    setAnswer(null);

    try {
      const response = await fetch(`${API_URL}/api/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question }),
      });

      if (!response.ok) {
        let errorMessage = `Error: ${response.status} ${response.statusText}`;
        try {
            const errorBody = await response.json();
            errorMessage = errorBody.detail || errorMessage;
        } catch (e) {
            // Ignore if the error body is not JSON
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      setAnswer(data.answer);

    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An unknown error occurred. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  }, [question, isLoading]);

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col items-center p-4 selection:bg-indigo-500 selection:text-white">
      <div className="w-full max-w-2xl mx-auto">
        <Header />
        <main className="mt-8 p-6 bg-gray-800/50 rounded-xl shadow-2xl border border-gray-700 backdrop-blur-sm">
          <form onSubmit={handleSubmit}>
            <div className="flex flex-col space-y-4">
              <label htmlFor="question-input" className="text-lg font-medium text-gray-300">
                Ask a Question
              </label>
              <TextInput
                id="question-input"
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., What is the capital of France?"
                disabled={isLoading}
              />
              <SubmitButton isLoading={isLoading} />
            </div>
          </form>
          <div className="mt-6">
            <AnswerDisplay
              isLoading={isLoading}
              error={error}
              answer={answer}
            />
          </div>
        </main>
      </div>
       <footer className="absolute bottom-4 text-center text-gray-500">
        <a 
          href="https://github.com/your-repo" 
          target="_blank" 
          rel="noopener noreferrer" 
          className="inline-flex items-center gap-2 hover:text-indigo-400 transition-colors"
        >
          <GithubIcon className="w-5 h-5" />
          <span>View on GitHub</span>
        </a>
      </footer>
    </div>
  );
};

export default App;
