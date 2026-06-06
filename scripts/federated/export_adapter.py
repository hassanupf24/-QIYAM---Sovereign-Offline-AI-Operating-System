import os
import argparse
import tarfile
from cryptography.fernet import Fernet
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("federated.export")

def generate_or_load_key() -> bytes:
    """Loads AES key from env or generates a new one (for demo purposes)."""
    key = os.getenv("FEDERATED_AES_KEY")
    if not key:
        key = Fernet.generate_key().decode('utf-8')
        logger.warning(f"FEDERATED_AES_KEY not found in env. Generated new key: {key}")
        logger.warning("Please add this to your .env file on both sending and receiving nodes.")
    return key.encode('utf-8')

def export_adapter(tenant_id: str, output_dir: str = "sync/export"):
    """
    Finds the latest LoRA adapter for a tenant, compresses it, and encrypts it via AES-256.
    """
    adapter_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..", "models", "adapters", tenant_id)
    
    if not os.path.exists(adapter_dir):
        logger.error(f"Adapter directory not found for tenant: {tenant_id}")
        return
        
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Compress adapter directory into a tarball
    tar_path = os.path.join(output_dir, f"adapter_{tenant_id}.tar.gz")
    logger.info(f"Compressing adapter to {tar_path}...")
    with tarfile.open(tar_path, "w:gz") as tar:
        tar.add(adapter_dir, arcname=os.path.basename(adapter_dir))
        
    # 2. Encrypt the tarball
    enc_path = os.path.join(output_dir, f"adapter_{tenant_id}.aes")
    logger.info(f"Encrypting {tar_path} into {enc_path}...")
    
    key = generate_or_load_key()
    fernet = Fernet(key)
    
    with open(tar_path, "rb") as f_in:
        encrypted_data = fernet.encrypt(f_in.read())
        
    with open(enc_path, "wb") as f_out:
        f_out.write(encrypted_data)
        
    # 3. Cleanup unencrypted tarball
    os.remove(tar_path)
    logger.info(f"Export complete. Encrypted payload ready at: {enc_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant", type=str, required=True, help="Tenant ID to export")
    parser.add_argument("--out", type=str, default="sync/export", help="Output directory")
    args = parser.parse_args()
    
    export_adapter(args.tenant, args.out)
