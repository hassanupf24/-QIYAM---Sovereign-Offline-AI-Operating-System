import os
import shutil
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from security.auth import get_current_user, TokenData
from config.logger import setup_logger

logger = setup_logger("api.federated_sync")
router = APIRouter()

HUB_DIR = "sync/central_hub"

@router.post("/upload")
async def upload_adapter(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    """
    Receives an encrypted LoRA adapter from a sovereign node.
    Requires Admin privileges.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can upload to the federated hub.")
        
    os.makedirs(HUB_DIR, exist_ok=True)
    
    if not file.filename.endswith(".aes"):
        raise HTTPException(status_code=400, detail="Only AES encrypted payloads are accepted.")
        
    file_path = os.path.join(HUB_DIR, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Successfully received federated payload: {file.filename} from tenant {current_user.tenant_id}")
        return {"status": "success", "filename": file.filename}
    except Exception as e:
        logger.error(f"Failed to save federated payload: {e}")
        raise HTTPException(status_code=500, detail="Failed to save payload")

@router.get("/download/{filename}")
async def download_adapter(
    filename: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Allows nodes to download peer adapters for merging.
    """
    from fastapi.responses import FileResponse
    
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can download from the federated hub.")
        
    file_path = os.path.join(HUB_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    logger.info(f"Tenant {current_user.tenant_id} downloading federated payload: {filename}")
    return FileResponse(file_path, media_type="application/octet-stream", filename=filename)
