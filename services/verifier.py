import json
import re
import google.generativeai as genai
from typing import Dict, List, Any

def verify_claim(claim: str, evidence: List[Dict[str, str]], api_key: str, model_name: str = "gemini-2.5-flash") -> Dict[str, Any]:
    if not api_key:
        raise ValueError("Gemini API key is required for claim verification.")
        
    if not evidence:
        return {
            "status": "FALSE",
            "reason": "No live web search results could be retrieved to verify this claim.",
            "correct_fact": "No search evidence available.",
            "confidence": 10
        }
        
    evidence_items = []
    for i, item in enumerate(evidence, 1):
        snippet = item.get("snippet", "").strip()
        title = item.get("title", "").strip()
        url = item.get("url", "").strip()
        source = item.get("source", "Web")
        evidence_items.append(
            f"[{i}] Source ({source}): {title}\nURL: {url}\nContent: {snippet}\n"
        )
        
    evidence_text = "\n".join(evidence_items)
    
    genai.configure(api_key=api_key)
    
    generation_config = {
        "temperature": 0.0,
        "top_p": 0.95,
        "max_output_tokens": 1024,
        "response_mime_type": "application/json"
    }
    
    prompt = f"""You are a professional fact-checker specializing in high-precision audit verification. Your task is to compare the provided factual CLAIM against the LIVE WEB EVIDENCE collected below.

Categorize the claim into one of these three states:
1. "VERIFIED": The live web evidence explicitly and accurately supports the claim without any significant discrepancies.
2. "INACCURATE": The claim is partially correct, but contains errors regarding numbers, dates, percentages, names, or general context (e.g. claiming "50% growth" when the evidence states "40% growth").
3. "FALSE": The claim is fundamentally incorrect, contradicted by the live web evidence, or fabricated.

CLAIM:
"{claim}"

LIVE WEB EVIDENCE:
---
{evidence_text}
---

INSTRUCTIONS:
- Analyze numbers, statistics, percentages, dates, and names with absolute precision.
- If there is conflicting information, prioritize highly authoritative and recent sources from the evidence list.
- In "correct_fact", write the specific, corrected factual statement if the status is INACCURATE or FALSE. If the status is VERIFIED, set "correct_fact" to empty.
- In "reason", write a concise, highly professional explanation of your decision. Specify WHICH sources (e.g., "[1]", "[2]") support or contradict the claim. Explain discrepancies in numbers or dates clearly.
- In "confidence", output a confidence score from 0 to 100 indicating the strength and alignment of the evidence.

You MUST return a strictly valid JSON object with exactly these keys:
- "status": Must be one of "VERIFIED", "INACCURATE", or "FALSE".
- "reason": Clear, professional reasoning.
- "correct_fact": The corrected factual statement or empty string.
- "confidence": Integer between 0 and 100.

Do not include any chat prefix, suffix, or markdown code blocks. Return ONLY raw JSON.
"""

    try:
        model = genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        if response_text.startswith("```"):
            response_text = re.sub(r"^```(?:json)?\n", "", response_text)
            response_text = re.sub(r"\n```$", "", response_text)
            response_text = response_text.strip()
            
        try:
            parsed_result = json.loads(response_text)
            status = str(parsed_result.get("status", "FALSE")).upper().strip()
            if status not in {"VERIFIED", "INACCURATE", "FALSE"}:
                status = "FALSE"
                
            return {
                "status": status,
                "reason": str(parsed_result.get("reason", "")).strip(),
                "correct_fact": str(parsed_result.get("correct_fact", "")).strip(),
                "confidence": int(parsed_result.get("confidence", 50))
            }
        except json.JSONDecodeError as json_err:
            status = "FALSE"
            status_match = re.search(r'"status"\s*:\s*"([^"]+)"', response_text, re.IGNORECASE)
            if status_match:
                status = status_match.group(1).upper().strip()
                
            confidence = 50
            confidence_match = re.search(r'"confidence"\s*:\s*(\d+)', response_text)
            if confidence_match:
                confidence = int(confidence_match.group(1))
                
            reason = ""
            reason_match = re.search(r'"reason"\s*:\s*"(.*?)"\s*(?:,|\n\s*"|(?:\s*\}))', response_text, re.DOTALL)
            if reason_match:
                reason = reason_match.group(1).strip()
            else:
                reason_match = re.search(r'"reason"\s*:\s*"(.*)"', response_text)
                if reason_match:
                    reason = reason_match.group(1).strip()
                    
            correct_fact = ""
            correct_match = re.search(r'"correct_fact"\s*:\s*"(.*?)"\s*(?:,|\n\s*"|(?:\s*\}))', response_text, re.DOTALL)
            if correct_match:
                correct_fact = correct_match.group(1).strip()
            else:
                correct_match = re.search(r'"correct_fact"\s*:\s*"(.*)"', response_text)
                if correct_match:
                    correct_fact = correct_match.group(1).strip()
            
            if status not in {"VERIFIED", "INACCURATE", "FALSE"}:
                status = "FALSE"
                
            if reason:
                return {
                    "status": status,
                    "reason": reason,
                    "correct_fact": correct_fact,
                    "confidence": confidence
                }
            else:
                raise json_err
                
    except Exception as e:
        return {
            "status": "FALSE",
            "reason": f"AI Verification Engine error: {str(e)}",
            "correct_fact": "N/A",
            "confidence": 0
        }
