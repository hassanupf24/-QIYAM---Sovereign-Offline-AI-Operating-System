from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from core.orchestrator import Orchestrator
from config.logger import setup_logger
from whatsapp.webhook import router as whatsapp_router
from api.routers.federated_sync import router as federated_router
from security.auth import create_access_token, get_current_user, TokenData
from memory.postgres_store import PostgresStore

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

# OpenTelemetry Setup
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    from opentelemetry.sdk.resources import Resource, SERVICE_NAME

    resource = Resource.create({SERVICE_NAME: "qiyam_api"})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://localhost:4317", insecure=True))
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    FastAPIInstrumentor.instrument_app(app)
    logger.info("OpenTelemetry instrumentation applied successfully.")
except ImportError:
    logger.warning("OpenTelemetry not installed. Skipping instrumentation.")

# Initialize the central brain
orchestrator = Orchestrator()
db_store = PostgresStore()

# Include external routers
app.include_router(whatsapp_router, prefix="/api/v1/whatsapp", tags=["WhatsApp"])
app.include_router(federated_router, prefix="/api/v1/federated", tags=["Federated Sync"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting QIYAM API Server...")

@app.get("/health")
async def health_check():
    return {"status": "online", "mode": "offline-sovereign", "version": "2.0.0"}

@app.post("/api/v1/auth/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # In a real app, verify against a password hash. For now, phone_number = username
    user = db_store.get_user_by_phone(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.id, "tenant_id": user.tenant_id, "role": user.role}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/v1/invoke")
async def invoke_agent(request: Request, current_user: TokenData = Depends(get_current_user)):
    data = await request.json()
    message = data.get("message")
    
    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
        
    logger.info(f"Received direct API invocation from user: {current_user.user_id} in tenant: {current_user.tenant_id}")
    
    # Run Orchestrator
    try:
        response = await orchestrator.process_message(message, current_user.user_id, current_user.tenant_id)
        return {"status": "success", "response": response}
    except Exception as e:
        logger.error(f"API Invocation Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Orchestration Error")
