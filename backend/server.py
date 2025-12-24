from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import jwt
import bcrypt
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_SECRET = os.environ.get('JWT_SECRET', 'fallback_secret')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Gemini Configuration
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ===================== MODELS =====================

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "student"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    email: str
    role: str
    created_at: str

class TokenResponse(BaseModel):
    token: str
    user: UserResponse

class Classroom(BaseModel):
    model_config = ConfigDict(extra="ignore")
    room_id: str
    floor: str
    capacity: int
    facilities: List[str]
    map_link: str

class RoomAvailability(BaseModel):
    room_id: str
    floor: str
    capacity: int
    facilities: List[str]
    map_link: str
    status: str
    predicted_availability: Dict[str, str]

class SearchQuery(BaseModel):
    query: str

class SearchResponse(BaseModel):
    message: Optional[str] = None
    rooms: Optional[List[RoomAvailability]] = None
    clarification_needed: Optional[str] = None

# ===================== CLASSROOM DATA =====================

CLASSROOMS = [
    # Ground Floor
    {"room_id": "LT-1", "floor": "Ground", "capacity": 120, "facilities": ["Projector", "Speaker", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+LT1"},
    {"room_id": "LT-2", "floor": "Ground", "capacity": 120, "facilities": ["Projector", "Speaker", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+LT2"},
    {"room_id": "LH-2", "floor": "Ground", "capacity": 60, "facilities": ["Projector", "Speaker", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+LH2"},
    {"room_id": "LH-3", "floor": "Ground", "capacity": 60, "facilities": ["Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+LH3"},
    # First Floor
    {"room_id": "LT-3", "floor": "First", "capacity": 120, "facilities": ["Projector", "Speaker", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+LT3"},
    {"room_id": "LT-4", "floor": "First", "capacity": 120, "facilities": ["Projector", "Speaker", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+LT4"},
    {"room_id": "101", "floor": "First", "capacity": 30, "facilities": ["Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+101"},
    {"room_id": "102", "floor": "First", "capacity": 30, "facilities": ["Projector", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+102"},
    {"room_id": "103", "floor": "First", "capacity": 60, "facilities": ["Projector", "Speaker", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+103"},
    {"room_id": "104", "floor": "First", "capacity": 30, "facilities": ["Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+104"},
    {"room_id": "105", "floor": "First", "capacity": 60, "facilities": ["Projector", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+105"},
    {"room_id": "106", "floor": "First", "capacity": 30, "facilities": ["Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+106"},
    {"room_id": "107", "floor": "First", "capacity": 60, "facilities": ["Projector", "Speaker", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+107"},
    {"room_id": "108", "floor": "First", "capacity": 30, "facilities": ["Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+108"},
    {"room_id": "109", "floor": "First", "capacity": 60, "facilities": ["Projector", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+109"},
    # Second Floor
    {"room_id": "201", "floor": "Second", "capacity": 30, "facilities": ["Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+201"},
    {"room_id": "202", "floor": "Second", "capacity": 60, "facilities": ["Projector", "Speaker", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+202"},
    {"room_id": "203", "floor": "Second", "capacity": 30, "facilities": ["Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+203"},
    {"room_id": "204", "floor": "Second", "capacity": 120, "facilities": ["Projector", "Speaker", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+204"},
    {"room_id": "205", "floor": "Second", "capacity": 60, "facilities": ["Projector", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+205"},
    {"room_id": "206", "floor": "Second", "capacity": 30, "facilities": ["Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+206"},
    {"room_id": "207", "floor": "Second", "capacity": 60, "facilities": ["Projector", "Speaker", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+207"},
    {"room_id": "208", "floor": "Second", "capacity": 30, "facilities": ["Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+208"},
    {"room_id": "209", "floor": "Second", "capacity": 120, "facilities": ["Projector", "Speaker", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+209"},
    {"room_id": "210", "floor": "Second", "capacity": 60, "facilities": ["Projector", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+210"},
    {"room_id": "211", "floor": "Second", "capacity": 30, "facilities": ["Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+211"},
    {"room_id": "212", "floor": "Second", "capacity": 60, "facilities": ["Projector", "Speaker", "Whiteboard", "Blackboard", "Podium"], "map_link": "https://maps.google.com/?q=IIPS+DAVV+212"},
]

# Mock schedule: room_id -> list of (start_hour, end_hour) occupied periods
MOCK_SCHEDULE = {
    "LT-1": [(8, 10), (11, 13), (14, 16)],
    "LT-2": [(9, 11), (12, 14), (15, 17)],
    "LH-2": [(8, 9), (10, 12), (14, 15), (16, 18)],
    "LH-3": [(9, 10), (11, 13), (15, 17)],
    "LT-3": [(8, 10), (12, 14), (16, 18)],
    "LT-4": [(9, 11), (13, 15), (17, 18)],
    "101": [(8, 9), (10, 11), (14, 15)],
    "102": [(9, 10), (11, 12), (15, 16)],
    "103": [(8, 10), (12, 14)],
    "104": [(10, 12), (14, 16)],
    "105": [(8, 9), (11, 13), (15, 17)],
    "106": [(9, 11), (13, 15)],
    "107": [(8, 10), (12, 13), (15, 16)],
    "108": [(10, 11), (13, 14), (16, 17)],
    "109": [(8, 9), (11, 12), (14, 15), (17, 18)],
    "201": [(9, 10), (12, 13), (15, 16)],
    "202": [(8, 10), (11, 13), (14, 16)],
    "203": [(10, 11), (13, 14), (16, 17)],
    "204": [(8, 9), (11, 12), (14, 15), (17, 18)],
    "205": [(9, 11), (12, 14), (15, 17)],
    "206": [(8, 10), (13, 15)],
    "207": [(10, 12), (14, 16), (17, 18)],
    "208": [(8, 9), (11, 12), (15, 16)],
    "209": [(9, 10), (12, 13), (16, 18)],
    "210": [(8, 10), (11, 13), (14, 15)],
    "211": [(10, 11), (13, 14), (16, 17)],
    "212": [(8, 9), (11, 12), (14, 16), (17, 18)],
}

# ===================== HELPER FUNCTIONS =====================

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        user = await db.users.find_one({"id": user_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def is_room_available(room_id: str, start_hour: float, end_hour: float) -> bool:
    """Check if room is available for the entire duration"""
    schedule = MOCK_SCHEDULE.get(room_id, [])
    for occupied_start, occupied_end in schedule:
        if not (end_hour <= occupied_start or start_hour >= occupied_end):
            return False
    return True

def get_room_status(room_id: str, current_hour: float) -> str:
    """Get current room status"""
    schedule = MOCK_SCHEDULE.get(room_id, [])
    for start, end in schedule:
        if start <= current_hour < end:
            return "Occupied"
    return "Available"

def get_predicted_availability(room_id: str, current_hour: float) -> Dict[str, str]:
    """Get predicted availability for next 30/60/90 minutes"""
    predictions = {}
    for mins, label in [(30, "next30"), (60, "next60"), (90, "next90")]:
        future_hour = current_hour + mins / 60
        if future_hour > 18.5:
            predictions[label] = "After Hours"
        elif is_room_available(room_id, current_hour, min(future_hour, 18.5)):
            predictions[label] = "Available"
        else:
            predictions[label] = "May be occupied"
    return predictions

def get_current_hour() -> float:
    """Get current hour in IST (UTC+5:30)"""
    now = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
    return now.hour + now.minute / 60

# ===================== AUTH ENDPOINTS =====================

@api_router.post("/auth/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_id = str(uuid.uuid4())
    user_doc = {
        "id": user_id,
        "name": user_data.name,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "role": user_data.role,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.users.insert_one(user_doc)
    
    token = create_token(user_id)
    user_response = UserResponse(
        id=user_id,
        name=user_data.name,
        email=user_data.email,
        role=user_data.role,
        created_at=user_doc["created_at"]
    )
    return TokenResponse(token=token, user=user_response)

@api_router.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    user = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"])
    user_response = UserResponse(
        id=user["id"],
        name=user["name"],
        email=user["email"],
        role=user["role"],
        created_at=user["created_at"]
    )
    return TokenResponse(token=token, user=user_response)

@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        name=current_user["name"],
        email=current_user["email"],
        role=current_user["role"],
        created_at=current_user["created_at"]
    )

# ===================== CLASSROOM ENDPOINTS =====================

@api_router.get("/classrooms", response_model=List[RoomAvailability])
async def get_classrooms(current_user: dict = Depends(get_current_user)):
    current_hour = get_current_hour()
    rooms = []
    for room in CLASSROOMS:
        status = get_room_status(room["room_id"], current_hour)
        predictions = get_predicted_availability(room["room_id"], current_hour)
        rooms.append(RoomAvailability(
            room_id=room["room_id"],
            floor=room["floor"],
            capacity=room["capacity"],
            facilities=room["facilities"],
            map_link=room["map_link"],
            status=status,
            predicted_availability=predictions
        ))
    return rooms

@api_router.get("/classrooms/{room_id}", response_model=RoomAvailability)
async def get_classroom(room_id: str, current_user: dict = Depends(get_current_user)):
    current_hour = get_current_hour()
    room = next((r for r in CLASSROOMS if r["room_id"] == room_id), None)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    status = get_room_status(room["room_id"], current_hour)
    predictions = get_predicted_availability(room["room_id"], current_hour)
    return RoomAvailability(
        room_id=room["room_id"],
        floor=room["floor"],
        capacity=room["capacity"],
        facilities=room["facilities"],
        map_link=room["map_link"],
        status=status,
        predicted_availability=predictions
    )

# ===================== SEARCH ENDPOINT =====================

SYSTEM_PROMPT = """You are an AI assistant for the "Empty Classroom Finder" at IIPS DAVV, Indore.
Your job is to interpret natural language queries and return structured JSON responses.

CAMPUS HOURS: Classrooms are available only between 8:00 AM and 6:30 PM.

ROOM DATA:
Ground Floor: LT-1 (120, Projector+Speaker), LT-2 (120, Projector+Speaker), LH-2 (60, Projector+Speaker), LH-3 (60, no projector)
First Floor: LT-3 (120, Projector+Speaker), LT-4 (120, Projector+Speaker), 101-109 (30/60 seats, mixed facilities)
Second Floor: 201-212 (30/60/120 seats, mixed facilities)
All rooms have Whiteboard, Blackboard, Podium (except special notes above).

CURRENT TIME INFO will be provided in the query.

RESPONSE FORMAT (always return valid JSON):
{
  "action": "search" | "error" | "clarify",
  "filters": {
    "floor": "Ground" | "First" | "Second" | null,
    "min_capacity": number | null,
    "facilities": ["Projector", "Speaker", etc] | null,
    "room_ids": ["LT-1", etc] | null,
    "start_hour": number (8-18.5) | null,
    "end_hour": number (8-18.5) | null
  },
  "message": "string (for errors or clarifications)",
  "time_context": "now" | "specific" | null
}

RULES:
1. If time is outside 8:00 AM - 6:30 PM, return action="error" with message about valid hours.
2. "now" means use current time. "next hour" means current time + 1 hour duration.
3. Parse relative times: "next 2 hours" = 2 hour duration from now.
4. For specific times like "10:00 AM to 12:30 PM", convert to start_hour=10, end_hour=12.5.
5. If query is ambiguous, return action="clarify" with a helpful question.
6. Always respond with valid JSON only, no extra text."""

@api_router.post("/search", response_model=SearchResponse)
async def search_classrooms(query: SearchQuery, current_user: dict = Depends(get_current_user)):
    current_hour = get_current_hour()
    current_time_str = f"{int(current_hour)}:{int((current_hour % 1) * 60):02d}"
    
    # Prepare context for LLM
    user_query = f"Current time: {current_time_str} (hour: {current_hour:.2f})\nUser query: {query.query}"
    
    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"search_{uuid.uuid4()}",
            system_message=SYSTEM_PROMPT
        ).with_model("gemini", "gemini-3-flash-preview")
        
        response = await chat.send_message(UserMessage(text=user_query))
        
        # Parse LLM response
        import json
        response_text = response.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        parsed = json.loads(response_text.strip())
        
        action = parsed.get("action", "search")
        
        if action == "error":
            return SearchResponse(message=parsed.get("message", "Invalid request"))
        
        if action == "clarify":
            return SearchResponse(clarification_needed=parsed.get("message", "Could you please clarify your request?"))
        
        # Apply filters
        filters = parsed.get("filters", {})
        filtered_rooms = CLASSROOMS.copy()
        
        # Filter by floor
        if filters.get("floor"):
            filtered_rooms = [r for r in filtered_rooms if r["floor"] == filters["floor"]]
        
        # Filter by room IDs
        if filters.get("room_ids"):
            filtered_rooms = [r for r in filtered_rooms if r["room_id"] in filters["room_ids"]]
        
        # Filter by capacity
        if filters.get("min_capacity"):
            filtered_rooms = [r for r in filtered_rooms if r["capacity"] >= filters["min_capacity"]]
        
        # Filter by facilities
        if filters.get("facilities"):
            required = set(filters["facilities"])
            filtered_rooms = [r for r in filtered_rooms if required.issubset(set(r["facilities"]))]
        
        # Filter by time availability
        start_hour = filters.get("start_hour")
        end_hour = filters.get("end_hour")
        time_context = parsed.get("time_context", "now")
        
        if time_context == "now" and not start_hour:
            start_hour = current_hour
            end_hour = min(current_hour + 1, 18.5)
        
        if start_hour is not None and end_hour is not None:
            # Validate time range
            if start_hour < 8 or end_hour > 18.5:
                return SearchResponse(message="Classrooms are available only between 8:00 AM and 6:30 PM. Please select a valid time range.")
            
            filtered_rooms = [r for r in filtered_rooms if is_room_available(r["room_id"], start_hour, end_hour)]
        
        # Build response with availability info
        result_rooms = []
        for room in filtered_rooms:
            check_hour = start_hour if start_hour else current_hour
            status = get_room_status(room["room_id"], check_hour)
            predictions = get_predicted_availability(room["room_id"], check_hour)
            result_rooms.append(RoomAvailability(
                room_id=room["room_id"],
                floor=room["floor"],
                capacity=room["capacity"],
                facilities=room["facilities"],
                map_link=room["map_link"],
                status="Available" if is_room_available(room["room_id"], start_hour or current_hour, end_hour or min(current_hour + 1, 18.5)) else status,
                predicted_availability=predictions
            ))
        
        if not result_rooms:
            return SearchResponse(message="No classrooms available matching your criteria.", rooms=[])
        
        return SearchResponse(rooms=result_rooms)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}, response: {response}")
        # Fallback: return all available rooms
        result_rooms = []
        for room in CLASSROOMS:
            status = get_room_status(room["room_id"], current_hour)
            if status == "Available":
                predictions = get_predicted_availability(room["room_id"], current_hour)
                result_rooms.append(RoomAvailability(
                    room_id=room["room_id"],
                    floor=room["floor"],
                    capacity=room["capacity"],
                    facilities=room["facilities"],
                    map_link=room["map_link"],
                    status=status,
                    predicted_availability=predictions
                ))
        return SearchResponse(rooms=result_rooms, message="Here are the currently available classrooms.")
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# ===================== ROOT & HEALTH =====================

@api_router.get("/")
async def root():
    return {"message": "Empty Classroom Finder API - IIPS DAVV"}

@api_router.get("/health")
async def health():
    return {"status": "healthy", "campus_hours": "8:00 AM - 6:30 PM"}

# Include router and middleware
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
