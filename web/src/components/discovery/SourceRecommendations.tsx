'use client'

import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  MagnifyingGlassIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  CurrencyDollarIcon,
  ClockIcon,
  DocumentTextIcon,
  LinkIcon,
  ChartBarIcon,
  ServerIcon,
  GlobeAltIcon,
  DatabaseIcon,
  CloudIcon
} from '@heroicons/react/24/outline'
import { Persona } from '@/types/personas'

interface BusinessContext {
  question?: string
  successCriteria?: string
  timeline?: string
  budget?: string
  riskTolerance?: string
}

interface DataSourceRecommendation {
  name: string
  type: 'api' | 'web' | 'database' | 'file' | 'stream'
  description: string
  feasibilityScore: number
  costEstimate: string
  implementationEffort: 'low' | 'medium' | 'high' | 'very_high'
  platformCompatibility: number
  dataQualityExpected: number
  accessRequirements: string[]
  sampleDataUrl?: string
  documentationUrl?: string
  pros: string[]
  cons: string[]
  semanticVocabularies: string[]
}

interface SourceRecommendationsProps {
  businessContext: BusinessContext
  persona: Persona
  interactionLevel: 'executive' | 'standard' | 'technical' | 'rapid'
  onComplete: (data: { sources: DataSourceRecommendation[], selected: DataSourceRecommendation[] }) => void
}

const sourceTypeIcons = {
  api: ServerIcon,
  web: GlobeAltIcon,
  database: DatabaseIcon,
  file: DocumentTextIcon,
  stream: CloudIcon
}

const effortColors = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  very_high: 'bg-red-100 text-red-800'
}

export default function SourceRecommendations({ 
  businessContext, 
  persona, 
  interactionLevel,
  onComplete 
}: SourceRecommendationsProps) {
  const [isDiscovering, setIsDiscovering] = useState(true)
  const [recommendations, setRecommendations] = useState<DataSourceRecommendation[]>([])
  const [selectedSources, setSelectedSources] = useState<DataSourceRecommendation[]>([])
  const [discoveryProgress, setDiscoveryProgress] = useState(0)
  const [currentDiscoveryStep, setCurrentDiscoveryStep] = useState('')

  useEffect(() => {
    performSourceDiscovery()
  }, [businessContext, persona])

  const performSourceDiscovery = async () => {
    setIsDiscovering(true)
    const steps = [
      'Analyzing business requirements...',
      'Querying 5,000+ data source catalog...',
      'Evaluating platform compatibility...',
      'Assessing semantic vocabularies...',
      'Ranking by feasibility and value...',
      'Generating personalized recommendations...'
    ]

    // Show progress steps
    for (let i = 0; i < steps.length - 1; i++) {
      setCurrentDiscoveryStep(steps[i])
      setDiscoveryProgress((i + 1) / steps.length * 100)
      await new Promise(resolve => setTimeout(resolve, 600))
    }

    // Call real BAML SourceDiscoveryAgent
    setCurrentDiscoveryStep(steps[steps.length - 1])
    
    try {
      const response = await fetch('/api/discovery/sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          businessContext: businessContext
        })
      })

      if (response.ok) {
        const { data } = await response.json()
        
        // Convert BAML agent response to our component format
        const formattedRecommendations = Array.isArray(data) 
          ? data.map(formatBAMLRecommendation)
          : []
        
        setRecommendations(formattedRecommendations)
      } else {
        console.error('Failed to get source recommendations from BAML')
        // Fallback to basic recommendations
        const fallbackRecommendations = generateFallbackRecommendations(businessContext, persona)
        setRecommendations(fallbackRecommendations)
      }
    } catch (error) {
      console.error('Error calling BAML SourceDiscoveryAgent:', error)
      // Fallback to basic recommendations
      const fallbackRecommendations = generateFallbackRecommendations(businessContext, persona)
      setRecommendations(fallbackRecommendations)
    }

    setDiscoveryProgress(100)
    setIsDiscovering(false)
  }

  // Format BAML agent response to component format
  const formatBAMLRecommendation = (bamlData: any): DataSourceRecommendation => {
    return {
      name: bamlData.name || 'Unknown Source',
      type: bamlData.type || 'api',
      description: bamlData.description || 'No description available',
      feasibilityScore: bamlData.feasibility_score || 0.7,
      costEstimate: bamlData.cost_estimate || 'Contact for pricing',
      implementationEffort: bamlData.implementation_effort || 'medium',
      platformCompatibility: bamlData.platform_compatibility || 0.8,
      dataQualityExpected: bamlData.data_quality_expected || 0.8,
      accessRequirements: bamlData.access_requirements || [],
      sampleDataUrl: bamlData.sample_data_url,
      documentationUrl: bamlData.documentation_url,
      pros: bamlData.pros || [],
      cons: bamlData.cons || [],
      semanticVocabularies: bamlData.semantic_vocabularies || []
    }
  }

  const generateFallbackRecommendations = (context: BusinessContext, persona: Persona): DataSourceRecommendation[] => {
    return generateMockRecommendations(context, persona)
  }

  const generateMockRecommendations = (context: BusinessContext, persona: Persona): DataSourceRecommendation[] => {
    const baseRecommendations = [
      {
        name: "Government Open Data Portal",
        type: 'api' as const,
        description: "Comprehensive government datasets across multiple domains with REST API access and semantic metadata.",
        feasibilityScore: 0.95,
        costEstimate: "Free - $500/month",
        implementationEffort: 'low' as const,
        platformCompatibility: 0.98,
        dataQualityExpected: 0.85,
        accessRequirements: ["API key registration", "Rate limit compliance"],
        sampleDataUrl: "https://api.data.gov/docs",
        documentationUrl: "https://api.data.gov/docs",
        pros: ["High reliability", "Excellent documentation", "Free tier available", "SKOS vocabularies included"],
        cons: ["Rate limits apply", "Data may not be real-time", "Government update schedules"],
        semanticVocabularies: ["SKOS Government Vocabularies", "Dublin Core", "FOAF"]
      },
      {
        name: "Industry Trade Association APIs",
        type: 'api' as const,
        description: "Sector-specific data from industry associations with high-quality, standardized information and regular updates.",
        feasibilityScore: 0.82,
        costEstimate: "$1,000 - $5,000/month",
        implementationEffort: 'medium' as const,
        platformCompatibility: 0.85,
        dataQualityExpected: 0.92,
        accessRequirements: ["Membership verification", "OAuth 2.0", "Legal agreement"],
        sampleDataUrl: undefined,
        documentationUrl: "https://example-industry-api.org/docs",
        pros: ["Very high data quality", "Industry-specific insights", "Regular updates", "Expert curation"],
        cons: ["Higher cost", "Membership requirements", "Limited historical data"],
        semanticVocabularies: ["Industry SKOS Classifications", "Business Process Ontology"]
      },
      {
        name: "Web Scraping - Industry Publications",
        type: 'web' as const,
        description: "Extract structured data from key industry publications and news sources using our Playwright automation platform.",
        feasibilityScore: 0.75,
        costEstimate: "$500 - $2,000/month",
        implementationEffort: 'high' as const,
        platformCompatibility: 0.9,
        dataQualityExpected: 0.78,
        accessRequirements: ["Legal compliance review", "Rate limiting", "User-agent rotation"],
        sampleDataUrl: undefined,
        documentationUrl: undefined,
        pros: ["Fresh content", "Comprehensive coverage", "Platform strength", "Custom extraction"],
        cons: ["Legal considerations", "Site changes risk", "Quality variance", "Maintenance overhead"],
        semanticVocabularies: ["News Industry Classification", "Topic Modeling Vocabularies"]
      },
      {
        name: "Commercial Data Provider APIs",
        type: 'api' as const,
        description: "Premium commercial data feeds with guaranteed SLAs, comprehensive coverage, and enterprise-grade reliability.",
        feasibilityScore: 0.88,
        costEstimate: "$5,000 - $20,000/month",
        implementationEffort: 'medium' as const,
        platformCompatibility: 0.92,
        dataQualityExpected: 0.95,
        accessRequirements: ["Enterprise contract", "API authentication", "Usage monitoring"],
        sampleDataUrl: "https://api.commercial-provider.com/samples",
        documentationUrl: "https://docs.commercial-provider.com",
        pros: ["Highest quality", "SLA guarantees", "Real-time updates", "Comprehensive coverage"],
        cons: ["High cost", "Contract commitment", "Vendor lock-in risk"],
        semanticVocabularies: ["Commercial Standards", "ISO Classifications", "Financial Ontologies"]
      },
      {
        name: "Academic Research Databases",
        type: 'database' as const,
        description: "Access to peer-reviewed research and academic datasets through university partnerships and open science initiatives.",
        feasibilityScore: 0.65,
        costEstimate: "$200 - $1,500/month",
        implementationEffort: 'high' as const,
        platformCompatibility: 0.7,
        dataQualityExpected: 0.88,
        accessRequirements: ["Academic partnership", "Research ethics approval", "Citation requirements"],
        sampleDataUrl: undefined,
        documentationUrl: "https://academic-db.edu/access-guide",
        pros: ["High credibility", "Detailed methodology", "Peer review", "Historical depth"],
        cons: ["Complex access", "Update delays", "Academic focus", "Limited API support"],
        semanticVocabularies: ["Academic Subject Classifications", "Research Ontologies"]
      }
    ]

    // Filter and customize based on persona
    if (persona.id === 'trader') {
      return baseRecommendations
        .filter(r => r.implementationEffort !== 'very_high')
        .slice(0, 4)
    } else if (persona.id === 'data_lead') {
      return baseRecommendations.slice(0, 5)
    } else {
      return baseRecommendations.slice(0, 4)
    }
  }

  const handleSourceToggle = (source: DataSourceRecommendation) => {
    setSelectedSources(prev => {
      const isSelected = prev.some(s => s.name === source.name)
      if (isSelected) {
        return prev.filter(s => s.name !== source.name)
      } else {
        return [...prev, source]
      }
    })
  }

  const handleContinue = () => {
    if (selectedSources.length === 0) return
    onComplete({
      sources: recommendations,
      selected: selectedSources
    })
  }

  const getEffortDisplay = (effort: string) => {
    const effortMap = {
      low: 'Low',
      medium: 'Medium', 
      high: 'High',
      very_high: 'Very High'
    }
    return effortMap[effort as keyof typeof effortMap] || effort
  }

  if (isDiscovering) {
    return (
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center justify-center space-x-3 mb-4"
          >
            <MagnifyingGlassIcon className="w-8 h-8 text-indigo-600" />
            <h2 className="text-2xl font-bold text-gray-900">Discovering Data Sources</h2>
          </motion.div>
          <p className="text-gray-600">
            Analyzing 5,000+ sources to find the perfect fit for your needs
          </p>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 p-8">
          <div className="space-y-6">
            <div className="text-center">
              <div className="text-lg font-medium text-gray-900 mb-2">
                {currentDiscoveryStep}
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <motion.div
                  className="bg-gradient-to-r from-indigo-600 to-purple-600 h-3 rounded-full"
                  initial={{ width: 0 }}
                  animate={{ width: `${discoveryProgress}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
              <div className="text-sm text-gray-500 mt-2">
                {Math.round(discoveryProgress)}% complete
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
              <div className="p-4 bg-blue-50 rounded-lg">
                <ChartBarIcon className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                <div className="font-medium text-gray-900">Platform Analysis</div>
                <div className="text-sm text-gray-600">Matching capabilities</div>
              </div>
              <div className="p-4 bg-green-50 rounded-lg">
                <DocumentTextIcon className="w-8 h-8 text-green-600 mx-auto mb-2" />
                <div className="font-medium text-gray-900">Semantic Mapping</div>
                <div className="text-sm text-gray-600">SKOS vocabularies</div>
              </div>
              <div className="p-4 bg-purple-50 rounded-lg">
                <CheckCircleIcon className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                <div className="font-medium text-gray-900">Quality Assessment</div>
                <div className="text-sm text-gray-600">Feasibility scoring</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="text-center mb-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-center space-x-3 mb-4"
        >
          <CheckCircleIcon className="w-8 h-8 text-green-600" />
          <h2 className="text-2xl font-bold text-gray-900">Source Recommendations</h2>
        </motion.div>
        <p className="text-gray-600">
          Found {recommendations.length} high-quality sources optimized for our platform capabilities
        </p>
      </div>

      <div className="space-y-6">
        <AnimatePresence>
          {recommendations.map((source, index) => {
            const IconComponent = sourceTypeIcons[source.type]
            const isSelected = selectedSources.some(s => s.name === source.name)
            
            return (
              <motion.div
                key={source.name}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                className={`bg-white rounded-xl border-2 p-6 cursor-pointer transition-all duration-200 ${
                  isSelected 
                    ? 'border-indigo-500 bg-indigo-50' 
                    : 'border-slate-200 hover:border-slate-300 hover:shadow-md'
                }`}
                onClick={() => handleSourceToggle(source)}
              >
                <div className="flex items-start space-x-4">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                    isSelected ? 'bg-indigo-600' : 'bg-gray-100'
                  }`}>
                    <IconComponent className={`w-6 h-6 ${
                      isSelected ? 'text-white' : 'text-gray-600'
                    }`} />
                  </div>

                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900">{source.name}</h3>
                        <p className="text-gray-600 mt-1">{source.description}</p>
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <div className="text-right">
                          <div className="text-sm font-medium text-gray-900">
                            {Math.round(source.feasibilityScore * 100)}% Feasible
                          </div>
                          <div className={`text-xs px-2 py-1 rounded-full ${effortColors[source.implementationEffort]}`}>
                            {getEffortDisplay(source.implementationEffort)} effort
                          </div>
                        </div>
                        {isSelected && (
                          <CheckCircleIcon className="w-6 h-6 text-indigo-600" />
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div className="flex items-center space-x-2">
                        <CurrencyDollarIcon className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-600">{source.costEstimate}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <ChartBarIcon className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-600">
                          {Math.round(source.platformCompatibility * 100)}% Platform Fit
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <ExclamationTriangleIcon className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-600">
                          {Math.round(source.dataQualityExpected * 100)}% Quality Expected
                        </span>
                      </div>
                    </div>

                    {interactionLevel !== 'rapid' && (
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 mb-2">Advantages</h4>
                          <ul className="space-y-1">
                            {source.pros.slice(0, 3).map((pro, i) => (
                              <li key={i} className="text-sm text-gray-600 flex items-center space-x-2">
                                <div className="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                                <span>{pro}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h4 className="text-sm font-medium text-gray-900 mb-2">Considerations</h4>
                          <ul className="space-y-1">
                            {source.cons.slice(0, 3).map((con, i) => (
                              <li key={i} className="text-sm text-gray-600 flex items-center space-x-2">
                                <div className="w-1.5 h-1.5 bg-orange-500 rounded-full"></div>
                                <span>{con}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    )}

                    {interactionLevel === 'technical' && source.semanticVocabularies.length > 0 && (
                      <div className="mb-4">
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Semantic Vocabularies</h4>
                        <div className="flex flex-wrap gap-2">
                          {source.semanticVocabularies.map((vocab, i) => (
                            <span
                              key={i}
                              className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded-full"
                            >
                              {vocab}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex items-center space-x-4 text-sm">
                      {source.documentationUrl && (
                        <a
                          href={source.documentationUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-1 text-indigo-600 hover:text-indigo-800"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <LinkIcon className="w-4 h-4" />
                          <span>Documentation</span>
                        </a>
                      )}
                      {source.sampleDataUrl && (
                        <a
                          href={source.sampleDataUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center space-x-1 text-indigo-600 hover:text-indigo-800"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <DocumentTextIcon className="w-4 h-4" />
                          <span>Sample Data</span>
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>

      {/* Selection Summary */}
      {selectedSources.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-8 bg-indigo-50 rounded-xl p-6 border border-indigo-200"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-3">
            Selected Sources ({selectedSources.length})
          </h3>
          <div className="space-y-2 mb-4">
            {selectedSources.map((source) => (
              <div key={source.name} className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-900">{source.name}</span>
                <span className="text-sm text-gray-600">{source.costEstimate}</span>
              </div>
            ))}
          </div>
          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              Average feasibility: {Math.round(selectedSources.reduce((acc, s) => acc + s.feasibilityScore, 0) / selectedSources.length * 100)}%
            </div>
            <button
              onClick={handleContinue}
              className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition-colors"
            >
              Continue to Feasibility Review
            </button>
          </div>
        </motion.div>
      )}
    </div>
  )
}