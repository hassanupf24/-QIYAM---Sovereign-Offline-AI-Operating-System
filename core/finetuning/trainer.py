import os
import argparse
from config.logger import setup_logger

logger = setup_logger("finetuning.trainer")

def train_lora(tenant_id: str, data_path: str, base_model: str = "meta-llama/Meta-Llama-3-8B-Instruct"):
    """
    Executes a Supervised Fine-Tuning (SFT) run using QLoRA on the specified tenant's dataset.
    This script is designed to be run offline, outside the main API loop.
    """
    try:
        import torch
        from datasets import load_dataset
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
        from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
        from trl import SFTTrainer
    except ImportError:
        logger.error("Missing PEFT/Transformers dependencies. Run: pip install transformers peft accelerate bitsandbytes trl datasets")
        return

    logger.info(f"Starting QLoRA fine-tuning for tenant: {tenant_id}")
    output_dir = f"models/adapters/{tenant_id}"
    os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(data_path):
        logger.error(f"Training data not found at {data_path}")
        return

    # Load dataset
    dataset = load_dataset("json", data_files=data_path, split="train")
    
    def format_chat_template(example):
        # Extremely basic conversational formatter
        # Assuming format: {"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}
        text = ""
        for turn in example['conversations']:
            role = "User" if turn["from"] == "human" else "AI"
            text += f"{role}: {turn['value']}\n"
        return {"text": text}

    dataset = dataset.map(format_chat_template)

    # 4-bit Quantization Config (QLoRA)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16
    )

    # Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(base_model)
    tokenizer.pad_token = tokenizer.eos_token

    # Load Base Model
    logger.info(f"Loading base model {base_model} in 4-bit precision...")
    model = AutoModelForCausalLM.from_pretrained(
        base_model,
        quantization_config=bnb_config,
        device_map="auto"
    )
    
    model = prepare_model_for_kbit_training(model)

    # LoRA Configuration
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # Training Arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=4,
        optim="paged_adamw_32bit",
        save_steps=50,
        logging_steps=10,
        learning_rate=2e-4,
        weight_decay=0.001,
        fp16=False,
        bf16=True,
        max_grad_norm=0.3,
        max_steps=200, # Short run for demo/incremental tuning
        warmup_ratio=0.03,
        group_by_length=True,
        lr_scheduler_type="cosine",
        report_to="none"
    )

    # Initialize Trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        peft_config=peft_config,
        dataset_text_field="text",
        max_seq_length=2048,
        tokenizer=tokenizer,
        args=training_args,
    )

    # Train
    logger.info("Executing training loop...")
    trainer.train()

    # Save Adapter
    logger.info(f"Training complete. Saving adapter to {output_dir}")
    trainer.model.save_pretrained(output_dir)
    tokenizer.save_pretrained(output_dir)
    logger.info("Adapter saved successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="QLoRA Fine-Tuning Script")
    parser.add_argument("--tenant", required=True, help="Tenant ID for the adapter")
    parser.add_argument("--data", default="training_data/dataset.jsonl", help="Path to JSONL training data")
    parser.add_argument("--model", default="meta-llama/Meta-Llama-3-8B-Instruct", help="HuggingFace Hub model ID")
    
    args = parser.parse_args()
    train_lora(args.tenant, args.data, args.model)
