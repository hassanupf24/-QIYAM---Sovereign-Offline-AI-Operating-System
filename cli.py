import asyncio
import sys
from core.orchestrator import orchestrator
from config.logger import setup_logger

logger = setup_logger("cli")

async def chat_loop():
    print("="*50)
    print("🤖 مرحباً بك في نظام QIYAM (قيام) - المساعد السيادي 🤖")
    print("="*50)
    print("اكتب 'خروج' أو 'exit' لإنهاء المحادثة.\n")
    
    # User phone/id mock
    user_id = "local_terminal_user"
    
    while True:
        try:
            user_input = input("أنت: ")
            
            if user_input.lower() in ["خروج", "exit", "quit"]:
                print("قيام: وداعاً! 👋")
                break
                
            if not user_input.strip():
                continue
                
            print("قيام يفكر...")
            
            # Process message through the orchestrator
            response = await orchestrator.process_message(user_input, user_id)
            
            print(f"قيام: {response}\n")
            
        except KeyboardInterrupt:
            print("\nقيام: تم إنهاء المحادثة. وداعاً! 👋")
            break
        except Exception as e:
            logger.error(f"Error in CLI loop: {str(e)}")
            print(f"\n[خطأ]: {str(e)}\n")

if __name__ == "__main__":
    # Ensure event loop handles async calls
    asyncio.run(chat_loop())
