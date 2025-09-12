'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  ChatBubbleLeftRightIcon,
  LightBulbIcon,
  ClockIcon,
  CurrencyDollarIcon,
  ExclamationTriangleIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline'
import { Persona } from '@/types/personas'

interface BusinessQuestionFlowProps {
  persona: Persona
  interactionLevel: 'executive' | 'standard' | 'technical' | 'rapid'
  onComplete: (data: any) => void
}

interface AIAssistantMessage {
  id: string
  type: 'assistant' | 'user' | 'system'
  content: string
  timestamp: Date
  suggestions?: string[]
}

interface BusinessContext {
  question: string
  successCriteria: string
  timeline: string
  budget: string
  riskTolerance: 'low' | 'medium' | 'high'
}

export default function BusinessQuestionFlow({ 
  persona, 
  interactionLevel,
  onComplete 
}: BusinessQuestionFlowProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [messages, setMessages] = useState<AIAssistantMessage[]>([])
  const [businessContext, setBusinessContext] = useState<Partial<BusinessContext>>({})
  const [isTyping, setIsTyping] = useState(false)

  // Initialize conversation based on persona
  useEffect(() => {
    const welcomeMessage = getPersonalizedWelcome(persona, interactionLevel)
    addMessage('assistant', welcomeMessage, getInitialSuggestions(persona))
  }, [persona, interactionLevel])

  const addMessage = (type: 'assistant' | 'user', content: string, suggestions?: string[]) => {
    const newMessage: AIAssistantMessage = {
      id: `msg_${Date.now()}`,
      type,
      content,
      timestamp: new Date(),
      suggestions
    }
    setMessages(prev => [...prev, newMessage])
  }

  const handleUserResponse = async (response: string, field?: keyof BusinessContext) => {
    addMessage('user', response)
    
    if (field) {
      setBusinessContext(prev => ({ ...prev, [field]: response }))
    }

    setIsTyping(true)
    
    const nextStep = currentStep + 1
    setCurrentStep(nextStep)
    
    if (nextStep < conversationSteps.length) {
      // Use real BAML agent for persona-aware responses
      try {
        const step = conversationSteps[nextStep]
        const aiResponse = step.getResponse(response, persona, interactionLevel)
        
        // Add small delay for better UX
        await new Promise(resolve => setTimeout(resolve, 800))
        
        addMessage('assistant', aiResponse.content, aiResponse.suggestions)
      } catch (error) {
        console.error('Error generating response:', error)
        // Fallback response
        addMessage('assistant', 'Thank you for your response. Please continue with the next question.')
      }
      setIsTyping(false)
    } else {
      // Complete the business context phase - call BAML BusinessContextAgent
      const completeContext = { ...businessContext, [field!]: response }
      
      try {
        const contextResponse = await fetch('/api/discovery/business-context', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question: completeContext.question,
            successCriteria: completeContext.successCriteria,
            timeline: completeContext.timeline,
            budget: completeContext.budget,
            riskTolerance: completeContext.riskTolerance,
            personaId: persona.id
          })
        })
        
        if (contextResponse.ok) {
          const { data } = await contextResponse.json()
          // Process the BAML agent response and enhance the context
          const enhancedContext = { ...completeContext, ...data }
          setIsTyping(false)
          setTimeout(() => onComplete(enhancedContext), 500)
        } else {
          console.error('Failed to process business context with BAML')
          setIsTyping(false)
          setTimeout(() => onComplete(completeContext), 500)
        }
      } catch (error) {
        console.error('Error calling BAML BusinessContextAgent:', error)
        setIsTyping(false)
        setTimeout(() => onComplete(completeContext), 500)
      }
    }
  }

  const conversationSteps = [
    {
      field: 'question' as keyof BusinessContext,
      getResponse: (userInput: string, persona: Persona, level: string) => ({
        content: getQuestionResponse(userInput, persona, level),
        suggestions: getSuccessCriteriaSuggestions(persona)
      })
    },
    {
      field: 'successCriteria' as keyof BusinessContext, 
      getResponse: (userInput: string, persona: Persona, level: string) => ({
        content: getSuccessCriteriaResponse(userInput, persona, level),
        suggestions: getTimelineSuggestions(persona)
      })
    },
    {
      field: 'timeline' as keyof BusinessContext,
      getResponse: (userInput: string, persona: Persona, level: string) => ({
        content: getTimelineResponse(userInput, persona, level),
        suggestions: getBudgetSuggestions(persona)
      })
    },
    {
      field: 'budget' as keyof BusinessContext,
      getResponse: (userInput: string, persona: Persona, level: string) => ({
        content: getBudgetResponse(userInput, persona, level),
        suggestions: ['Low Risk - Prefer proven sources', 'Medium Risk - Balanced approach', 'High Risk - Explore innovative sources']
      })
    },
    {
      field: 'riskTolerance' as keyof BusinessContext,
      getResponse: (userInput: string, persona: Persona, level: string) => ({
        content: `Perfect! I now understand your business context. Let me analyze this and discover the best data sources for your needs...`,
        suggestions: []
      })
    }
  ]

  const currentStepData = conversationSteps[currentStep]

  return (
    <div className="max-w-4xl mx-auto">
      {/* Phase Header */}
      <div className="text-center mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-center space-x-3 mb-4"
        >
          <ChatBubbleLeftRightIcon className="w-8 h-8 text-blue-600" />
          <h2 className="text-2xl font-bold text-gray-900">Business Context Discovery</h2>
        </motion.div>
        <p className="text-gray-600">
          Let's start with your business question, not available data
        </p>
      </div>

      {/* Chat Interface */}
      <div className="bg-white rounded-xl border border-slate-200 overflow-hidden">
        {/* Messages */}
        <div className="h-96 overflow-y-auto p-6 space-y-4">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-xs lg:max-w-md px-4 py-3 rounded-lg ${
                  message.type === 'user' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 text-gray-900'
                }`}>
                  {message.type === 'assistant' && (
                    <div className="flex items-center space-x-2 mb-2">
                      <div className="w-6 h-6 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center">
                        <span className="text-xs text-white font-medium">AI</span>
                      </div>
                      <span className="text-xs text-gray-500">Assistant</span>
                    </div>
                  )}
                  
                  <div className="text-sm leading-relaxed">
                    {message.content}
                  </div>
                  
                  {message.suggestions && message.suggestions.length > 0 && (
                    <div className="mt-3 space-y-1">
                      {message.suggestions.map((suggestion, index) => (
                        <button
                          key={index}
                          onClick={() => handleUserResponse(suggestion, currentStepData?.field)}
                          className="block w-full text-left text-xs bg-white/20 hover:bg-white/30 rounded px-3 py-2 transition-colors"
                        >
                          💡 {suggestion}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Typing Indicator */}
          {isTyping && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="bg-gray-100 text-gray-900 px-4 py-3 rounded-lg max-w-xs">
                <div className="flex items-center space-x-2">
                  <div className="w-6 h-6 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center">
                    <span className="text-xs text-white font-medium">AI</span>
                  </div>
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Input Area */}
        {currentStep < conversationSteps.length && (
          <div className="border-t border-gray-200 p-4">
            <BusinessQuestionInput
              step={currentStep}
              onSubmit={(value) => handleUserResponse(value, currentStepData?.field)}
              placeholder={getInputPlaceholder(currentStep, persona)}
            />
          </div>
        )}
      </div>

      {/* Progress Indicator */}
      <div className="mt-6">
        <div className="flex justify-between text-sm text-gray-500 mb-2">
          <span>Business Context Progress</span>
          <span>{Math.round((currentStep / conversationSteps.length) * 100)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <motion.div
            className="bg-gradient-to-r from-blue-600 to-indigo-600 h-2 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${(currentStep / conversationSteps.length) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>
    </div>
  )
}

// Input Component
function BusinessQuestionInput({ 
  step, 
  onSubmit, 
  placeholder 
}: { 
  step: number
  onSubmit: (value: string) => void
  placeholder: string 
}) {
  const [value, setValue] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (value.trim()) {
      onSubmit(value)
      setValue('')
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex space-x-3">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
      />
      <button
        type="submit"
        disabled={!value.trim()}
        className="px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        Send
      </button>
    </form>
  )
}

// Helper Functions
function getPersonalizedWelcome(persona: Persona, level: string): string {
  const baseGreeting = `Hi! I'm your AI data sourcing assistant. I see you're a ${persona.name} - perfect!`
  
  switch (persona.id) {
    case 'business_analyst':
      return `${baseGreeting} I'll help you discover data sources that align with your strategic goals. Let's start with your business question - what problem are you trying to solve?`
    case 'trader':
      return `${baseGreeting} I'll keep this focused and efficient. What business decision do you need data to support?`
    case 'data_lead':
      return `${baseGreeting} I'll provide technical depth on platform capabilities. What's the core business problem you're architecting a solution for?`
    default:
      return `${baseGreeting} What business question can I help you find the right data sources for?`
  }
}

function getInitialSuggestions(persona: Persona): string[] {
  switch (persona.id) {
    case 'trader':
      return [
        'How can we predict market movements?',
        'What drives customer behavior changes?',
        'Which regions show growth potential?'
      ]
    case 'business_analyst':
      return [
        'How can we predict supply chain disruptions?',
        'What factors influence customer churn?',
        'How do market trends affect our pricing strategy?'
      ]
    case 'data_lead':
      return [
        'How can we build real-time analytics for operations?',
        'What data architecture supports predictive modeling?',
        'How do we integrate external data with internal systems?'
      ]
    default:
      return [
        'How can we improve operational efficiency?',
        'What drives customer satisfaction?',
        'How do we identify new market opportunities?'
      ]
  }
}

function getQuestionResponse(question: string, persona: Persona, level: string): string {
  return `Excellent question! "${question}" - this gives me a clear direction. Now, how will you measure success? What specific outcomes would indicate we've solved this problem?`
}

function getSuccessCriteriaSuggestions(persona: Persona): string[] {
  switch (persona.id) {
    case 'trader':
      return ['95% prediction accuracy', '2-week advance warning', '10% cost reduction']
    default:
      return ['85% accuracy improvement', '2-week lead time', '15% efficiency gain', '90% stakeholder satisfaction']
  }
}

function getSuccessCriteriaResponse(criteria: string, persona: Persona, level: string): string {
  return `Perfect! "${criteria}" gives me concrete targets to optimize for. What's your timeline for needing these insights?`
}

function getTimelineSuggestions(persona: Persona): string[] {
  switch (persona.id) {
    case 'trader':
      return ['Within 2 weeks', 'End of month', 'Next quarter']
    default:
      return ['Within 6 months', 'End of quarter', 'By year-end', 'Flexible timeline']
  }
}

function getTimelineResponse(timeline: string, persona: Persona, level: string): string {
  return `Got it - "${timeline}" helps me prioritize feasible sources. What's your budget range for data acquisition and development?`
}

function getBudgetSuggestions(persona: Persona): string[] {
  switch (persona.id) {
    case 'data_lead':
      return ['Under $25k', '$25k-$100k', '$100k-$500k', 'Flexible based on ROI']
    default:
      return ['Under $10k', '$10k-$50k', '$50k-$200k', 'Depends on business value']
  }
}

function getBudgetResponse(budget: string, persona: Persona, level: string): string {
  return `Understood - "${budget}" helps me focus on cost-effective solutions. Finally, what's your risk tolerance for trying new or unproven data sources?`
}

function getInputPlaceholder(step: number, persona: Persona): string {
  const placeholders = [
    'Describe your business question...',
    'How will you measure success?',
    'What\'s your timeline?',
    'What\'s your budget range?',
    'Choose your risk tolerance...'
  ]
  
  return placeholders[step] || 'Type your response...'
}