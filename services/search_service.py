import time
import requests
from typing import List, Dict, Any

try:
    from duckduckgo_search import DDGS
    DDG_AVAILABLE = True
except ImportError:
    DDG_AVAILABLE = False

def search_duckduckgo(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    if not DDG_AVAILABLE:
        raise ImportError("duckduckgo_search library is not installed.")
        
    results = []
    try:
        with DDGS() as ddgs:
            ddg_results = list(ddgs.text(query, max_results=max_results))
            for r in ddg_results:
                title = r.get("title", "")
                snippet = r.get("body", r.get("snippet", ""))
                url = r.get("href", r.get("url", ""))
                
                if title or snippet or url:
                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "url": url,
                        "source": "DuckDuckGo"
                    })
    except Exception as e:
        raise RuntimeError(f"DuckDuckGo search error: {str(e)}")
        
    return results

def search_tavily(query: str, api_key: str, max_results: int = 5) -> List[Dict[str, str]]:
    if not api_key:
        raise ValueError("Tavily API key is missing.")
        
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "max_results": max_results,
        "include_answer": False,
        "include_raw_content": False
    }
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        tavily_results = data.get("results", [])
        for r in tavily_results:
            title = r.get("title", "")
            snippet = r.get("content", r.get("snippet", ""))
            link = r.get("url", "")
            
            if title or snippet or link:
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "url": link,
                    "source": "Tavily"
                })
        return results
    except Exception as e:
        raise RuntimeError(f"Tavily search API error: {str(e)}")

def search_claim(claim: str, tavily_api_key: str = None, max_results: int = 5) -> Dict[str, Any]:
    search_report = {
        "success": False,
        "results": [],
        "error": None,
        "engine_used": "None"
    }
    
    if not claim.strip():
        search_report["error"] = "Empty search query."
        return search_report

    if DDG_AVAILABLE:
        try:
            results = search_duckduckgo(claim, max_results=max_results)
            if results:
                search_report["success"] = True
                search_report["results"] = results
                search_report["engine_used"] = "DuckDuckGo"
                return search_report
        except Exception as ddg_err:
            search_report["error"] = f"DuckDuckGo failed: {str(ddg_err)}"

    if tavily_api_key:
        try:
            results = search_tavily(claim, tavily_api_key, max_results=max_results)
            if results:
                search_report["success"] = True
                search_report["results"] = results
                search_report["engine_used"] = "Tavily"
                search_report["error"] = None
                return search_report
        except Exception as tav_err:
            combined_error = f"{search_report['error']} | Tavily fallback failed: {str(tav_err)}"
            search_report["error"] = combined_error
    else:
        if not search_report["success"]:
            search_report["error"] = (
                f"{search_report['error']} (Tavily key not configured for fallback)"
            )
            
    return search_report
