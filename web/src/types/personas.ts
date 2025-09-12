export interface Persona {
  id: string
  name: string
  title: string
  description: string
  optimalDuration: string
  attentionSpan: 'low' | 'medium' | 'high' | 'very-high'
  painPoints: string[]
  valueFocus: string[]
  interactionStyle: 'executive' | 'standard' | 'technical' | 'rapid'
  technicalDepth: 'minimal' | 'balanced' | 'detailed' | 'expert'
  color: string
  icon: string
}

export const personas: Persona[] = [
  {
    id: 'business_analyst',
    name: 'Business Analyst',
    title: 'Strategic Data Planning',
    description: 'Focused on business impact, feasibility assessment, and strategic data initiatives',
    optimalDuration: '15-20 minutes',
    attentionSpan: 'high',
    painPoints: [
      'Technical complexity uncertainty',
      'Feasibility vs business value trade-offs',
      'Timeline and resource estimation',
      'Cross-functional alignment challenges'
    ],
    valueFocus: [
      'Business impact analysis',
      'Risk assessment and mitigation', 
      'Timeline and cost clarity',
      'Stakeholder communication'
    ],
    interactionStyle: 'standard',
    technicalDepth: 'balanced',
    color: 'blue',
    icon: 'chart-bar'
  },
  {
    id: 'data_analyst',
    name: 'Data Analyst', 
    title: 'Technical Data Assessment',
    description: 'Concerned with data quality, structure, integration patterns, and analytical workflows',
    optimalDuration: '12-18 minutes',
    attentionSpan: 'high',
    painPoints: [
      'Data quality unknowns',
      'Integration complexity assessment',
      'Schema compatibility issues',
      'Processing pipeline design'
    ],
    valueFocus: [
      'Data structure and quality',
      'API documentation access',
      'Integration patterns',
      'Processing requirements'
    ],
    interactionStyle: 'technical',
    technicalDepth: 'detailed',
    color: 'green',
    icon: 'code-bracket'
  },
  {
    id: 'data_lead',
    name: 'Data Lead/Architect',
    title: 'Platform Architecture & Strategy',
    description: 'Responsible for platform capabilities, team capacity, and architectural decisions',
    optimalDuration: '20-25 minutes',
    attentionSpan: 'very-high',
    painPoints: [
      'Platform limitation assessment',
      'Resource allocation optimization',
      'Technical debt considerations',
      'Scalability planning'
    ],
    valueFocus: [
      'Technical feasibility analysis',
      'Team capacity utilization',
      'Architecture alignment',
      'Long-term platform evolution'
    ],
    interactionStyle: 'technical',
    technicalDepth: 'expert',
    color: 'purple',
    icon: 'cog-6-tooth'
  },
  {
    id: 'trader',
    name: 'Trader/Business User',
    title: 'Fast Decision Making',
    description: 'Results-focused, needs quick insights and clear cost/benefit analysis',
    optimalDuration: '8-12 minutes',
    attentionSpan: 'medium',
    painPoints: [
      'Too much technical detail',
      'Slow decision processes',
      'Unclear ROI calculations',
      'Complex implementation timelines'
    ],
    valueFocus: [
      'Speed to insights',
      'Clear cost/benefit ratios',
      'Risk/reward assessment',
      'Implementation timeline'
    ],
    interactionStyle: 'rapid',
    technicalDepth: 'minimal',
    color: 'orange',
    icon: 'lightning-bolt'
  }
]

export type InteractionLevel = 'executive' | 'standard' | 'technical' | 'rapid'

export interface PersonaSettings {
  persona: Persona
  customInteractionLevel?: InteractionLevel
  customTechnicalDepth?: 'minimal' | 'balanced' | 'detailed' | 'expert'
  timeConstraint?: 'flexible' | 'standard' | 'urgent'
}