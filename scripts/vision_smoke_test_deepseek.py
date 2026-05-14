"""
Adapted Smoke Test for Turtle-DB Streamlit App (DeepSeek API - No Vision)
==========================================================================
Executed by: Agent Zero (autonomous)
Validates: browser-use + DeepSeek can navigate, interact, screenshot via DOM
Note: DeepSeek API (deepseek-v4-pro) does NOT support image/vision input.
browser-use falls back to DOM/accessibility tree text for navigation.
Still captures screenshots via Playwright for visual evidence.
"""
import asyncio
import os
import sys
import shutil
from datetime import datetime
from pathlib import Path

WORKDIR = Path("/a0/usr/workdir")
TMPDIR = WORKDIR / "tmp"
TMPDIR.mkdir(parents=True, exist_ok=True)


def get_llm():
    """Configure browser-use to use DeepSeek API as the LLM provider."""
    from langchain_openai import ChatOpenAI
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable not set")
    
    base_url = os.getenv("OPENAI_API_BASE", "https://api.deepseek.com/v1")
    # Use text-only model - deepseek-v4-pro is the only available model that works
    model = "deepseek-v4-pro"
    
    print(f"  LLM Config: base_url={base_url}, model={model} (text-only, use_vision=False)")
    
    return ChatOpenAI(
        base_url=base_url,
        api_key=api_key,
        model=model,
        temperature=0.1,
        timeout=120
    )


async def take_screenshot(browser, path: Path) -> bool:
    """Take an explicit screenshot using Playwright browser directly."""
    try:
        # get_playwright_browser() returns a coroutine in browser_use 0.1.40
        pw_browser = await browser.get_playwright_browser()
        if pw_browser:
            pages = []
            for context in pw_browser.contexts:
                pages.extend(context.pages)
            if pages:
                page = pages[0]
                await page.screenshot(path=str(path), full_page=True)
                print(f"  Screenshot saved: {path}")
                return True
        print("  Could not access Playwright page for screenshot")
        return False
    except Exception as e:
        print(f"  Screenshot failed: {e}")
        return False


async def smoke_test():
    """Run the adapted smoke test: navigate Observations page, screenshot, verify"""
    from browser_use import Agent, Browser, BrowserConfig
    
    print(f"\n{'='*60}")
    print(f"BROWSER-USE SMOKE TEST (DeepSeek) STARTED: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")
    
    task = """
    You are performing a DOM-based smoke test of a turtle egg tracking web application.
    Follow these steps EXACTLY in order:

    1. Navigate to http://localhost:8501/Observations?active_case_id=I2026051314148
    2. Wait for the page to fully load (look for text like 'Observations', 'Property Matrix', or data tables)
    3. Verify the Observations page loaded successfully - check for egg stage indicators (S0-S5), nest ID, or property matrix
    4. Report what you see on the page

    REPORT exactly what you did and whether each step succeeded.
    """
    
    result = None
    browser = None
    agent = None
    
    try:
        browser = Browser(config=BrowserConfig(headless=True))
        llm = get_llm()
        
        print("  Creating Agent with DeepSeek LLM (use_vision=False for text-based DOM nav)...")
        agent = Agent(
            task=task,
            llm=llm,
            browser=browser,
            use_vision=False  # DeepSeek API does NOT support image inputs
        )
        
        print("  Running agent (DOM-based navigation)...")
        result = await agent.run()
        
        print(f"\n{'='*60}")
        print(f"AGENT RESULT: {str(result)[:500]}")
        print(f"{'='*60}")
        
        # Save result text
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        result_path = TMPDIR / f"vision_smoke_deepseek_{timestamp}.txt"
        with open(result_path, "w") as f:
            f.write(str(result))
        print(f"\n  Result saved to: {result_path}")
        
        # Take explicit screenshot for visual evidence (no AI analysis of image)
        screenshot_path = TMPDIR / "vision_smoke_deepseek.png"
        await take_screenshot(browser, screenshot_path)
        
        print(f"\n✅ Browser-use smoke test (DeepSeek DOM) completed.")
        
    except Exception as e:
        print(f"\n❌ BROWSER-USE SMOKE TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        result = f"ERROR: {e}"
        
    finally:
        try:
            if browser:
                await browser.close()
        except:
            pass
    
    return str(result)


if __name__ == "__main__":
    asyncio.run(smoke_test())
