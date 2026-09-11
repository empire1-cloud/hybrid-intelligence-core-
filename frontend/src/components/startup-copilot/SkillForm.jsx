/**
 * Startup Copilot: Skill Form
 *
 * Renders the input form for a single founder skill, submits it to the
 * Startup Copilot API, and displays the returned guidance.
 *
 * Field definitions come from the skill catalog (see skills.js). Each field
 * maps to a key on the corresponding Pydantic input model; skills whose model
 * nests values (e.g. IdeaValidationInput.founder_background) supply a
 * buildPayload() to assemble the request body.
 */

import React, { useCallback, useMemo, useState } from 'react';
import { useAuth } from '../../context/AuthContext';

const isEmpty = (value) => {
  if (value === null || value === undefined) return true;
  if (typeof value === 'string') return value.trim() === '';
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'number') return Number.isNaN(value);
  return false;
};

const SkillForm = ({ skill, onComplete }) => {
  const { authAxios } = useAuth();
  const [formData, setFormData] = useState(() => {
    const initial = {};
    skill.fields.forEach((field) => {
      if (field.type === 'array') initial[field.name] = [];
      else if (field.type === 'checkbox') initial[field.name] = false;
      else if ('defaultValue' in field) initial[field.name] = field.defaultValue;
      else initial[field.name] = '';
    });
    return initial;
  });
  const [errors, setErrors] = useState({});
  const [submitError, setSubmitError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleChange = useCallback((name, value) => {
    setFormData((prev) => ({ ...prev, [name]: value }));
    setErrors((prev) => (prev[name] ? { ...prev, [name]: '' } : prev));
  }, []);

  const buildBody = useCallback(() => {
    // Drop empty optional values so Pydantic applies its own defaults.
    const cleaned = {};
    skill.fields.forEach((field) => {
      const value = formData[field.name];
      if (field.type === 'checkbox') {
        cleaned[field.name] = Boolean(value);
        return;
      }
      if (isEmpty(value)) return;
      cleaned[field.name] = field.type === 'number' ? Number(value) : value;
    });
    return skill.buildPayload ? skill.buildPayload(cleaned) : cleaned;
  }, [formData, skill]);

  const handleSubmit = useCallback(
    async (event) => {
      event.preventDefault();
      setSubmitError('');

      const nextErrors = {};
      skill.fields.forEach((field) => {
        if (field.required && field.type !== 'checkbox' && isEmpty(formData[field.name])) {
          nextErrors[field.name] = `${field.label} is required`;
        }
      });
      setErrors(nextErrors);
      if (Object.keys(nextErrors).length > 0) return;

      setIsLoading(true);
      try {
        const response = await authAxios().post(
          `/startup-copilot/${skill.endpoint}`,
          buildBody()
        );
        const payload = response.data;
        if (payload.status === 'error') {
          setSubmitError(payload.error || 'The skill returned an error.');
          return;
        }
        setResult(payload);
        if (onComplete) onComplete(skill, payload);
      } catch (err) {
        const detail = err.response?.data?.detail;
        setSubmitError(
          typeof detail === 'string' ? detail : detail ? JSON.stringify(detail) : err.message
        );
      } finally {
        setIsLoading(false);
      }
    },
    [authAxios, buildBody, formData, onComplete, skill]
  );

  if (result) {
    return (
      <SkillResult
        skill={skill}
        result={result}
        onReset={() => {
          setResult(null);
          setSubmitError('');
        }}
      />
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {skill.fields.map((field) => (
        <SkillField
          key={field.name}
          field={field}
          value={formData[field.name]}
          error={errors[field.name]}
          onChange={(value) => handleChange(field.name, value)}
        />
      ))}

      {submitError && (
        <div className="rounded-lg border border-red-300 bg-red-50 p-4 text-sm text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-300">
          {submitError}
        </div>
      )}

      <button
        type="submit"
        disabled={isLoading}
        className="w-full rounded-lg bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-gray-400"
      >
        {isLoading ? 'Analyzing…' : 'Get guidance'}
      </button>
    </form>
  );
};

const SkillField = ({ field, value, error, onChange }) => {
  const base = `w-full rounded-lg border px-4 py-2 dark:bg-gray-800 dark:text-white ${
    error ? 'border-red-500 dark:border-red-600' : 'border-gray-300 dark:border-gray-600'
  }`;

  return (
    <div>
      <label htmlFor={field.name} className="mb-2 block text-sm font-medium text-gray-900 dark:text-white">
        {field.label}
        {field.required && <span className="ml-1 text-red-600">*</span>}
      </label>

      {field.type === 'textarea' && (
        <textarea
          id={field.name}
          rows={4}
          className={`${base} resize-y`}
          placeholder={field.placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      )}

      {field.type === 'text' && (
        <input
          id={field.name}
          type="text"
          className={base}
          placeholder={field.placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      )}

      {field.type === 'number' && (
        <input
          id={field.name}
          type="number"
          className={base}
          placeholder={field.placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value === '' ? '' : Number(e.target.value))}
        />
      )}

      {field.type === 'select' && (
        <select id={field.name} className={base} value={value} onChange={(e) => onChange(e.target.value)}>
          <option value="">Select {field.label.toLowerCase()}…</option>
          {field.options.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      )}

      {field.type === 'checkbox' && (
        <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
          <input
            id={field.name}
            type="checkbox"
            className="h-4 w-4 rounded border-gray-300"
            checked={Boolean(value)}
            onChange={(e) => onChange(e.target.checked)}
          />
          {field.checkboxLabel || 'Yes'}
        </label>
      )}

      {field.type === 'array' && (
        <TagInput value={value || []} onChange={onChange} placeholder={field.placeholder} />
      )}

      {field.help && <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">{field.help}</p>}
      {error && <p className="mt-1 text-xs text-red-600 dark:text-red-400">{error}</p>}
    </div>
  );
};

const TagInput = ({ value, onChange, placeholder }) => {
  const [draft, setDraft] = useState('');

  const add = () => {
    const entry = draft.trim();
    if (entry && !value.includes(entry)) onChange([...value, entry]);
    setDraft('');
  };

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <input
          type="text"
          className="flex-1 rounded-lg border border-gray-300 px-4 py-2 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
          placeholder={placeholder}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              add();
            }
          }}
        />
        <button
          type="button"
          onClick={add}
          className="rounded-lg bg-gray-200 px-4 py-2 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white"
        >
          Add
        </button>
      </div>
      {value.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {value.map((tag) => (
            <span
              key={tag}
              className="flex items-center gap-2 rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
            >
              {tag}
              <button
                type="button"
                aria-label={`Remove ${tag}`}
                onClick={() => onChange(value.filter((t) => t !== tag))}
                className="text-blue-600 hover:text-blue-900 dark:text-blue-400"
              >
                ×
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

export const ResultValue = ({ value }) => {
  if (value === null || value === undefined || value === '') {
    return <span className="text-gray-400">—</span>;
  }
  if (Array.isArray(value)) {
    if (value.length === 0) return <span className="text-gray-400">—</span>;
    return (
      <ul className="ml-4 list-disc space-y-1">
        {value.map((item, i) => (
          <li key={i}>
            <ResultValue value={item} />
          </li>
        ))}
      </ul>
    );
  }
  if (typeof value === 'object') {
    return (
      <div className="space-y-1">
        {Object.entries(value).map(([k, v]) => (
          <div key={k}>
            <span className="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
              {k.replace(/_/g, ' ')}
            </span>
            <div className="text-sm text-gray-800 dark:text-gray-200">
              <ResultValue value={v} />
            </div>
          </div>
        ))}
      </div>
    );
  }
  if (typeof value === 'boolean') return <span>{value ? 'Yes' : 'No'}</span>;
  return <span className="whitespace-pre-wrap">{String(value)}</span>;
};

const SkillResult = ({ skill, result, onReset }) => {
  const [copied, setCopied] = useState(false);
  const sections = useMemo(() => Object.entries(result.data || {}), [result]);

  const copyJson = async () => {
    try {
      await navigator.clipboard.writeText(JSON.stringify(result.data, null, 2));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="rounded-lg border border-green-300 bg-green-50 p-5 dark:border-green-800 dark:bg-green-900/20">
        <h3 className="text-lg font-bold text-green-900 dark:text-green-300">
          {skill.name} complete
        </h3>
        <p className="text-sm text-green-800 dark:text-green-400">
          Generated by the {skill.framework} framework.
        </p>
      </div>

      {sections.length === 0 ? (
        <p className="text-sm text-gray-600 dark:text-gray-400">
          The skill returned no content. Try again with more detail in your inputs.
        </p>
      ) : (
        <div className="space-y-5">
          {sections.map(([key, value]) => (
            <section
              key={key}
              className="rounded-lg border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800"
            >
              <h4 className="mb-2 text-sm font-bold uppercase tracking-wide text-gray-700 dark:text-gray-300">
                {key.replace(/_/g, ' ')}
              </h4>
              <div className="text-sm text-gray-800 dark:text-gray-200">
                <ResultValue value={value} />
              </div>
            </section>
          ))}
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        <button
          onClick={copyJson}
          className="rounded-lg bg-gray-200 px-4 py-2 font-semibold text-gray-900 hover:bg-gray-300 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600"
        >
          {copied ? 'Copied' : 'Copy JSON'}
        </button>
        <button
          onClick={onReset}
          className="rounded-lg bg-blue-600 px-4 py-2 font-semibold text-white hover:bg-blue-700"
        >
          Run again
        </button>
      </div>
    </div>
  );
};

export default SkillForm;
