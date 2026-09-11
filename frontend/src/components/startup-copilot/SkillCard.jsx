/**
 * Startup Copilot: Skill Card
 *
 * One selectable tile in the founder dashboard grid.
 */

import React from 'react';

const CATEGORY_STYLES = {
  validation: 'border-blue-200 bg-blue-50 dark:border-blue-800 dark:bg-blue-900/20',
  funding: 'border-purple-200 bg-purple-50 dark:border-purple-800 dark:bg-purple-900/20',
  execution: 'border-green-200 bg-green-50 dark:border-green-800 dark:bg-green-900/20',
  team: 'border-orange-200 bg-orange-50 dark:border-orange-800 dark:bg-orange-900/20',
  legal: 'border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20',
};

const SkillCard = ({ skill, completed, onSelect }) => (
  <button
    type="button"
    onClick={onSelect}
    className={`flex h-full w-full flex-col rounded-lg border p-5 text-left transition hover:shadow-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
      CATEGORY_STYLES[skill.category] || CATEGORY_STYLES.execution
    }`}
  >
    <div className="mb-3 flex items-start justify-between">
      <span className="text-3xl" aria-hidden="true">
        {skill.icon}
      </span>
      {completed && (
        <span className="rounded-full bg-green-600 px-2 py-0.5 text-xs font-semibold text-white">
          Done
        </span>
      )}
    </div>
    <h3 className="mb-1 text-lg font-bold text-gray-900 dark:text-white">{skill.name}</h3>
    <p className="mb-3 flex-1 text-sm text-gray-600 dark:text-gray-400">{skill.description}</p>
    <span className="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-gray-400">
      {skill.framework}
    </span>
  </button>
);

export default SkillCard;
