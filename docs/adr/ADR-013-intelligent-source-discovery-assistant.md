# ADR-013: Intelligent Source Discovery & Feasibility Assistant

## Status
**PROPOSED** - AI-powered assistant for business-question-driven data source discovery

## Context

Current data sourcing approach starts with available data and tries to answer business questions. This creates bias and suboptimal solutions. Users often:

- Start with familiar data sources instead of optimal ones
- Miss high-value but challenging-to-access data
- Underestimate/overestimate technical feasibility 
- Make decisions without understanding our platform capabilities
- Spend effort on impossible or unnecessary data acquisition

**Key Insight**: We need to flip the process - start with business questions and work backwards to optimal sources while being transparent about our technical capabilities.

## Decision

Implement an **Intelligent Source Discovery & Feasibility Assistant** that:

1. **Business-Question-First**: Starts with user's business problem, not data availability
2. **Source Intelligence**: Knows thousands of data sources with access patterns
3. **Platform-Aware**: Understands our exact technical capabilities and limitations  
4. **Feasibility-Transparent**: Clear pros/cons with effort estimates
5. **Opinionated Recommendations**: Suggests optimal paths with reasoning

## Interactive Source Discovery Workflow

### Phase 1: Business Context Elicitation (3-5 minutes)

```
🎯 AI Assistant: "Let's start with your business question, not available data"

User Input Flow:
┌─ Business Question: "How can we predict supply chain disruptions?"
├─ Success Criteria: "2-week advance warning, 85% accuracy" 
├─ Decision Timeline: "Need insights within 6 months"
├─ Budget Constraints: "$50k data acquisition, $100k development"
└─ Risk Tolerance: "Medium - can handle some data gaps"

🤖 Assistant Analysis:
"I understand you need supply chain disruption prediction with 2-week lead time. 
Let me identify optimal data sources considering our platform capabilities..."
```

### Phase 2: Source Discovery & Feasibility Matrix (5-8 minutes)

```
🔍 DISCOVERED SOURCES RANKED BY BUSINESS IMPACT vs TECHNICAL FEASIBILITY

High Impact, High Feasibility (🟢 RECOMMENDED):
┌─────────────────────────────────────────────────────────────────────┐
│ 📊 Port Congestion APIs                             Feasibility: 95% │
│ ├─ Sources: Port Authority APIs, MarineTraffic      Cost: $2k/month  │
│ ├─ Our Capabilities: ✅ REST APIs, ✅ Real-time processing           │  
│ ├─ Business Value: Direct disruption indicator      Impact: HIGH     │
│ └─ Implementation: 2-3 weeks with existing collectors                │
│                                                                       │
│ 🌐 Trade Flow Data                                  Feasibility: 90%  │
│ ├─ Sources: UN Comtrade, EU Trade databases        Cost: Free + $5k   │
│ ├─ Our Capabilities: ✅ SPARQL, ✅ CSV processing                    │
│ ├─ Business Value: Historical disruption patterns  Impact: HIGH      │
│ └─ Implementation: 3-4 weeks, leverage SKOS mapping                  │
│                                                                       │
│ [✅ Select Both] [📊 Deep Analysis] [💰 Cost Breakdown]              │
└─────────────────────────────────────────────────────────────────────┘

High Impact, Medium Feasibility (🟡 CONSIDER WITH CAUTION):
┌─────────────────────────────────────────────────────────────────────┐
│ 🛰️ Satellite Imagery Analysis                      Feasibility: 65%  │
│ ├─ Sources: Planet Labs, Maxar                     Cost: $15k/month  │
│ ├─ Our Capabilities: ❌ Image processing pipeline (need development)  │
│ ├─ Business Value: Factory activity monitoring     Impact: HIGH      │
│ └─ Implementation: 4-6 months + ML team hiring                       │
│                                                                       │
│ ⚠️  Challenges: No existing computer vision pipeline                  │
│ 💡 Alternative: Partner with imagery analytics vendor                 │
│                                                                       │
│ [⚠️  Select with Risks] [🔄 Explore Alternatives] [❌ Skip for Now]   │
└─────────────────────────────────────────────────────────────────────┘

Medium Impact, High Feasibility (🔵 QUICK WINS):
┌─────────────────────────────────────────────────────────────────────┐
│ 📰 News Sentiment Analysis                         Feasibility: 90%  │
│ ├─ Sources: Reuters API, Financial news feeds     Cost: $8k/month   │
│ ├─ Our Capabilities: ✅ NLP pipeline, ✅ Real-time ingestion         │
│ ├─ Business Value: Early warning signals          Impact: MEDIUM    │
│ └─ Implementation: 2 weeks, reuse existing NER components            │
│                                                                       │
│ [📈 Add as Supplementary] [📋 Technical Details]                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Phase 3: Platform Capability Transparency (2-3 minutes)

```
🏗️ OUR PLATFORM CAPABILITIES ASSESSMENT

Current Strengths (✅ Ready to Use):
├─ REST API Collection: 500+ successful integrations
├─ SPARQL/Semantic Web: EU vocabularies, AGROVOC, LOV 
├─ Real-time Processing: KuzuDB, streaming pipelines
├─ NER/Text Processing: spaCy, multilingual support
├─ Geospatial Analysis: PostGIS integration
└─ SKOS Translation: 40+ languages, deterministic routing

Current Gaps (❌ Need Development):
├─ Computer Vision: No satellite imagery processing
├─ Audio Processing: No voice/sound analysis
├─ Blockchain APIs: Limited crypto data access
├─ Social Media: No Twitter/LinkedIn enterprise APIs
└─ IoT Sensors: No direct device integration

Development Capacity:
├─ Team Bandwidth: 2 senior devs, 1 data scientist
├─ Sprint Capacity: 40 story points / 2 weeks  
├─ Current Backlog: 60% capacity allocated through Q2
└─ New Feature Window: 40% capacity available

🎯 Recommendation: Focus on our strengths (APIs, semantic web, real-time) 
   rather than building new capabilities from scratch.
```

### Phase 4: Opinionated Source Recommendations (3-5 minutes)

```
🤖 AI ASSISTANT OPINIONATED RECOMMENDATIONS

Based on your business question + our platform capabilities:

🏆 OPTIMAL PATH (Confidence: 92%)
┌─────────────────────────────────────────────────────────────────────┐
│ "For supply chain disruption prediction, I strongly recommend this   │
│ data combination that leverages our existing semantic capabilities:" │
│                                                                       │
│ Primary Sources (Core Prediction):                                    │
│ 1. Port Congestion APIs → Real-time bottleneck detection             │
│ 2. UN Comtrade Data → Historical disruption pattern analysis         │
│ 3. Weather APIs → Climate-related shipping delays                    │
│                                                                       │
│ Why This Combination Works:                                           │
│ ✅ Leverages our SKOS multilingual routing                           │
│ ✅ Uses existing KuzuDB geospatial capabilities                      │  
│ ✅ Reuses proven REST API collection patterns                        │
│ ✅ Achievable with current team in 6-8 weeks                         │
│                                                                       │
│ Expected Outcomes:                                                    │
│ • 1-2 week disruption prediction (meets your requirement)            │
│ • 80-85% accuracy after 3 months tuning                             │
│ • Total cost: $12k setup + $7k/month operational                    │
│                                                                       │
│ [✅ Accept Recommendation] [🔧 Customize] [💭 Explore Alternatives]   │
└─────────────────────────────────────────────────────────────────────┘

⚠️  RISKY BUT VALUABLE PATH (Confidence: 45%)  
┌─────────────────────────────────────────────────────────────────────┐
│ "If you're willing to take risks for higher impact:"                 │
│                                                                       │
│ • Add satellite imagery for factory monitoring                       │
│ • Requires 6-month ML team expansion                                  │
│ • Could achieve 95% accuracy but 10x complexity                      │
│ • Success depends on hiring computer vision experts                  │
│                                                                       │
│ My Opinion: Don't do this now. Master the optimal path first,        │
│ then add satellite data as Phase 2.                                  │
│                                                                       │
│ [❌ I Agree - Skip for Now] [⚠️  I Want to Take the Risk]           │
└─────────────────────────────────────────────────────────────────────┘
```

### Phase 5: Real-Time SOW Generation (Visual Split-Screen)

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📋 LIVE SOW CONTRACT GENERATION                              🔄 Live │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│ Left Panel: Conversation                Right Panel: Generated SOW  │
│ ┌─────────────────────────┐             ┌─────────────────────────┐ │
│ │ 🤖 "Great choices!      │             │ sow_contract_id:        │ │
│ │ I'm now generating      │             │   "SUPPLY_DISRUPTION_  │ │
│ │ your SOW contract       │             │    PREDICTION_2025"     │ │
│ │ based on our            │             │                         │ │
│ │ conversation..."        │             │ business_objective:     │ │
│ │                         │             │   "Predict supply chain │ │
│ │ 👤 "Can you add the     │             │   disruptions 2 weeks  │ │
│ │ weather data we         │             │   in advance"           │ │
│ │ discussed?"             │             │                         │ │
│ │                         │             │ success_criteria:       │ │
│ │ 🤖 "Adding weather APIs │    ──────►  │   accuracy: "85%"       │ │
│ │ to data requirements... │             │   lead_time: "14 days"  │ │
│ │ Updated!"               │             │                         │ │
│ │                         │             │ data_sources:           │ │
│ │                         │             │   primary:              │ │
│ │                         │             │   - name: "Port APIs"   │ │
│ │                         │             │     cost: "$2k/month"   │ │
│ │                         │             │     feasibility: 95%    │ │
│ │                         │             │   - name: "UN Comtrade" │ │
│ │                         │             │     cost: "Free"        │ │  
│ │                         │             │     feasibility: 90%    │ │
│ └─────────────────────────┘             │   - name: "Weather APIs"│ │
│                                         │     cost: "$1k/month"   │ │
│                                         │     feasibility: 95%    │ │
│                                         │                         │ │
│                                         │ platform_capabilities:  │ │
│                                         │   leveraged:            │ │
│                                         │   - "SKOS translation"  │ │
│                                         │   - "KuzuDB geospatial" │ │
│                                         │   - "REST collection"   │ │
│                                         │                         │ │
│                                         │ [📋 View Full] [📤 Export] │
│                                         │ [🔗 Share] [💾 Save]    │ │
│                                         └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

### Phase 6: Interactive Knowledge Graph Visualization

```
┌─────────────────────────────────────────────────────────────────────┐
│ 🕸️ REAL-TIME KNOWLEDGE GRAPH (Powered by KuzuDB + yFiles)          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│        🎯 Business Question                                         │
│         │                                                           │
│         │ drives                                                    │
│         ▼                                                           │
│    📊 Port APIs ────────► 🤖 Disruption Model ────► 📈 2-week Alert │
│         │                        │                                  │
│         │ correlates with        │ enhanced by                      │
│         ▼                        ▼                                  │
│    🌐 Trade Data ──────────► 📍 Geospatial Context                  │
│         │                        │                                  │
│         │ SKOS mapped           │ stored in                         │
│         ▼                        ▼                                  │
│    📚 EU Vocabulary ────────► 🗄️ KuzuDB Graph                       │
│                                                                     │
│ 🎨 Interactive Features:                                           │
│ • Click nodes: See data source details                             │
│ • Drag relationships: Adjust data flow                             │
│ • Add nodes: Suggest additional sources                            │
│ • Color coding: Feasibility (green=easy, red=hard)                 │
│                                                                     │
│ [🔄 Auto-Layout] [➕ Add Source] [🎯 Focus on Business Value]       │
└─────────────────────────────────────────────────────────────────────┘
```

## Optimal Process Timing by Persona

### Persona-Optimized Duration

```yaml
Business Analyst (Primary User):
  optimal_duration: "15-20 minutes"
  attention_span: "High for strategic questions"
  pain_points: ["Technical complexity", "Feasibility uncertainty"]
  value_focus: ["Business impact", "Risk assessment", "Timeline clarity"]
  
Data Analyst: 
  optimal_duration: "12-18 minutes"
  attention_span: "High for technical details"
  pain_points: ["Data quality unknowns", "Integration complexity"]
  value_focus: ["Data structure", "API documentation", "Quality metrics"]
  
Data Lead/Architect:
  optimal_duration: "20-25 minutes"
  attention_span: "Very high for technical depth"  
  pain_points: ["Platform limitations", "Resource allocation"]
  value_focus: ["Technical feasibility", "Team capacity", "Architecture fit"]
  
Trader/Business User:
  optimal_duration: "8-12 minutes"
  attention_span: "Medium, results-focused"
  pain_points: ["Too much technical detail", "Slow decisions"]
  value_focus: ["Speed to insights", "Cost/benefit", "Risk/reward"]
```

### Adaptive Process Flow

```python
class PersonaAdaptiveAssistant:
    def __init__(self, user_persona: str):
        self.persona = user_persona
        self.interaction_level = "medium"  # adjustable
        
    def adjust_interaction_depth(self, level: str):
        """User can adjust detail level anytime"""
        self.interaction_depth = {
            "executive": "High-level only, focus on business impact",
            "standard": "Balanced business + technical details", 
            "technical": "Deep technical analysis and constraints",
            "rapid": "Quick decisions, minimal explanation"
        }[level]
    
    def get_optimal_timing(self) -> dict:
        return {
            "business_analyst": {
                "context_gathering": "4-5 min",
                "source_discovery": "6-8 min", 
                "feasibility_review": "3-4 min",
                "sow_generation": "2-3 min",
                "total": "15-20 min"
            },
            "trader": {
                "context_gathering": "2-3 min",
                "source_discovery": "4-5 min",
                "feasibility_review": "1-2 min", 
                "sow_generation": "1-2 min",
                "total": "8-12 min"
            }
        }
```

## Key Assistant Capabilities

### Business Question Intelligence
- Recognizes 200+ common business question patterns
- Maps questions to optimal data source categories
- Understands feasibility vs impact trade-offs

### Source Knowledge Base  
- 5,000+ curated data sources with access patterns
- Real-time API status monitoring
- Cost intelligence (pricing models, rate limits)
- Quality ratings based on user feedback

### Platform Awareness
- Exact inventory of our technical capabilities
- Team capacity and skill assessments  
- Historical project success rates
- Real platform limitations and constraints

### Feasibility Modeling
- Technical complexity scoring (1-100)
- Resource requirement estimation
- Risk assessment with mitigation strategies
- Timeline prediction with confidence intervals

This creates a **business-question-first data sourcing experience** that prevents bias, optimizes for our platform capabilities, and provides transparent feasibility assessment before users commit to data acquisition paths.