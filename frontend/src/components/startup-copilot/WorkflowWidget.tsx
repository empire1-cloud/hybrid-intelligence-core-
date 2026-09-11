/**
 * Startup Copilot: Workflow Widget Component
 *
 * Multi-skill chained workflow orchestrator.
 * Guides founders through sequences of related skills:
 * - Validate → Pitch (idea + business model + fundraising)
 * - Validate → Launch (idea + business model + GTM + product)
 */

import React, { useState } from 'react';

interface WorkflowStep {
  skillName: string;
  skillDescription: string;
  endpoint: string;
  icon: string;
}

interface Workflow {
  id: string;
  name: string;
  description: string;
  icon: string;
  duration: string;
  steps: WorkflowStep[];
  expectedOutput: string;
}

const WORKFLOWS: Workflow[] = [
  {
    id: 'validate-to-pitch',
    name: 'Validate → Pitch',
    description:
      'Complete path from idea validation through investor pitch deck in 3 connected steps.',
    icon: '🚀',
    duration: '~45 minutes',
    steps: [
      {
        skillName: 'Idea Validation',
        skillDescription: 'Validate founder-market fit using Mom Test framework',
        endpoint: 'validate-idea',
        icon: '✓',
      },
      {
        skillName: 'Business Model',
        skillDescription: 'Design business model with unit economics (LTV/CAC)',
        endpoint: 'design-business-model',
        icon: '📊',
      },
      {
        skillName: 'Fundraising',
        skillDescription: 'Generate pitch deck and investor targeting strategy',
        endpoint: 'create-fundraising-strategy',
        icon: '💰',
      },
    ],
    expectedOutput:
      'Complete pitch deck with validated problem, business model, and investor strategy',
  },
  {
    id: 'validate-to-launch',
    name: 'Validate → Launch',
    description:
      'Full product launch path: idea validation → business model → go-to-market → product strategy.',
    icon: '🎯',
    duration: '~60 minutes',
    steps: [
      {
        skillName: 'Idea Validation',
        skillDescription: 'Validate founder-market fit using Mom Test framework',
        endpoint: 'validate-idea',
        icon: '✓',
      },
      {
        skillName: 'Business Model',
        skillDescription: 'Design business model with unit economics (LTV/CAC)',
        endpoint: 'design-business-model',
        icon: '📊',
      },
      {
        skillName: 'Go-to-Market',
        skillDescription: 'Design 90-day GTM roadmap',
        endpoint: 'create-gtm-strategy',
        icon: '🚀',
      },
      {
        skillName: 'Product',
        skillDescription: 'Write PRD and RICE-scored roadmap',
        endpoint: 'create-product-strategy',
        icon: '🛠',
      },
    ],
    expectedOutput:
      'Complete launch plan with validated problem, business model, GTM strategy, and product roadmap',
  },
];

export const WorkflowWidget: React.FC = () => {
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [completedSteps, setCompletedSteps] = useState<Set<string>>(new Set());
  const [currentStep, setCurrentStep] = useState(0);
  const [workflowResults, setWorkflowResults] = useState<Map<string, any>>(new Map());

  const [inputs, setInputs] = useState({
    domain: '',
    yearsExperience: '',
    productDescription: '',
    targetMarket: '',
  });
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [finalOutput, setFinalOutput] = useState<Record<string, any> | null>(null);

  const resetRun = () => {
    setCompletedSteps(new Set());
    setCurrentStep(0);
    setWorkflowResults(new Map());
    setFinalOutput(null);
    setError(null);
  };

  const handleWorkflowSelect = (workflow: Workflow) => {
    setSelectedWorkflow(workflow);
    resetRun();
  };

  const canRun =
    inputs.domain.trim() !== '' &&
    inputs.productDescription.trim() !== '' &&
    inputs.targetMarket.trim() !== '';

  /**
   * Run the whole workflow.
   *
   * The backend chains the skills server-side and returns every step from one
   * POST, so there is a single request here rather than one call per step.
   */
  const runWorkflow = async () => {
    if (!selectedWorkflow || !canRun) return;

    setIsRunning(true);
    resetRun();

    try {
      const response = await fetch(
        `/api/startup-copilot/workflow/${selectedWorkflow.id}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify({
            workflow_type: selectedWorkflow.id.replace(/-/g, '_'),
            founder_background: {
              domain: inputs.domain,
              years_experience: Number(inputs.yearsExperience) || 0,
            },
            product_description: inputs.productDescription,
            target_market: inputs.targetMarket,
          }),
        }
      );

      if (!response.ok) {
        throw new Error(`Workflow failed (${response.status})`);
      }

      const result = await response.json();
      const returnedSteps: any[] = Array.isArray(result.steps) ? result.steps : [];

      // The response reports how far the chain actually got: a "kill" verdict
      // stops it early, so mark only the steps that came back.
      const reached = selectedWorkflow.steps.slice(0, returnedSteps.length);
      setCompletedSteps(new Set(reached.map((s) => s.skillName)));
      setWorkflowResults(
        new Map(reached.map((s, i) => [s.skillName, returnedSteps[i]]))
      );
      setCurrentStep(Math.min(returnedSteps.length, selectedWorkflow.steps.length - 1));
      setFinalOutput(result.final_output ?? null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Workflow failed');
    } finally {
      setIsRunning(false);
    }
  };

  const progress =
    selectedWorkflow && selectedWorkflow.steps.length > 0
      ? Math.round((completedSteps.size / selectedWorkflow.steps.length) * 100)
      : 0;

  if (!selectedWorkflow) {
    return (
      <div className="workflow-selection space-y-6">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            Multi-Skill Workflows
          </h2>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Chain multiple founder skills together for guided, end-to-end strategy development.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {WORKFLOWS.map((workflow) => (
            <button
              key={workflow.id}
              onClick={() => handleWorkflowSelect(workflow)}
              className="workflow-card text-left p-6 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:shadow-lg hover:scale-105 transition-all"
            >
              {/* Icon and Header */}
              <div className="mb-4">
                <span className="text-4xl">{workflow.icon}</span>
              </div>

              {/* Title */}
              <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                {workflow.name}
              </h3>

              {/* Description */}
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {workflow.description}
              </p>

              {/* Duration */}
              <p className="text-sm text-gray-500 dark:text-gray-500 mb-4">
                ⏱️ {workflow.duration}
              </p>

              {/* Steps Preview */}
              <div className="mb-4">
                <p className="text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2 uppercase">
                  {workflow.steps.length} Steps:
                </p>
                <div className="space-y-1">
                  {workflow.steps.map((step, idx) => (
                    <div
                      key={idx}
                      className="text-sm text-gray-600 dark:text-gray-400 flex items-center gap-2"
                    >
                      <span>{step.icon}</span>
                      <span>{step.skillName}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Expected Output */}
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded p-3">
                <p className="text-xs font-semibold text-blue-900 dark:text-blue-300 mb-1">
                  Expected Output:
                </p>
                <p className="text-xs text-blue-800 dark:text-blue-400">
                  {workflow.expectedOutput}
                </p>
              </div>

              {/* CTA */}
              <div className="mt-4 text-blue-600 hover:text-blue-700 font-semibold">
                Start Workflow →
              </div>
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="workflow-execution space-y-8">
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => {
            setSelectedWorkflow(null);
            setCompletedSteps(new Set());
            setCurrentStep(0);
          }}
          className="text-blue-600 hover:text-blue-800 font-semibold mb-4"
        >
          ← Back to Workflows
        </button>
        <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          {selectedWorkflow.icon} {selectedWorkflow.name}
        </h2>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          {selectedWorkflow.description}
        </p>
      </div>

      {/* Workflow Inputs */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 space-y-4">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white">
          Your Startup
        </h3>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              Your domain
            </span>
            <input
              type="text"
              value={inputs.domain}
              onChange={(e) => setInputs({ ...inputs, domain: e.target.value })}
              placeholder="e.g. fintech payments"
              className="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white px-3 py-2"
            />
          </label>
          <label className="block">
            <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
              Years of experience
            </span>
            <input
              type="number"
              min="0"
              value={inputs.yearsExperience}
              onChange={(e) =>
                setInputs({ ...inputs, yearsExperience: e.target.value })
              }
              placeholder="e.g. 7"
              className="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white px-3 py-2"
            />
          </label>
        </div>
        <label className="block">
          <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            What are you building?
          </span>
          <textarea
            value={inputs.productDescription}
            onChange={(e) =>
              setInputs({ ...inputs, productDescription: e.target.value })
            }
            rows={3}
            placeholder="Describe the problem and your solution"
            className="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white px-3 py-2"
          />
        </label>
        <label className="block">
          <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            Target market
          </span>
          <input
            type="text"
            value={inputs.targetMarket}
            onChange={(e) =>
              setInputs({ ...inputs, targetMarket: e.target.value })
            }
            placeholder="e.g. SMB finance teams in the US"
            className="mt-1 w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-900 text-gray-900 dark:text-white px-3 py-2"
          />
        </label>

        <button
          onClick={runWorkflow}
          disabled={!canRun || isRunning}
          className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-lg font-semibold transition"
        >
          {isRunning ? 'Running workflow…' : `Run ${selectedWorkflow.name}`}
        </button>

        {error && (
          <div
            role="alert"
            className="rounded-lg border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 px-4 py-3 text-sm text-red-800 dark:text-red-300"
          >
            {error}
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
            Overall Progress
          </span>
          <span className="text-2xl font-bold text-blue-600">{progress}%</span>
        </div>
        <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
          <div
            className="bg-blue-600 h-3 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <div className="mt-3 text-xs text-gray-600 dark:text-gray-400">
          {completedSteps.size} of {selectedWorkflow.steps.length} steps completed
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-4">
        {selectedWorkflow.steps.map((step, idx) => {
          const isCompleted = completedSteps.has(step.skillName);
          const isCurrent = idx === currentStep;
          const isLocked = idx > currentStep;

          return (
            <div
              key={idx}
              className={`workflow-step p-6 rounded-lg border transition-all ${
                isCompleted
                  ? 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
                  : isCurrent
                  ? 'bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700 ring-2 ring-blue-400'
                  : isLocked
                  ? 'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600 opacity-60'
                  : 'bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700'
              }`}
            >
              <div className="flex items-start gap-4">
                {/* Step Number / Icon */}
                <div
                  className={`flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg ${
                    isCompleted
                      ? 'bg-green-200 dark:bg-green-900 text-green-800 dark:text-green-300'
                      : isCurrent
                      ? 'bg-blue-200 dark:bg-blue-900 text-blue-800 dark:text-blue-300'
                      : isLocked
                      ? 'bg-gray-300 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                  }`}
                >
                  {isCompleted ? '✓' : isCurrent ? '→' : idx + 1}
                </div>

                {/* Step Content */}
                <div className="flex-1">
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-1">
                        {step.icon} {step.skillName}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {step.skillDescription}
                      </p>
                    </div>
                  </div>

                  {/* Status Badge */}
                  <div className="mt-3">
                    {isCompleted && (
                      <span className="inline-block px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 text-xs font-semibold rounded-full">
                        ✓ Completed
                      </span>
                    )}
                    {isCurrent && (
                      <span className="inline-block px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 text-xs font-semibold rounded-full">
                        Currently Active
                      </span>
                    )}
                    {isLocked && (
                      <span className="inline-block px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs font-semibold rounded-full">
                        Locked - Complete previous steps first
                      </span>
                    )}
                  </div>

                  {/* What this step actually returned */}
                  {isCompleted && workflowResults.has(step.skillName) && (
                    <pre className="mt-4 overflow-x-auto rounded-lg bg-gray-900 p-4 text-xs text-gray-100">
                      {JSON.stringify(workflowResults.get(step.skillName), null, 2)}
                    </pre>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Workflow Completion Summary */}
      {completedSteps.size === selectedWorkflow.steps.length && (
        <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
          <h3 className="text-2xl font-bold text-green-900 dark:text-green-300 mb-2">
            ✓ Workflow Complete!
          </h3>
          <p className="text-green-800 dark:text-green-400 mb-4">
            All {selectedWorkflow.steps.length} steps completed. Your {selectedWorkflow.name} strategy is ready.
          </p>
          <p className="text-green-800 dark:text-green-400 mb-4 font-semibold">
            Expected Output: {selectedWorkflow.expectedOutput}
          </p>
          {finalOutput && (
            <pre className="mb-4 overflow-x-auto rounded-lg bg-gray-900 p-4 text-xs text-gray-100">
              {JSON.stringify(finalOutput, null, 2)}
            </pre>
          )}
          <div className="flex gap-3">
            <button
              onClick={() => handleWorkflowSelect(selectedWorkflow)}
              className="px-4 py-2 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-900 dark:text-white rounded-lg font-semibold transition"
            >
              🔄 Restart Workflow
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowWidget;
