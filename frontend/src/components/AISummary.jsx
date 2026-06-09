import React, { useState } from 'react';
import { candidatesAPI } from '../api/client';

function AISummary({ candidateId }) {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const generateSummary = async () => {
    setLoading(true);
    setError(null);
    setSummary(null);
    
    try {
      const response = await candidatesAPI.generateSummary(candidateId);
      setSummary(response.data.summary);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate summary');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px', flexWrap: 'wrap', gap: '10px' }}>
        <h3 style={{ margin: 0 }}>🤖 AI-Generated Summary</h3>
        <button
          onClick={generateSummary}
          disabled={loading}
          className="btn-primary"
        >
          {loading ? 'Generating... (2s delay)' : 'Generate AI Summary'}
        </button>
      </div>
      
      {loading && (
        <div className="loading-container" style={{ minHeight: '150px' }}>
          <div>
            <div className="loading-spinner" style={{ margin: '0 auto 15px' }}></div>
            <p style={{ textAlign: 'center', color: '#6b7280' }}>AI is analyzing candidate data...</p>
            <p style={{ textAlign: 'center', color: '#9ca3af', fontSize: '12px', marginTop: '8px' }}>This takes 2 seconds (simulated LLM call)</p>
          </div>
        </div>
      )}
      
      {error && (
        <div className="error-alert">
          {error}
        </div>
      )}
      
      {summary && !loading && (
        <div className="ai-summary">
          <p>{summary.summary}</p>
          
          {summary.metrics && (
            <div className="ai-metrics">
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <strong>Total Scores:</strong> {summary.metrics.total_scores}
                </div>
                {summary.metrics.average_score && (
                  <div>
                    <strong>Average Score:</strong> {summary.metrics.average_score}/5
                  </div>
                )}
                {summary.metrics.categories_evaluated && summary.metrics.categories_evaluated.length > 0 && (
                  <div style={{ gridColumn: 'span 2' }}>
                    <strong>Categories:</strong> {summary.metrics.categories_evaluated.join(', ')}
                  </div>
                )}
              </div>
            </div>
          )}
          
          <p style={{ fontSize: '11px', color: '#9ca3af', marginTop: '12px' }}>
            Generated at {new Date(summary.generated_at).toLocaleString()}
          </p>
        </div>
      )}
      
      {!summary && !loading && !error && (
        <p style={{ textAlign: 'center', color: '#6b7280', padding: '30px' }}>
          Click "Generate AI Summary" to get AI-powered insights about this candidate
        </p>
      )}
    </div>
  );
}

export default AISummary;