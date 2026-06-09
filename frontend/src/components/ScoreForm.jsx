import React, { useState } from 'react';

function ScoreForm({ candidateId, onSubmit }) {
  const [category, setCategory] = useState('');
  const [score, setScore] = useState(3);
  const [note, setNote] = useState('');
  const [loading, setLoading] = useState(false);

  const categories = ['technical', 'communication', 'problem_solving', 'team_fit', 'leadership'];

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!category) {
      alert('Please select a category');
      return;
    }
    setLoading(true);
    try {
      await onSubmit({ category, score, note });
      setCategory('');
      setScore(3);
      setNote('');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h3>📊 Submit Score</h3>
      <form onSubmit={handleSubmit}>
        {/* Category */}
        <div style={{ marginBottom: '1rem' }}>
          <label>Category</label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="input-field"
            required
          >
            <option value="">Select category</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>
                {cat.replace('_', ' ').toUpperCase()}
              </option>
            ))}
          </select>
        </div>

        {/* Score slider */}
        <div style={{ marginBottom: '1rem' }}>
          <label>Score (1–5)</label>
          <div className="score-slider-container">
            <input
              type="range"
              min="1"
              max="5"
              value={score}
              onChange={(e) => setScore(parseInt(e.target.value))}
              className="score-slider"
              style={{ flex: 1 }}
            />
            <span className="score-value">{score}</span>
          </div>
          <div className="score-labels">
            <span>Poor</span>
            <span>Fair</span>
            <span>Good</span>
            <span>Very Good</span>
            <span>Excellent</span>
          </div>
        </div>

        {/* Note */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label>Note (Optional)</label>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            rows="3"
            className="input-field"
            placeholder="Add your comments about this score..."
          />
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={loading}
          className="btn-primary"
          style={{ width: '100%' }}
        >
          {loading ? 'Submitting...' : 'Submit Score'}
        </button>
      </form>
    </div>
  );
}

export default ScoreForm;