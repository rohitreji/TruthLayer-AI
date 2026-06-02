import json
import re
import google.generativeai as genai
from typing import List, Dict, Any

def extract_claims(text: str, api_key: str, max_claims: int = 10, model_name: str = "gemini-2.5-flash") -> List[Dict[str, str]]:
    if not api_key:
        raise ValueError("Gemini API key is required for claim extraction.")
        
    if not text.strip():
        return []
        
    genai.configure(api_key=api_key)
    
    generation_config = {
        "temperature": 0.1,
        "top_p": 0.95,
        "max_output_tokens": 4096,
        "response_mime_type": "application/json"
    }
    
    prompt = f"""You are a high-precision fact-checking assistant. Your task is to extract up to {max_claims} clear, factual claims from the provided text that can be validated or disproven via standard web search.

Focus ONLY on specific factual claims belonging to these categories:
1. "statistic" (numerical measurements, rankings, quantities)
2. "date" (historical assertions, specific milestones, chronological facts)
3. "percentage" (proportions, rates, growth figures)
4. "financial" (monetary values, revenue, costs, funding amounts)
5. "technical" (scientific claims, specifications, software versions, system configurations)

Strictly ignore:
- Subjective statements or opinions (e.g. "We provide the best customer experience")
- Vague statements (e.g. "Our software is incredibly fast")
- Empty marketing language or hyperbole (e.g. "The revolutionary design represents a paradigm shift")
- Purely forward-looking predictions (e.g. "We will double our revenue next year") unless they specify a historical projection that has already elapsed.

IMPORTANT REQUIREMENT: Make each claim a self-contained, standalone sentence. Replace relative pronouns (like "the company", "it", "they", "we", "he") with the actual names of the entities they refer to (e.g., instead of "It achieved 80% growth", write "TruthLayer AI achieved 80% growth"). This ensures the claims are optimized for web search queries.

You MUST return a JSON array containing objects with exactly these keys:
- "claim": The self-contained, search-friendly factual assertion.
- "type": One of the five categories: "statistic", "date", "percentage", "financial", "technical".

Example output format:
[
  {{
    "claim": "Tesla delivered 484,507 electric vehicles in the fourth quarter of 2023.",
    "type": "statistic"
  }}
]

Text to analyze:
---
{text}
---
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
            
        claims = json.loads(response_text)
        
        if not isinstance(claims, list):
            if isinstance(claims, dict) and "claims" in claims:
                claims = claims["claims"]
            else:
                return []
                
        valid_claims = []
        valid_types = {"statistic", "date", "percentage", "financial", "technical"}
        
        for item in claims:
            if isinstance(item, dict) and "claim" in item and "type" in item:
                claim_text = str(item["claim"]).strip()
                claim_type = str(item["type"]).lower().strip()
                
                if claim_type not in valid_types:
                    claim_type = "statistic"
                    
                if claim_text:
                    valid_claims.append({
                        "claim": claim_text,
                        "type": claim_type
                    })
                    
        return valid_claims[:max_claims]
        
    except Exception as e:
        raise RuntimeError(f"Error extracting claims with Gemini API: {str(e)}")
