"""
Vision Smoke Test for Turtle-DB Streamlit App
===============================================
Executed by: MSI Stealth Agent Zero (autonomous)
Validates: browser-use + Gemma 4 can navigate, login, fill form, click, save, verify
"""
import asyncio
import sys
from datetime import datetime
from pathlib import Path

WORKDIR = Path("/a0/usr/workdir")
TMPDIR = WORKDIR / "tmp"
TMPDIR.mkdir(parents=True, exist_ok=True)


async def smoke_test():
    """Run the full smoke test: login → new intake → save → verify"""
    from browser_use import Agent, Browser
    
    print(f"\n{'='*60}")
    print(f"SMOKE TEST STARTED: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    browser = Browser(headless=False)  # Visible for debugging
    
    task = """
    You are testing a turtle egg tracking web application.
    Follow these steps EXACTLY in order:
    
    1. Navigate to http://localhost:8501
    2. Wait for the page to fully load
    3. Log in with:
       - Email: admin@turtledb.com
       - Password: admin123
    4. Verify the Dashboard page loaded. Look for text 'Dashboard' or 'Welcome'.
    5. Find and click the 'New Intake' button (may be in sidebar or main area)
    6. On the New Intake form:
       - Select Species: 'Loggerhead'
       - Enter Mass: 25.5
       - Enter Nest Size: 1
       - Enter Nest ID: VISION-TEST-A
       - Enter Clutch: 1
    7. Click the SAVE button
    8. Wait for and verify a success message appears (toast, notification, or green text)
    9. Take a screenshot and save it
    
    REPORT exactly what you did and whether each step succeeded.
    """
    
    try:
        agent = Agent(
            task=task,
            llm="ollama/gemma4:9b",
            browser=browser
        )
        result = await agent.run()
        
        print(f"\n{'='*60}")
        print(f"AGENT RESULT: {str(result)[:500]}")
        print(f"{'='*60}")
        
        # Save result to file
        result_path = TMPDIR / f"smoke_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(result_path, "w") as f:
            f.write(str(result))
        
        print(f"\n✅ Smoke test completed. Result saved to: {result_path}")
        return str(result)
        
    except Exception as e:
        print(f"\n❌ SMOKE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return f"ERROR: {e}"


if __name__ == "__main__":
    asyncio.run(smoke_test())
