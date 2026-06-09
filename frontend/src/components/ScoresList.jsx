import React from 'react';
import { format } from 'date-fns';

function ScoresList({ scores, userRole }) {
  if (!scores || scores.length === 0) {
    return (
      <div className="card">
        <h3>📝 Scores</h3>
        <p style={{ textAlign: 'center', color: '#6b7280', padding: '2rem 0' }}>
          No scores submitted yet
        </p>
      </div>
    );
  }

  const getScoreColor = (score) => {
    if (score >= 4) return '#16a34a'; // green
    if (score >= 3) return '#ca8a04'; // yellow
    return '#dc2626'; // red
  };

  return (
    <div className="card">
      <h3>
        📝 Scores {userRole === 'admin' && '(All Reviewers)'}
      </h3>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {scores.map((score) => (
          <div
            key={score.id}
            style={{
              borderBottom: '1px solid #e5e7eb',
              paddingBottom: '0.75rem',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <span style={{ fontWeight: 600, textTransform: 'capitalize' }}>
                  {score.category.replace('_', ' ')}
                </span>
                {userRole === 'admin' && score.reviewer_name && (
                  <span style={{ fontSize: '0.75rem', color: '#6b7280', marginLeft: '0.5rem' }}>
                    by {score.reviewer_name}
                  </span>
                )}
              </div>
              <span style={{ fontSize: '1.5rem', fontWeight: 'bold', color: getScoreColor(score.score) }}>
                {score.score}/5
              </span>
            </div>
            {score.note && (
              <p style={{ color: '#4b5563', fontSize: '0.875rem', marginTop: '0.25rem' }}>
                {score.note}
              </p>
            )}
            <p style={{ color: '#9ca3af', fontSize: '0.75rem', marginTop: '0.25rem' }}>
              {format(new Date(score.created_at), 'MMM dd, yyyy HH:mm')}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ScoresList;