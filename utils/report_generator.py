import pandas as pd
from typing import List, Dict, Any

def generate_csv_report(verification_results: List[Dict[str, Any]]) -> str:
    rows = []
    
    for item in verification_results:
        evidence_list = item.get("evidence", [])
        formatted_sources = []
        for i, ev in enumerate(evidence_list, 1):
            title = ev.get("title", "Source").replace(",", " ")
            url = ev.get("url", "")
            formatted_sources.append(f"[{i}] {title}: {url}")
            
        sources_str = " | ".join(formatted_sources) if formatted_sources else "No web sources found."
        
        row = {
            "Claim": item.get("claim", ""),
            "Claim Type": item.get("type", "statistic").capitalize(),
            "Status": item.get("status", "FALSE"),
            "Confidence (%)": item.get("confidence", 0),
            "Correct Fact": item.get("correct_fact", ""),
            "Sources": sources_str
        }
        rows.append(row)
        
    df = pd.DataFrame(rows)
    return df.to_csv(index=False, encoding="utf-8")
