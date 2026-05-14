import sys
import traceback

sys.path.insert(0, '/a0')
sys.path.insert(0, '/a0/usr/skills/telegram-bot')

print("=== TELEGRAM BRIDGE DIAGNOSTIC ===")
print(f"Python: {sys.version}")
sys.stdout.flush()

# Step 1: dotenv
try:
    from dotenv import load_dotenv
    import os
    load_dotenv('/a0/usr/secrets.env')
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    uid = os.getenv('TELEGRAM_OWNER_USER_ID') or os.getenv('TELEGRAM_ALLOWED_USERS')
    print(f"[OK] dotenv - TOKEN present: {bool(token)}, USER_ID: {uid}")
except Exception as e:
    print(f"[FAIL] dotenv: {e}")
    traceback.print_exc()
sys.stdout.flush()

# Step 2: telegram library
try:
    from telegram import Update
    from telegram.ext import ApplicationBuilder
    import telegram
    print(f"[OK] python-telegram-bot v{telegram.__version__}")
except Exception as e:
    print(f"[FAIL] telegram: {e}")
    traceback.print_exc()
sys.stdout.flush()

# Step 3: agent import
try:
    from agent import Agent, AgentConfig
    print("[OK] agent import - Agent and AgentConfig found")
except Exception as e:
    print(f"[FAIL] agent import: {e}")
    traceback.print_exc()
sys.stdout.flush()

# Step 4: Try instantiating AgentConfig
try:
    config = AgentConfig(mcp_servers="")
    print(f"[OK] AgentConfig instantiated: {config}")
except Exception as e:
    print(f"[FAIL] AgentConfig(): {e}")
    traceback.print_exc()
sys.stdout.flush()

print("=== DIAGNOSTIC COMPLETE ===")
