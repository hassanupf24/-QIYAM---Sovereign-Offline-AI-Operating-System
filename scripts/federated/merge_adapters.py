import os
import tarfile
import logging
from cryptography.fernet import Fernet
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("federated.merge")

def generate_or_load_key() -> bytes:
    key = os.getenv("FEDERATED_AES_KEY")
    if not key:
        logger.error("FEDERATED_AES_KEY not found in env. Cannot decrypt payloads.")
        raise ValueError("Missing AES key")
    return key.encode('utf-8')

def decrypt_and_extract(import_dir: str = "sync/import", extract_dir: str = "sync/extracted"):
    """Decrypts and extracts all .aes files in the import directory."""
    os.makedirs(extract_dir, exist_ok=True)
    key = generate_or_load_key()
    fernet = Fernet(key)
    
    adapter_paths = []
    
    for filename in os.listdir(import_dir):
        if filename.endswith(".aes"):
            enc_path = os.path.join(import_dir, filename)
            tar_path = os.path.join(import_dir, filename.replace(".aes", ".tar.gz"))
            
            logger.info(f"Decrypting {filename}...")
            with open(enc_path, "rb") as f_in:
                decrypted_data = fernet.decrypt(f_in.read())
            
            with open(tar_path, "wb") as f_out:
                f_out.write(decrypted_data)
                
            logger.info(f"Extracting {tar_path}...")
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(path=extract_dir)
                
            # Clean up the decrypted tarball
            os.remove(tar_path)
            
            # Assuming the tarball contains a single directory matching the adapter name
            extracted_folder = filename.replace(".aes", "").replace("adapter_", "")
            adapter_paths.append(os.path.join(extract_dir, extracted_folder))
            
    return adapter_paths

def merge_adapters(base_model_name: str, adapter_paths: list, output_dir: str = "models/adapters/global"):
    """Uses PEFT to load and merge multiple LoRA adapters."""
    if not adapter_paths:
        logger.info("No new adapters to merge.")
        return
        
    logger.info(f"Loading base model: {base_model_name}")
    # Load base model in 16-bit to save memory during merge
    base_model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    logger.info(f"Loading first adapter from {adapter_paths[0]}...")
    model = PeftModel.from_pretrained(base_model, adapter_paths[0], adapter_name="adapter_0")
    
    adapter_names = ["adapter_0"]
    
    for i, path in enumerate(adapter_paths[1:], start=1):
        name = f"adapter_{i}"
        logger.info(f"Loading adapter {name} from {path}...")
        model.load_adapter(path, adapter_name=name)
        adapter_names.append(name)
        
    logger.info(f"Merging adapters: {adapter_names} with linear averaging...")
    # Add a weighted adapter combining all loaded adapters equally
    weights = [1.0 / len(adapter_names)] * len(adapter_names)
    
    model.add_weighted_adapter(
        adapters=adapter_names,
        weights=weights,
        adapter_name="merged_global",
        combination_type="linear"
    )
    
    # Set the active adapter to the newly merged one
    model.set_adapter("merged_global")
    
    logger.info("Merging weights into base model (if fully combining) or saving adapter...")
    # For federated sync, we save the resulting merged LoRA, NOT the whole model.
    # To save the merged LoRA, we actually need to merge and unload, but `add_weighted_adapter` 
    # creates a new adapter state. We can save this specific adapter state.
    
    os.makedirs(output_dir, exist_ok=True)
    model.save_pretrained(output_dir)
    logger.info(f"Successfully saved global merged adapter to {output_dir}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_model", type=str, default="meta-llama/Llama-2-7b-chat-hf", help="HuggingFace base model ID")
    parser.add_argument("--import_dir", type=str, default="sync/import", help="Directory containing downloaded .aes files")
    args = parser.parse_args()
    
    if not os.path.exists(args.import_dir):
        logger.info(f"Import directory {args.import_dir} does not exist. Nothing to do.")
    else:
        paths = decrypt_and_extract(args.import_dir)
        merge_adapters(args.base_model, paths)
