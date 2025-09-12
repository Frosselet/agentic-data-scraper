'use client'

import { motion } from 'framer-motion'
import { 
  ChatBubbleLeftRightIcon,
  MagnifyingGlassIcon,
  CheckCircleIcon,
  DocumentTextIcon
} from '@heroicons/react/24/outline'
import { DiscoveryPhase } from '../SourceDiscoveryAssistant'

interface Phase {
  id: string
  name: string
  duration: string
}

interface ProgressIndicatorProps {
  phases: Phase[]
  currentPhase: DiscoveryPhase
  percentage: number
}

const phaseIcons = {
  business_context: ChatBubbleLeftRightIcon,
  source_discovery: MagnifyingGlassIcon,
  feasibility_review: CheckCircleIcon,
  sow_generation: DocumentTextIcon
}

export default function ProgressIndicator({ 
  phases, 
  currentPhase, 
  percentage 
}: ProgressIndicatorProps) {
  const currentPhaseIndex = phases.findIndex(p => p.id === currentPhase)

  return (
    <div className="w-full">
      {/* Phase Steps */}
      <div className="flex items-center justify-between mb-3">
        {phases.map((phase, index) => {
          const IconComponent = phaseIcons[phase.id as keyof typeof phaseIcons]
          const isActive = phase.id === currentPhase
          const isCompleted = index < currentPhaseIndex
          const isUpcoming = index > currentPhaseIndex

          return (
            <div key={phase.id} className="flex flex-col items-center flex-1">
              {/* Phase Icon */}
              <motion.div
                className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300 ${
                  isCompleted
                    ? 'bg-green-500 border-green-500'
                    : isActive
                    ? 'bg-blue-500 border-blue-500'
                    : 'bg-gray-100 border-gray-300'
                }`}
                whileHover={isActive ? { scale: 1.05 } : {}}
              >
                {isCompleted ? (
                  <CheckCircleIcon className="w-5 h-5 text-white" />
                ) : (
                  <IconComponent className={`w-5 h-5 ${
                    isActive ? 'text-white' : 'text-gray-400'
                  }`} />
                )}
              </motion.div>

              {/* Phase Label */}
              <div className="text-center mt-2">
                <div className={`text-sm font-medium ${
                  isActive 
                    ? 'text-blue-600' 
                    : isCompleted 
                    ? 'text-green-600' 
                    : 'text-gray-500'
                }`}>
                  {phase.name}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  {phase.duration}
                </div>
              </div>

              {/* Progress Line */}
              {index < phases.length - 1 && (
                <div className="absolute left-0 right-0 h-0.5 bg-gray-200 mt-5" 
                     style={{ 
                       left: `${(index + 1) / phases.length * 100}%`,
                       right: `${(phases.length - index - 2) / phases.length * 100}%`,
                       top: '20px',
                       zIndex: -1
                     }}>
                  <motion.div
                    className="h-full bg-blue-500"
                    initial={{ width: '0%' }}
                    animate={{ width: isCompleted ? '100%' : '0%' }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Overall Progress Bar */}
      <div className="relative">
        <div className="flex items-center justify-between text-sm text-gray-500 mb-2">
          <span>Overall Progress</span>
          <span>{Math.round(percentage)}%</span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
          <motion.div
            className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full"
            initial={{ width: '0%' }}
            animate={{ width: `${percentage}%` }}
            transition={{ duration: 0.8, ease: 'easeInOut' }}
          />
        </div>

        {/* Active Phase Indicator */}
        {currentPhase && (
          <motion.div
            className="absolute -top-1 w-4 h-4 bg-blue-500 rounded-full border-2 border-white shadow-md"
            initial={{ left: '0%' }}
            animate={{ left: `${Math.max(0, Math.min(100, percentage - 2))}%` }}
            transition={{ duration: 0.8, ease: 'easeInOut' }}
          />
        )}
      </div>

      {/* Phase Description */}
      <motion.div
        key={currentPhase}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3 }}
        className="mt-4 text-center"
      >
        <div className="text-sm text-gray-600">
          {getPhaseDescription(currentPhase)}
        </div>
      </motion.div>
    </div>
  )
}

function getPhaseDescription(phase: DiscoveryPhase): string {
  const descriptions = {
    business_context: 'Understanding your business question and success criteria',
    source_discovery: 'Finding optimal data sources with platform compatibility analysis',
    feasibility_review: 'Assessing technical feasibility and implementation approach',
    sow_generation: 'Generating contract and implementation plan',
    completion: 'Discovery complete - ready for implementation'
  }
  
  return descriptions[phase] || 'Processing...'
}