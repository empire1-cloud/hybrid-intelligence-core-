/**
 * Startup Copilot: Founder Dashboard
 *
 * Central hub for all 12 founder skills.
 * - Browse and select skills
 * - Track your founder journey
 * - Access saved results
 * - Run multi-skill workflows
 */

import React, { useState, useEffect } from 'react';
import SkillForm from './SkillForm';
import { SkillCard } from './SkillCard';
import { WorkflowWidget } from './WorkflowWidget';

interface Skill {
  id: number;
  name: string;
  endpoint: string;
  description: string;
  icon: string;
  category: 'validation' | 'funding' | 'execution' | 'team' | 'legal';
  fields: any[];
}

const SKILLS: Skill[] = [
  {
    id: 1,
    name: 'Idea Validation',
    endpoint: 'validate-idea',
    description: 'Validate founder-market fit using Mom Test framework',
    icon: '✓',
    category: 'validation',
    fields: [
      {
        name: 'founder_background',
        label: 'Your Background',
        type: 'object',
        required: true,
        help: 'Years in domain, previous exits, key relationships',
      },
      {
        name: 'market_problem',
        label: 'Problem Statement',
        type: 'textarea',
        required: true,
        placeholder: 'Describe the problem you\'re solving',
      },
      {
        name: 'existing_solutions',
        label: 'Existing Solutions',
        type: 'array',
        placeholder: 'Add competitors or alternatives',
      },
      {
        name: 'interviews_conducted',
        label: 'Customer Interviews',
        type: 'number',
        placeholder: '0',
      },
    ],
  },
  {
    id: 2,
    name: 'Business Model',
    endpoint: 'design-business-model',
    description: 'Design business model with unit economics (LTV/CAC)',
    icon: '📊',
    category: 'funding',
    fields: [
      {
        name: 'product_description',
        label: 'Product Description',
        type: 'textarea',
        required: true,
      },
      {
        name: 'target_market',
        label: 'Target Market',
        type: 'text',
        required: true,
      },
      {
        name: 'market_size_tam',
        label: 'TAM Estimate ($)',
        type: 'number',
      },
    ],
  },
  {
    id: 3,
    name: 'Fundraising',
    endpoint: 'create-fundraising-strategy',
    description: 'Generate pitch deck and investor targeting strategy',
    icon: '💰',
    category: 'funding',
    fields: [
      {
        name: 'current_stage',
        label: 'Funding Stage',
        type: 'select',
        required: true,
        options: [
          { value: 'pre_seed', label: 'Pre-Seed' },
          { value: 'seed', label: 'Seed' },
          { value: 'series_a', label: 'Series A' },
        ],
      },
      {
        name: 'target_raise',
        label: 'Target Raise ($)',
        type: 'number',
        required: true,
      },
      {
        name: 'use_of_funds',
        label: 'Use of Funds',
        type: 'textarea',
      },
    ],
  },
  {
    id: 4,
    name: 'Go-to-Market',
    endpoint: 'create-gtm-strategy',
    description: 'Design 90-day GTM roadmap',
    icon: '🚀',
    category: 'execution',
    fields: [
      {
        name: 'product_type',
        label: 'Product Type',
        type: 'select',
        options: [
          { value: 'b2b_saas', label: 'B2B SaaS' },
          { value: 'b2c', label: 'B2C' },
          { value: 'marketplace', label: 'Marketplace' },
        ],
      },
      {
        name: 'target_acv',
        label: 'Target ACV ($)',
        type: 'number',
      },
      {
        name: 'target_customers',
        label: 'First Customers Goal',
        type: 'number',
        placeholder: '100',
      },
    ],
  },
  {
    id: 5,
    name: 'Product',
    endpoint: 'create-product-strategy',
    description: 'Write PRD and RICE-scored roadmap',
    icon: '🛠',
    category: 'execution',
    fields: [
      {
        name: 'problem_statement',
        label: 'Problem Statement',
        type: 'textarea',
        required: true,
      },
      {
        name: 'target_user',
        label: 'Target User',
        type: 'text',
        required: true,
      },
      {
        name: 'key_features',
        label: 'Key Features',
        type: 'array',
      },
    ],
  },
  {
    id: 6,
    name: 'Sales',
    endpoint: 'create-sales-strategy',
    description: 'Design sales methodology (BANT/MEDDIC/Challenger)',
    icon: '🤝',
    category: 'execution',
    fields: [
      {
        name: 'deal_complexity',
        label: 'Deal Complexity',
        type: 'select',
        options: [
          { value: 'simple', label: 'Simple' },
          { value: 'moderate', label: 'Moderate' },
          { value: 'complex', label: 'Complex' },
        ],
      },
      {
        name: 'acv',
        label: 'ACV ($)',
        type: 'number',
      },
    ],
  },
  {
    id: 7,
    name: 'Marketing & Brand',
    endpoint: 'create-marketing-strategy',
    description: 'Brand voice, content pillars, SEO strategy',
    icon: '📢',
    category: 'execution',
    fields: [
      {
        name: 'brand_positioning',
        label: 'Brand Positioning',
        type: 'textarea',
        required: true,
      },
      {
        name: 'target_audience',
        label: 'Target Audience',
        type: 'text',
        required: true,
      },
    ],
  },
  {
    id: 8,
    name: 'Growth & Analytics',
    endpoint: 'create-growth-strategy',
    description: 'AARRR metrics, North Star, retention analysis',
    icon: '📈',
    category: 'execution',
    fields: [
      {
        name: 'current_product_stage',
        label: 'Product Stage',
        type: 'select',
        options: [
          { value: 'idea', label: 'Idea' },
          { value: 'mvp', label: 'MVP' },
          { value: 'beta', label: 'Beta' },
          { value: 'live', label: 'Live' },
        ],
      },
      {
        name: 'primary_metric',
        label: 'Primary Metric',
        type: 'text',
        placeholder: 'e.g., DAU, MRR',
      },
    ],
  },
  {
    id: 9,
    name: 'Operations',
    endpoint: 'create-operations-strategy',
    description: 'Hiring plan, OKRs, board management',
    icon: '⚙️',
    category: 'team',
    fields: [
      {
        name: 'current_headcount',
        label: 'Current Headcount',
        type: 'number',
      },
      {
        name: 'target_headcount',
        label: 'Target Headcount',
        type: 'number',
      },
    ],
  },
  {
    id: 10,
    name: 'Finance',
    endpoint: 'create-financial-model',
    description: 'Cash flow forecasting and runway analysis',
    icon: '💸',
    category: 'team',
    fields: [
      {
        name: 'current_cash',
        label: 'Current Cash ($)',
        type: 'number',
        required: true,
      },
      {
        name: 'monthly_burn_rate',
        label: 'Monthly Burn Rate ($)',
        type: 'number',
        required: true,
      },
      {
        name: 'headcount',
        label: 'Current Headcount',
        type: 'number',
      },
    ],
  },
  {
    id: 11,
    name: 'Customer Success',
    endpoint: 'create-customer-success-strategy',
    description: 'Onboarding flows, health scoring, churn prevention',
    icon: '😊',
    category: 'execution',
    fields: [
      {
        name: 'product_type',
        label: 'Product Type',
        type: 'select',
        options: [
          { value: 'plg', label: 'Product-Led' },
          { value: 'sales_led', label: 'Sales-Led' },
        ],
      },
      {
        name: 'customer_segment',
        label: 'Customer Segment',
        type: 'text',
      },
    ],
  },
  {
    id: 12,
    name: 'Legal & Compliance',
    endpoint: 'create-legal-strategy',
    description: 'Entity selection, cap table, compliance checklist',
    icon: '⚖️',
    category: 'legal',
    fields: [
      {
        name: 'entity_type',
        label: 'Entity Type',
        type: 'select',
        options: [
          { value: 'c_corp', label: 'C-Corp' },
          { value: 'llc', label: 'LLC' },
          { value: 's_corp', label: 'S-Corp' },
        ],
      },
      {
        name: 'jurisdictions',
        label: 'Operating Jurisdictions',
        type: 'array',
      },
    ],
  },
];

export const FounderDashboard: React.FC = () => {
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null);
  const [savedResults, setSavedResults] = useState<Map<string, any>>(new Map());
  const [view, setView] = useState<'skills' | 'skill' | 'workflows'>('skills');

  const handleSkillSubmit = async (data: any) => {
    if (!selectedSkill) return;

    try {
      const response = await fetch(
        `/api/startup-copilot/${selectedSkill.endpoint}`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
          body: JSON.stringify(data),
        }
      );

      if (!response.ok) throw new Error('API call failed');
      const result = await response.json();

      // Save result
      setSavedResults((prev) =>
        new Map(prev).set(selectedSkill.name, result.data)
      );

      return result.data;
    } catch (error) {
      console.error('Skill execution error:', error);
      throw error;
    }
  };

  if (selectedSkill && view === 'skill') {
    return (
      <div>
        <button
          onClick={() => {
            setSelectedSkill(null);
            setView('skills');
          }}
          className="mb-4 px-4 py-2 text-blue-600 hover:text-blue-800 font-semibold"
        >
          ← Back to Skills
        </button>
        <SkillForm
          skillName={selectedSkill.name}
          skillDescription={selectedSkill.description}
          fields={selectedSkill.fields}
          onSubmit={handleSkillSubmit}
        />
      </div>
    );
  }

  if (view === 'workflows') {
    return (
      <div>
        <button
          onClick={() => setView('skills')}
          className="mb-4 px-4 py-2 text-blue-600 hover:text-blue-800 font-semibold"
        >
          ← Back to Skills
        </button>
        <WorkflowWidget />
      </div>
    );
  }

  return (
    <div className="founder-dashboard p-8">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
          🚀 Founder Dashboard
        </h1>
        <p className="text-xl text-gray-600 dark:text-gray-400">
          Complete guidance from idea validation through scaling.
        </p>
      </div>

      {/* Workflow Shortcuts */}
      <div className="mb-12 grid grid-cols-1 md:grid-cols-2 gap-4">
        <button
          onClick={() => setView('workflows')}
          className="p-6 bg-gradient-to-br from-purple-500 to-indigo-600 text-white rounded-lg hover:shadow-lg transition text-left"
        >
          <h3 className="text-xl font-bold mb-2">Validate → Pitch</h3>
          <p className="text-sm opacity-90">
            Idea validation + Business model + Fundraising deck
          </p>
        </button>
        <button
          onClick={() => setView('workflows')}
          className="p-6 bg-gradient-to-br from-green-500 to-teal-600 text-white rounded-lg hover:shadow-lg transition text-left"
        >
          <h3 className="text-xl font-bold mb-2">Validate → Launch</h3>
          <p className="text-sm opacity-90">
            Idea validation + Business model + GTM + Product
          </p>
        </button>
      </div>

      {/* Skills Grid by Category */}
      <div className="space-y-12">
        {/* Validation Skills */}
        <SkillsSection
          title="1. Idea Validation"
          description="Start here to validate your idea is worth pursuing"
          skills={SKILLS.filter((s) => s.category === 'validation')}
          onSelectSkill={(skill) => {
            setSelectedSkill(skill);
            setView('skill');
          }}
        />

        {/* Funding Skills */}
        <SkillsSection
          title="2. Funding"
          description="Design your business model and prepare to raise capital"
          skills={SKILLS.filter((s) => s.category === 'funding')}
          onSelectSkill={(skill) => {
            setSelectedSkill(skill);
            setView('skill');
          }}
        />

        {/* Execution Skills */}
        <SkillsSection
          title="3. Execution"
          description="Build, launch, and scale your product"
          skills={SKILLS.filter((s) => s.category === 'execution')}
          onSelectSkill={(skill) => {
            setSelectedSkill(skill);
            setView('skill');
          }}
        />

        {/* Team Skills */}
        <SkillsSection
          title="4. Team & Operations"
          description="Hire, manage, and optimize your organization"
          skills={SKILLS.filter((s) => s.category === 'team')}
          onSelectSkill={(skill) => {
            setSelectedSkill(skill);
            setView('skill');
          }}
        />

        {/* Legal Skills */}
        <SkillsSection
          title="5. Legal & Compliance"
          description="Navigate the legal side of building a company"
          skills={SKILLS.filter((s) => s.category === 'legal')}
          onSelectSkill={(skill) => {
            setSelectedSkill(skill);
            setView('skill');
          }}
        />
      </div>

      {/* Saved Results */}
      {savedResults.size > 0 && (
        <div className="mt-16 pt-8 border-t border-gray-200 dark:border-gray-700">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
            📋 Your Results
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from(savedResults.entries()).map(([skillName, result]) => (
              <div
                key={skillName}
                className="p-4 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg"
              >
                <h3 className="font-bold text-gray-900 dark:text-white mb-2">
                  {skillName}
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Saved result ready for export
                </p>
                <button className="text-blue-600 hover:text-blue-800 text-sm font-semibold">
                  View & Export →
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * Skill Section Component
 */
const SkillsSection: React.FC<{
  title: string;
  description: string;
  skills: Skill[];
  onSelectSkill: (skill: Skill) => void;
}> = ({ title, description, skills, onSelectSkill }) => {
  return (
    <div>
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
          {title}
        </h2>
        <p className="text-gray-600 dark:text-gray-400">{description}</p>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {skills.map((skill) => (
          <SkillCard
            key={skill.id}
            skill={skill}
            onSelect={() => onSelectSkill(skill)}
          />
        ))}
      </div>
    </div>
  );
};

export default FounderDashboard;
