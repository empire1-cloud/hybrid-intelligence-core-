/**
 * Startup Copilot: Skill Card Component
 *
 * Displays individual skill cards in the founder dashboard.
 * Shows skill name, description, icon, and category.
 * Clickable to open the skill form.
 */

import React from 'react';

interface Skill {
  id: number;
  name: string;
  endpoint: string;
  description: string;
  icon: string;
  category: 'validation' | 'funding' | 'execution' | 'team' | 'legal';
  fields: any[];
}

interface SkillCardProps {
  skill: Skill;
  onSelect: () => void;
}

const CATEGORY_COLORS: Record<Skill['category'], { bg: string; text: string; border: string }> = {
  validation: {
    bg: 'bg-blue-50 dark:bg-blue-900/20',
    text: 'text-blue-700 dark:text-blue-300',
    border: 'border-blue-200 dark:border-blue-800',
  },
  funding: {
    bg: 'bg-purple-50 dark:bg-purple-900/20',
    text: 'text-purple-700 dark:text-purple-300',
    border: 'border-purple-200 dark:border-purple-800',
  },
  execution: {
    bg: 'bg-green-50 dark:bg-green-900/20',
    text: 'text-green-700 dark:text-green-300',
    border: 'border-green-200 dark:border-green-800',
  },
  team: {
    bg: 'bg-orange-50 dark:bg-orange-900/20',
    text: 'text-orange-700 dark:text-orange-300',
    border: 'border-orange-200 dark:border-orange-800',
  },
  legal: {
    bg: 'bg-red-50 dark:bg-red-900/20',
    text: 'text-red-700 dark:text-red-300',
    border: 'border-red-200 dark:border-red-800',
  },
};

export const SkillCard: React.FC<SkillCardProps> = ({ skill, onSelect }) => {
  const colors = CATEGORY_COLORS[skill.category];

  return (
    <button
      onClick={onSelect}
      className={`skill-card w-full text-left p-6 border rounded-lg transition-all hover:shadow-lg hover:scale-105 ${colors.bg} ${colors.border}`}
    >
      {/* Icon */}
      <div className="text-4xl mb-4">{skill.icon}</div>

      {/* Skill Name */}
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
        {skill.name}
      </h3>

      {/* Description */}
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
        {skill.description}
      </p>

      {/* Category Badge */}
      <div className="flex items-center justify-between">
        <span className={`inline-block text-xs font-semibold px-3 py-1 rounded-full ${colors.text} ${colors.bg}`}>
          {skill.category.charAt(0).toUpperCase() + skill.category.slice(1)}
        </span>
        <span className="text-gray-400 group-hover:text-gray-600">→</span>
      </div>
    </button>
  );
};

export default SkillCard;
