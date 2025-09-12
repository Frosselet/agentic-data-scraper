'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ArrowLeftIcon,
  ChatBubbleLeftRightIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  DocumentTextIcon,
  EyeIcon,
  ShareIcon
} from '@heroicons/react/24/outline'
import { Persona } from '@/types/personas'
import BusinessQuestionFlow from './discovery/BusinessQuestionFlow'
import SourceRecommendations from './discovery/SourceRecommendations' 
import SplitScreenSOWBuilder from './discovery/SplitScreenSOWBuilder'
import ProgressIndicator from './discovery/ProgressIndicator'

interface SourceDiscoveryAssistantProps {
  persona: Persona
  onBack: () => void
}

export type DiscoveryPhase = 
  | 'business_context'
  | 'source_discovery'
  | 'feasibility_review'
  | 'sow_generation'
  | 'completion'

interface DiscoverySession {
  sessionId: string
  persona: Persona
  currentPhase: DiscoveryPhase
  startTime: Date
  estimatedDuration: number // minutes
  businessContext: {
    question?: string
    successCriteria?: string
    timeline?: string
    budget?: string
    riskTolerance?: string
  }
  discoveredSources: any[]
  selectedSources: any[]
  generatedSOW: any
  interactionLevel: 'executive' | 'standard' | 'technical' | 'rapid'
}

export default function SourceDiscoveryAssistant({ 
  persona, 
  onBack 
}: SourceDiscoveryAssistantProps) {
  const [session, setSession] = useState<DiscoverySession>({
    sessionId: `session_${Date.now()}`,
    persona,
    currentPhase: 'business_context',
    startTime: new Date(),
    estimatedDuration: parseInt(persona.optimalDuration.split('-')[1]) || 20,
    businessContext: {},
    discoveredSources: [],
    selectedSources: [],
    generatedSOW: null,
    interactionLevel: persona.interactionStyle
  })

  const [elapsed, setElapsed] = useState(0)
  const [showSplitScreen, setShowSplitScreen] = useState(false)

  // Timer for session tracking
  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date()
      const elapsedMinutes = Math.floor((now.getTime() - session.startTime.getTime()) / 60000)
      setElapsed(elapsedMinutes)
    }, 1000)

    return () => clearInterval(timer)
  }, [session.startTime])

  const handlePhaseComplete = (phase: DiscoveryPhase, data: any) => {
    setSession(prev => {
      const newSession = { ...prev }
      
      switch (phase) {
        case 'business_context':
          newSession.businessContext = data
          newSession.currentPhase = 'source_discovery'
          break
        case 'source_discovery':
          newSession.discoveredSources = data.sources
          newSession.selectedSources = data.selected
          newSession.currentPhase = 'feasibility_review'
          break
        case 'feasibility_review':
          newSession.currentPhase = 'sow_generation'
          setShowSplitScreen(true)
          break
        case 'sow_generation':
          newSession.generatedSOW = data
          newSession.currentPhase = 'completion'
          break
      }
      
      return newSession
    })
  }

  const handleInteractionLevelChange = (level: 'executive' | 'standard' | 'technical' | 'rapid') => {
    setSession(prev => ({ ...prev, interactionLevel: level }))
  }

  const phases = [
    { id: 'business_context', name: 'Business Context', duration: '3-5 min' },
    { id: 'source_discovery', name: 'Source Discovery', duration: '5-8 min' },
    { id: 'feasibility_review', name: 'Feasibility Review', duration: '2-3 min' },
    { id: 'sow_generation', name: 'SOW Generation', duration: '2-3 min' }
  ]

  const currentPhaseIndex = phases.findIndex(p => p.id === session.currentPhase)
  const progressPercentage = ((currentPhaseIndex + 1) / phases.length) * 100

  if (showSplitScreen && session.currentPhase === 'sow_generation') {
    return (
      <SplitScreenSOWBuilder
        session={session}
        onComplete={(sovData) => handlePhaseComplete('sow_generation', sovData)}
        onBack={() => setShowSplitScreen(false)}
      />
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header with Progress */}
      <header className="bg-white/80 backdrop-blur-sm border-b border-slate-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            {/* Back Navigation */}
            <div className="flex items-center space-x-4">
              <button
                onClick={onBack}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <ArrowLeftIcon className="w-5 h-5" />
                <span className="font-medium">Back</span>
              </button>
              
              <div className="h-6 w-px bg-gray-300" />
              
              <div>
                <h1 className="text-lg font-semibold text-gray-900">
                  Source Discovery Assistant
                </h1>
                <p className="text-sm text-gray-500">
                  {persona.name} • {persona.interactionStyle} mode
                </p>
              </div>
            </div>

            {/* Session Info */}
            <div className="flex items-center space-x-6">
              {/* Interaction Level Selector */}
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-500">Detail Level:</span>
                <select 
                  value={session.interactionLevel}
                  onChange={(e) => handleInteractionLevelChange(e.target.value as any)}
                  className="text-sm bg-white border border-gray-200 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="executive">Executive</option>
                  <option value="standard">Standard</option>
                  <option value="technical">Technical</option>
                  <option value="rapid">Rapid</option>
                </select>
              </div>

              {/* Time Tracking */}
              <div className="flex items-center space-x-2 text-sm">
                <ClockIcon className="w-4 h-4 text-gray-400" />
                <span className={`${elapsed > session.estimatedDuration ? 'text-orange-600' : 'text-gray-600'}`}>
                  {elapsed} / {session.estimatedDuration} min
                </span>
              </div>

              {/* Status */}
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-500">Active Session</span>
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <ProgressIndicator
              phases={phases}
              currentPhase={session.currentPhase}
              percentage={progressPercentage}
            />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <AnimatePresence mode="wait">
          {session.currentPhase === 'business_context' && (
            <motion.div
              key="business_context"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <BusinessQuestionFlow
                persona={session.persona}
                interactionLevel={session.interactionLevel}
                onComplete={(data) => handlePhaseComplete('business_context', data)}
              />
            </motion.div>
          )}

          {session.currentPhase === 'source_discovery' && (
            <motion.div
              key="source_discovery" 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <SourceRecommendations
                businessContext={session.businessContext}
                persona={session.persona}
                interactionLevel={session.interactionLevel}
                onComplete={(data) => handlePhaseComplete('source_discovery', data)}
              />
            </motion.div>
          )}

          {session.currentPhase === 'feasibility_review' && (
            <motion.div
              key="feasibility_review"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.3 }}
            >
              <div className="bg-white rounded-xl p-8 border border-slate-200">
                <div className="text-center mb-8">
                  <CheckCircleIcon className="w-12 h-12 text-green-600 mx-auto mb-4" />
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">
                    Feasibility Review Complete
                  </h2>
                  <p className="text-gray-600">
                    Ready to generate your SOW contract and implementation plan
                  </p>
                </div>

                <div className="flex justify-center">
                  <button
                    onClick={() => handlePhaseComplete('feasibility_review', {})}
                    className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-8 py-3 rounded-lg font-medium hover:from-blue-700 hover:to-indigo-700 transition-all duration-200"
                  >
                    Generate SOW Contract
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {session.currentPhase === 'completion' && (
            <motion.div
              key="completion"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
            >
              <div className="bg-white rounded-xl p-8 border border-slate-200 text-center">
                <CheckCircleIcon className="w-16 h-16 text-green-600 mx-auto mb-6" />
                <h2 className="text-3xl font-bold text-gray-900 mb-4">
                  Discovery Complete!
                </h2>
                <p className="text-xl text-gray-600 mb-8">
                  Your SOW contract and implementation plan are ready
                </p>

                <div className="flex justify-center space-x-4">
                  <button className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                    <DocumentTextIcon className="w-5 h-5" />
                    <span>Download SOW</span>
                  </button>
                  <button className="flex items-center space-x-2 bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors">
                    <ShareIcon className="w-5 h-5" />
                    <span>Share Session</span>
                  </button>
                  <button 
                    onClick={onBack}
                    className="flex items-center space-x-2 bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                  >
                    <span>Start New Discovery</span>
                  </button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  )
}