import fitz

def create_kaggle_test_pdf():
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    
    content = """TruthLayer AI – Test Verification Document

Kaggle Platform Overview & Factual Audit Data

Kaggle is the world's largest data science and machine learning community, offering datasets, notebooks, GPU resources, and competitive challenges. Below is a compiled list of factual statistics, dates, and historical details for validation testing:

1. Founders & Launch Date:
Kaggle was founded in April 2010 by Anthony Goldbloom and Jeremy Howard to provide a platform for data science competitions.

2. Series A Funding:
In November 2011, Kaggle raised 11 million dollars in Series A funding led by Index Ventures.

3. The Google Acquisition:
Kaggle was acquired by Google in March 2017 to expand Google Cloud's developer ecosystem.

4. Microsoft Rumors:
Kaggle was acquired by Microsoft in December 2021 for 500 million dollars.

5. Registered Users:
Kaggle announced that its platform had reached over 15 million registered users in 2023.

6. Leadership:
The current CEO of Kaggle is Satya Nadella, who succeeded the original founders.

---
This document contains a mix of TRUE, INACCURATE, and FALSE claims.
- Claims 1, 3, and 5 are historically TRUE.
- Claim 2 is INACCURATE (Series A funding was actually led by Khosla Ventures, not Index Ventures).
- Claims 4 and 6 are completely FALSE (Kaggle belongs to Google, and Satya Nadella is the CEO of Microsoft).
"""
    
    title_rect = fitz.Rect(50, 50, 545, 100)
    page.insert_textbox(
        title_rect, 
        "TruthLayer AI - Kaggle Fact Checking Test PDF", 
        fontsize=16, 
        fontname="Helvetica-Bold", 
        color=(0.388, 0.4, 0.945)
    )
    
    body_rect = fitz.Rect(50, 110, 545, 780)
    page.insert_textbox(
        body_rect,
        content,
        fontsize=11,
        fontname="Helvetica",
        lineheight=1.4
    )
    
    pdf_filename = "kaggle_test_report.pdf"
    doc.save(pdf_filename)
    doc.close()
    print(f"Success: Created '{pdf_filename}' test PDF file!")

if __name__ == "__main__":
    create_kaggle_test_pdf()
