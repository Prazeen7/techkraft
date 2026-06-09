import React from 'react';

function FilterBar({ filters, onFilterChange, onReset }) {
  const statuses = ['', 'new', 'reviewed', 'hired', 'rejected'];
  const roles = ['', 'Senior Full Stack Engineer', 'Backend Engineer', 'Frontend Developer', 'DevOps Engineer', 'Data Engineer'];

  const handleChange = (key, value) => {
    onFilterChange({ ...filters, [key]: value, page: 1 });
  };

  return (
    <div className="filter-bar">
      <div className="filter-grid">
        <div>
          <label>Status</label>
          <select
            value={filters.status || ''}
            onChange={(e) => handleChange('status', e.target.value)}
            className="input-field"
          >
            {statuses.map(status => (
              <option key={status || 'all'} value={status}>
                {status || 'All Statuses'}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Role</label>
          <select
            value={filters.role_applied || ''}
            onChange={(e) => handleChange('role_applied', e.target.value)}
            className="input-field"
          >
            {roles.map(role => (
              <option key={role || 'all'} value={role}>
                {role || 'All Roles'}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label>Skill (partial match - shows as you type)</label>
          <input
            type="text"
            value={filters.skill || ''}
            onChange={(e) => handleChange('skill', e.target.value)}
            placeholder="e.g., Pyt, Rea, Java (matches partially)"
            className="input-field"
          />
          <small style={{ fontSize: '11px', color: '#6b7280', marginTop: '4px', display: 'block' }}>
            Results update as you type (e.g., "Pyt" matches "Python")
          </small>
        </div>

        <div>
          <label>Keyword</label>
          <input
            type="text"
            value={filters.keyword || ''}
            onChange={(e) => handleChange('keyword', e.target.value)}
            placeholder="Search name, email..."
            className="input-field"
          />
        </div>
      </div>
      
      <div className="filter-actions">
        <button onClick={onReset} className="btn-secondary">
          Reset Filters
        </button>
      </div>
    </div>
  );
}

export default FilterBar;