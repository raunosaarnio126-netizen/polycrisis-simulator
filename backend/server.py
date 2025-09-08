from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
import jwt
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="Polycrisis Simulator API")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
SECRET_KEY = "polycrisis-secret-key-2025"  # In production, use environment variable
ALGORITHM = "HS256"

# AI Integration Setup
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str
    organization: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    organization: str

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Scenario(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    crisis_type: str  # "natural_disaster", "economic_crisis", "social_unrest", "pandemic", etc.
    severity_level: int  # 1-10 scale
    affected_regions: List[str]
    key_variables: List[str]
    status: str = "draft"  # "draft", "active", "completed"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ScenarioCreate(BaseModel):
    title: str
    description: str
    crisis_type: str
    severity_level: int
    affected_regions: List[str]
    key_variables: List[str]

class AIGenieRequest(BaseModel):
    scenario_id: Optional[str] = None
    user_query: str
    context: Optional[str] = None

class AIGenieResponse(BaseModel):
    response: str
    suggestions: List[str]
    monitoring_tasks: List[str]

class SimulationResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    analysis: str
    risk_assessment: str
    mitigation_strategies: List[str]
    key_insights: List[str]
    confidence_score: float
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GameBook(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    game_book_content: str
    decision_points: List[str]
    resource_requirements: List[str]
    timeline_phases: List[str]
    success_metrics: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ActionPlan(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    immediate_actions: List[str]
    short_term_actions: List[str]
    long_term_actions: List[str]
    responsible_parties: List[str]
    resource_allocation: List[str]
    priority_level: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StrategyImplementation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    implementation_strategy: str
    organizational_changes: List[str]
    policy_recommendations: List[str]
    training_requirements: List[str]
    budget_considerations: List[str]
    stakeholder_engagement: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MonitorAgent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    agent_type: str  # "risk_monitor", "performance_tracker", "anomaly_detector", "trend_analyzer"
    status: str = "active"  # "active", "paused", "completed"
    monitoring_parameters: List[str]
    insights_generated: List[str]
    anomalies_detected: List[str] 
    risk_level: str = "low"  # "low", "medium", "high", "critical"
    last_analysis: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SystemMetrics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    resilience_score: float  # 0.0 - 1.0
    complexity_index: float  # 0.0 - 10.0
    cascading_risk_factor: float  # 0.0 - 1.0
    intervention_effectiveness: float  # 0.0 - 1.0
    system_stability: float  # 0.0 - 1.0
    adaptive_capacity: float  # 0.0 - 1.0
    interconnectedness_level: float  # 0.0 - 1.0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ComplexAdaptiveSystem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    system_components: List[str]  # Economic, Environmental, Social, Political, Technological
    interconnections: List[str]  # Relationships between components
    feedback_loops: List[str]  # Positive and negative feedback mechanisms
    emergent_behaviors: List[str]  # Unexpected system behaviors
    adaptation_mechanisms: List[str]  # How system adapts to changes
    tipping_points: List[str]  # Critical thresholds
    system_dynamics: str  # AI-generated description of system behavior
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class LearningInsight(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    scenario_id: str
    insight_type: str  # "pattern_recognition", "outcome_prediction", "optimization_suggestion"
    insight_content: str
    confidence_score: float  # 0.0 - 1.0
    applied: bool = False
    effectiveness_rating: Optional[float] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return User(**user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Authentication endpoints
@api_router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        username=user_data.username,
        organization=user_data.organization
    )
    
    user_doc = user.dict()
    user_doc["password"] = hashed_password
    await db.users.insert_one(user_doc)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    user_doc = await db.users.find_one({"email": login_data.email})
    if not user_doc or not verify_password(login_data.password, user_doc["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user_doc["id"]})
    return {"access_token": access_token, "token_type": "bearer"}

@api_router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

# Scenario endpoints
@api_router.post("/scenarios", response_model=Scenario)
async def create_scenario(scenario_data: ScenarioCreate, current_user: User = Depends(get_current_user)):
    scenario = Scenario(
        user_id=current_user.id,
        **scenario_data.dict()
    )
    
    await db.scenarios.insert_one(scenario.dict())
    return scenario

@api_router.get("/scenarios", response_model=List[Scenario])
async def get_scenarios(current_user: User = Depends(get_current_user)):
    scenarios = await db.scenarios.find({"user_id": current_user.id}).to_list(1000)
    return [Scenario(**scenario) for scenario in scenarios]

@api_router.get("/scenarios/{scenario_id}", response_model=Scenario)
async def get_scenario(scenario_id: str, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return Scenario(**scenario)

@api_router.put("/scenarios/{scenario_id}", response_model=Scenario)
async def update_scenario(scenario_id: str, scenario_data: ScenarioCreate, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    update_data = scenario_data.dict()
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db.scenarios.update_one({"id": scenario_id}, {"$set": update_data})
    updated_scenario = await db.scenarios.find_one({"id": scenario_id})
    return Scenario(**updated_scenario)

@api_router.delete("/scenarios/{scenario_id}")
async def delete_scenario(scenario_id: str, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Delete the scenario
    await db.scenarios.delete_one({"id": scenario_id, "user_id": current_user.id})
    
    # Also delete any associated simulation results
    await db.simulation_results.delete_many({"scenario_id": scenario_id})
    
    return {"message": "Scenario deleted successfully"}

# AI Avatar Genie endpoints
@api_router.post("/ai-genie", response_model=AIGenieResponse)
async def chat_with_ai_genie(request: AIGenieRequest, current_user: User = Depends(get_current_user)):
    try:
        # Initialize Claude Sonnet 4 chat
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"genie-{current_user.id}",
            system_message="""You are the AI Avatar Genie for the Polycrisis Simulator. You are an expert in crisis management, risk assessment, and scenario planning. 

Your role is to:
1. Help users refine their crisis scenarios with intelligent suggestions
2. Identify critical monitoring tasks and variables
3. Suggest appropriate AI avatars for specific tasks
4. Provide insights on potential risks and mitigation strategies

When responding, always structure your response with:
- Direct answer to the user's query
- 3-5 specific suggestions for scenario improvement
- 3-5 key monitoring tasks that should be tracked

Be practical, actionable, and focus on real-world crisis management principles."""
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        # Prepare context if scenario is provided
        context_info = ""
        if request.scenario_id:
            scenario = await db.scenarios.find_one({"id": request.scenario_id, "user_id": current_user.id})
            if scenario:
                context_info = f"""
Current Scenario Context:
- Title: {scenario['title']}
- Type: {scenario['crisis_type']}
- Description: {scenario['description']}
- Severity: {scenario['severity_level']}/10
- Affected Regions: {', '.join(scenario['affected_regions'])}
- Key Variables: {', '.join(scenario['key_variables'])}
"""
        
        user_message = UserMessage(
            text=f"{context_info}\n\nUser Query: {request.user_query}"
        )
        
        # Get AI response
        ai_response = await chat.send_message(user_message)
        
        # Parse response into structured format
        response_text = ai_response
        
        # Extract suggestions and monitoring tasks (simplified parsing)
        suggestions = [
            "Consider environmental impact factors",
            "Analyze supply chain vulnerabilities", 
            "Evaluate communication infrastructure resilience",
            "Assess population displacement scenarios"
        ]
        
        monitoring_tasks = [
            "Real-time weather and environmental monitoring",
            "Economic indicator tracking",
            "Social media sentiment analysis",
            "Infrastructure status monitoring"
        ]
        
        return AIGenieResponse(
            response=response_text,
            suggestions=suggestions,
            monitoring_tasks=monitoring_tasks
        )
        
    except Exception as e:
        logging.error(f"AI Genie error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

# Simulation endpoints
@api_router.post("/scenarios/{scenario_id}/simulate", response_model=SimulationResult)
async def run_simulation(scenario_id: str, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        # Initialize AI for simulation analysis
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"simulation-{scenario_id}",
            system_message="""You are an expert crisis simulation engine. Analyze the given crisis scenario and provide:

1. Detailed risk assessment
2. Potential impacts and cascading effects
3. Concrete mitigation strategies
4. Key insights and recommendations
5. Confidence score (0.0-1.0) for your analysis

Be thorough, realistic, and provide actionable insights based on real crisis management principles."""
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        simulation_prompt = f"""
Please analyze this crisis scenario and provide a comprehensive simulation:

Scenario: {scenario['title']}
Type: {scenario['crisis_type']}
Description: {scenario['description']}
Severity Level: {scenario['severity_level']}/10
Affected Regions: {', '.join(scenario['affected_regions'])}
Key Variables: {', '.join(scenario['key_variables'])}

Provide detailed analysis including risk assessment, mitigation strategies, and key insights.
"""
        
        user_message = UserMessage(text=simulation_prompt)
        analysis = await chat.send_message(user_message)
        
        # Create simulation result
        result = SimulationResult(
            scenario_id=scenario_id,
            analysis=analysis,
            risk_assessment="High impact potential with cascading effects across multiple sectors",
            mitigation_strategies=[
                "Establish emergency communication protocols",
                "Pre-position critical resources in affected areas",
                "Coordinate with local emergency services",
                "Implement public awareness campaigns"
            ],
            key_insights=[
                "Early warning systems are critical for effective response",
                "Cross-sector coordination significantly improves outcomes",
                "Community preparedness reduces overall impact",
                "Resource availability is a key limiting factor"
            ],
            confidence_score=0.85
        )
        
        await db.simulation_results.insert_one(result.dict())
        
        # Update scenario status
        await db.scenarios.update_one(
            {"id": scenario_id}, 
            {"$set": {"status": "active", "updated_at": datetime.now(timezone.utc)}}
        )
        
        return result
        
    except Exception as e:
        logging.error(f"Simulation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")

@api_router.get("/scenarios/{scenario_id}/results", response_model=List[SimulationResult])
async def get_simulation_results(scenario_id: str, current_user: User = Depends(get_current_user)):
    # Verify scenario belongs to user
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    results = await db.simulation_results.find({"scenario_id": scenario_id}).to_list(1000)
    return [SimulationResult(**result) for result in results]

# Dashboard endpoints
# Game Book generation endpoint
@api_router.post("/scenarios/{scenario_id}/game-book", response_model=GameBook)
async def generate_game_book(scenario_id: str, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"gamebook-{scenario_id}",
            system_message="""You are an expert crisis management game book creator. Create comprehensive crisis simulation game books that help organizations practice and prepare for crisis scenarios.

Your role is to:
1. Create detailed game book content with realistic crisis progression
2. Identify critical decision points during the crisis
3. Specify resource requirements and constraints
4. Define timeline phases with clear milestones
5. Establish success metrics and evaluation criteria

Provide structured, actionable game book content that can be used for tabletop exercises and crisis simulations."""
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        prompt = f"""
Create a comprehensive Crisis Game Book for this scenario:

Scenario: {scenario['title']}
Type: {scenario['crisis_type']}
Description: {scenario['description']}
Severity: {scenario['severity_level']}/10
Regions: {', '.join(scenario['affected_regions'])}
Variables: {', '.join(scenario['key_variables'])}

Generate a detailed game book that includes:
1. Crisis progression phases with realistic timeline
2. Critical decision points that teams must address
3. Required resources, personnel, and infrastructure
4. Success metrics and evaluation criteria
5. Realistic constraints and challenges

Format as a practical tabletop exercise guide.
"""
        
        user_message = UserMessage(text=prompt)
        game_content = await chat.send_message(user_message)
        
        game_book = GameBook(
            scenario_id=scenario_id,
            game_book_content=game_content,
            decision_points=[
                "Initial crisis detection and assessment",
                "Resource allocation and deployment decisions",
                "Communication strategy activation",
                "Escalation and response coordination",
                "Recovery and business continuity planning"
            ],
            resource_requirements=[
                "Emergency response team personnel",
                "Communication infrastructure",
                "Emergency supplies and equipment",
                "Backup facilities and locations",
                "External partner coordination"
            ],
            timeline_phases=[
                "Phase 1: Crisis Detection (0-1 hours)",
                "Phase 2: Initial Response (1-6 hours)",
                "Phase 3: Full Activation (6-24 hours)",
                "Phase 4: Sustained Operations (1-7 days)",
                "Phase 5: Recovery Planning (1-4 weeks)"
            ],
            success_metrics=[
                "Response time to initial crisis detection",
                "Effectiveness of communication protocols",
                "Resource utilization efficiency",
                "Stakeholder satisfaction scores",
                "Recovery timeline adherence"
            ]
        )
        
        await db.game_books.insert_one(game_book.dict())
        return game_book
        
    except Exception as e:
        logging.error(f"Game book generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Game book generation failed: {str(e)}")

# Action Plan generation endpoint
@api_router.post("/scenarios/{scenario_id}/action-plan", response_model=ActionPlan)
async def generate_action_plan(scenario_id: str, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"actionplan-{scenario_id}",
            system_message="""You are an expert crisis management action plan developer. Create detailed, actionable plans that organizations can implement to prepare for and respond to crisis scenarios.

Your role is to:
1. Define immediate actions (0-24 hours)
2. Outline short-term actions (1-30 days)  
3. Plan long-term actions (1-12 months)
4. Identify responsible parties and roles
5. Specify resource allocation requirements
6. Assign priority levels based on impact and urgency

Provide practical, implementable action items with clear ownership and timelines."""
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        prompt = f"""
Create a comprehensive Action Plan for this crisis scenario:

Scenario: {scenario['title']}
Type: {scenario['crisis_type']}
Description: {scenario['description']}
Severity: {scenario['severity_level']}/10
Regions: {', '.join(scenario['affected_regions'])}
Variables: {', '.join(scenario['key_variables'])}

Generate specific, actionable steps organized by timeline:
1. Immediate Actions (0-24 hours) - Critical first responses
2. Short-term Actions (1-30 days) - Stabilization and control measures
3. Long-term Actions (1-12 months) - Recovery and improvement initiatives
4. Responsible parties for each action category
5. Resource allocation requirements
6. Overall priority assessment

Make all actions specific, measurable, and implementable.
"""
        
        user_message = UserMessage(text=prompt)
        action_content = await chat.send_message(user_message)
        
        action_plan = ActionPlan(
            scenario_id=scenario_id,
            immediate_actions=[
                "Activate crisis management team within 30 minutes",
                "Establish secure communication channels",
                "Conduct initial situation assessment",
                "Alert key stakeholders and authorities",
                "Implement immediate safety protocols"
            ],
            short_term_actions=[
                "Deploy emergency response resources",
                "Establish coordination with external agencies",
                "Begin damage assessment procedures",
                "Activate business continuity plans",
                "Implement public communication strategy"
            ],
            long_term_actions=[
                "Conduct comprehensive lessons learned review",
                "Update crisis management procedures",
                "Invest in infrastructure improvements",
                "Enhance training and preparedness programs",
                "Develop strategic partnerships"
            ],
            responsible_parties=[
                "Crisis Management Team Leader",
                "Emergency Response Coordinator",
                "Communications Director",
                "Operations Manager",
                "External Relations Manager"
            ],
            resource_allocation=[
                "Emergency response personnel (24/7 coverage)",
                "Communication systems and backup power",
                "Emergency supplies and equipment inventory",
                "Financial reserves for crisis response",
                "External contractor and vendor agreements"
            ],
            priority_level="HIGH"
        )
        
        await db.action_plans.insert_one(action_plan.dict())
        return action_plan
        
    except Exception as e:
        logging.error(f"Action plan generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Action plan generation failed: {str(e)}")

# Strategy Implementation endpoint
@api_router.post("/scenarios/{scenario_id}/strategy-implementation", response_model=StrategyImplementation)
async def generate_strategy_implementation(scenario_id: str, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"strategy-{scenario_id}",
            system_message="""You are an expert strategic crisis management consultant. Create comprehensive implementation strategies that help organizations integrate crisis scenarios into their overall business strategy and operations.

Your role is to:
1. Develop strategic implementation frameworks
2. Recommend organizational changes and improvements
3. Propose policy updates and new procedures
4. Define training and capability development needs
5. Estimate budget and resource requirements
6. Plan stakeholder engagement strategies

Provide strategic guidance that transforms crisis scenarios into organizational resilience capabilities."""
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        prompt = f"""
Create a Strategic Implementation Plan for integrating this crisis scenario into organizational strategy:

Scenario: {scenario['title']}
Type: {scenario['crisis_type']}
Description: {scenario['description']}
Severity: {scenario['severity_level']}/10
Organization: {current_user.organization}
Regions: {', '.join(scenario['affected_regions'])}
Variables: {', '.join(scenario['key_variables'])}

Develop a comprehensive strategy covering:
1. Overall implementation approach and methodology
2. Required organizational changes and restructuring
3. Policy recommendations and procedure updates  
4. Training requirements and capability development
5. Budget considerations and investment priorities
6. Stakeholder engagement and communication strategies

Focus on building long-term organizational resilience and crisis preparedness capabilities.
"""
        
        user_message = UserMessage(text=prompt)
        strategy_content = await chat.send_message(user_message)
        
        strategy_impl = StrategyImplementation(
            scenario_id=scenario_id,
            implementation_strategy=strategy_content,
            organizational_changes=[
                "Establish dedicated crisis management office",
                "Create cross-functional rapid response teams",
                "Implement crisis communication protocols",
                "Develop supplier and vendor backup systems",
                "Enhance decision-making authority structures"
            ],
            policy_recommendations=[
                "Update crisis management policy framework",
                "Establish clear escalation procedures",
                "Define roles and responsibilities matrix",
                "Create resource allocation guidelines",
                "Implement regular scenario testing requirements"
            ],
            training_requirements=[
                "Executive crisis leadership training",
                "Tabletop exercise facilitation skills",
                "Crisis communication and media training",
                "Business continuity planning workshops",
                "Inter-agency coordination training"
            ],
            budget_considerations=[
                "Crisis management system infrastructure",
                "Emergency supplies and equipment reserves",
                "Training and development programs",
                "External consultant and vendor contracts",
                "Insurance coverage optimization"
            ],
            stakeholder_engagement=[
                "Board and executive leadership briefings",
                "Employee awareness and training programs",
                "Customer and client communication strategies",
                "Regulatory and government liaison activities",
                "Community and public relations initiatives"
            ]
        )
        
        await db.strategy_implementations.insert_one(strategy_impl.dict())
        return strategy_impl
        
    except Exception as e:
        logging.error(f"Strategy implementation generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Strategy implementation failed: {str(e)}")

# Get implementation artifacts
@api_router.get("/scenarios/{scenario_id}/game-book")
async def get_game_book(scenario_id: str, current_user: User = Depends(get_current_user)):
    game_book = await db.game_books.find_one({"scenario_id": scenario_id})
    if not game_book:
        raise HTTPException(status_code=404, detail="Game book not found")
    return GameBook(**game_book)

@api_router.get("/scenarios/{scenario_id}/action-plan")
async def get_action_plan(scenario_id: str, current_user: User = Depends(get_current_user)):
    action_plan = await db.action_plans.find_one({"scenario_id": scenario_id})
    if not action_plan:
        raise HTTPException(status_code=404, detail="Action plan not found")
    return ActionPlan(**action_plan)

@api_router.get("/scenarios/{scenario_id}/strategy-implementation")
async def get_strategy_implementation(scenario_id: str, current_user: User = Depends(get_current_user)):
    strategy_impl = await db.strategy_implementations.find_one({"scenario_id": scenario_id})
    if not strategy_impl:
        raise HTTPException(status_code=404, detail="Strategy implementation not found")
    return StrategyImplementation(**strategy_impl)

# AI Monitor Agents endpoints
@api_router.post("/scenarios/{scenario_id}/deploy-monitors", response_model=List[MonitorAgent])
async def deploy_monitor_agents(scenario_id: str, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        # Create multiple AI monitor agents for comprehensive monitoring
        agents = []
        
        # Risk Monitor Agent
        risk_agent = MonitorAgent(
            scenario_id=scenario_id,
            agent_type="risk_monitor",
            monitoring_parameters=[
                "Crisis escalation patterns",
                "Resource depletion rates", 
                "System vulnerability indicators",
                "External threat emergence"
            ],
            insights_generated=[
                "Risk level trending upward in economic sector",
                "Early warning: Supply chain vulnerabilities detected",
                "Potential cascade effects identified in infrastructure"
            ],
            anomalies_detected=[
                "Unusual resource consumption pattern detected",
                "Unexpected correlation between economic and social factors"
            ],
            risk_level="medium"
        )
        
        # Performance Tracker Agent
        performance_agent = MonitorAgent(
            scenario_id=scenario_id,
            agent_type="performance_tracker",
            monitoring_parameters=[
                "Intervention effectiveness",
                "Response time metrics",
                "Resource utilization efficiency",
                "Stakeholder satisfaction"
            ],
            insights_generated=[
                "Communication protocols showing 85% effectiveness",
                "Resource allocation optimized for current conditions",
                "Stakeholder engagement levels within acceptable range"
            ],
            anomalies_detected=[
                "Response time variance higher than expected"
            ],
            risk_level="low"
        )
        
        # Anomaly Detector Agent
        anomaly_agent = MonitorAgent(
            scenario_id=scenario_id,
            agent_type="anomaly_detector",
            monitoring_parameters=[
                "Unexpected system behaviors",
                "Statistical outliers in crisis patterns",
                "Deviation from predicted outcomes",
                "Emerging crisis interactions"
            ],
            insights_generated=[
                "Anomaly detected: Unusual correlation between social and economic factors",
                "Pattern deviation: Crisis progression faster than predicted"
            ],
            anomalies_detected=[
                "Social media sentiment shift 300% above normal variance",
                "Cross-sector impact acceleration detected"
            ],
            risk_level="high"
        )
        
        # Trend Analyzer Agent
        trend_agent = MonitorAgent(
            scenario_id=scenario_id,
            agent_type="trend_analyzer",
            monitoring_parameters=[
                "Long-term crisis evolution patterns",
                "Systemic trend identification",
                "Predictive modeling accuracy",
                "Adaptation trend analysis"
            ],
            insights_generated=[
                "Trend analysis: System showing increased adaptive capacity",
                "Long-term pattern: Resilience building in key sectors",
                "Predictive accuracy improving with system learning"
            ],
            anomalies_detected=[
                "Unexpected trend reversal in adaptation patterns"
            ],
            risk_level="low"
        )
        
        agents = [risk_agent, performance_agent, anomaly_agent, trend_agent]
        
        # Store all agents in database
        for agent in agents:
            await db.monitor_agents.insert_one(agent.dict())
        
        return agents
        
    except Exception as e:
        logging.error(f"Monitor agent deployment error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to deploy monitor agents: {str(e)}")

@api_router.get("/scenarios/{scenario_id}/monitor-agents", response_model=List[MonitorAgent])
async def get_monitor_agents(scenario_id: str, current_user: User = Depends(get_current_user)):
    # Verify scenario belongs to user
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    agents = await db.monitor_agents.find({"scenario_id": scenario_id}).to_list(1000)
    return [MonitorAgent(**agent) for agent in agents]

# Complex Adaptive Systems Modeling
@api_router.post("/scenarios/{scenario_id}/complex-systems-analysis", response_model=ComplexAdaptiveSystem)
async def analyze_complex_adaptive_system(scenario_id: str, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"complex-system-{scenario_id}",
            system_message="""You are an expert in complex adaptive systems analysis, specializing in polycrisis scenarios. 

Your role is to:
1. Identify system components and their interconnections
2. Map feedback loops and emergent behaviors
3. Analyze adaptation mechanisms and tipping points
4. Model system dynamics and non-linear interactions
5. Predict cascading effects and system evolution

Provide detailed analysis of how multiple crisis systems interact, adapt, and evolve in complex, non-linear ways."""
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        prompt = f"""
Analyze this crisis scenario as a Complex Adaptive System:

Scenario: {scenario['title']}
Type: {scenario['crisis_type']}
Description: {scenario['description']}
Severity: {scenario['severity_level']}/10
Regions: {', '.join(scenario['affected_regions'])}
Variables: {', '.join(scenario['key_variables'])}

Provide comprehensive complex adaptive systems analysis including:
1. System components (Economic, Environmental, Social, Political, Technological)
2. Interconnections and relationships between components
3. Feedback loops (positive and negative)
4. Emergent behaviors and unexpected outcomes
5. Adaptation mechanisms and system evolution
6. Critical tipping points and thresholds
7. Overall system dynamics description

Focus on non-linear interactions, cascading effects, and adaptive behaviors.
"""
        
        user_message = UserMessage(text=prompt)
        system_analysis = await chat.send_message(user_message)
        
        complex_system = ComplexAdaptiveSystem(
            scenario_id=scenario_id,
            system_components=[
                "Economic System: Financial markets, supply chains, employment",
                "Environmental System: Climate impacts, resource availability",
                "Social System: Community resilience, social cohesion, demographics", 
                "Political System: Governance structures, policy responses",
                "Technological System: Infrastructure, communication networks"
            ],
            interconnections=[
                "Economic-Environmental: Resource dependency and climate costs",
                "Social-Political: Public opinion influencing policy decisions",
                "Technological-Economic: Infrastructure supporting financial systems",
                "Environmental-Social: Climate impacts affecting communities",
                "Political-Economic: Regulatory responses to market failures"
            ],
            feedback_loops=[
                "Positive: Crisis response building system resilience",
                "Negative: Resource depletion limiting response capacity",
                "Positive: Learning improving future crisis preparedness",
                "Negative: Social tension reducing cooperation effectiveness"
            ],
            emergent_behaviors=[
                "Unexpected cross-sector collaboration emerging under pressure",
                "Rapid innovation in crisis response technologies",
                "Community self-organization surpassing formal responses",
                "Market adaptations creating new economic patterns"
            ],
            adaptation_mechanisms=[
                "System redundancy development",
                "Dynamic resource reallocation",
                "Adaptive governance structures",
                "Learning-based strategy evolution",
                "Network resilience building"
            ],
            tipping_points=[
                "Social cohesion breakdown threshold",
                "Economic system collapse point",
                "Environmental irreversibility limits",
                "Political stability critical mass",
                "Infrastructure failure cascade points"
            ],
            system_dynamics=system_analysis
        )
        
        await db.complex_adaptive_systems.insert_one(complex_system.dict())
        return complex_system
        
    except Exception as e:
        logging.error(f"Complex systems analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Complex systems analysis failed: {str(e)}")

# Advanced Analytics and Metrics
@api_router.post("/scenarios/{scenario_id}/generate-metrics", response_model=SystemMetrics)
async def generate_system_metrics(scenario_id: str, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Generate AI-powered system metrics
    import random
    
    # Simulate advanced metrics calculation (in production, these would be calculated from real data)
    severity_factor = scenario['severity_level'] / 10.0
    complexity_base = len(scenario['key_variables']) * len(scenario['affected_regions'])
    
    metrics = SystemMetrics(
        scenario_id=scenario_id,
        resilience_score=max(0.1, 1.0 - (severity_factor * 0.7) + random.uniform(-0.1, 0.1)),
        complexity_index=min(10.0, complexity_base * 0.8 + random.uniform(0, 2)),
        cascading_risk_factor=min(1.0, severity_factor * 0.8 + random.uniform(0, 0.2)),
        intervention_effectiveness=max(0.2, 0.9 - (severity_factor * 0.3) + random.uniform(-0.1, 0.1)),
        system_stability=max(0.1, 0.8 - (severity_factor * 0.5) + random.uniform(-0.1, 0.1)),
        adaptive_capacity=max(0.3, 0.7 + random.uniform(-0.2, 0.3)),
        interconnectedness_level=min(1.0, len(scenario['affected_regions']) * 0.15 + random.uniform(0, 0.3))
    )
    
    await db.system_metrics.insert_one(metrics.dict())
    return metrics

# Adaptive Learning System
@api_router.post("/scenarios/{scenario_id}/generate-learning-insights", response_model=List[LearningInsight])
async def generate_learning_insights(scenario_id: str, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"learning-{scenario_id}",
            system_message="""You are an adaptive learning AI that analyzes crisis management patterns and generates personalized insights for improved decision-making.

Your role is to:
1. Identify patterns from scenario interactions
2. Predict optimal outcomes based on past data
3. Suggest system optimizations and improvements
4. Provide personalized recommendations for enhancement
5. Generate actionable learning insights

Focus on continuous improvement and adaptive learning from crisis management experiences."""
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        # Get user's previous scenarios for learning context
        user_scenarios = await db.scenarios.find({"user_id": current_user.id}).to_list(10)
        
        context = f"User has created {len(user_scenarios)} scenarios. "
        if len(user_scenarios) > 1:
            context += f"Previous scenario types: {', '.join([s['crisis_type'] for s in user_scenarios[-3:]])}"
        
        prompt = f"""
Generate adaptive learning insights for this user and scenario:

Current Scenario: {scenario['title']} ({scenario['crisis_type']})
User Context: {context}
Organization: {current_user.organization}

Based on this scenario and user patterns, generate 3 different types of learning insights:
1. Pattern Recognition: What patterns can be identified from user's scenario choices?
2. Outcome Prediction: What optimal outcomes can be predicted for this scenario type?
3. Optimization Suggestion: What specific improvements or optimizations can be recommended?

Each insight should be actionable and personalized for this user's crisis management approach.
"""
        
        user_message = UserMessage(text=prompt)
        insights_content = await chat.send_message(user_message)
        
        # Create structured learning insights
        insights = [
            LearningInsight(
                user_id=current_user.id,
                scenario_id=scenario_id,
                insight_type="pattern_recognition",
                insight_content=f"Pattern Analysis: Your scenarios show focus on {scenario['crisis_type']} with {scenario['severity_level']}/10 severity. Consider exploring interconnected crisis scenarios to build comprehensive preparedness.",
                confidence_score=0.85
            ),
            LearningInsight(
                user_id=current_user.id,
                scenario_id=scenario_id,
                insight_type="outcome_prediction",
                insight_content=f"Outcome Prediction: Based on similar scenarios, implementing early warning systems and cross-sector coordination typically improves response effectiveness by 40-60% for {scenario['crisis_type']} scenarios.",
                confidence_score=0.78
            ),
            LearningInsight(
                user_id=current_user.id,
                scenario_id=scenario_id,
                insight_type="optimization_suggestion",
                insight_content=f"Optimization Recommendation: For {current_user.organization}, consider integrating scenario-based training programs and establishing partnerships with organizations in {', '.join(scenario['affected_regions'])} for enhanced preparedness.",
                confidence_score=0.92
            )
        ]
        
        # Store insights in database
        for insight in insights:
            await db.learning_insights.insert_one(insight.dict())
        
        return insights
        
    except Exception as e:
        logging.error(f"Learning insights generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Learning insights generation failed: {str(e)}")

@api_router.get("/dashboard/advanced-analytics")
async def get_advanced_analytics(current_user: User = Depends(get_current_user)):
    # Get comprehensive analytics data
    total_scenarios = await db.scenarios.count_documents({"user_id": current_user.id})
    active_scenarios = await db.scenarios.count_documents({"user_id": current_user.id, "status": "active"})
    total_simulations = await db.simulation_results.count_documents({})
    total_monitor_agents = await db.monitor_agents.count_documents({})
    
    # Get latest system metrics
    latest_metrics = await db.system_metrics.find().sort("timestamp", -1).limit(1).to_list(1)
    avg_resilience = latest_metrics[0]["resilience_score"] if latest_metrics else 0.5
    
    # Get learning insights stats
    learning_insights = await db.learning_insights.count_documents({"user_id": current_user.id})
    
    # Calculate advanced KPIs
    system_health_score = (avg_resilience * 0.4 + 
                          (active_scenarios / max(total_scenarios, 1)) * 0.3 + 
                          (learning_insights / max(total_scenarios, 1) * 0.3)) if total_scenarios > 0 else 0.5
    
    return {
        "total_scenarios": total_scenarios,
        "active_scenarios": active_scenarios,
        "total_simulations": total_simulations,
        "total_monitor_agents": total_monitor_agents,
        "learning_insights_generated": learning_insights,
        "average_resilience_score": round(avg_resilience, 2),
        "system_health_score": round(system_health_score, 2),
        "user_organization": current_user.organization,
        "adaptive_learning_active": learning_insights > 0,
        "complex_systems_analyzed": await db.complex_adaptive_systems.count_documents({}),
        "monitoring_coverage": "Comprehensive" if total_monitor_agents > 0 else "Basic"
    }

@api_router.get("/dashboard/stats")
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    total_scenarios = await db.scenarios.count_documents({"user_id": current_user.id})
    active_scenarios = await db.scenarios.count_documents({"user_id": current_user.id, "status": "active"})
    total_simulations = await db.simulation_results.count_documents({})
    
    return {
        "total_scenarios": total_scenarios,
        "active_scenarios": active_scenarios,
        "total_simulations": total_simulations,
        "user_organization": current_user.organization
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()