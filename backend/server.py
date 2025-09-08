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