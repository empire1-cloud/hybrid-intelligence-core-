/**
 * Startup Copilot: Workflow Widget
 *
 * Runs a chained multi-skill workflow. The backend executes every step in a
 * single request (see WorkflowRequest in startup_copilot_routes.py), so this
 * collects one shared set of inputs and renders the per-step output it returns.
 */

import React, { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { ResultValue } from './SkillForm';

export const WORKFLOWS = [
  {
    id: 'validate-to-pitch',
    endpoint: 'workflow/validate-to-pitch',
    workflowType: 'validate_to_pitch',
    name: 'Validate → Pitch',
    description: 'Validate the idea, model the business, then build the raise.',
    steps: ['Idea Validation', 'Business Model', 'Fundraising'],
  },
  {
    id: 'validate-to-launch',
    endpoint: 'workflow/validate-to-launch',
    workflowType: 'validate_to_launch',
    name: 'Validate → Launch',
    description: 'Validate the idea, model the business, then plan GTM and product.',
    steps: ['Idea Validation', 'Business Model', 'Go-to-Market', 'Product'],
  },
];

const WorkflowWidget = ({ workflow, onBack }) => {
  const { authAxios } = useAuth();
  const [form, setForm] = useState({
    years_experience: '',
    domain: '',
    product_description: '',
    target_market: '',
  });
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);

  const set = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
    setErrors((prev) => (prev[key] ? { ...prev, [key]: '' } : prev));
  };

  const submit = async (event) => {
    event.preventDefault();
    setSubmitError('');

    const next = {};
    if (form.years_experience === '') next.years_experience = 'Years of experience is required';
    if (!form.domain.trim()) next.domain = 'Domain is required';
    if (!form.product_description.trim()) next.product_description = 'Product description is required';
    if (!form.target_market.trim()) next.target_market = 'Target market is required';
    setErrors(next);
    if (Object.keys(next).length > 0) return;

    setIsLoading(true);
    try {
      const response = await authAxios().post(`/startup-copilot/${workflow.endpoint}`, {
        workflow_type: workflow.workflowType,
        founder_background: {
          years_experience: Number(form.years_experience),
          domain: form.domain,
        },
        product_description: form.product_description,
        target_market: form.target_market,
      });
      setResult(response.data);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setSubmitError(
        typeof detail === 'string' ? detail : detail ? JSON.stringify(detail) : err.message
      );
    } finally {
      setIsLoading(false);
    }
  };

  const inputClass = (key) =>
    `w-full rounded-lg border px-4 py-2 dark:bg-gray-800 dark:text-white ${
      errors[key] ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
    }`;

  return (
    <div className="space-y-6">
      <div>
        <button onClick={onBack} className="mb-4 text-sm font-semibold text-blue-600 hover:text-blue-800">
          ← Back
        </button>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{workflow.name}</h2>
        <p className="text-gray-600 dark:text-gray-400">{workflow.description}</p>
        <ol className="mt-3 flex flex-wrap gap-2">
          {workflow.steps.map((step, i) => (
            <li
              key={step}
              className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700 dark:bg-gray-700 dark:text-gray-300"
            >
              {i + 1}. {step}
            </li>
          ))}
        </ol>
      </div>

      {!result ? (
        <form onSubmit={submit} className="space-y-5">
          <p className="text-sm text-gray-600 dark:text-gray-400">
            These inputs feed every step of the workflow.
          </p>

          <div>
            <label htmlFor="wf-years" className="mb-2 block text-sm font-medium text-gray-900 dark:text-white">
              Years in this domain <span className="text-red-600">*</span>
            </label>
            <input
              id="wf-years"
              type="number"
              className={inputClass('years_experience')}
              value={form.years_experience}
              onChange={(e) => set('years_experience', e.target.value === '' ? '' : Number(e.target.value))}
            />
            {errors.years_experience && <p className="mt-1 text-xs text-red-600">{errors.years_experience}</p>}
          </div>

          <div>
            <label htmlFor="wf-domain" className="mb-2 block text-sm font-medium text-gray-900 dark:text-white">
              Your domain expertise <span className="text-red-600">*</span>
            </label>
            <input
              id="wf-domain"
              type="text"
              className={inputClass('domain')}
              placeholder="Fintech / payments"
              value={form.domain}
              onChange={(e) => set('domain', e.target.value)}
            />
            {errors.domain && <p className="mt-1 text-xs text-red-600">{errors.domain}</p>}
          </div>

          <div>
            <label htmlFor="wf-product" className="mb-2 block text-sm font-medium text-gray-900 dark:text-white">
              Product description <span className="text-red-600">*</span>
            </label>
            <textarea
              id="wf-product"
              rows={4}
              className={inputClass('product_description')}
              value={form.product_description}
              onChange={(e) => set('product_description', e.target.value)}
            />
            {errors.product_description && (
              <p className="mt-1 text-xs text-red-600">{errors.product_description}</p>
            )}
          </div>

          <div>
            <label htmlFor="wf-market" className="mb-2 block text-sm font-medium text-gray-900 dark:text-white">
              Target market <span className="text-red-600">*</span>
            </label>
            <input
              id="wf-market"
              type="text"
              className={inputClass('target_market')}
              placeholder="US freelancers earning $50k+"
              value={form.target_market}
              onChange={(e) => set('target_market', e.target.value)}
            />
            {errors.target_market && <p className="mt-1 text-xs text-red-600">{errors.target_market}</p>}
          </div>

          {submitError && (
            <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300">
              {submitError}
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white hover:bg-blue-700 disabled:bg-gray-400"
          >
            {isLoading ? `Running ${workflow.steps.length} steps…` : `Run ${workflow.name}`}
          </button>
          {isLoading && (
            <p className="text-center text-xs text-gray-500 dark:text-gray-400">
              Each step calls a model in sequence; this can take a minute.
            </p>
          )}
        </form>
      ) : (
        <div className="space-y-5">
          <div className="rounded-lg border border-green-300 bg-green-50 p-5 dark:border-green-800 dark:bg-green-900/20">
            <h3 className="text-lg font-bold text-green-900 dark:text-green-300">Workflow complete</h3>
            <p className="text-sm text-green-800 dark:text-green-400">
              {result.steps?.length || 0} steps returned output.
            </p>
          </div>

          {(result.steps || []).map((step, i) => (
            <section
              key={i}
              className="rounded-lg border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800"
            >
              <h4 className="mb-2 text-sm font-bold uppercase tracking-wide text-gray-700 dark:text-gray-300">
                Step {i + 1}
                {step.skill ? ` — ${step.skill}` : ''}
              </h4>
              <div className="text-sm text-gray-800 dark:text-gray-200">
                <ResultValue value={step} />
              </div>
            </section>
          ))}

          {result.final_output && Object.keys(result.final_output).length > 0 && (
            <section className="rounded-lg border border-blue-300 bg-blue-50 p-5 dark:border-blue-800 dark:bg-blue-900/20">
              <h4 className="mb-2 text-sm font-bold uppercase tracking-wide text-blue-900 dark:text-blue-300">
                Final output
              </h4>
              <div className="text-sm text-gray-800 dark:text-gray-200">
                <ResultValue value={result.final_output} />
              </div>
            </section>
          )}

          <button
            onClick={() => setResult(null)}
            className="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700"
          >
            Run again
          </button>
        </div>
      )}
    </div>
  );
};

export default WorkflowWidget;
