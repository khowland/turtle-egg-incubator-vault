import os
import logging
import httpx
import asyncio
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import BadRequest
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(message)s',
    level=logging.INFO
)
log = logging.getLogger("telegram_bot")

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OWNER_ID = int(os.getenv("TELEGRAM_OWNER_USER_ID", "0"))
A0_API_BASE = "http://127.0.0.1:80"
DEFAULT_CONTEXT = "telegram_session_v2"

# Global state for toggles
THINKING_MODE = False

def is_a0_alive():
    try:
        with httpx.Client() as client:
            resp = client.get(f"{A0_API_BASE}/api/health", timeout=2.0)
            return resp.status_code == 200
    except:
        return False

async def a0_poll_response(ctxid: str, update_msg=None, timeout: int = 300):
    log.info(f"Polling A0 for response in context {ctxid} (Thinking: {THINKING_MODE})...")
    start_time = time.time()
    last_status = ""
    last_heartbeat = time.time()
    
    while time.time() - start_time < timeout:
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(f"{A0_API_BASE}/api/poll", json={"context": ctxid})
                resp.raise_for_status()
                data = resp.json()
                
                # Heartbeat every 30s if no status change
                if time.time() - last_heartbeat > 30:
                    log.info(f"Still polling for {ctxid}...")
                    last_heartbeat = time.time()

                # Handle Snapshot V1 format
                progress = data.get("log_progress", "")
                is_active = data.get("log_progress_active", False)
                
                # Check for intermediate status updates
                if THINKING_MODE and update_msg:
                    # Try to get more detailed status from the latest log entry
                    logs = data.get("logs", [])
                    status_text = progress
                    if logs:
                        latest_log = logs[-1]
                        # Use heading if available, otherwise fallback to progress string
                        status_text = latest_log.get("heading") or progress
                    
                    if status_text and status_text != last_status:
                        try:
                            # Clean up and truncate status for Telegram
                            display_text = (status_text[:200] + '...') if len(status_text) > 200 else status_text
                            await update_msg.edit_text(f"💭 {display_text}")
                            last_status = status_text
                        except BadRequest: # Message might not have changed or already deleted
                            pass

                # Detect completion: "Waiting for input" means agent is done
                # Also fallback to "done" and "message" for backward compatibility
                if (progress == "Waiting for input" and not is_active) or (data.get("done") and data.get("message")):
                    log.info("A0 processing complete.")
                    
                    if data.get("done") and data.get("message"):
                        return data.get("message")
                        
                    # Extract last response from logs if not provided in "message"
                    logs = data.get("logs", [])
                    for item in reversed(logs):
                        if item.get("type") == "response":
                            # Handle both tool_args format and direct content
                            resp_text = item.get("tool_args", {}).get("text") or item.get("content")
                            if resp_text: return resp_text
                            
                    return "Done (no explicit response found)."
                
                await asyncio.sleep(1.5)
            except Exception as e:
                log.error(f"Error polling A0: {e}")
                await asyncio.sleep(5)
    return "A0 timed out waiting for a response."

async def a0_send_message(text: str, ctxid: str = DEFAULT_CONTEXT):
    payload = {
        "text": text,
        "context": ctxid
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{A0_API_BASE}/api/message_async", json=payload, timeout=30.0)
        resp.raise_for_status()
        return resp.json()

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        log.warning(f"Unauthorized access from user {update.effective_user.id} (Owner: {OWNER_ID})")
        return
    await update.message.reply_text(
        "🐢 Native Agent Zero is ready.\n\n"
        "Commands:\n"
        "/status - Check API health\n"
        "/thinking - Toggle live thinking process\n"
        "Send any message to start relaying."
    )

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        log.warning(f"Unauthorized access from user {update.effective_user.id} (Owner: {OWNER_ID})")
        return
    alive = is_a0_alive()
    await update.message.reply_text(
        f"{'✅ A0 API is UP' if alive else '❌ A0 API is DOWN'} | Thinking Mode: {'ON' if THINKING_MODE else 'OFF'}"
    )

async def cmd_toggle_thinking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global THINKING_MODE
    if update.effective_user.id != OWNER_ID:
        log.warning(f"Unauthorized access from user {update.effective_user.id} (Owner: {OWNER_ID})")
        return
    THINKING_MODE = not THINKING_MODE
    await update.message.reply_text(f"💭 Thinking mode is now {'ENABLED' if THINKING_MODE else 'DISABLED'}.")

async def cmd_toggle_brain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        log.warning(f"Unauthorized access from user {update.effective_user.id} (Owner: {OWNER_ID})")
        return
    # This logic assumes you have a way to update the .env or session model
    # For now, we will simulate the toggle and report it.
    current_model = os.getenv("CHAT_MODEL", "deepseek-v4-pro")
    new_model = "claude-3-5-sonnet" if "deepseek" in current_model else "deepseek-v4-pro"
    
    # Update .env file natively
    try:
        with open(".env", "r") as f:
            lines = f.readlines()
        with open(".env", "w") as f:
            for line in lines:
                if line.startswith("CHAT_MODEL="):
                    f.write(f"CHAT_MODEL={new_model}\n")
                else:
                    f.write(line)
        os.environ["CHAT_MODEL"] = new_model
        await update.message.reply_text(f"🧠 Brain swapped! Orchestrator is now using: **{new_model}**")
    except Exception as e:
        await update.message.reply_text(f"❌ Error swapping brain: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    if update.effective_user.id != OWNER_ID:
        log.warning(f"Unauthorized access from user {update.effective_user.id} (Owner: {OWNER_ID})")
        return

    text = update.message.text
    log.info(f"RECEIVED: {text}")
    
    if not is_a0_alive():
        await update.message.reply_text("⚠️ Agent Zero is still starting up.")
        return

    progress_msg = await update.message.reply_text("⏳ Sending to Agent Zero...")
    
    try:
        # Step 1: Send message asynchronously
        init_response = await a0_send_message(text)
        ctxid = init_response.get("context", DEFAULT_CONTEXT)
        
        # Step 2: Poll for the final answer
        if THINKING_MODE:
            await progress_msg.edit_text("💭 Thinking: Initializing...")
            
        final_answer = await a0_poll_response(ctxid, update_msg=progress_msg if THINKING_MODE else None)
        
        # Step 3: Cleanup and send final answer
        try:
            await progress_msg.delete()
        except:
            pass

        if len(final_answer) > 4000:
            for i in range(0, len(final_answer), 4000):
                await update.message.reply_text(final_answer[i:i+4000])
        else:
            await update.message.reply_text(f"🤖 {final_answer}")
            
    except Exception as e:
        log.error(f"Relay error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error talking to A0: {e}")

if __name__ == '__main__':
    log.info(f"Starting Telegram Bridge | Owner: {OWNER_ID}")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler('start', cmd_start))
    app.add_handler(CommandHandler('status', cmd_status))
    app.add_handler(CommandHandler('thinking', cmd_toggle_thinking))
    app.add_handler(CommandHandler('brain', cmd_toggle_brain))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(drop_pending_updates=True)
