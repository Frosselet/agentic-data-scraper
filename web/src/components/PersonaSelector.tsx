'use client'

import { motion } from 'framer-motion'
import { 
  ChartBarIcon,
  CodeBracketIcon,
  Cog6ToothIcon,
  BoltIcon,
  UserGroupIcon,
  ClockIcon
} from '@heroicons/react/24/outline'
import { Persona, personas } from '@/types/personas'

interface PersonaSelectorProps {
  onPersonaSelect: (persona: Persona) => void
}

const iconMap = {
  'chart-bar': ChartBarIcon,
  'code-bracket': CodeBracketIcon,
  'cog-6-tooth': Cog6ToothIcon,
  'lightning-bolt': BoltIcon,
}

const colorMap = {
  blue: 'from-blue-500 to-blue-600',
  green: 'from-green-500 to-green-600', 
  purple: 'from-purple-500 to-purple-600',
  orange: 'from-orange-500 to-orange-600',
}

export default function PersonaSelector({ onPersonaSelect }: PersonaSelectorProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {personas.map((persona, index) => {
        const IconComponent = iconMap[persona.icon as keyof typeof iconMap]
        const gradientColor = colorMap[persona.color as keyof typeof colorMap]
        
        return (
          <motion.div
            key={persona.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
            whileHover={{ y: -5, scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="cursor-pointer"
            onClick={() => onPersonaSelect(persona)}
          >
            <div className="bg-white/80 backdrop-blur-sm rounded-xl p-6 border border-slate-200 hover:border-slate-300 transition-all duration-200 hover:shadow-lg">
              {/* Icon */}
              <div className={`w-12 h-12 bg-gradient-to-r ${gradientColor} rounded-lg flex items-center justify-center mb-4`}>
                <IconComponent className="w-6 h-6 text-white" />
              </div>
              
              {/* Header */}
              <div className="mb-4">
                <h3 className="font-semibold text-gray-900 mb-1">
                  {persona.name}
                </h3>
                <p className="text-sm text-gray-600">
                  {persona.title}
                </p>
              </div>
              
              {/* Description */}
              <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                {persona.description}
              </p>
              
              {/* Duration */}
              <div className="flex items-center space-x-2 mb-4">
                <ClockIcon className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-500">
                  {persona.optimalDuration}
                </span>
              </div>
              
              {/* Key Focus Areas */}
              <div className="mb-4">
                <p className="text-xs font-medium text-gray-700 mb-2">Focus Areas:</p>
                <div className="flex flex-wrap gap-1">
                  {persona.valueFocus.slice(0, 2).map((focus, i) => (
                    <span 
                      key={i}
                      className={`inline-block px-2 py-1 bg-gradient-to-r ${gradientColor} bg-opacity-10 text-xs rounded-full text-gray-600`}
                    >
                      {focus.split(' ').slice(0, 2).join(' ')}
                    </span>
                  ))}
                </div>
              </div>
              
              {/* Interaction Style */}
              <div className="flex items-center justify-between text-xs text-gray-500">
                <span className="capitalize">{persona.interactionStyle} mode</span>
                <span className="capitalize">{persona.attentionSpan} attention</span>
              </div>
              
              {/* CTA */}
              <div className="mt-4 pt-4 border-t border-gray-100">
                <div className={`text-center text-sm font-medium bg-gradient-to-r ${gradientColor} bg-clip-text text-transparent`}>
                  Start Discovery →
                </div>
              </div>
            </div>
          </motion.div>
        )
      })}
      
      {/* Custom Persona Option */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: personas.length * 0.1 }}
        whileHover={{ y: -5, scale: 1.02 }}
        className="cursor-pointer"
      >
        <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border-2 border-dashed border-slate-300 hover:border-slate-400 transition-all duration-200 hover:bg-white/80">
          <div className="text-center">
            <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center mx-auto mb-4">
              <UserGroupIcon className="w-6 h-6 text-gray-400" />
            </div>
            
            <h3 className="font-semibold text-gray-700 mb-2">
              Custom Role
            </h3>
            
            <p className="text-sm text-gray-500 mb-4">
              Configure your own interaction preferences and technical depth
            </p>
            
            <div className="text-sm text-gray-400">
              Coming Soon
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}