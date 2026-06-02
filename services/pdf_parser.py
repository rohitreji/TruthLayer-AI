import fitz
from typing import Dict, Any

def extract_text_from_pdf(pdf_file) -> Dict[str, Any]:
    result = {
        "success": False,
        "text": "",
        "page_count": 0,
        "metadata": {},
        "error": None,
        "is_scanned": False
    }
    
    try:
        pdf_bytes = pdf_file.read()
        pdf_file.seek(0)
        
        if not pdf_bytes:
            result["error"] = "The uploaded file is empty (0 bytes)."
            return result
            
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        result["page_count"] = len(doc)
        result["metadata"] = dict(doc.metadata)
        
        if result["page_count"] == 0:
            result["error"] = "This PDF has no pages."
            return result
            
        full_text = []
        for page_num in range(result["page_count"]):
            page = doc[page_num]
            text = page.get_text()
            full_text.append(text)
            
        compiled_text = "\n".join(full_text).strip()
        result["text"] = compiled_text
        
        if len(compiled_text) < 50 and result["page_count"] > 0:
            result["is_scanned"] = True
            result["error"] = "Minimal text extracted. This PDF might be scanned/image-only and requires OCR."
        else:
            result["success"] = True
            
        doc.close()
        
    except Exception as e:
        result["error"] = f"Failed to parse PDF: {str(e)}"
        
    return result
