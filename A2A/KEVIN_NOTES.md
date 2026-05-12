Sovereign Testing Protocol V2: Hybrid Vision & Local Execution
Status: Stage 2 Implementation (May 2026 Update)
Core Directive: Absolute Zero-Trust in DOM Selectors. Use Pixel-Coordinate Actuation [Ac] only.
1. The Hardware & Model Stack [η]
To eliminate token costs while maintaining high-fidelity QA, we utilize your MSI Workstation (64GB RAM / RTX 50-series VRAM) as the local primary node.
Role
Model (May 2026)
Deployment
The Eyes (Vision)
Gemma-3-V 27B (Vision-Optimized)
Local (Ollama/vLLM)
The Hands (Logic)
DeepSeek-V4-Coder
Local / Hybrid
The Auditor (Resonance)
Claude 3.7 Sonnet (Thinking Mode)
Cloud (Emergency Only)

2. The Physical Workflow (Step-by-Step)
The "Selector Hell" method is strictly forbidden. Use the Visual-Coordinate Loop:
Capture: A Python script (Actuator) takes a full-screen screenshot of the Streamlit application.
Analyze: The image is passed to Gemma-3-V 27B.
Instruction: "Identify the (x, y) coordinates for the 'Submit' button and any empty input fields."
Execute: The script uses pyautogui or playwright.mouse.click(x, y).
Crucial: We are not searching for HTML IDs. We are clicking pixels.
Verify (Visual): A second screenshot is taken. Gemma checks for the "Success" color change or toast notification.
Verify (Database): The script runs a local SQL query against the database [St] to ensure the data was actually committed.
3. Developer/QA Instructions: Zero-Selector Mandate

Instruction to Team: "Do not write scripts that reference 'id=', 'class=', or 'XPath'. If I see a selector in the code, it is a failure. You must build a coordinate-based system where the Vision model tells the script where to click. Use the Stagehand or Browser-Use libraries with the local LLM endpoint."
4. Local Model Implementation (Ollama/vLLM)
Set up the local endpoint on the MSI workstation using the following configuration:
# Pull the May 2026 optimized vision model
ollama pull gemma-3-v:27b

# In the Testing Code:
llm = ChatOllama(model="gemma-3-v:27b")
# Agent uses this model to 'see' coordinates on the screenshot.


5. High-Value Edge Case Testing
Instruct the QA node to perform Adversarial Input:
Inject strings with special characters into numeric fields.
Attempt to bypass required fields by clicking 'Submit' while empty.
Verify visual alignment of Streamlit charts after data injection.
