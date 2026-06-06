import os
import sys
import json
import argparse
from typing import List, Dict, Any

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from memory.postgres_store import PostgresStore, Message, MessageFeedback

def export_data(tenant_id: str = None, output_file: str = "dataset.jsonl"):
    """
    Exports conversation history into a ShareGPT-formatted JSONL file for SFT/LoRA training.
    Format: {"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}
    """
    store = PostgresStore()
    
    with store.SessionLocal() as db:
        query = db.query(Message)
        if tenant_id:
            query = query.filter(Message.tenant_id == tenant_id)
            
        messages = query.order_by(Message.session_id, Message.timestamp).all()
        
        # Get all negative message feedbacks
        negative_feedbacks = db.query(MessageFeedback).filter(MessageFeedback.rating < 0).all()
        negative_msg_ids = set(f.message_id for f in negative_feedbacks)
        
    if not messages:
        print("No messages found.")
        return

    # Group messages by session_id and track if session has any negative feedback
    sessions: Dict[str, List[Message]] = {}
    bad_sessions = set()
    
    for msg in messages:
        if msg.id in negative_msg_ids:
            bad_sessions.add(msg.session_id)
            
        if msg.session_id not in sessions:
            sessions[msg.session_id] = []
        sessions[msg.session_id].append(msg)
        
    # Format to ShareGPT and write to file
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    
    count = 0
    with open(output_file, 'w', encoding='utf-8') as f:
        for session_id, msgs in sessions.items():
            if session_id in bad_sessions:
                # RLHF: Skip conversations that were rated poorly by the user
                continue
                
            # We need at least a human-gpt pair
            if len(msgs) < 2:
                continue
                
            conversations = []
            for msg in msgs:
                # Map role to ShareGPT format ('human' or 'gpt')
                role = "human" if msg.role == "user" else "gpt"
                conversations.append({
                    "from": role,
                    "value": msg.content
                })
                
            record = {"conversations": conversations}
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
            
    print(f"Successfully exported {count} conversation sessions to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export training data from QIYAM database.")
    parser.add_argument("--tenant", type=str, help="Specific tenant_id to filter by", default=None)
    parser.add_argument("--output", type=str, help="Output JSONL file path", default="training_data/dataset.jsonl")
    
    args = parser.parse_args()
    export_data(args.tenant, args.output)
