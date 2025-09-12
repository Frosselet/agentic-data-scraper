'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ChatBubbleLeftRightIcon, 
  MagnifyingGlassIcon,
  ChartBarIcon,
  ClockIcon,
  UserGroupIcon,
  SparklesIcon
} from '@heroicons/react/24/outline'
import SourceDiscoveryAssistant from '@/components/SourceDiscoveryAssistant'
import PersonaSelector from '@/components/PersonaSelector'
import { Persona } from '@/types/personas'

export default function HomePage() {
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null)
  const [showAssistant, setShowAssistant] = useState(false)
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const handlePersonaSelect = (persona: Persona) => {
    setSelectedPersona(persona)
    setShowAssistant(true)
  }

  const resetToHome = () => {
    setSelectedPersona(null)
    setShowAssistant(false)
  }

  if (showAssistant && selectedPersona) {
    return (
      <SourceDiscoveryAssistant 
        persona={selectedPersona}
        onBack={resetToHome}
      />
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Header */}
      <header className="relative overflow-hidden bg-white/80 backdrop-blur-sm border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                  <SparklesIcon className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-gray-900">Agentic Data Sourcing</h1>
                  <p className="text-sm text-gray-500">Intelligent Source Discovery Platform</p>
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-6 text-sm text-gray-500">
              <div className="flex items-center space-x-2">
                <ClockIcon className="w-4 h-4" />
                <span>{currentTime.toLocaleTimeString()}</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                <span>Platform Online</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Start with Your <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Business Question</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Our AI assistant discovers optimal data sources by understanding your business needs first, 
              then recommends the most feasible path with our platform capabilities.
            </p>
          </motion.div>

          {/* Key Value Props */}
          <motion.div 
            className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-slate-200">
              <ChatBubbleLeftRightIcon className="w-8 h-8 text-blue-600 mb-4 mx-auto" />
              <h3 className="font-semibold text-gray-900 mb-2">Business-Question-First</h3>
              <p className="text-gray-600 text-sm">
                Start with what you need to solve, not what data you think you need
              </p>
            </div>
            
            <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-slate-200">
              <MagnifyingGlassIcon className="w-8 h-8 text-indigo-600 mb-4 mx-auto" />
              <h3 className="font-semibold text-gray-900 mb-2">Intelligent Source Discovery</h3>
              <p className="text-gray-600 text-sm">
                Access 5,000+ data sources with feasibility analysis based on our platform
              </p>
            </div>
            
            <div className="bg-white/60 backdrop-blur-sm rounded-xl p-6 border border-slate-200">
              <ChartBarIcon className="w-8 h-8 text-purple-600 mb-4 mx-auto" />
              <h3 className="font-semibold text-gray-900 mb-2">Real-Time SOW Generation</h3>
              <p className="text-gray-600 text-sm">
                Watch your data contract and SOW build as you make decisions
              </p>
            </div>
          </motion.div>
        </div>

        {/* Persona Selection */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Choose Your Role to Start
            </h3>
            <p className="text-gray-600 max-w-2xl mx-auto">
              The assistant adapts its conversation style, technical depth, and timing based on your role and preferences.
            </p>
          </div>

          <PersonaSelector onPersonaSelect={handlePersonaSelect} />
        </motion.div>

        {/* Platform Capabilities Preview */}
        <motion.div
          className="mt-20 bg-white/40 backdrop-blur-sm rounded-2xl p-8 border border-slate-200"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Platform Capabilities We'll Leverage
            </h3>
            <p className="text-gray-600">
              Our assistant knows exactly what we can do well and will recommend sources accordingly
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <div className="w-6 h-6 bg-green-600 rounded-full"></div>
              </div>
              <h4 className="font-medium text-gray-900 mb-1">REST APIs</h4>
              <p className="text-sm text-gray-500">500+ successful integrations</p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <div className="w-6 h-6 bg-green-600 rounded-full"></div>
              </div>
              <h4 className="font-medium text-gray-900 mb-1">Semantic Web</h4>
              <p className="text-sm text-gray-500">SKOS, SPARQL, 40+ languages</p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <div className="w-6 h-6 bg-green-600 rounded-full"></div>
              </div>
              <h4 className="font-medium text-gray-900 mb-1">Real-time Processing</h4>
              <p className="text-sm text-gray-500">KuzuDB, streaming pipelines</p>
            </div>

            <div className="text-center">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                <div className="w-6 h-6 bg-red-600 rounded-full"></div>
              </div>
              <h4 className="font-medium text-gray-900 mb-1">Computer Vision</h4>
              <p className="text-sm text-gray-500">Not available - we'll suggest alternatives</p>
            </div>
          </div>

          <div className="mt-6 text-center">
            <p className="text-sm text-gray-500">
              ✅ Green = Our strengths we'll leverage | ❌ Red = Gaps we'll help you navigate
            </p>
          </div>
        </motion.div>

        {/* Example Business Questions */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          <h3 className="text-xl font-semibold text-gray-900 mb-6">
            Example Business Questions We Can Help With
          </h3>
          <div className="flex flex-wrap justify-center gap-3">
            {[
              "How can we predict supply chain disruptions?",
              "What drives customer churn in our industry?", 
              "How do market trends affect our pricing?",
              "Which regions show the highest growth potential?",
              "What are early indicators of equipment failure?"
            ].map((question, index) => (
              <motion.div
                key={index}
                className="bg-white/60 backdrop-blur-sm px-4 py-2 rounded-full text-sm text-gray-700 border border-slate-200"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 300 }}
              >
                "{question}"
              </motion.div>
            ))}
          </div>
        </motion.div>
      </main>
    </div>
  )
}