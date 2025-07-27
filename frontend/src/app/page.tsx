'use client';

import { useState, useEffect } from 'react';

interface Stats {
  vector_store: {
    total_documents: number;
    collection_name: string;
  };
  chunk_size: number;
  embedding_model: string;
  llm_model: string;
}

interface Source {
  title: string;
  url: string;
  score: number;
  content_preview: string;
  source: string;
}

interface QueryResponse {
  answer: string;
  sources: Source[];
}

export default function Home() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const res = await fetch('/api/stats');
      if (!res.ok) throw new Error('Failed to load stats');
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error('Error loading stats:', err);
      setError('Failed to load system stats');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question.trim() }),
      });

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || 'Query failed');
      }

      const data = await res.json();
      setResponse(data);
    } catch (err) {
      console.error('Error querying:', err);
      setError(err instanceof Error ? err.message : 'Query failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl p-8 w-full max-w-4xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            🏛️ ASU RAG System
          </h1>
          <p className="text-gray-600">
            Ask anything about ASU courses, professors, campus life, and more
          </p>
        </div>

        {/* Stats */}
        <div className="bg-blue-50 rounded-lg p-4 mb-6 text-center">
          {stats ? (
            <div className="text-sm text-blue-800">
              📊 {stats.vector_store.total_documents.toLocaleString()} documents | 
              {stats.vector_store.collection_name} | 
              {stats.embedding_model} | 
              {stats.llm_model}
            </div>
          ) : (
            <div className="text-sm text-blue-800">
              📊 Loading system stats...
            </div>
          )}
        </div>

        {/* Query Form */}
        <form onSubmit={handleSubmit} className="mb-8">
          <div className="flex gap-4">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask something about ASU..."
              className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 text-gray-800"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !question.trim()}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            >
              {loading ? '⏳ Thinking...' : '🔍 Ask'}
            </button>
          </div>
        </form>

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="text-red-800 font-medium">❌ Error</div>
            <div className="text-red-600">{error}</div>
          </div>
        )}

        {/* Response */}
        {response && (
          <div className="space-y-6">
            {/* Answer */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-3">Answer</h2>
              <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {response.answer}
              </div>
            </div>

            {/* Sources */}
            {response.sources && response.sources.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-800 mb-3">Sources</h3>
                <div className="space-y-3">
                  {response.sources.map((source, index) => (
                    <div key={index} className="bg-gray-50 border-l-4 border-blue-500 rounded-r-lg p-4">
                      <div className="font-medium text-gray-800 mb-1">
                        {source.title || 'No title'}
                      </div>
                      <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 text-sm break-all block mb-2"
                      >
                        {source.url}
                      </a>
                      <div className="text-xs text-gray-500 mb-2">
                        Score: {(source.score * 100).toFixed(1)}% | Source: {source.source}
                      </div>
                      <div className="text-sm text-gray-600">
                        {source.content_preview}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
