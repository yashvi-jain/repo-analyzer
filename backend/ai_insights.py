import os
import json
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from groq import Groq

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-2.5-flash-lite"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env")
    
groq_client = Groq(api_key=GROQ_API_KEY)

GROQ_MODEL = "llama-3.3-70b-versatile"

MAX_CHARS = 15000

def _read_file(file_path: str) -> str:
    """
    Read source code safely.
    Truncate very large files to avoid excessive token usage.
    """

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            source = f.read()

        if len(source) > MAX_CHARS:
            source = (
                source[:MAX_CHARS]
                + "\n\n... [TRUNCATED DUE TO FILE SIZE] ..."
            )

        return source

    except Exception:
        return ""


def generate_ai_insights(repo_path: str, files: list):
    """
    Generate AI explanations for important files.
    """

    prompt = """
You are a senior software engineer performing a code review.

You will receive source files and static analysis metrics.

For each file:

1. Explain the engineering issues you observe in the code.
2. Relate those issues to the provided metrics (complexity, maintainability, risk, duplication, hotspot, dead code).
3. Mention the likely root causes behind the high scores.
4. Incase of duplicate %, also show what the possible duplicates are.
5. Note that potentially unused functions are simply those that have not been called in the same file- they may not be dead code hence dont emphasize on them.
6. Give actionable refactoring suggestions, with reference to the source code.

Rules:
- Keep the explanation under 100 words.
- Do NOT simply repeat the metric values.
- Base your reasoning primarily on the source code.
- If the metrics look reasonable, explicitly say so.
- Return ONLY valid JSON.
- Generate the severity as low/medium/high.

Output format:

[
    {
        "file":"...",

        "severity":"...",

        "summary":"...",

        "root_causes":[
            "...",
            "...",
            "..."
        ],

        "suggestions":[
            "...",
            "...",
            "..."
        ]
    }
]

Do NOT wrap the JSON in markdown.
"""

    payload = ""

    for file in files:

        absolute_path = Path(repo_path) / file["file"]

        source = _read_file(absolute_path)

        payload += f"""

==========================
FILE: {file["file"]}

Language:
{file["language"]}

Complexity:
{file["complexity"]}

Maintainability:
{file["maintainability"]}

Risk:
{file["risk"]}

Duplicate:
{file["duplicate"]}

Hotspot:
{file["hotspot"]}

Potentially Unused Functions:
{file["dead_code"]}

Source Code:

{source}

"""

    full_prompt = prompt + payload

    fallback_used = False

    try:

        text = _generate_with_gemini(full_prompt).strip()

    except Exception as e:

        print(f"Gemini failed: {e}")
        print("Falling back to Groq...")

        fallback_used = True

        try:
            text = _generate_with_groq(full_prompt).strip()

        except Exception as e:

            return {
                "provider": None,
                "fallback": True,
                "insights": [],
                "error": str(e),
            }

    if text.startswith("```json"):
        text = text[len("```json"):]

    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    try:

        parsed = json.loads(text)

        return {
            "provider": "groq" if fallback_used else "gemini",
            "fallback": fallback_used,
            "insights": parsed,
            "error": None,
        }

    except Exception:

        return {
            "provider": "groq" if fallback_used else "gemini",
            "fallback": fallback_used,
            "insights": [],
            "error": text,
        }

def _generate_with_gemini(prompt):

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
    )

    return response.text


def _generate_with_groq(prompt):

    response = groq_client.chat.completions.create(

        model=GROQ_MODEL,

        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],

        temperature=0.2,
    )

    return response.choices[0].message.content