from fastapi import APIRouter, HTTPException
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import json
import re

router = APIRouter()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

async def resource_optimizer() -> dict:
    """
    Uses Gemini LLM to simulate warehouse resource optimization.

    This function invokes the Gemini language model to randomly estimate:
    - Number of forklifts (between 1 to 10)
    - Number of trucks (between 1 to 10)
    - Number of labourers (between 20 to 100)

    Returns:
        dict: A dictionary with randomly generated resource allocations:
              Example: {"forklifts": 7, "trucks": 3, "labour": 56}

    Raises:
        Exception: If the LLM fails to respond or response is invalid.
    """
    prompt = (
        "Generate a JSON object with random realistic values for warehouse resources. "
        "The object should contain:\n"
        "- 'forklifts': an integer between 1 and 10\n"
        "- 'trucks': an integer between 1 and 10\n"
        "- 'labour': an integer between 20 and 100\n\n"
        "Respond only with the JSON object."
    )

    response = await llm.ainvoke(prompt)
    content = response.content.strip()

    # Remove markdown code block syntax if present
    if content.startswith("```"):
        content = re.sub(r"```(?:json)?", "", content)
        content = content.replace("```", "").strip()

    try:
        return json.loads(content)
    except Exception:
        raise Exception(f"Invalid response from LLM after cleanup: {content}")

@router.get("/resource_optimizer")
async def resource_optimizer_route():
    try:
        return await resource_optimizer()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
