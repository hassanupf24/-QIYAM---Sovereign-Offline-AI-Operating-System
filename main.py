import uvicorn
from config.settings import settings
from config.logger import setup_logger

logger = setup_logger("main")

def main():
    logger.info(f"Starting QIYAM on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=(settings.ENVIRONMENT == "development")
    )

if __name__ == "__main__":
    main()
