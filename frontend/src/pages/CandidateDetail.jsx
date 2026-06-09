import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { candidatesAPI } from '../api/client';
import ScoreForm from '../components/ScoreForm';
import ScoresList from '../components/ScoresList';
import AISummary from '../components/AISummary';
import InternalNotes from '../components/InternalNotes';

function CandidateDetail({ user }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [candidate, setCandidate] = useState(null);
  const [scores, setScores] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [updatingStatus, setUpdatingStatus] = useState(false);
  const [showArchiveConfirm, setShowArchiveConfirm] = useState(false);

  const fetchCandidateDetails = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await candidatesAPI.getById(id);
      setCandidate(response.data.candidate);
      setScores(response.data.scores);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch candidate details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCandidateDetails();
  }, [id]);

  const handleSubmitScore = async (scoreData) => {
    try {
      const response = await candidatesAPI.submitScore(id, scoreData);
      setScores([response.data, ...scores]);
      alert('Score submitted successfully!');
      fetchCandidateDetails();
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to submit score');
    }
  };

  const handleUpdateNotes = async (newNotes) => {
    try {
      await candidatesAPI.updateNotes(id, newNotes);
      setCandidate({ ...candidate, internal_notes: newNotes });
      alert('Internal notes updated successfully');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update notes');
    }
  };

  const handleStatusChange = async (newStatus) => {
    setUpdatingStatus(true);
    try {
      await candidatesAPI.updateStatus(id, newStatus);
      setCandidate({ ...candidate, status: newStatus });
      alert(`Status updated to ${newStatus}`);
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to update status');
    } finally {
      setUpdatingStatus(false);
    }
  };

  const handleArchive = async () => {
    try {
      await candidatesAPI.archive(id);
      alert('Candidate archived successfully');
      navigate('/');
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to archive candidate');
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (error || !candidate) {
    return (
      <>
        <div className="error-alert">
          {error || 'Candidate not found'}
        </div>
        <button onClick={() => navigate('/')} className="btn-secondary">
          ← Back to Candidates
        </button>
      </>
    );
  }

  const statusOptions = ['new', 'reviewed', 'hired', 'rejected'];

  return (
    <>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '10px' }}>
        <button onClick={() => navigate('/')} className="btn-secondary">
          ← Back to Candidates
        </button>
        
        {user.role === 'admin' && (
          <button onClick={() => setShowArchiveConfirm(true)} className="btn-danger">
            Archive Candidate
          </button>
        )}
      </div>

      {/* Archive Confirmation Modal */}
      {showArchiveConfirm && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000
        }}>
          <div className="card" style={{ maxWidth: '400px', margin: '20px' }}>
            <h3 style={{ marginBottom: '15px' }}>Confirm Archive</h3>
            <p>Are you sure you want to archive {candidate.name}?</p>
            <div style={{ display: 'flex', gap: '10px', marginTop: '20px', justifyContent: 'flex-end' }}>
              <button onClick={() => setShowArchiveConfirm(false)} className="btn-secondary">Cancel</button>
              <button onClick={handleArchive} className="btn-danger">Archive</button>
            </div>
          </div>
        </div>
      )}

      {/* Candidate Profile */}
      <div className="card">
        <div className="candidate-header">
          <div className="candidate-info">
            <h2>{candidate.name}</h2>
            <p>{candidate.email}</p>
            <p><strong>Role:</strong> {candidate.role_applied}</p>
            <div style={{ marginTop: '10px' }}>
              <strong>Skills:</strong>
              <div className="skills-container" style={{ marginTop: '5px' }}>
                {candidate.skills?.map((skill, idx) => (
                  <span key={idx} className="skill-tag">{skill}</span>
                ))}
              </div>
            </div>
          </div>
          <div className="candidate-status">
            <div style={{ marginBottom: '10px' }}>
              <span className={`status-badge status-${candidate.status}`}>
                {candidate.status}
              </span>
            </div>
            
            {user.role === 'admin' && (
              <div>
                <label style={{ fontSize: '12px', marginBottom: '5px', display: 'block' }}>Change Status:</label>
                <select
                  value={candidate.status}
                  onChange={(e) => handleStatusChange(e.target.value)}
                  disabled={updatingStatus}
                  className="input-field"
                  style={{ fontSize: '13px', padding: '6px 10px', minWidth: '140px' }}
                >
                  {statusOptions.map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="two-columns">
        <div>
          <ScoreForm candidateId={id} onSubmit={handleSubmitScore} />
          <ScoresList scores={scores} userRole={user.role} />
        </div>
        <div>
          <AISummary candidateId={id} />
          {user.role === 'admin' && (
            <InternalNotes
              candidateId={id}
              initialNotes={candidate.internal_notes}
              onUpdate={handleUpdateNotes}
            />
          )}
        </div>
      </div>
    </>
  );
}

export default CandidateDetail;