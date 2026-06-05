from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.orchestrator import Orchestrator
from config.settings import settings
from config.logger import setup_logger
from whatsapp.webhook import router as whatsapp_router

logger = setup_logger("api.main")

app = FastAPI(
    title="QIYAM Sovereign AI OS",
    description="Enterprise Multi-Agent Operating System with Arabic-First Intelligence",
    version="2.0.0"
)

# Enable CORS for the Next.js Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the central brain
orchestrator = Orchestrator()

# Include external routers
app.include_router(whatsapp_router, prefix="/api/v1/whatsapp", tags=["WhatsApp"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting QIYAM API Server...")
    # System initialization hooks (Plugin loading, ML model warming)
    # orchestrator.initialize_subsystems()

@app.get("/health")
async def health_check():
    """Returns the operational status of the QIYAM Intelligence Stack."""
    return {"status": "online", "mode": "offline-sovereign", "version": "2.0.0"}

@app.post("/api/v1/invoke")
async def invoke_agent(request: Request, background_tasks: BackgroundTasks):
    """
    Direct API endpoint to invoke the Orchestrator (useful for desktop/web clients).
    """
    data = await request.json()
    message = data.get("message")
    user_id = data.get("user_id", "anonymous")
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
        
    logger.info(f"Received direct API invocation from user: {user_id}")
    
    # Run Orchestrator
    try:
        response = await orchestrator.process_message(message, user_id)
        return {"status": "success", "response": response}
    except Exception as e:
        logger.error(f"API Invocation Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Orchestration Error")
