# my_agents.py

import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI
from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel, set_tracing_disabled
from pydantic import BaseModel
from typing import Dict, List

# Load environment variables
load_dotenv(override=True)

# Disable tracing if you don't have OPENAI_API_KEY (avoids errors)
set_tracing_disabled(True)

# Configure Gemini client
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
gemini_api_key = os.getenv("GEMINI_API_KEY", "")
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=gemini_api_key)

# Create a Gemini-compatible model for agents
gemini_model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=gemini_client
)

# Define a structured output class for email drafts
class EmailDraft(BaseModel):
    subject: str
    body: str

def save_email_to_file(subject: str, body: str) -> Dict[str, str]:
    """Plain Python function to save the generated email to file."""
    try:
        filename = "generated_email.txt"
        full_email = f"Subject: {subject}\n\n{body}"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(full_email)
        return {"status": "success", "filename": filename}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Tool wrapper for the Agent framework
@function_tool
def save_email(subject: str, body: str) -> Dict[str, str]:
    """Gemini tool wrapper that calls the real save function."""
    return save_email_to_file(subject, body)


# ✅ Updated workflow – takes parameters from Streamlit (no input())
async def run_structured_output_workflow(tone: str, target: str, linkedin_url: str, product_details: str):
    """
    Generate multiple email drafts using Gemini model.
    """

    # Build instructions for Gemini
    instructions = f"""
    You are a cold email assistant.
    Tone: {tone}
    Target Audience: {target}
    LinkedIn URL: {linkedin_url}
    Product Details: {product_details}

    Generate 5 short professional cold sales emails in JSON format:
    [
      {{"subject": "...", "body": "..."}} ,
      ...
    ]
    Each email should be concise, polite, and professional, and include a call to action.
    """

    # Create the agent
    sales_agent = Agent(
        name="Structured Sales Agent",
        instructions=instructions,
        model=gemini_model,
        output_type=List[EmailDraft],
        tools=[save_email]
    )

    # Run the agent
    try:
        result = await Runner.run(sales_agent, "Generate cold emails")
        return result.final_output  # List[EmailDraft]
    except Exception as e:
        print(f"Error during email generation: {e}")
        return []
