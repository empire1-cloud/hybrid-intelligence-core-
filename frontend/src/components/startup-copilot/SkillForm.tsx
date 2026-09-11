/**
 * Startup Copilot: Skill Form Component
 *
 * Generic form component for collecting skill inputs.
 * Adapts to each of 12 founder skills with dynamic fields.
 */

import React, { useState, useCallback } from 'react';
import { useAsync } from 'react-use';

interface FormField {
  name: string;
  label: string;
  type: 'text' | 'number' | 'textarea' | 'select' | 'array' | 'object';
  required?: boolean;
  placeholder?: string;
  options?: { value: string; label: string }[];
  help?: string;
}

interface SkillFormProps {
  skillName: string;
  skillDescription: string;
  fields: FormField[];
  onSubmit: (data: any) => Promise<any>;
  isLoading?: boolean;
}

/**
 * SkillForm Component
 *
 * Usage:
 * <SkillForm
 *   skillName="idea-validation"
 *   skillDescription="Validate founder-market fit using Mom Test"
 *   fields={[
 *     { name: 'founder_background', label: 'Your Background', type: 'object', required: true },
 *     { name: 'market_problem', label: 'Problem Statement', type: 'textarea', required: true }
 *   ]}
 *   onSubmit={async (data) => await apiCall(data)}
 * />
 */
export const SkillForm: React.FC<SkillFormProps> = ({
  skillName,
  skillDescription,
  fields,
  onSubmit,
  isLoading = false,
}) => {
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [result, setResult] = useState<any>(null);
  const [showResult, setShowResult] = useState(false);

  // Validate required fields
  const validateForm = useCallback((): boolean => {
    const newErrors: Record<string, string> = {};

    fields.forEach((field) => {
      if (field.required && !formData[field.name]) {
        newErrors[field.name] = `${field.label} is required`;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [fields, formData]);

  // Handle form submission
  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();

      if (!validateForm()) return;

      try {
        const response = await onSubmit(formData);
        setResult(response);
        setShowResult(true);
      } catch (error) {
        setErrors({
          submit: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    },
    [formData, onSubmit, validateForm]
  );

  // Handle field changes
  const handleChange = useCallback(
    (fieldName: string, value: any) => {
      setFormData((prev) => ({ ...prev, [fieldName]: value }));
      // Clear error when user starts typing
      if (errors[fieldName]) {
        setErrors((prev) => ({ ...prev, [fieldName]: '' }));
      }
    },
    [errors]
  );

  return (
    <div className="skill-form-container max-w-2xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          {skillName
            .split('-')
            .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
            .join(' ')}
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          {skillDescription}
        </p>
      </div>

      {!showResult ? (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Form Fields */}
          {fields.map((field) => (
            <FormField
              key={field.name}
              field={field}
              value={formData[field.name] || ''}
              error={errors[field.name]}
              onChange={(value) => handleChange(field.name, value)}
            />
          ))}

          {/* Submit Error */}
          {errors.submit && (
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <p className="text-red-800 dark:text-red-400">{errors.submit}</p>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg transition"
          >
            {isLoading ? 'Analyzing...' : 'Get Results'}
          </button>
        </form>
      ) : (
        <ResultsDisplay result={result} onReset={() => setShowResult(false)} />
      )}
    </div>
  );
};

/**
 * Individual Form Field Component
 */
const FormField: React.FC<{
  field: FormField;
  value: any;
  error?: string;
  onChange: (value: any) => void;
}> = ({ field, value, error, onChange }) => {
  const baseClasses =
    'w-full px-4 py-2 border rounded-lg dark:bg-gray-800 dark:text-white ' +
    (error
      ? 'border-red-500 dark:border-red-600'
      : 'border-gray-300 dark:border-gray-600');

  return (
    <div className="form-field">
      <label className="block text-sm font-medium text-gray-900 dark:text-white mb-2">
        {field.label}
        {field.required && <span className="text-red-600 ml-1">*</span>}
      </label>

      {field.type === 'textarea' && (
        <textarea
          className={`${baseClasses} resize-none`}
          rows={4}
          placeholder={field.placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      )}

      {field.type === 'text' && (
        <input
          type="text"
          className={baseClasses}
          placeholder={field.placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        />
      )}

      {field.type === 'number' && (
        <input
          type="number"
          className={baseClasses}
          placeholder={field.placeholder}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
        />
      )}

      {field.type === 'select' && (
        <select
          className={baseClasses}
          value={value}
          onChange={(e) => onChange(e.target.value)}
        >
          <option value="">Select {field.label}</option>
          {field.options?.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      )}

      {field.type === 'array' && (
        <TagInput
          value={value || []}
          onChange={onChange}
          placeholder={field.placeholder}
        />
      )}

      {field.help && (
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          {field.help}
        </p>
      )}

      {error && (
        <p className="text-xs text-red-600 dark:text-red-400 mt-1">{error}</p>
      )}
    </div>
  );
};

/**
 * Tag Input Component (for array fields)
 */
const TagInput: React.FC<{
  value: string[];
  onChange: (value: string[]) => void;
  placeholder?: string;
}> = ({ value, onChange, placeholder }) => {
  const [inputValue, setInputValue] = useState('');

  const handleAdd = () => {
    if (inputValue.trim() && !value.includes(inputValue.trim())) {
      onChange([...value, inputValue.trim()]);
      setInputValue('');
    }
  };

  const handleRemove = (tag: string) => {
    onChange(value.filter((t) => t !== tag));
  };

  return (
    <div className="space-y-2">
      <div className="flex gap-2">
        <input
          type="text"
          className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-800 dark:text-white"
          placeholder={placeholder}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter') {
              e.preventDefault();
              handleAdd();
            }
          }}
        />
        <button
          type="button"
          onClick={handleAdd}
          className="px-4 py-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
        >
          Add
        </button>
      </div>
      <div className="flex flex-wrap gap-2">
        {value.map((tag) => (
          <div
            key={tag}
            className="bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 px-3 py-1 rounded-full text-sm flex items-center gap-2"
          >
            {tag}
            <button
              type="button"
              onClick={() => handleRemove(tag)}
              className="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-200"
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

/**
 * Results Display Component
 */
const ResultsDisplay: React.FC<{
  result: any;
  onReset: () => void;
}> = ({ result, onReset }) => {
  const [copied, setCopied] = useState(false);

  const handleExportPDF = () => {
    // PDF export logic will be implemented here
    console.log('Export to PDF', result);
  };

  const handleCopyJSON = () => {
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="results-display space-y-6">
      {/* Results Header */}
      <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
        <h3 className="text-2xl font-bold text-green-900 dark:text-green-300 mb-2">
          ✓ Analysis Complete
        </h3>
        <p className="text-green-800 dark:text-green-400">
          Your founder guidance report is ready below.
        </p>
      </div>

      {/* Results Body */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 space-y-4">
        <pre className="bg-gray-50 dark:bg-gray-900 p-4 rounded text-sm overflow-auto max-h-96 text-gray-900 dark:text-gray-100">
          {JSON.stringify(result, null, 2)}
        </pre>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4">
        <button
          onClick={handleExportPDF}
          className="flex-1 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-semibold transition"
        >
          📄 Export as PDF
        </button>
        <button
          onClick={handleCopyJSON}
          className="flex-1 px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-lg font-semibold transition"
        >
          {copied ? '✓ Copied' : '📋 Copy JSON'}
        </button>
        <button
          onClick={onReset}
          className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-semibold transition"
        >
          ← New Analysis
        </button>
      </div>
    </div>
  );
};

export default SkillForm;
