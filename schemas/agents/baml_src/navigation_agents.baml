// Mississippi River Navigation Intelligence Agents
// Specialized agents for route optimization, cost analysis, and navigation decision-making

enum TransportMode {
  RIVER
  RAIL  
  TRUCK
  MULTIMODAL
}

enum NavigationPriority {
  COST_OPTIMIZATION
  TIME_CRITICAL
  RISK_MITIGATION
  FUEL_EFFICIENCY
  RELIABILITY
}

enum RiskLevel {
  LOW
  MODERATE
  HIGH
  CRITICAL
}

class WaterwayConditions {
  water_level float
  flow_rate float
  navigation_status string
  ice_conditions string?
  weather_impact string?
  lock_delays int[]
  depth_restrictions float[]
}

class VesselSpecifications {
  vessel_id string
  vessel_type string
  length float
  width float
  draft float
  cargo_capacity float
  current_load float
  fuel_consumption float
}

class RoutingRequest {
  origin_port string
  destination_port string
  commodity string
  quantity_tons float
  departure_time string
  priority NavigationPriority
  max_delay_hours int?
  budget_constraint float?
  vessel_specs VesselSpecifications?
}

class RouteOption {
  route_id string
  transport_mode TransportMode
  total_distance_miles float
  estimated_travel_time_hours float
  total_cost_usd float
  risk_assessment RiskLevel
  fuel_cost float
  lock_fees float[]
  delay_probability float
  confidence_score float
  route_segments string[]
  alternative_modes string[]
  cost_breakdown map<string, float>
}

class NavigationRecommendation {
  recommended_route RouteOption
  alternative_routes RouteOption[]
  risk_factors string[]
  cost_analysis map<string, float>
  timing_considerations string[]
  weather_alerts string[]
  market_insights string[]
  action_items string[]
  decision_rationale string
}

class CongestionAlert {
  location string
  river_mile float
  severity RiskLevel
  estimated_delay_hours float
  affected_vessels int
  alternative_routes string[]
  cost_impact_percent float
}

class MarketOpportunity {
  commodity string
  origin_price float
  destination_price float
  arbitrage_potential float
  transport_cost float
  net_profit_per_ton float
  market_window_days int
  confidence_level float
}

// Core Navigation Intelligence Agent
function NavigationIntelligenceAgent(
  routing_request: RoutingRequest,
  current_conditions: WaterwayConditions
) -> NavigationRecommendation {
  client GPT4
  
  prompt #"
    You are the Mississippi River Navigation Intelligence Agent, an expert system for optimizing inland waterway transportation routes and costs.
    
    ROUTING REQUEST:
    Origin: {{ routing_request.origin_port }}
    Destination: {{ routing_request.destination_port }}
    Commodity: {{ routing_request.commodity }} ({{ routing_request.quantity_tons }} tons)
    Departure: {{ routing_request.departure_time }}
    Priority: {{ routing_request.priority }}
    {% if routing_request.vessel_specs %}
    Vessel: {{ routing_request.vessel_specs.vessel_type }} ({{ routing_request.vessel_specs.length }}ft x {{ routing_request.vessel_specs.width }}ft, {{ routing_request.vessel_specs.draft }}ft draft)
    {% endif %}

    CURRENT WATERWAY CONDITIONS:
    Water Level: {{ current_conditions.water_level }}ft
    Flow Rate: {{ current_conditions.flow_rate }} cfs
    Navigation Status: {{ current_conditions.navigation_status }}
    {% if current_conditions.ice_conditions %}Ice Conditions: {{ current_conditions.ice_conditions }}{% endif %}
    {% if current_conditions.weather_impact %}Weather Impact: {{ current_conditions.weather_impact }}{% endif %}
    Lock Delays: {{ current_conditions.lock_delays | join(', ') }} minutes

    ANALYSIS REQUIREMENTS:
    1. **Route Optimization**: Analyze all viable transportation routes (river primary, rail/truck alternatives)
    2. **Cost Analysis**: Calculate comprehensive costs including fuel, lock fees, delays, opportunity costs
    3. **Risk Assessment**: Evaluate navigation risks, weather impacts, congestion, seasonal factors
    4. **Multi-Modal Integration**: Consider combined river-rail-truck solutions for optimal efficiency
    5. **Market Intelligence**: Factor in commodity prices, transport rate differentials, timing premiums

    DECISION FRAMEWORK:
    - **Cost Priority**: Minimize total delivered cost per ton
    - **Time Priority**: Optimize for fastest delivery with acceptable cost premium
    - **Risk Priority**: Choose most reliable route with contingency planning
    - **Fuel Priority**: Minimize fuel consumption and environmental impact
    - **Reliability Priority**: Select historically most dependable routing options

    Provide detailed analysis with:
    - Primary route recommendation with full justification
    - Alternative routes ranked by optimization criteria
    - Risk factors and mitigation strategies
    - Cost breakdown showing all components
    - Timing analysis with delay probabilities
    - Market insights and profit optimization opportunities
    - Specific action items for operators

    Focus on actionable intelligence that enables optimal navigation decisions.
  "#
}

// Hydroogical Risk Assessment Agent
function HydrologicalRiskAgent(
  waterway_segments: string[],
  forecast_period_days: int
) -> map<string, RiskLevel> {
  client GPT4
  
  prompt #"
    You are the Hydrological Risk Assessment Agent specializing in Mississippi River navigation conditions.

    WATERWAY SEGMENTS TO ANALYZE: {{ waterway_segments | join(', ') }}
    FORECAST PERIOD: {{ forecast_period_days }} days

    Analyze each waterway segment for navigation risks:

    RISK FACTORS TO EVALUATE:
    1. **Water Levels**: Current vs. historical patterns, flood/drought conditions
    2. **Flow Rates**: Impact on navigation speed and vessel control
    3. **Seasonal Patterns**: Historical trends for this time of year
    4. **Weather Forecasts**: Precipitation, temperature, wind impacts
    5. **Ice Conditions**: Formation risk, thickness, navigation impacts
    6. **Lock Operations**: Planned maintenance, capacity constraints
    7. **Channel Conditions**: Depth restrictions, dredging needs, debris

    For each segment, classify risk as LOW, MODERATE, HIGH, or CRITICAL and provide:
    - Primary risk factors
    - Probability of navigation disruption
    - Expected duration of any restrictions
    - Alternative routing recommendations
    - Monitoring points and trigger conditions

    Return risk assessment map with segment IDs as keys and detailed risk analysis.
  "#
}

// Economic Optimization Agent  
function EconomicOptimizationAgent(
  market_data: map<string, float>,
  transport_rates: map<string, float>,
  routing_options: RouteOption[]
) -> MarketOpportunity[] {
  client GPT4
  
  prompt #"
    You are the Economic Optimization Agent for Mississippi River commodity trading and transportation.

    MARKET DATA:
    {% for key, value in market_data.items() %}
    - {{ key }}: ${{ value }}
    {% endfor %}

    TRANSPORT RATES:
    {% for key, value in transport_rates.items() %}
    - {{ key }}: ${{ value }}/ton
    {% endfor %}

    ROUTING OPTIONS ANALYSIS:
    {% for route in routing_options %}
    Route {{ route.route_id }}:
    - Mode: {{ route.transport_mode }}
    - Cost: ${{ route.total_cost_usd }}
    - Time: {{ route.estimated_travel_time_hours }} hours
    - Risk: {{ route.risk_assessment }}
    {% endfor %}

    OPTIMIZATION ANALYSIS:
    1. **Arbitrage Opportunities**: Identify profitable commodity movements based on price differentials
    2. **Transport Cost Efficiency**: Compare route economics across all transport modes
    3. **Timing Premiums**: Calculate value of faster delivery vs. cost savings
    4. **Risk-Adjusted Returns**: Factor transportation risks into profit calculations
    5. **Market Windows**: Identify optimal timing based on seasonal patterns and forecasts
    6. **Portfolio Effects**: Consider multiple shipments and route diversification

    For each viable market opportunity, calculate:
    - Net profit per ton after all transportation costs
    - Market window duration and urgency
    - Risk-adjusted expected returns
    - Optimal route selection rationale
    - Volume recommendations and capacity constraints

    Focus on actionable trading and routing decisions that maximize economic value.
  "#
}

// Congestion Management Agent
function CongestionManagementAgent(
  current_traffic: map<string, int>,
  lock_queues: map<string, int>
) -> CongestionAlert[] {
  client GPT4
  
  prompt #"
    You are the Congestion Management Agent for Mississippi River navigation traffic optimization.

    CURRENT TRAFFIC VOLUMES:
    {% for key, value in current_traffic.items() %}
    - {{ key }}: {{ value }} vessels
    {% endfor %}

    LOCK QUEUE STATUS:
    {% for key, value in lock_queues.items() %}
    - {{ key }}: {{ value }} vessels waiting
    {% endfor %}

    CONGESTION ANALYSIS:
    1. **Traffic Bottlenecks**: Identify current and predicted congestion points
    2. **Lock Efficiency**: Analyze lockage delays and queue management
    3. **Alternative Routing**: Recommend traffic distribution strategies  
    4. **Peak Hour Management**: Optimize vessel scheduling to reduce conflicts
    5. **Capacity Utilization**: Maximize throughput within safety constraints
    6. **Emergency Protocols**: Plan for breakdown scenarios and traffic diversions

    For each congestion point, provide:
    - Severity assessment and current delay estimates
    - Root cause analysis (traffic volume, lock maintenance, weather, etc.)
    - Alternative routing options with cost/time impacts
    - Traffic management recommendations
    - Expected resolution timeline
    - Prevention strategies for future occurrences

    Generate actionable congestion alerts with specific vessel routing recommendations.
  "#
}

// Multi-Modal Optimization Agent
function MultiModalOptimizationAgent(
  origin: string,
  destination: string,
  commodity: string,
  quantity_tons: float,
  service_requirements: map<string, string>
) -> RouteOption[] {
  client GPT4
  
  prompt #"
    You are the Multi-Modal Transportation Optimization Agent specializing in river-rail-truck integration for agricultural and industrial commodities.

    SHIPMENT DETAILS:
    Origin: {{ origin }}
    Destination: {{ destination }}
    Commodity: {{ commodity }}
    Quantity: {{ quantity_tons }} tons

    SERVICE REQUIREMENTS:
    {% for key, value in service_requirements.items() %}
    - {{ key }}: {{ value }}
    {% endfor %}

    MULTI-MODAL ANALYSIS:
    1. **River-Only Route**: Traditional barge transportation via Mississippi River system
    2. **Rail-Only Route**: Unit train or manifest freight via Class I railroads
    3. **Truck-Only Route**: Over-the-road transportation (for smaller quantities)
    4. **River-Rail Combination**: Optimize modal split for cost/service balance
    5. **River-Truck Combination**: Last-mile trucking with river main haul
    6. **Rail-Truck Combination**: Truck pickup/delivery with rail line haul

    For each viable combination, calculate:
    - Total transportation cost including transload fees
    - Transit time from origin to destination
    - Service reliability and on-time performance
    - Capacity constraints and booking requirements
    - Environmental impact and sustainability metrics
    - Risk factors including weather, congestion, equipment availability

    OPTIMIZATION CRITERIA:
    - Minimize total delivered cost
    - Meet service time requirements
    - Ensure adequate capacity and equipment availability
    - Balance cost vs. reliability based on commodity value
    - Consider seasonal factors and modal capacity constraints

    Rank route options by overall value proposition with detailed justification.
  "#
}

// Real-Time Decision Support Agent
function DecisionSupportAgent(
  current_situation: string,
  available_options: RouteOption[],
  constraints: map<string, string>
) -> string {
  client GPT4
  
  prompt #"
    You are the Real-Time Decision Support Agent for Mississippi River navigation operations.

    CURRENT SITUATION:
    {{ current_situation }}

    AVAILABLE OPTIONS:
    {% for option in available_options %}
    Option {{ loop.index }}: {{ option.transport_mode }}
    - Cost: ${{ option.total_cost_usd }}
    - Time: {{ option.estimated_travel_time_hours }} hours
    - Risk: {{ option.risk_assessment }}
    - Confidence: {{ option.confidence_score }}%
    {% endfor %}

    OPERATIONAL CONSTRAINTS:
    {% for constraint_key in constraints %}
    - {{ constraint_key }}: {{ constraints[constraint_key] }}
    {% endfor %}

    DECISION SUPPORT ANALYSIS:
    You must provide immediate, actionable decision support for navigation operators facing time-critical situations.

    1. **Situation Assessment**: Analyze the urgency and complexity of the current situation
    2. **Option Evaluation**: Rank available options by decision criteria (cost, time, risk, reliability)
    3. **Trade-off Analysis**: Clearly explain key trade-offs between options
    4. **Recommendation**: Provide specific, actionable recommendation with clear rationale
    5. **Contingency Planning**: Outline backup plans if primary recommendation fails
    6. **Monitoring Points**: Identify key indicators to monitor for decision validation

    Your response should be:
    - Clear and decisive for immediate action
    - Backed by quantitative analysis where possible
    - Acknowledge uncertainties and provide confidence levels
    - Include specific next steps and timeline
    - Consider both immediate and downstream impacts

    Provide executive-level decision guidance that enables confident operational choices.
  "#
}