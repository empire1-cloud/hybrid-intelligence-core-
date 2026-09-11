/**
 * Startup Copilot: Founder Dashboard
 *
 * Entry point for the 12 founder skills and the chained workflows.
 * Results are held in component state for the session; nothing is persisted
 * server-side yet.
 */

import React, { useState } from 'react';
import SkillCard from './SkillCard';
import SkillForm from './SkillForm';
import WorkflowWidget, { WORKFLOWS } from './WorkflowWidget';
import { CATEGORIES, SKILLS } from './skills';

const FounderDashboard = () => {
  const [activeSkill, setActiveSkill] = useState(null);
  const [activeWorkflow, setActiveWorkflow] = useState(null);
  const [results, setResults] = useState({});

  const handleComplete = (skill, payload) => {
    setResults((prev) => ({ ...prev, [skill.id]: payload }));
  };

  if (activeWorkflow) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <WorkflowWidget workflow={activeWorkflow} onBack={() => setActiveWorkflow(null)} />
      </div>
    );
  }

  if (activeSkill) {
    return (
      <div className="mx-auto max-w-3xl px-4 py-8">
        <button
          onClick={() => setActiveSkill(null)}
          className="mb-4 text-sm font-semibold text-blue-600 hover:text-blue-800"
        >
          ← All skills
        </button>
        <header className="mb-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {activeSkill.icon} {activeSkill.name}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">{activeSkill.description}</p>
        </header>
        <SkillForm skill={activeSkill} onComplete={handleComplete} />
      </div>
    );
  }

  const completedCount = Object.keys(results).length;

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <header className="mb-10">
        <h1 className="mb-2 text-3xl font-bold text-gray-900 dark:text-white">Startup Copilot</h1>
        <p className="text-lg text-gray-600 dark:text-gray-400">
          Twelve founder skills, from validating the idea to running the company.
        </p>
        {completedCount > 0 && (
          <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
            {completedCount} of {SKILLS.length} run this session.
          </p>
        )}
      </header>

      <section className="mb-12">
        <h2 className="mb-1 text-xl font-bold text-gray-900 dark:text-white">Guided workflows</h2>
        <p className="mb-4 text-sm text-gray-600 dark:text-gray-400">
          Chain several skills together from one set of inputs.
        </p>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {WORKFLOWS.map((workflow) => (
            <button
              key={workflow.id}
              type="button"
              onClick={() => setActiveWorkflow(workflow)}
              className="rounded-lg border border-gray-200 bg-white p-5 text-left transition hover:shadow-md dark:border-gray-700 dark:bg-gray-800"
            >
              <h3 className="mb-1 text-lg font-bold text-gray-900 dark:text-white">{workflow.name}</h3>
              <p className="mb-3 text-sm text-gray-600 dark:text-gray-400">{workflow.description}</p>
              <span className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
                {workflow.steps.length} steps
              </span>
            </button>
          ))}
        </div>
      </section>

      <div className="space-y-10">
        {CATEGORIES.map((category) => {
          const skills = SKILLS.filter((s) => s.category === category.id);
          if (skills.length === 0) return null;
          return (
            <section key={category.id}>
              <h2 className="mb-1 text-xl font-bold text-gray-900 dark:text-white">{category.title}</h2>
              <p className="mb-4 text-sm text-gray-600 dark:text-gray-400">{category.blurb}</p>
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                {skills.map((skill) => (
                  <SkillCard
                    key={skill.id}
                    skill={skill}
                    completed={Boolean(results[skill.id])}
                    onSelect={() => setActiveSkill(skill)}
                  />
                ))}
              </div>
            </section>
          );
        })}
      </div>
    </div>
  );
};

export default FounderDashboard;
