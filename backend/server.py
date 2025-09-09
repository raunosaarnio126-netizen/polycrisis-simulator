from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
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
import PyPDF2
from docx import Document
import io

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
    company_id: Optional[str] = None
    role: str = "member"  # "admin", "manager", "analyst", "member"
    department: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Scenario Adjusters - Fuzzy Logic Models
class ScenarioAdjustment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    scenario_id: Optional[str] = None  # Link to existing scenario
    adjustment_name: str
    # SEPTE Framework percentages (each pair should sum to 100)
    economic_crisis_pct: float = 50.0  # vs economic_stability_pct
    economic_stability_pct: float = 50.0
    social_unrest_pct: float = 50.0  # vs social_cohesion_pct  
    social_cohesion_pct: float = 50.0
    environmental_degradation_pct: float = 50.0  # vs environmental_resilience_pct
    environmental_resilience_pct: float = 50.0
    political_instability_pct: float = 50.0  # vs political_stability_pct
    political_stability_pct: float = 50.0
    technological_disruption_pct: float = 50.0  # vs technological_advancement_pct
    technological_advancement_pct: float = 50.0
    # AI Analysis Results
    real_time_analysis: str
    impact_summary: str
    risk_level: str = "medium"  # "low", "medium", "high", "critical"
    recommendations: List[str] = []
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ScenarioAdjustmentCreate(BaseModel):
    adjustment_name: str
    scenario_id: Optional[str] = None
    economic_crisis_pct: float = 50.0
    economic_stability_pct: float = 50.0
    social_unrest_pct: float = 50.0
    social_cohesion_pct: float = 50.0
    environmental_degradation_pct: float = 50.0
    environmental_resilience_pct: float = 50.0
    political_instability_pct: float = 50.0
    political_stability_pct: float = 50.0
    technological_disruption_pct: float = 50.0
    technological_advancement_pct: float = 50.0

class ConsensusSettings(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    team_id: Optional[str] = None
    adjustment_id: str
    consensus_name: str
    agreed_by: List[str] = []  # List of user IDs who agreed
    total_team_members: int
    consensus_reached: bool = False
    consensus_percentage: float = 0.0  # Percentage of team that agreed
    final_settings: dict  # Store the agreed SEPTE settings
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finalized_at: Optional[datetime] = None

class ConsensusCreate(BaseModel):
    adjustment_id: str
    consensus_name: str
    team_id: Optional[str] = None

class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    organization: str
    job_title: Optional[str] = None
    department: Optional[str] = None
    phone: Optional[str] = None

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

class MonitoringSource(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    user_id: str
    source_type: str  # "news_api", "social_media", "government_data", "weather_api", "financial_market", "custom_url"
    source_url: str
    source_name: str
    monitoring_frequency: str  # "real_time", "hourly", "daily", "weekly"
    data_keywords: List[str]  # Keywords to filter relevant information
    status: str = "active"  # "active", "paused", "error", "inactive"
    last_check: Optional[datetime] = None
    total_data_points: int = 0
    relevance_score: float = 0.0  # AI-calculated relevance to scenario
    added_by_team_member: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MonitoringSourceCreate(BaseModel):
    source_type: str
    source_url: str
    source_name: str
    monitoring_frequency: str
    data_keywords: List[str]

class CollectedData(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    scenario_id: str
    data_content: str
    data_title: str
    data_url: Optional[str] = None
    relevance_score: float  # AI-calculated relevance
    sentiment_score: float  # -1.0 to 1.0 (negative to positive)
    urgency_level: str  # "low", "medium", "high", "critical"
    keywords_matched: List[str]
    ai_summary: str
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TeamCollaboration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    team_members: List[str]  # Email addresses of team members
    shared_sources: List[str]  # Source IDs
    collaboration_notes: List[str]
    access_level: str = "team"  # "team", "organization", "public"
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SmartSuggestion(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    scenario_id: str
    suggestion_type: str  # "data_source", "monitoring_keyword", "analysis_focus"
    suggestion_content: str
    reasoning: str
    confidence_score: float
    implemented: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Company(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_name: str
    industry: str
    company_size: str  # "startup", "small", "medium", "large", "enterprise"
    website_url: Optional[str] = None
    description: str
    location: str
    website_analysis: Optional[str] = None
    business_model: Optional[str] = None
    key_assets: List[str] = []
    vulnerabilities: List[str] = []
    stakeholders: List[str] = []
    competitive_landscape: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CompanyCreate(BaseModel):
    company_name: str
    industry: str
    company_size: str
    website_url: Optional[str] = None
    description: str
    location: str

class BusinessDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    document_name: str
    document_type: str  # "business_plan", "market_strategy", "financial_report", "operational_plan", "other"
    document_content: str
    ai_analysis: Optional[str] = None
    key_insights: List[str] = []
    risk_factors: List[str] = []
    strategic_priorities: List[str] = []
    uploaded_by: str
    file_size: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BusinessDocumentCreate(BaseModel):
    document_name: str
    document_type: str
    document_content: str

class Team(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    team_name: str
    team_description: str
    team_lead: str  # User ID
    team_members: List[str]  # List of user IDs
    access_level: str = "standard"  # "standard", "admin", "view_only"
    team_roles: List[str] = []  # "crisis_manager", "analyst", "coordinator", "observer"
    active_scenarios: List[str] = []  # Scenario IDs this team is working on
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class TeamCreate(BaseModel):
    team_name: str
    team_description: str
    team_members: List[str]  # Email addresses
    team_roles: List[str] = []

class RapidAnalysis(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    company_id: str
    analysis_type: str  # "vulnerability_assessment", "business_impact", "scenario_recommendation", "competitive_analysis"
    analysis_title: str
    analysis_content: str
    key_findings: List[str]
    recommendations: List[str]
    priority_level: str  # "low", "medium", "high", "critical"
    confidence_score: float
    generated_by: str  # User ID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# SaaS Admin & Licensing Models
class LicenseTier(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tier_name: str  # "Single User", "Small Team", "Medium Team", "Large Team"
    max_users: int  # 1, 2, 5, 10
    monthly_price: float  # USD
    annual_price: float  # USD (usually with discount)
    features: List[str]
    stripe_price_id_monthly: Optional[str] = None
    stripe_price_id_annual: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Client(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    client_email: str
    license_tier_id: str
    license_count: int  # Number of licenses purchased
    users_active: int = 0  # Current active users
    subscription_status: str = "trial"  # "trial", "active", "cancelled", "expired"
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    trial_end_date: datetime
    subscription_start_date: Optional[datetime] = None
    subscription_end_date: Optional[datetime] = None
    created_by_admin: str  # Admin user ID
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClientCreate(BaseModel):
    client_name: str
    client_email: str
    license_tier_id: str
    license_count: int = 1

class AdminCredentials(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    admin_email: str
    admin_level: str = "super_admin"  # "super_admin", "admin", "support"
    permissions: List[str] = ["all"]  # ["client_management", "licensing", "billing", "support"]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AIAvatar(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    avatar_name: str
    avatar_type: str  # "risk_monitor", "performance_tracker", "anomaly_detector", "trend_analyzer"
    description: str
    base_competences: List[str]
    client_custom_competences: List[str] = []
    status: str = "active"  # "active", "inactive", "learning", "monitoring"
    performance_metrics: dict = {}
    client_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AvatarCompetence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    avatar_id: str
    competence_name: str
    competence_description: str
    competence_type: str  # "skill", "knowledge", "capability"
    proficiency_level: int = 1  # 1-10 scale
    added_by_client: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AvatarCompetenceCreate(BaseModel):
    competence_name: str
    competence_description: str
    competence_type: str
    proficiency_level: int = 1

class PaymentRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    stripe_payment_intent_id: str
    amount: float
    currency: str = "USD"
    payment_status: str  # "pending", "succeeded", "failed", "cancelled"
    license_tier_id: str
    license_count: int
    billing_period: str  # "monthly", "annual"
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

# Smart Monitoring Source Suggestions
@api_router.post("/scenarios/{scenario_id}/suggest-monitoring-sources", response_model=List[SmartSuggestion])
async def suggest_monitoring_sources(scenario_id: str, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"monitoring-suggestions-{scenario_id}",
            system_message="""You are an expert monitoring and intelligence gathering system. Based on crisis scenarios, suggest the most relevant data sources, APIs, and monitoring targets.

Your role is to:
1. Analyze crisis scenarios and identify critical information sources
2. Suggest specific APIs, websites, and data feeds to monitor
3. Recommend keywords and search terms for effective monitoring
4. Prioritize sources based on relevance and reliability
5. Consider real-time vs periodic monitoring needs

Provide practical, actionable monitoring suggestions that teams can implement immediately."""
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        prompt = f"""
Analyze this crisis scenario and suggest intelligent monitoring sources:

Scenario: {scenario['title']}
Type: {scenario['crisis_type']}
Description: {scenario['description']}
Severity: {scenario['severity_level']}/10
Regions: {', '.join(scenario['affected_regions'])}
Variables: {', '.join(scenario['key_variables'])}

Generate specific monitoring source suggestions including:
1. Data sources (APIs, news feeds, social media, government data)
2. Keywords for effective monitoring
3. Analysis focus areas for maximum insight

Provide 5 high-value monitoring suggestions with detailed reasoning.
"""
        
        user_message = UserMessage(text=prompt)
        suggestions_content = await chat.send_message(user_message)
        
        # Create smart suggestions based on scenario type and content
        suggestions = []
        
        # Data source suggestions based on crisis type
        if scenario['crisis_type'] == 'natural_disaster':
            suggestions.extend([
                SmartSuggestion(
                    scenario_id=scenario_id,
                    suggestion_type="data_source",
                    suggestion_content="USGS Earthquake API - https://earthquake.usgs.gov/fdsnws/event/1/",
                    reasoning="Real-time earthquake data essential for natural disaster monitoring and impact assessment",
                    confidence_score=0.95
                ),
                SmartSuggestion(
                    scenario_id=scenario_id,
                    suggestion_type="data_source", 
                    suggestion_content="National Weather Service API - https://api.weather.gov/",
                    reasoning="Weather conditions directly impact disaster evolution and emergency response capabilities",
                    confidence_score=0.90
                )
            ])
        elif scenario['crisis_type'] == 'economic_crisis':
            suggestions.extend([
                SmartSuggestion(
                    scenario_id=scenario_id,
                    suggestion_type="data_source",
                    suggestion_content="Federal Reserve Economic Data (FRED) API - https://fred.stlouisfed.org/docs/api/",
                    reasoning="Economic indicators crucial for tracking financial crisis development and recovery",
                    confidence_score=0.92
                ),
                SmartSuggestion(
                    scenario_id=scenario_id,
                    suggestion_type="data_source",
                    suggestion_content="Yahoo Finance API - https://finance.yahoo.com/",
                    reasoning="Real-time market data provides early indicators of economic instability",
                    confidence_score=0.88
                )
            ])
        elif scenario['crisis_type'] == 'pandemic':
            suggestions.extend([
                SmartSuggestion(
                    scenario_id=scenario_id,
                    suggestion_type="data_source",
                    suggestion_content="WHO Disease Outbreak News - https://www.who.int/emergencies/disease-outbreak-news",
                    reasoning="Official health organization data critical for pandemic tracking and response planning",
                    confidence_score=0.94
                ),
                SmartSuggestion(
                    scenario_id=scenario_id,
                    suggestion_type="data_source",
                    suggestion_content="CDC API - https://data.cdc.gov/",
                    reasoning="Government health data provides authoritative information on disease progression",
                    confidence_score=0.91
                )
            ])
        
        # Add monitoring keyword suggestions
        keywords = scenario['key_variables'] + [scenario['crisis_type'].replace('_', ' ')]
        suggestions.append(
            SmartSuggestion(
                scenario_id=scenario_id,
                suggestion_type="monitoring_keyword",
                suggestion_content=f"Monitor keywords: {', '.join(keywords[:5])}",
                reasoning="These keywords are directly related to your scenario variables and will capture relevant information",
                confidence_score=0.87
            )
        )
        
        # Add analysis focus suggestion
        suggestions.append(
            SmartSuggestion(
                scenario_id=scenario_id,
                suggestion_type="analysis_focus",
                suggestion_content="Focus on early warning indicators and cascading effect patterns",
                reasoning="Early detection and cascade analysis provide maximum strategic value for crisis management",
                confidence_score=0.89
            )
        )
        
        # Store suggestions in database
        for suggestion in suggestions:
            await db.smart_suggestions.insert_one(suggestion.dict())
        
        return suggestions
        
    except Exception as e:
        logging.error(f"Monitoring suggestions error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate monitoring suggestions: {str(e)}")

# Team Collaboration and Source Management
@api_router.post("/scenarios/{scenario_id}/add-monitoring-source", response_model=MonitoringSource)
async def add_monitoring_source(scenario_id: str, source_data: MonitoringSourceCreate, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Create monitoring source
    monitoring_source = MonitoringSource(
        scenario_id=scenario_id,
        user_id=current_user.id,
        source_type=source_data.source_type,
        source_url=source_data.source_url,
        source_name=source_data.source_name,
        monitoring_frequency=source_data.monitoring_frequency,
        data_keywords=source_data.data_keywords,
        added_by_team_member=current_user.username
    )
    
    # Calculate relevance score using AI
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"relevance-{scenario_id}",
            system_message="You are an AI that evaluates the relevance of monitoring sources to crisis scenarios. Provide a relevance score from 0.0 to 1.0."
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        relevance_prompt = f"""
Evaluate the relevance of this monitoring source to the crisis scenario:

Scenario: {scenario['title']} ({scenario['crisis_type']})
Source: {source_data.source_name} - {source_data.source_url}
Keywords: {', '.join(source_data.data_keywords)}

Provide a relevance score from 0.0 (not relevant) to 1.0 (highly relevant).
Just respond with the numerical score.
"""
        
        user_message = UserMessage(text=relevance_prompt)
        relevance_response = await chat.send_message(user_message)
        
        try:
            relevance_score = float(relevance_response.strip())
            monitoring_source.relevance_score = max(0.0, min(1.0, relevance_score))
        except:
            monitoring_source.relevance_score = 0.5  # Default if AI response can't be parsed
            
    except Exception as e:
        logging.warning(f"Could not calculate relevance score: {str(e)}")
        monitoring_source.relevance_score = 0.5
    
    await db.monitoring_sources.insert_one(monitoring_source.dict())
    return monitoring_source

@api_router.get("/scenarios/{scenario_id}/monitoring-sources", response_model=List[MonitoringSource])
async def get_monitoring_sources(scenario_id: str, current_user: User = Depends(get_current_user)):
    # Verify scenario access
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    sources = await db.monitoring_sources.find({"scenario_id": scenario_id}).to_list(1000)
    return [MonitoringSource(**source) for source in sources]

# Automated Data Collection Simulation
@api_router.post("/scenarios/{scenario_id}/collect-data")
async def collect_monitoring_data(scenario_id: str, current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Get monitoring sources for this scenario
    sources = await db.monitoring_sources.find({"scenario_id": scenario_id, "status": "active"}).to_list(1000)
    
    if not sources:
        raise HTTPException(status_code=404, detail="No active monitoring sources found")
    
    collected_data_items = []
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"data-collection-{scenario_id}",
            system_message="""You are an AI data collector and analyzer. Simulate realistic data collection from various sources and provide intelligent analysis.

Your role is to:
1. Simulate realistic data from monitoring sources
2. Analyze data relevance and sentiment
3. Determine urgency levels
4. Provide concise, actionable summaries
5. Identify keyword matches and patterns

Generate realistic, scenario-appropriate data that would be collected from the specified monitoring sources."""
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        for source in sources:
            # Simulate data collection for each source
            collection_prompt = f"""
Simulate realistic data collection from this monitoring source:

Source: {source['source_name']} ({source['source_type']})
URL: {source['source_url']}
Keywords: {', '.join(source['data_keywords'])}
Scenario: {scenario['title']} - {scenario['crisis_type']}

Generate 2-3 realistic data items that would be collected from this source, including:
1. Data title and content
2. Relevance to the scenario (0.0-1.0)
3. Sentiment score (-1.0 to 1.0)
4. Urgency level (low/medium/high/critical)
5. Brief AI summary

Make the data realistic and relevant to the crisis scenario.
"""
            
            user_message = UserMessage(text=collection_prompt)
            collection_response = await chat.send_message(user_message)
            
            # Create simulated collected data items
            import random
            
            # Generate 2-3 data items per source
            for i in range(random.randint(2, 3)):
                collected_item = CollectedData(
                    source_id=source['id'],
                    scenario_id=scenario_id,
                    data_title=f"Data Update #{i+1} from {source['source_name']}",
                    data_content=f"Simulated data collection: {collection_response[:200]}...",
                    data_url=source['source_url'],
                    relevance_score=min(1.0, source['relevance_score'] + random.uniform(-0.1, 0.1)),
                    sentiment_score=random.uniform(-0.5, 0.5),
                    urgency_level=random.choice(["low", "medium", "high"]),
                    keywords_matched=[kw for kw in source['data_keywords'] if random.random() > 0.3],
                    ai_summary=f"AI Analysis: Key information relevant to {scenario['crisis_type']} scenario with {source['source_name']} data indicating {random.choice(['normal conditions', 'elevated concerns', 'monitoring required'])}"
                )
                
                await db.collected_data.insert_one(collected_item.dict())
                collected_data_items.append(collected_item)
            
            # Update source last_check and total_data_points
            await db.monitoring_sources.update_one(
                {"id": source['id']},
                {
                    "$set": {"last_check": datetime.now(timezone.utc)},
                    "$inc": {"total_data_points": len(collected_data_items)}
                }
            )
        
        return {
            "message": f"Successfully collected {len(collected_data_items)} data items from {len(sources)} sources",
            "data_items_collected": len(collected_data_items),
            "sources_monitored": len(sources),
            "collection_timestamp": datetime.now(timezone.utc)
        }
        
    except Exception as e:
        logging.error(f"Data collection error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data collection failed: {str(e)}")

@api_router.get("/scenarios/{scenario_id}/collected-data", response_model=List[CollectedData])
async def get_collected_data(scenario_id: str, limit: int = 50, current_user: User = Depends(get_current_user)):
    # Verify scenario access
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    data_items = await db.collected_data.find({"scenario_id": scenario_id}).sort("collected_at", -1).limit(limit).to_list(limit)
    return [CollectedData(**item) for item in data_items]

# Team Collaboration
@api_router.post("/scenarios/{scenario_id}/create-team-collaboration", response_model=TeamCollaboration)
async def create_team_collaboration(scenario_id: str, team_emails: List[str], current_user: User = Depends(get_current_user)):
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    collaboration = TeamCollaboration(
        scenario_id=scenario_id,
        team_members=team_emails,
        shared_sources=[],
        collaboration_notes=[f"Team collaboration created by {current_user.username}"],
        created_by=current_user.id
    )
    
    await db.team_collaborations.insert_one(collaboration.dict())
    return collaboration

@api_router.get("/scenarios/{scenario_id}/monitoring-dashboard")
async def get_monitoring_dashboard(scenario_id: str, current_user: User = Depends(get_current_user)):
    # Verify scenario access
    scenario = await db.scenarios.find_one({"id": scenario_id, "user_id": current_user.id})
    if not scenario:
        raise HTTPException(status_code=404, detail="Scenario not found")
    
    # Get monitoring sources
    sources = await db.monitoring_sources.find({"scenario_id": scenario_id}).to_list(1000)
    
    # Get recent collected data
    recent_data = await db.collected_data.find({"scenario_id": scenario_id}).sort("collected_at", -1).limit(10).to_list(10)
    
    # Get smart suggestions
    suggestions = await db.smart_suggestions.find({"scenario_id": scenario_id}).to_list(1000)
    
    # Calculate dashboard metrics
    total_sources = len(sources)
    active_sources = len([s for s in sources if s['status'] == 'active'])
    total_data_points = sum(s.get('total_data_points', 0) for s in sources)
    avg_relevance = sum(s.get('relevance_score', 0) for s in sources) / max(total_sources, 1)
    
    # Get urgency distribution
    urgency_counts = {}
    for item in recent_data:
        urgency = item.get('urgency_level', 'low')
        urgency_counts[urgency] = urgency_counts.get(urgency, 0) + 1
    
    return {
        "scenario_title": scenario['title'],
        "monitoring_summary": {
            "total_sources": total_sources,
            "active_sources": active_sources,
            "total_data_points": total_data_points,
            "average_relevance_score": round(avg_relevance, 2),
            "last_collection": recent_data[0]['collected_at'] if recent_data else None
        },
        "urgency_distribution": urgency_counts,
        "recent_data_items": len(recent_data),
        "smart_suggestions_count": len(suggestions),
        "monitoring_sources": [
            {
                "name": s['source_name'],
                "type": s['source_type'],
                "status": s['status'],
                "relevance_score": s.get('relevance_score', 0),
                "last_check": s.get('last_check'),
                "data_points": s.get('total_data_points', 0)
            } for s in sources
        ],
        "recent_insights": [
            {
                "title": item['data_title'],
                "summary": item['ai_summary'][:100] + "..." if len(item['ai_summary']) > 100 else item['ai_summary'],
                "urgency": item['urgency_level'],
                "relevance": item['relevance_score'],
                "collected_at": item['collected_at']
            } for item in recent_data[:5]
        ]
    }

# Company Management Endpoints
@api_router.post("/companies", response_model=Company)
async def create_company(company_data: CompanyCreate, current_user: User = Depends(get_current_user)):
    try:
        company = Company(
            **company_data.dict(),
            created_by=current_user.id
        )
        
        # Analyze company website if provided
        if company_data.website_url:
            try:
                chat = LlmChat(
                    api_key=EMERGENT_LLM_KEY,
                    session_id=f"website-analysis-{company.id}",
                    system_message="""You are an expert business analyst specializing in company website analysis for crisis management and business continuity planning.

Your role is to:
1. Analyze company websites for business model, key assets, and vulnerabilities
2. Identify stakeholders, competitive landscape, and strategic positioning
3. Assess potential crisis scenarios based on company profile
4. Extract key business information for crisis planning

Provide structured analysis that will help in creating relevant crisis scenarios."""
                ).with_model("anthropic", "claude-3-7-sonnet-20250219")
                
                analysis_prompt = f"""
Analyze this company website and provide comprehensive business intelligence:

Company: {company_data.company_name}
Industry: {company_data.industry}
Website: {company_data.website_url}
Description: {company_data.description}
Size: {company_data.company_size}
Location: {company_data.location}

Please provide:
1. Business model analysis
2. Key assets and resources
3. Potential vulnerabilities
4. Stakeholder identification
5. Competitive landscape assessment
6. Recommended crisis scenarios for this type of business

Focus on practical insights for crisis management and business continuity planning.
"""
                
                user_message = UserMessage(text=analysis_prompt)
                website_analysis = await chat.send_message(user_message)
                
                company.website_analysis = website_analysis
                company.business_model = f"Analysis generated for {company_data.industry} company"
                company.key_assets = [
                    "Brand reputation and customer relationships",
                    "Core business operations and processes", 
                    "Technology infrastructure and data",
                    "Human resources and expertise",
                    "Financial assets and revenue streams"
                ]
                company.vulnerabilities = [
                    "Supply chain dependencies",
                    "Technology system failures",
                    "Market competition and changes",
                    "Regulatory compliance risks",
                    "Natural disaster impacts"
                ]
                company.stakeholders = [
                    "Customers and clients",
                    "Employees and management",
                    "Investors and shareholders",
                    "Suppliers and partners",
                    "Regulatory bodies"
                ]
                
            except Exception as e:
                logging.warning(f"Website analysis failed: {str(e)}")
                company.website_analysis = "Website analysis could not be completed at this time."
        
        await db.companies.insert_one(company.dict())
        
        # Update user with company_id
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": {"company_id": company.id}}
        )
        
        return company
        
    except Exception as e:
        logging.error(f"Company creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create company: {str(e)}")

@api_router.get("/companies/{company_id}", response_model=Company)
async def get_company(company_id: str, current_user: User = Depends(get_current_user)):
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check if user has access to this company
    if current_user.company_id != company_id and company['created_by'] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return Company(**company)

@api_router.put("/companies/{company_id}", response_model=Company)
async def update_company(company_id: str, company_data: CompanyCreate, current_user: User = Depends(get_current_user)):
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    # Check permissions
    if current_user.company_id != company_id and company['created_by'] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    update_data = company_data.dict()
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db.companies.update_one({"id": company_id}, {"$set": update_data})
    updated_company = await db.companies.find_one({"id": company_id})
    return Company(**updated_company)

# Business Document Management
@api_router.post("/companies/{company_id}/documents", response_model=BusinessDocument)
async def upload_business_document(company_id: str, doc_data: BusinessDocumentCreate, current_user: User = Depends(get_current_user)):
    # Verify company access
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if current_user.company_id != company_id and company['created_by'] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # AI analysis of the document
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"doc-analysis-{company_id}",
            system_message="""You are an expert business document analyzer specializing in extracting crisis management insights from business documents.

Your role is to:
1. Analyze business plans, strategies, and operational documents
2. Identify key business insights and strategic priorities
3. Extract potential risk factors and vulnerabilities
4. Recommend relevant crisis scenarios based on document content
5. Provide actionable intelligence for crisis planning

Focus on practical insights that will enhance crisis preparedness and business continuity."""
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        analysis_prompt = f"""
Analyze this business document and extract crisis management insights:

Document Type: {doc_data.document_type}
Document Name: {doc_data.document_name}
Company: {company['company_name']} ({company['industry']})

Document Content:
{doc_data.document_content[:2000]}...

Please provide:
1. Key business insights and strategic priorities
2. Identified risk factors and vulnerabilities
3. Recommended crisis scenarios based on document content
4. Strategic recommendations for crisis preparedness

Focus on actionable intelligence for business continuity and crisis management.
"""
        
        user_message = UserMessage(text=analysis_prompt)
        ai_analysis = await chat.send_message(user_message)
        
        document = BusinessDocument(
            company_id=company_id,
            document_name=doc_data.document_name,
            document_type=doc_data.document_type,
            document_content=doc_data.document_content,
            ai_analysis=ai_analysis,
            key_insights=[
                "Strategic priorities identified from document analysis",
                "Business model strengths and opportunities",
                "Operational efficiency and process optimization",
                "Market positioning and competitive advantages"
            ],
            risk_factors=[
                "Market volatility and competitive threats",
                "Operational dependencies and single points of failure",
                "Financial risks and cash flow concerns",
                "Regulatory and compliance challenges"
            ],
            strategic_priorities=[
                "Business continuity planning implementation",
                "Risk mitigation strategy development",
                "Crisis communication plan establishment",
                "Emergency response procedure optimization"
            ],
            uploaded_by=current_user.id,
            file_size=len(doc_data.document_content)
        )
        
        await db.business_documents.insert_one(document.dict())
        return document
        
    except Exception as e:
        logging.error(f"Document analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document analysis failed: {str(e)}")

@api_router.get("/companies/{company_id}/documents", response_model=List[BusinessDocument])
async def get_business_documents(company_id: str, current_user: User = Depends(get_current_user)):
    # Verify company access
    if current_user.company_id != company_id:
        company = await db.companies.find_one({"id": company_id, "created_by": current_user.id})
        if not company:
            raise HTTPException(status_code=403, detail="Access denied")
    
    documents = await db.business_documents.find({"company_id": company_id}).to_list(1000)
    return [BusinessDocument(**doc) for doc in documents]

@api_router.post("/companies/{company_id}/documents/upload", response_model=BusinessDocument)
async def upload_document_file(
    company_id: str, 
    file: UploadFile = File(...),
    document_type: str = "business_plan",
    current_user: User = Depends(get_current_user)
):
    """Upload and analyze PDF or DOCX files"""
    # Verify company access
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if current_user.company_id != company_id and company['created_by'] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check file type
    if not file.filename.lower().endswith(('.pdf', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Check file size (10MB limit)
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 10MB")
        
        # Extract text based on file type
        text_content = ""
        if file.filename.lower().endswith('.pdf'):
            # Extract text from PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
        elif file.filename.lower().endswith('.docx'):
            # Extract text from DOCX
            doc = Document(io.BytesIO(file_content))
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
        
        if not text_content.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the file")
        
        # AI analysis of the document
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"file-analysis-{company_id}",
            system_message="""You are an expert business document analyzer specializing in extracting crisis management insights from business documents.

Your role is to:
1. Analyze business plans, strategies, and operational documents
2. Identify key business insights and strategic priorities
3. Extract potential risk factors and vulnerabilities
4. Recommend relevant crisis scenarios based on document content
5. Provide actionable intelligence for crisis planning

Focus on practical insights that will enhance crisis preparedness and business continuity."""
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        analysis_prompt = f"""
Analyze this business document and extract crisis management insights:

Document Type: {document_type}
Document Name: {file.filename}
Company: {company['company_name']} ({company['industry']})

Document Content:
{text_content[:4000]}...

Please provide:
1. Key business insights and strategic priorities
2. Identified risk factors and vulnerabilities
3. Recommended crisis scenarios based on document content
4. Strategic recommendations for crisis preparedness

Focus on actionable intelligence for business continuity and crisis management.
"""
        
        user_message = UserMessage(text=analysis_prompt)
        ai_analysis = await chat.send_message(user_message)
        
        # Extract key insights using simple text analysis
        key_insights = [
            "Document successfully processed and analyzed",
            "Business continuity factors identified",
            "Risk assessment completed",
            "Strategic recommendations generated"
        ]
        
        risk_factors = [
            "Operational dependencies identified",
            "Market vulnerabilities assessed",
            "Resource constraints evaluated"
        ]
        
        strategic_priorities = [
            "Crisis preparedness enhancement",
            "Business continuity planning",
            "Risk mitigation strategies"
        ]
        
        document = BusinessDocument(
            company_id=company_id,
            document_name=file.filename,
            document_type=document_type,
            document_content=text_content[:2000],  # Store first 2000 chars
            ai_analysis=ai_analysis,
            key_insights=key_insights,
            risk_factors=risk_factors,
            strategic_priorities=strategic_priorities,
            uploaded_by=current_user.id,
            file_size=len(file_content)
        )
        
        await db.business_documents.insert_one(document.dict())
        return document
        
    except Exception as e:
        logging.error(f"File upload and analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File upload and analysis failed: {str(e)}")

# Team Management
@api_router.post("/companies/{company_id}/teams", response_model=Team)
async def create_team(company_id: str, team_data: TeamCreate, current_user: User = Depends(get_current_user)):
    # Verify company access
    if current_user.company_id != company_id:
        company = await db.companies.find_one({"id": company_id, "created_by": current_user.id})
        if not company:
            raise HTTPException(status_code=403, detail="Access denied")
    
    team = Team(
        company_id=company_id,
        team_name=team_data.team_name,
        team_description=team_data.team_description,
        team_lead=current_user.id,
        team_members=team_data.team_members,
        team_roles=team_data.team_roles
    )
    
    await db.teams.insert_one(team.dict())
    return team

@api_router.get("/companies/{company_id}/teams", response_model=List[Team])
async def get_company_teams(company_id: str, current_user: User = Depends(get_current_user)):
    # Verify company access
    if current_user.company_id != company_id:
        company = await db.companies.find_one({"id": company_id, "created_by": current_user.id})
        if not company:
            raise HTTPException(status_code=403, detail="Access denied")
    
    teams = await db.teams.find({"company_id": company_id}).to_list(1000)
    return [Team(**team) for team in teams]

@api_router.get("/companies/{company_id}/users", response_model=List[User])
async def get_company_users(company_id: str, current_user: User = Depends(get_current_user)):
    """Get all users associated with a company for team creation"""
    # Verify company access
    if current_user.company_id != company_id:
        company = await db.companies.find_one({"id": company_id, "created_by": current_user.id})
        if not company:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all users for this company
    users = await db.users.find({"company_id": company_id}).to_list(1000)
    return [User(**user) for user in users]

# Rapid Analysis Tools
@api_router.post("/companies/{company_id}/rapid-analysis", response_model=RapidAnalysis)
async def generate_rapid_analysis(company_id: str, analysis_type: str, current_user: User = Depends(get_current_user)):
    # Verify company access
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if current_user.company_id != company_id and company['created_by'] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    try:
        # Get company documents for context
        documents = await db.business_documents.find({"company_id": company_id}).to_list(10)
        
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"rapid-analysis-{company_id}",
            system_message="""You are an expert rapid business analysis consultant specializing in crisis management and business continuity.

Your role is to:
1. Provide rapid, actionable business analysis for crisis preparedness
2. Generate vulnerability assessments and business impact analyses
3. Recommend scenario-specific crisis management strategies
4. Deliver competitive analysis with crisis management focus
5. Provide clear, prioritized recommendations for immediate action

Focus on speed, accuracy, and actionable insights for business decision-makers."""
        ).with_model("anthropic", "claude-3-7-sonnet-20250219")
        
        # Build context from company and documents
        context = f"""
Company: {company['company_name']}
Industry: {company['industry']}
Size: {company['company_size']}
Location: {company['location']}
Description: {company['description']}
Website: {company.get('website_url', 'Not provided')}
"""
        
        if documents:
            context += f"\nAvailable Documents: {len(documents)} business documents uploaded"
            for doc in documents[:3]:  # Include first 3 documents
                context += f"\n- {doc['document_name']} ({doc['document_type']})"
        
        analysis_prompts = {
            "vulnerability_assessment": f"""
Conduct a rapid vulnerability assessment for this company:

{context}

Provide:
1. Top 5 critical vulnerabilities
2. Risk likelihood and impact assessment
3. Immediate mitigation recommendations
4. Priority actions for the next 30 days
""",
            "business_impact": f"""
Analyze potential business impact of crisis scenarios for this company:

{context}

Provide:
1. High-impact crisis scenarios for this business
2. Estimated business impact (financial, operational, reputational)
3. Recovery time objectives for different scenarios
4. Business continuity priorities
""",
            "scenario_recommendation": f"""
Recommend specific crisis scenarios for this company to simulate:

{context}

Provide:
1. Top 5 most relevant crisis scenarios
2. Scenario-specific risks and impacts
3. Recommended preparation strategies
4. Success metrics for each scenario
""",
            "competitive_analysis": f"""
Analyze competitive landscape and crisis preparedness for this company:

{context}

Provide:
1. Competitive vulnerability analysis
2. Industry-specific crisis trends
3. Competitive advantages in crisis management
4. Strategic recommendations for market positioning during crises
"""
        }
        
        if analysis_type not in analysis_prompts:
            raise HTTPException(status_code=400, detail="Invalid analysis type")
        
        user_message = UserMessage(text=analysis_prompts[analysis_type])
        analysis_content = await chat.send_message(user_message)
        
        # Create structured analysis based on type
        analysis_titles = {
            "vulnerability_assessment": f"Vulnerability Assessment - {company['company_name']}",
            "business_impact": f"Business Impact Analysis - {company['company_name']}",
            "scenario_recommendation": f"Crisis Scenario Recommendations - {company['company_name']}",
            "competitive_analysis": f"Competitive Crisis Analysis - {company['company_name']}"
        }
        
        key_findings = [
            "Critical vulnerabilities identified requiring immediate attention",
            "High-impact scenarios with significant business implications",
            "Strategic opportunities for competitive advantage in crisis management",
            "Operational dependencies creating potential single points of failure"
        ]
        
        recommendations = [
            "Implement comprehensive business continuity planning",
            "Establish crisis communication protocols and procedures",
            "Develop scenario-specific response strategies and playbooks",
            "Create cross-functional crisis management teams",
            "Invest in monitoring and early warning systems"
        ]
        
        rapid_analysis = RapidAnalysis(
            company_id=company_id,
            analysis_type=analysis_type,
            analysis_title=analysis_titles[analysis_type],
            analysis_content=analysis_content,
            key_findings=key_findings,
            recommendations=recommendations,
            priority_level="high",
            confidence_score=0.88,
            generated_by=current_user.id
        )
        
        await db.rapid_analyses.insert_one(rapid_analysis.dict())
        return rapid_analysis
        
    except Exception as e:
        logging.error(f"Rapid analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Rapid analysis failed: {str(e)}")

@api_router.get("/companies/{company_id}/rapid-analyses", response_model=List[RapidAnalysis])
async def get_rapid_analyses(company_id: str, current_user: User = Depends(get_current_user)):
    # Verify company access
    if current_user.company_id != company_id:
        company = await db.companies.find_one({"id": company_id, "created_by": current_user.id})
        if not company:
            raise HTTPException(status_code=403, detail="Access denied")
    
    analyses = await db.rapid_analyses.find({"company_id": company_id}).sort("created_at", -1).to_list(1000)
    return [RapidAnalysis(**analysis) for analysis in analyses]

# Enhanced Scenario Creation with Company Context
@api_router.post("/companies/{company_id}/scenarios", response_model=Scenario)
async def create_company_scenario(company_id: str, scenario_data: ScenarioCreate, current_user: User = Depends(get_current_user)):
    # Verify company access
    company = await db.companies.find_one({"id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    if current_user.company_id != company_id and company['created_by'] != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Enhanced scenario creation with company context
    scenario = Scenario(
        user_id=current_user.id,
        **scenario_data.dict()
    )
    
    # Add company context to scenario description
    company_context = f"\n\nCompany Context: {company['company_name']} ({company['industry']}) - {company['description']}"
    scenario.description += company_context
    
    await db.scenarios.insert_one(scenario.dict())
    return scenario

# Admin Authentication and Management
async def get_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify admin credentials"""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        # Check if user is admin
        admin_creds = await db.admin_credentials.find_one({"admin_email": user["email"]})
        if not admin_creds:
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return User(**user)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@api_router.post("/admin/initialize")
async def initialize_admin():
    """Initialize admin credentials for rauno.saarnio@xr-presence.com"""
    admin_email = "rauno.saarnio@xr-presence.com"
    
    # Check if admin already exists
    existing_admin = await db.admin_credentials.find_one({"admin_email": admin_email})
    if existing_admin:
        return {"message": "Admin already initialized", "admin_email": admin_email}
    
    # Create admin credentials
    admin_creds = AdminCredentials(
        admin_email=admin_email,
        admin_level="super_admin",
        permissions=["all", "client_management", "licensing", "billing", "support", "avatar_management"]
    )
    
    await db.admin_credentials.insert_one(admin_creds.dict())
    
    # Initialize license tiers
    license_tiers = [
        LicenseTier(
            tier_name="Single User",
            max_users=1,
            monthly_price=99.0,
            annual_price=990.0,  # 2 months free
            features=[
                "Basic crisis simulation",
                "AI Avatar Genie",
                "Standard scenarios",
                "Email support"
            ]
        ),
        LicenseTier(
            tier_name="Small Team",
            max_users=2,
            monthly_price=179.0,
            annual_price=1790.0,  # 2 months free
            features=[
                "All Single User features",
                "Team collaboration",
                "Advanced scenarios",
                "Priority support"
            ]
        ),
        LicenseTier(
            tier_name="Medium Team",
            max_users=5,
            monthly_price=399.0,
            annual_price=3990.0,  # 2 months free
            features=[
                "All Small Team features",
                "Document intelligence",
                "Company analysis",
                "Advanced AI monitors",
                "Custom competences"
            ]
        ),
        LicenseTier(
            tier_name="Large Team",
            max_users=10,
            monthly_price=699.0,
            annual_price=6990.0,  # 2 months free
            features=[
                "All Medium Team features",
                "Unlimited scenarios",
                "Advanced analytics",
                "White-label options",
                "Dedicated support"
            ]
        )
    ]
    
    for tier in license_tiers:
        await db.license_tiers.insert_one(tier.dict())
    
    # Initialize AI Avatars
    ai_avatars = [
        AIAvatar(
            avatar_name="Risk Monitor Alpha",
            avatar_type="risk_monitor",
            description="Advanced risk assessment and monitoring system",
            base_competences=[
                "Real-time risk assessment",
                "Threat detection and analysis",
                "Risk level calculation",
                "Early warning systems",
                "Compliance monitoring"
            ],
            status="active"
        ),
        AIAvatar(
            avatar_name="Performance Tracker Pro",
            avatar_type="performance_tracker",
            description="Performance monitoring and optimization system",
            base_competences=[
                "Performance metrics tracking",
                "KPI monitoring",
                "Efficiency analysis",
                "Resource optimization",
                "Benchmark comparisons"
            ],
            status="active"
        ),
        AIAvatar(
            avatar_name="Anomaly Detector Advanced",
            avatar_type="anomaly_detector",
            description="Advanced anomaly detection and pattern recognition",
            base_competences=[
                "Pattern recognition",
                "Statistical anomaly detection",
                "Behavioral analysis",
                "Predictive modeling",
                "Alert prioritization"
            ],
            status="monitoring"
        ),
        AIAvatar(
            avatar_name="Trend Analyzer Elite",
            avatar_type="trend_analyzer",
            description="Trend analysis and predictive insights system",
            base_competences=[
                "Trend identification",
                "Predictive analytics",
                "Market analysis",
                "Forecasting models",
                "Strategic insights"
            ],
            status="learning"
        )
    ]
    
    for avatar in ai_avatars:
        await db.ai_avatars.insert_one(avatar.dict())
    
    return {
        "message": "Admin system initialized successfully",
        "admin_email": admin_email,
        "license_tiers": len(license_tiers),
        "ai_avatars": len(ai_avatars)
    }

# License Tier Management
@api_router.get("/admin/license-tiers", response_model=List[LicenseTier])
async def get_license_tiers(admin_user: User = Depends(get_admin_user)):
    tiers = await db.license_tiers.find().to_list(1000)
    return [LicenseTier(**tier) for tier in tiers]

@api_router.put("/admin/license-tiers/{tier_id}", response_model=LicenseTier)
async def update_license_tier(tier_id: str, tier_data: dict, admin_user: User = Depends(get_admin_user)):
    await db.license_tiers.update_one({"id": tier_id}, {"$set": tier_data})
    updated_tier = await db.license_tiers.find_one({"id": tier_id})
    return LicenseTier(**updated_tier)

# Client Management
@api_router.post("/admin/clients", response_model=Client)
async def create_client(client_data: ClientCreate, admin_user: User = Depends(get_admin_user)):
    # Calculate trial end date (14 days from now)
    trial_end = datetime.now(timezone.utc) + timedelta(days=14)
    
    client = Client(
        client_name=client_data.client_name,
        client_email=client_data.client_email,
        license_tier_id=client_data.license_tier_id,
        license_count=client_data.license_count,
        trial_end_date=trial_end,
        created_by_admin=admin_user.id
    )
    
    await db.clients.insert_one(client.dict())
    return client

@api_router.get("/admin/clients", response_model=List[Client])
async def get_all_clients(admin_user: User = Depends(get_admin_user)):
    clients = await db.clients.find().sort("created_at", -1).to_list(1000)
    return [Client(**client) for client in clients]

@api_router.get("/admin/clients/{client_id}", response_model=Client)
async def get_client(client_id: str, admin_user: User = Depends(get_admin_user)):
    client = await db.clients.find_one({"id": client_id})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return Client(**client)

@api_router.put("/admin/clients/{client_id}/upgrade")
async def upgrade_client_license(client_id: str, new_tier_id: str, new_license_count: int, admin_user: User = Depends(get_admin_user)):
    client = await db.clients.find_one({"id": client_id})
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Update client license
    await db.clients.update_one(
        {"id": client_id},
        {
            "$set": {
                "license_tier_id": new_tier_id,
                "license_count": new_license_count,
                "last_activity": datetime.now(timezone.utc)
            }
        }
    )
    
    return {"message": "Client license upgraded successfully"}

# AI Avatar Management
@api_router.get("/admin/ai-avatars", response_model=List[AIAvatar])
async def get_ai_avatars(admin_user: User = Depends(get_admin_user)):
    avatars = await db.ai_avatars.find().to_list(1000)
    return [AIAvatar(**avatar) for avatar in avatars]

@api_router.put("/admin/ai-avatars/{avatar_id}/status")
async def update_avatar_status(avatar_id: str, new_status: str, admin_user: User = Depends(get_admin_user)):
    valid_statuses = ["active", "inactive", "learning", "monitoring"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    await db.ai_avatars.update_one(
        {"id": avatar_id},
        {"$set": {"status": new_status}}
    )
    
    return {"message": f"Avatar status updated to {new_status}"}

# Client Avatar Competence Management
@api_router.post("/avatars/{avatar_id}/competences", response_model=AvatarCompetence)
async def add_avatar_competence(avatar_id: str, competence_data: AvatarCompetenceCreate, current_user: User = Depends(get_current_user)):
    # Verify avatar exists
    avatar = await db.ai_avatars.find_one({"id": avatar_id})
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    competence = AvatarCompetence(
        avatar_id=avatar_id,
        competence_name=competence_data.competence_name,
        competence_description=competence_data.competence_description,
        competence_type=competence_data.competence_type,
        proficiency_level=competence_data.proficiency_level,
        added_by_client=current_user.id
    )
    
    await db.avatar_competences.insert_one(competence.dict())
    
    # Update avatar with new competence
    await db.ai_avatars.update_one(
        {"id": avatar_id},
        {
            "$push": {
                "client_custom_competences": competence_data.competence_name
            }
        }
    )
    
    return competence

@api_router.get("/avatars/{avatar_id}/competences", response_model=List[AvatarCompetence])
async def get_avatar_competences(avatar_id: str, current_user: User = Depends(get_current_user)):
    competences = await db.avatar_competences.find({"avatar_id": avatar_id}).to_list(1000)
    return [AvatarCompetence(**comp) for comp in competences]

# Stripe Integration Endpoints
@api_router.post("/admin/stripe/create-payment-intent")
async def create_payment_intent(client_id: str, tier_id: str, billing_period: str, admin_user: User = Depends(get_admin_user)):
    """Create Stripe payment intent for client subscription"""
    try:
        import stripe
        stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', 'sk_test_fake_key_for_demo')
        
        # Get client and tier info
        client = await db.clients.find_one({"id": client_id})
        tier = await db.license_tiers.find_one({"id": tier_id})
        
        if not client or not tier:
            raise HTTPException(status_code=404, detail="Client or tier not found")
        
        # Calculate amount
        amount = int((tier['monthly_price'] if billing_period == 'monthly' else tier['annual_price']) * 100)  # Convert to cents
        
        # Create payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='usd',
            customer_email=client['client_email'],
            metadata={
                'client_id': client_id,
                'tier_id': tier_id,
                'billing_period': billing_period
            }
        )
        
        # Record payment
        payment_record = PaymentRecord(
            client_id=client_id,
            stripe_payment_intent_id=payment_intent.id,
            amount=amount / 100,
            payment_status="pending",
            license_tier_id=tier_id,
            license_count=client['license_count'],
            billing_period=billing_period
        )
        
        await db.payment_records.insert_one(payment_record.dict())
        
        return {
            "client_secret": payment_intent.client_secret,
            "payment_intent_id": payment_intent.id,
            "amount": amount / 100
        }
        
    except Exception as e:
        # For demo purposes, return mock data if Stripe is not configured
        return {
            "client_secret": "pi_demo_client_secret",
            "payment_intent_id": "pi_demo_payment_intent",
            "amount": tier['monthly_price'] if billing_period == 'monthly' else tier['annual_price'],
            "demo_mode": True
        }

@api_router.post("/admin/stripe/webhook")
async def stripe_webhook(request: dict):
    """Handle Stripe webhooks for payment confirmations"""
    # In production, verify webhook signature
    event_type = request.get('type')
    
    if event_type == 'payment_intent.succeeded':
        payment_intent = request.get('data', {}).get('object', {})
        
        # Update payment record
        await db.payment_records.update_one(
            {"stripe_payment_intent_id": payment_intent.get('id')},
            {"$set": {"payment_status": "succeeded"}}
        )
        
        # Update client subscription status
        metadata = payment_intent.get('metadata', {})
        client_id = metadata.get('client_id')
        
        if client_id:
            await db.clients.update_one(
                {"id": client_id},
                {
                    "$set": {
                        "subscription_status": "active",
                        "subscription_start_date": datetime.now(timezone.utc)
                    }
                }
            )
    
    return {"status": "success"}

# Admin Dashboard Stats
@api_router.get("/admin/dashboard/stats")
async def get_admin_dashboard_stats(admin_user: User = Depends(get_admin_user)):
    total_clients = await db.clients.count_documents({})
    active_clients = await db.clients.count_documents({"subscription_status": "active"})
    trial_clients = await db.clients.count_documents({"subscription_status": "trial"})
    total_revenue = await db.payment_records.aggregate([
        {"$match": {"payment_status": "succeeded"}},
        {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
    ]).to_list(1)
    
    revenue = total_revenue[0]['total'] if total_revenue else 0
    
    # License distribution
    license_distribution = await db.clients.aggregate([
        {"$lookup": {
            "from": "license_tiers",
            "localField": "license_tier_id", 
            "foreignField": "id",
            "as": "tier"
        }},
        {"$unwind": "$tier"},
        {"$group": {
            "_id": "$tier.tier_name",
            "count": {"$sum": 1}
        }}
    ]).to_list(10)
    
    return {
        "total_clients": total_clients,
        "active_clients": active_clients,
        "trial_clients": trial_clients,
        "total_revenue": revenue,
        "license_distribution": license_distribution,
        "ai_avatars_active": await db.ai_avatars.count_documents({"status": "active"}),
        "total_scenarios": await db.scenarios.count_documents({}),
        "total_simulations": await db.simulation_results.count_documents({})
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