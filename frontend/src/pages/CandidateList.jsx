import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { candidatesAPI } from '../api/client';
import FilterBar from '../components/FilterBar';
import Pagination from '../components/Pagination';

function CandidateList({ user }) {
  const navigate = useNavigate();
  const [candidates, setCandidates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    status: '',
    role_applied: '',
    skill: '',
    keyword: '',
    page: 1,
    page_size: 20
  });
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    page_size: 20,
    total_pages: 0
  });

  const fetchCandidates = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const params = {};
      if (filters.status) params.status = filters.status;
      if (filters.role_applied) params.role_applied = filters.role_applied;
      if (filters.skill) params.skill = filters.skill;
      if (filters.keyword) params.keyword = filters.keyword;
      params.page = filters.page;
      params.page_size = filters.page_size;
      
      const response = await candidatesAPI.getAll(params);
      setCandidates(response.data.items);
      setPagination({
        total: response.data.total,
        page: response.data.page,
        page_size: response.data.page_size,
        total_pages: response.data.total_pages
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to fetch candidates');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  // Debounce the fetch to avoid too many API calls while typing
  useEffect(() => {
    const timer = setTimeout(() => {
      fetchCandidates();
    }, 300); // Wait 300ms after user stops typing
    
    return () => clearTimeout(timer);
  }, [fetchCandidates]);

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleResetFilters = () => {
    setFilters({
      status: '',
      role_applied: '',
      skill: '',
      keyword: '',
      page: 1,
      page_size: 20
    });
  };

  const handlePageChange = (newPage) => {
    setFilters({ ...filters, page: newPage });
  };

  return (
    <>
      <div className="candidate-header">
        <div>
          <h2>Candidates</h2>
          <p>Manage and score candidate assessments</p>
        </div>
      </div>

      <FilterBar
        filters={filters}
        onFilterChange={handleFilterChange}
        onReset={handleResetFilters}
      />

      {loading && (
        <div className="loading-container">
          <div className="loading-spinner"></div>
        </div>
      )}

      {error && (
        <div className="error-alert">
          {error}
        </div>
      )}

      {!loading && !error && (
        <>
          <div className="table-container">
            <table className="table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Role</th>
                  <th>Skills</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {candidates.map((candidate) => (
                  <tr key={candidate.id}>
                    <td>
                      <div style={{ fontWeight: '500' }}>{candidate.name}</div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>{candidate.email}</div>
                    </td>
                    <td>{candidate.role_applied}</td>
                    <td>
                      <div className="skills-container">
                        {candidate.skills?.slice(0, 3).map((skill, idx) => (
                          <span key={idx} className="skill-tag">
                            {skill}
                          </span>
                        ))}
                        {candidate.skills?.length > 3 && (
                          <span className="skill-tag">+{candidate.skills.length - 3}</span>
                        )}
                      </div>
                    </td>
                    <td>
                      <span className={`status-badge status-${candidate.status}`}>
                        {candidate.status}
                      </span>
                    </td>
                    <td>
                      <button
                        onClick={() => navigate(`/candidates/${candidate.id}`)}
                        className="btn-primary"
                        style={{ padding: '6px 12px', fontSize: '13px' }}
                      >
                        View Details →
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {candidates.length === 0 && (
            <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
              No candidates found matching the filters
            </div>
          )}

          <Pagination
            currentPage={pagination.page}
            totalPages={pagination.total_pages}
            onPageChange={handlePageChange}
          />
        </>
      )}
    </>
  );
}

export default CandidateList;