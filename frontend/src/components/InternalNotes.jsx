import React, { useState } from 'react';
import { candidatesAPI } from '../api/client';

function InternalNotes({ candidateId, initialNotes, onUpdate }) {
  const [notes, setNotes] = useState(initialNotes || '');
  const [isEditing, setIsEditing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSave = async () => {
    setLoading(true);
    setError(null);
    
    try {
      await candidatesAPI.updateNotes(candidateId, notes);
      setIsEditing(false);
      onUpdate(notes);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update notes');
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setNotes(initialNotes || '');
    setIsEditing(false);
    setError(null);
  };

  return (
    <div className="card border-2 border-yellow-200 bg-yellow-50">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-lg font-semibold text-yellow-800">
          🔒 Internal Notes (Admin Only)
        </h3>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="btn-secondary text-sm"
          >
            Edit Notes
          </button>
        )}
      </div>
      
      {isEditing ? (
        <div className="space-y-3">
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows="6"
            className="input-field"
            placeholder="Add internal notes about this candidate (only visible to admins)..."
          />
          {error && (
            <div className="text-red-600 text-sm">{error}</div>
          )}
          <div className="flex space-x-2">
            <button
              onClick={handleSave}
              disabled={loading}
              className="btn-primary disabled:opacity-50"
            >
              {loading ? 'Saving...' : 'Save Notes'}
            </button>
            <button
              onClick={handleCancel}
              className="btn-secondary"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-lg p-4">
          {notes ? (
            <p className="text-gray-700 whitespace-pre-wrap">{notes}</p>
          ) : (
            <p className="text-gray-400 italic">No internal notes added yet</p>
          )}
        </div>
      )}
    </div>
  );
}

export default InternalNotes;