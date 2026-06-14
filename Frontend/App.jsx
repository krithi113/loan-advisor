import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [formData, setFormData] = useState({
    annual_income: '',
    existing_debt: '',
    credit_score: '',
    requested_loan_amount: '',
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [metrics, setMetrics] = useState(null);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value === '' ? '' : parseFloat(value),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/evaluate`, {
        annual_income: formData.annual_income,
        existing_debt: formData.existing_debt,
        credit_score: parseInt(formData.credit_score),
        requested_loan_amount: formData.requested_loan_amount,
      });

      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error evaluating eligibility');
    } finally {
      setLoading(false);
    }
  };

  const fetchMetrics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/metrics`);
      setMetrics(response.data);
    } catch (err) {
      console.error('Error fetching metrics:', err);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>💰 Loan Eligibility Advisor</h1>
        <p>AI-powered loan eligibility assessment powered by RAG + LLM agents</p>
      </header>

      <main className="app-main">
        <div className="container">
          {/* Form Section */}
          <section className="form-section">
            <h2>Evaluate Your Eligibility</h2>
            <form onSubmit={handleSubmit} className="form">
              <div className="form-group">
                <label htmlFor="annual_income">Annual Income ($)</label>
                <input
                  type="number"
                  id="annual_income"
                  name="annual_income"
                  value={formData.annual_income}
                  onChange={handleInputChange}
                  placeholder="e.g., 75000"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="existing_debt">Existing Debt ($)</label>
                <input
                  type="number"
                  id="existing_debt"
                  name="existing_debt"
                  value={formData.existing_debt}
                  onChange={handleInputChange}
                  placeholder="e.g., 15000"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="credit_score">Credit Score</label>
                <input
                  type="number"
                  id="credit_score"
                  name="credit_score"
                  value={formData.credit_score}
                  onChange={handleInputChange}
                  placeholder="e.g., 720"
                  min="300"
                  max="850"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="requested_loan_amount">Requested Loan Amount ($)</label>
                <input
                  type="number"
                  id="requested_loan_amount"
                  name="requested_loan_amount"
                  value={formData.requested_loan_amount}
                  onChange={handleInputChange}
                  placeholder="e.g., 25000"
                  required
                />
              </div>

              <button type="submit" disabled={loading} className="btn-submit">
                {loading ? 'Evaluating...' : 'Evaluate Eligibility'}
              </button>
            </form>

            <button onClick={fetchMetrics} className="btn-metrics">
              View System Metrics
            </button>
          </section>

          {/* Results Section */}
          {result && (
            <section className="results-section">
              <h2>Evaluation Results</h2>

              {/* Customer Profile */}
              <div className="card profile-card">
                <h3>Your Profile</h3>
                <div className="profile-grid">
                  <div className="profile-item">
                    <span className="label">Annual Income:</span>
                    <span className="value">${result.customer_profile.annual_income.toLocaleString()}</span>
                  </div>
                  <div className="profile-item">
                    <span className="label">Existing Debt:</span>
                    <span className="value">${result.customer_profile.existing_debt.toLocaleString()}</span>
                  </div>
                  <div className="profile-item">
                    <span className="label">Debt-to-Income Ratio:</span>
                    <span className="value">{(result.customer_profile.debt_to_income_ratio * 100).toFixed(1)}%</span>
                  </div>
                  <div className="profile-item">
                    <span className="label">Credit Score:</span>
                    <span className="value">{result.customer_profile.credit_score}</span>
                  </div>
                  <div className="profile-item">
                    <span className="label">Requested Amount:</span>
                    <span className="value">${result.customer_profile.requested_loan_amount.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* Eligible Products */}
              {result.eligible_products && result.eligible_products.length > 0 && (
                <div className="card products-card">
                  <h3>✅ You're Eligible For</h3>
                  <div className="products-list">
                    {result.eligible_products.map((product, idx) => (
                      <div key={idx} className="product-item">
                        <h4>{product.name}</h4>
                        <span className={`risk-badge risk-${product.risk_level}`}>
                          {product.risk_level.toUpperCase()}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Risk Assessment */}
              {result.risk_assessment && result.risk_assessment.length > 0 && (
                <div className="card risks-card">
                  <h3>⚠️ Risk Flags</h3>
                  <ul className="risk-list">
                    {result.risk_assessment.map((risk, idx) => (
                      <li key={idx} className={risk.includes('HIGH') ? 'high-risk' : 'medium-risk'}>
                        {risk}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Human Review Required */}
              {result.requires_human_review && (
                <div className="card alert-card alert-warning">
                  <h3>🔍 Human Review Required</h3>
                  <p>Your application has complexity or risk factors that require specialist review. A loan officer will contact you shortly.</p>
                </div>
              )}

              {/* Recommendation */}
              <div className="card recommendation-card">
                <h3>💡 Recommendation</h3>
                <p>{result.recommendation}</p>
              </div>

              <p className="evaluation-timestamp">
                Evaluated at: {new Date(result.evaluation_timestamp).toLocaleString()}
              </p>
            </section>
          )}

          {/* Metrics Section */}
          {metrics && (
            <section className="metrics-section">
              <h2>System Metrics</h2>
              <div className="card metrics-card">
                <div className="metric-item">
                  <span className="label">Total Evaluations:</span>
                  <span className="value">{metrics.total_evaluations}</span>
                </div>
                <div className="metric-item">
                  <span className="label">Flagged for Review:</span>
                  <span className="value">{metrics.flagged_for_review}</span>
                </div>
                <div className="metric-item">
                  <span className="label">Flag Rate:</span>
                  <span className="value">{metrics.flag_rate_percent}%</span>
                </div>
                <div className="metric-item">
                  <span className="label">High Risk Flags:</span>
                  <span className="value">{metrics.high_risk_flags}</span>
                </div>
              </div>
            </section>
          )}

          {/* Error Section */}
          {error && (
            <section className="error-section">
              <h2>❌ Error</h2>
              <p className="error-message">{error}</p>
            </section>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>This is a demonstration of AI-powered loan eligibility assessment using RAG + LLM agents</p>
      </footer>
    </div>
  );
}

export default App;
