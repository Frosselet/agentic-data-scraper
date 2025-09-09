"""
SOW Elicitation Wizard - Business-Friendly Interface

Creates a magical experience where business users feel understood while the system
captures everything needed for the revolutionary 4D ET(K)L platform.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from uuid import uuid4

from ..schemas.sow import (
    SemanticStatementOfWork,
    ExplicitRequirements,
    BusinessChallenge,
    EntityToTrack,
    SpatialContext,
    LocationMention,
    TemporalContext,
    CriticalPeriod,
    StakeholderInvolved,
    DesiredOutcome,
    ConstraintsAndLimitations,
    ElicitationSession,
    SessionParticipant,
    ElicitationStep,
    BusinessValidation,
    InferredContext,
    AnalyticalOpportunities,
    FourDimensionalContext,
    InferenceMetadata
)
from .inference_engine import SemanticInferenceEngine
from .graph_discovery import GraphDiscoveryEngine


class SOWElicitationWizard:
    """
    Business-friendly elicitation wizard that creates a magical experience.
    
    Hides technical complexity while capturing complete semantic richness
    for 4D analytics capabilities.
    """

    def __init__(self):
        """Initialize the elicitation wizard."""
        self.inference_engine = SemanticInferenceEngine()
        self.graph_discovery = GraphDiscoveryEngine()
        self.current_session: Optional[ElicitationSession] = None
        self.current_requirements: Optional[ExplicitRequirements] = None
        
    async def start_session(self, participants: List[SessionParticipant]) -> str:
        """Start a new elicitation session."""
        session_id = str(uuid4())
        self.current_session = ElicitationSession(
            session_id=session_id,
            timestamp=datetime.utcnow(),
            participants=participants,
            elicitation_flow=[],
            business_validation=None
        )
        return session_id

    async def conduct_elicitation(self) -> SemanticStatementOfWork:
        """
        Conduct the complete elicitation process.
        
        Returns a complete Semantic SOW with inferred opportunities.
        """
        if not self.current_session:
            raise ValueError("No active session. Call start_session() first.")

        # Phase 1: Natural Business Discovery
        print("\n🎯 Welcome to the Agentic Data Scraper Requirements Discovery!")
        print("Let's understand your business challenge in natural terms...")
        
        business_challenge = await self._elicit_business_challenge()
        desired_outcomes = await self._elicit_desired_outcomes()
        constraints = await self._elicit_constraints()
        
        # Build explicit requirements
        self.current_requirements = ExplicitRequirements(
            business_challenge=business_challenge,
            desired_outcomes=desired_outcomes,
            constraints_and_limitations=constraints
        )

        # Phase 2: Semantic Inference (Hidden from User)
        print("\n🧠 Analyzing your requirements and discovering opportunities...")
        inferred_context = await self.inference_engine.infer_context(self.current_requirements)
        analytical_opportunities = await self.graph_discovery.discover_opportunities(
            self.current_requirements, inferred_context
        )
        four_d_context = await self.inference_engine.expand_4d_context(
            self.current_requirements, inferred_context, analytical_opportunities
        )

        # Phase 3: Business Validation & Surprise Discovery
        validated_opportunities = await self._present_and_validate_opportunities(
            analytical_opportunities
        )

        # Phase 4: Generate Complete SOW
        return await self._generate_semantic_sow(
            inferred_context, validated_opportunities, four_d_context
        )

    async def _elicit_business_challenge(self) -> BusinessChallenge:
        """Elicit business challenge in natural, conversational way."""
        
        # Main challenge description
        description = await self._ask_question(
            "what_challenge",
            "Tell us about your business challenge",
            "What business problem are you trying to solve? Describe it in your own words."
        )

        # Entities to track (what do you want to track?)
        entities = await self._elicit_entities_to_track()
        
        # Spatial context (where does this happen?)
        spatial_context = await self._elicit_spatial_context(description)
        
        # Temporal context (when is this important?)
        temporal_context = await self._elicit_temporal_context(description)
        
        # Stakeholders (who is involved?)
        stakeholders = await self._elicit_stakeholders()

        return BusinessChallenge(
            description=description,
            entities_to_track=entities,
            spatial_context=spatial_context,
            temporal_context=temporal_context,
            stakeholders_involved=stakeholders
        )

    async def _elicit_entities_to_track(self) -> List[EntityToTrack]:
        """Elicit entities in business-friendly terms."""
        
        entities_response = await self._ask_question(
            "entities_to_track",
            "What do you want to track?",
            "What are the key things (entities) you need to monitor? Examples: customers, products, suppliers, orders, inventory, etc."
        )

        # Parse entities from natural language response
        entities = []
        entity_keywords = self._extract_entity_keywords(entities_response)
        
        for keyword in entity_keywords:
            importance = await self._ask_question(
                f"importance_{keyword}",
                f"How important is tracking {keyword}?",
                f"On a scale of critical, high, medium, low - how important is tracking {keyword}?",
                options=["critical", "high", "medium", "low"]
            )
            
            # Infer semantic type (hidden from business user)
            semantic_type = self._infer_semantic_type(keyword)
            
            entities.append(EntityToTrack(
                entity=keyword,
                importance=importance,
                semantic_type=semantic_type,
                business_context=f"Mentioned in context: {entities_response[:100]}..."
            ))

        return entities

    async def _elicit_spatial_context(self, description: str) -> Optional[SpatialContext]:
        """Elicit spatial context through smart questioning."""
        
        # Check if geographic context is implied
        has_geographic_context = any(keyword in description.lower() for keyword in 
            ["global", "international", "country", "region", "location", "supplier", "customer", "market"])
        
        if not has_geographic_context:
            geographic_relevance = await self._ask_question(
                "geographic_relevance",
                "Does location matter for your challenge?",
                "Does geography or location play a role in this business challenge?",
                options=["Yes", "No"]
            )
            if geographic_relevance.lower() == "no":
                return None

        # Elicit geographic scope
        geographic_scope = await self._ask_question(
            "geographic_scope",
            "What's your geographic scope?",
            "Is this challenge local, regional, national, international, or global?",
            options=["local", "regional", "national", "international", "global"]
        )

        # Elicit specific locations if mentioned
        locations_mentioned = []
        if any(keyword in description.lower() for keyword in ["country", "city", "region", "location"]):
            locations_response = await self._ask_question(
                "specific_locations",
                "Which specific locations are important?",
                "Can you name specific countries, regions, or cities that are particularly important?"
            )
            locations_mentioned = self._parse_locations(locations_response)

        return SpatialContext(
            locations_mentioned=locations_mentioned,
            geographic_scope=geographic_scope
        )

    async def _elicit_temporal_context(self, description: str) -> Optional[TemporalContext]:
        """Elicit temporal context through intelligent questioning."""
        
        # Detect time-related keywords
        time_keywords = ["daily", "weekly", "monthly", "quarterly", "yearly", "seasonal", "real-time", "historic"]
        mentioned_horizons = [kw for kw in time_keywords if kw in description.lower()]
        
        # Ask about time horizons
        time_horizons_response = await self._ask_question(
            "time_horizons",
            "What time periods matter most?",
            "Are you interested in real-time data, daily, weekly, monthly, quarterly, yearly trends, or historical analysis?"
        )
        
        time_horizons = self._parse_time_horizons(time_horizons_response, mentioned_horizons)
        
        # Check for critical periods
        critical_periods = []
        has_critical_periods = await self._ask_question(
            "has_critical_periods",
            "Are there specific time periods that are especially critical?",
            "Are there particular times of year, month, or day when this challenge is most important?",
            options=["Yes", "No"]
        )
        
        if has_critical_periods.lower() == "yes":
            periods_response = await self._ask_question(
                "critical_periods",
                "Tell us about these critical periods",
                "Describe the critical time periods and why they're important."
            )
            critical_periods = self._parse_critical_periods(periods_response)
        
        # Detect seasonality
        seasonality_mentioned = any(keyword in description.lower() for keyword in 
            ["seasonal", "season", "quarterly", "holiday", "peak", "cycle"])

        return TemporalContext(
            time_horizons=time_horizons,
            critical_periods=critical_periods,
            seasonality_mentioned=seasonality_mentioned
        )

    async def _elicit_stakeholders(self) -> List[StakeholderInvolved]:
        """Elicit stakeholders in conversational manner."""
        
        stakeholders_response = await self._ask_question(
            "stakeholders",
            "Who are the key people involved?",
            "Which departments, roles, or individuals are involved in this challenge? Who makes the key decisions?"
        )

        return self._parse_stakeholders(stakeholders_response)

    async def _elicit_desired_outcomes(self) -> List[DesiredOutcome]:
        """Elicit desired outcomes conversationally."""
        
        outcomes_response = await self._ask_question(
            "desired_outcomes",
            "What do you want to achieve?",
            "What are your goals? What does success look like? What specific outcomes do you want?"
        )

        outcomes = self._parse_desired_outcomes(outcomes_response)
        
        # Ask about priorities for each outcome
        for outcome in outcomes:
            outcome.priority = await self._ask_question(
                f"priority_{hash(outcome.outcome)}",
                f"How important is: {outcome.outcome[:50]}...?",
                f"Is this a must-have, should-have, or nice-to-have outcome?",
                options=["must-have", "should-have", "nice-to-have"]
            )

        return outcomes

    async def _elicit_constraints(self) -> Optional[ConstraintsAndLimitations]:
        """Elicit constraints conversationally."""
        
        has_constraints = await self._ask_question(
            "has_constraints",
            "Are there any constraints we should know about?",
            "Do you have budget, timeline, technical, regulatory, or organizational constraints?",
            options=["Yes", "No"]
        )
        
        if has_constraints.lower() == "no":
            return None

        constraints_response = await self._ask_question(
            "constraints",
            "Tell us about your constraints",
            "Describe any limitations, restrictions, or constraints that might affect this project."
        )

        return self._parse_constraints(constraints_response)

    async def _present_and_validate_opportunities(
        self, 
        opportunities: AnalyticalOpportunities
    ) -> AnalyticalOpportunities:
        """Present discovered opportunities to business for validation."""
        
        print("\n✨ Based on your requirements, we've discovered some exciting analytical opportunities!")
        print("These go beyond what you explicitly asked for but could provide significant additional value:\n")

        presented_count = 0
        accepted_count = 0
        modified_count = 0
        rejected_count = 0
        feedback = []

        # Present cross-domain opportunities
        validated_cross_domain = []
        for i, opp in enumerate(opportunities.cross_domain_opportunities, 1):
            print(f"💡 Opportunity {i}: {opp.title}")
            print(f"   Description: {opp.description}")
            print(f"   Value Proposition: {opp.business_value_proposition}")
            print(f"   Surprise Factor: {opp.surprise_factor}")
            print(f"   Complexity: {opp.implementation_complexity}")
            print(f"   Confidence: {opp.confidence_level:.0%}\n")
            
            presented_count += 1
            
            decision = await self._ask_question(
                f"opportunity_decision_{opp.opportunity_id}",
                f"What do you think about this opportunity?",
                "Would you like to include this in your analytics platform?",
                options=["Accept", "Modify", "Reject", "Learn More"]
            )
            
            if decision == "Accept":
                validated_cross_domain.append(opp)
                accepted_count += 1
            elif decision == "Modify":
                modified_opp = await self._modify_opportunity(opp)
                validated_cross_domain.append(modified_opp)
                modified_count += 1
            elif decision == "Reject":
                reject_reason = await self._ask_question(
                    f"reject_reason_{opp.opportunity_id}",
                    "Why are you not interested?",
                    "Could you tell us why this opportunity doesn't fit your needs?"
                )
                feedback.append(f"Rejected {opp.title}: {reject_reason}")
                rejected_count += 1
            else:  # Learn More
                await self._explain_opportunity_details(opp)
                # Ask again after explanation
                decision = await self._ask_question(
                    f"opportunity_decision_2_{opp.opportunity_id}",
                    f"Now what do you think?",
                    "After learning more, would you like to include this opportunity?",
                    options=["Accept", "Modify", "Reject"]
                )
                
                if decision == "Accept":
                    validated_cross_domain.append(opp)
                    accepted_count += 1
                elif decision == "Modify":
                    modified_opp = await self._modify_opportunity(opp)
                    validated_cross_domain.append(modified_opp)
                    modified_count += 1
                else:
                    rejected_count += 1

        # Update business validation in session
        if self.current_session:
            self.current_session.business_validation = BusinessValidation(
                opportunities_presented=presented_count,
                opportunities_accepted=accepted_count,
                opportunities_modified=modified_count,
                opportunities_rejected=rejected_count,
                business_feedback=feedback
            )

        # Return validated opportunities
        return AnalyticalOpportunities(
            cross_domain_opportunities=validated_cross_domain,
            predictive_opportunities=opportunities.predictive_opportunities,
            optimization_opportunities=opportunities.optimization_opportunities
        )

    async def _generate_semantic_sow(
        self,
        inferred_context: InferredContext,
        analytical_opportunities: AnalyticalOpportunities,
        four_d_context: FourDimensionalContext
    ) -> SemanticStatementOfWork:
        """Generate the complete Semantic SOW."""
        
        # Generate inference metadata
        inference_metadata = InferenceMetadata(
            reasoning_engine_version="1.0.0",
            ontologies_used=[],
            inference_confidence=None,
            reasoning_trace=[]
        )

        return SemanticStatementOfWork(
            explicit_requirements=self.current_requirements,
            inferred_context=inferred_context,
            analytical_opportunities=analytical_opportunities,
            four_dimensional_context=four_d_context,
            inference_metadata=inference_metadata,
            elicitation_session=self.current_session
        )

    # Helper methods for parsing and interaction

    async def _ask_question(
        self, 
        question_id: str, 
        short_prompt: str, 
        full_question: str,
        options: Optional[List[str]] = None
    ) -> str:
        """Ask a question and record the interaction."""
        
        print(f"\n❓ {short_prompt}")
        if options:
            print(f"   Options: {', '.join(options)}")
        print(f"   {full_question}")
        
        # In a real implementation, this would use a proper UI
        # For now, simulate with input
        response = input("   Your answer: ").strip()
        
        # Record in elicitation flow
        if self.current_session:
            step = ElicitationStep(
                step=len(self.current_session.elicitation_flow) + 1,
                question_type=question_id.split('_')[0],
                question=full_question,
                response=response,
                inferences_triggered=[]
            )
            self.current_session.elicitation_flow.append(step)
        
        return response

    def _extract_entity_keywords(self, response: str) -> List[str]:
        """Extract entity keywords from natural language response."""
        # Simple keyword extraction - in reality would use NLP
        common_entities = [
            "customers", "suppliers", "products", "inventory", "orders", 
            "shipments", "employees", "sales", "costs", "revenue", "profits",
            "compliance", "quality", "performance", "risks", "opportunities"
        ]
        
        found_entities = []
        response_lower = response.lower()
        for entity in common_entities:
            if entity in response_lower or entity[:-1] in response_lower:
                found_entities.append(entity)
        
        return found_entities[:5]  # Limit to top 5

    def _infer_semantic_type(self, entity: str) -> Optional[str]:
        """Infer semantic type from entity name."""
        type_mapping = {
            "suppliers": "supply:Supplier",
            "customers": "business:Customer", 
            "products": "business:Product",
            "inventory": "supply:Inventory",
            "orders": "business:Order",
            "costs": "finance:Cost",
            "revenue": "finance:Revenue",
            "compliance": "finance:Compliance"
        }
        return type_mapping.get(entity.lower())

    def _parse_locations(self, response: str) -> List[LocationMention]:
        """Parse location mentions from response."""
        # Simple parsing - in reality would use NER
        locations = []
        location_keywords = ["usa", "europe", "asia", "china", "india", "germany", "uk"]
        
        for location in location_keywords:
            if location in response.lower():
                locations.append(LocationMention(
                    location=location.title(),
                    type="country" if len(location) <= 3 else "region",
                    relevance=f"Mentioned in context: {response[:50]}..."
                ))
        
        return locations

    def _parse_time_horizons(self, response: str, mentioned: List[str]) -> List[str]:
        """Parse time horizons from response."""
        horizons = set(mentioned)
        response_lower = response.lower()
        
        horizon_mapping = {
            "real-time": ["real-time", "live", "immediate", "instant"],
            "daily": ["daily", "day", "every day"],
            "weekly": ["weekly", "week", "every week"],
            "monthly": ["monthly", "month", "every month"],
            "quarterly": ["quarterly", "quarter", "q1", "q2", "q3", "q4"],
            "yearly": ["yearly", "annual", "year", "every year"],
            "historical": ["historical", "historic", "past", "trend"]
        }
        
        for horizon, keywords in horizon_mapping.items():
            if any(kw in response_lower for kw in keywords):
                horizons.add(horizon)
        
        return list(horizons)

    def _parse_critical_periods(self, response: str) -> List[CriticalPeriod]:
        """Parse critical periods from response."""
        # Simple parsing - in reality would be more sophisticated
        periods = []
        if "holiday" in response.lower() or "christmas" in response.lower():
            periods.append(CriticalPeriod(
                period="Holiday Season",
                description="Year-end holiday shopping period",
                business_impact="Peak demand and revenue"
            ))
        if "quarter" in response.lower() or "q4" in response.lower():
            periods.append(CriticalPeriod(
                period="Quarter End",
                description="Financial reporting period",
                business_impact="Compliance and reporting requirements"
            ))
        return periods

    def _parse_stakeholders(self, response: str) -> List[StakeholderInvolved]:
        """Parse stakeholders from response."""
        stakeholders = []
        
        # Common role mappings
        role_keywords = {
            "cfo": ("CFO", "finance", "high"),
            "ceo": ("CEO", "executive", "high"),
            "operations": ("Operations Manager", "operations", "medium"),
            "procurement": ("Procurement Manager", "procurement", "medium"),
            "analyst": ("Data Analyst", "analytics", "low"),
            "manager": ("Manager", "management", "medium")
        }
        
        response_lower = response.lower()
        for keyword, (role, dept, authority) in role_keywords.items():
            if keyword in response_lower:
                stakeholders.append(StakeholderInvolved(
                    role=role,
                    department=dept,
                    responsibilities=[f"Mentioned in context: {response[:100]}..."],
                    decision_authority=authority
                ))
        
        return stakeholders

    def _parse_desired_outcomes(self, response: str) -> List[DesiredOutcome]:
        """Parse desired outcomes from response."""
        # Simple parsing - extract sentences as potential outcomes
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        outcomes = []
        
        for sentence in sentences[:3]:  # Limit to 3 outcomes
            if len(sentence) > 10:  # Meaningful outcome
                outcomes.append(DesiredOutcome(
                    outcome=sentence,
                    success_metrics=[],
                    business_value=None,
                    priority="must-have"  # Will be updated later
                ))
        
        return outcomes

    def _parse_constraints(self, response: str) -> ConstraintsAndLimitations:
        """Parse constraints from response."""
        response_lower = response.lower()
        
        budget = None
        if "budget" in response_lower or "$" in response or "cost" in response_lower:
            budget = "Budget constraints mentioned"
        
        timeline = None  
        if "time" in response_lower or "deadline" in response_lower or "month" in response_lower:
            timeline = "Timeline constraints mentioned"
        
        technical = []
        if "technical" in response_lower or "system" in response_lower:
            technical.append("Technical constraints mentioned")
        
        regulatory = []
        if "compliance" in response_lower or "regulation" in response_lower:
            regulatory.append("Regulatory constraints mentioned")
        
        organizational = []
        if "organization" in response_lower or "approval" in response_lower:
            organizational.append("Organizational constraints mentioned")

        return ConstraintsAndLimitations(
            budget_constraints=budget,
            timeline_constraints=timeline,
            technical_constraints=technical,
            regulatory_constraints=regulatory,
            organizational_constraints=organizational
        )

    async def _modify_opportunity(self, opportunity) -> Any:
        """Allow business user to modify an opportunity."""
        print(f"\n🔧 Let's modify: {opportunity.title}")
        
        new_title = await self._ask_question(
            f"modify_title_{opportunity.opportunity_id}",
            "What would you like to call this opportunity?",
            f"Current title: {opportunity.title}\nWhat title would you prefer?"
        )
        
        new_description = await self._ask_question(
            f"modify_description_{opportunity.opportunity_id}",
            "How would you describe this opportunity?",
            f"Current description: {opportunity.description}\nHow would you like to describe it?"
        )
        
        # Create modified opportunity
        opportunity.title = new_title if new_title else opportunity.title
        opportunity.description = new_description if new_description else opportunity.description
        opportunity.confidence_level *= 0.9  # Slightly reduce confidence for modified opportunity
        
        return opportunity

    async def _explain_opportunity_details(self, opportunity) -> None:
        """Provide detailed explanation of an opportunity."""
        print(f"\n📖 Let me explain '{opportunity.title}' in more detail:")
        print(f"   Primary Domain: {opportunity.primary_domain}")
        print(f"   Connected Domains: {', '.join(opportunity.connected_domains)}")
        print(f"   Implementation Complexity: {opportunity.implementation_complexity}")
        print(f"   Why this is valuable: {opportunity.business_value_proposition}")
        print(f"   Why this might surprise you: {opportunity.surprise_factor}")
        
        if opportunity.required_capabilities:
            print(f"   Required Capabilities:")
            for cap in opportunity.required_capabilities:
                print(f"     - {cap.capability}: {cap.justification}")
        
        print(f"\nThis opportunity demonstrates the power of our 4D ET(K)L platform to discover")
        print(f"valuable analytical insights that extend beyond your explicit requirements!")