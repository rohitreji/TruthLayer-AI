import streamlit as st
import time
import os
from io import BytesIO

from services.pdf_parser import extract_text_from_pdf
from services.claim_extractor import extract_claims
from services.search_service import search_claim
from services.verifier import verify_claim
from utils.report_generator import generate_csv_report
from utils.helpers import (
    inject_custom_css,
    render_metric_cards,
    get_status_badge_html,
    get_type_icon
)

st.set_page_config(
    page_title="TruthLayer AI – Automated Fact Checking",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()

if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = ""
if "pdf_metadata" not in st.session_state:
    st.session_state.pdf_metadata = {}
if "claims" not in st.session_state:
    st.session_state.claims = []
if "verification_results" not in st.session_state:
    st.session_state.verification_results = []
if "processing" not in st.session_state:
    st.session_state.processing = False
if "current_file_name" not in st.session_state:
    st.session_state.current_file_name = ""

with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 10px 0 20px 0;">
            <span style="font-size: 2.2rem;">🛡️</span>
            <h2 style="margin: 5px 0 0 0; color: #f8fafc; font-size: 1.5rem;">TruthLayer AI</h2>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-top: 2px;">Fact-Checking & Audit Engine</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("⚙️ Verification Settings")
    
    max_claims = st.slider(
        "Max Claims to Verify",
        min_value=3,
        max_value=15,
        value=8,
        help="Higher limits increase processing time and API requests."
    )
    
    search_depth = st.slider(
        "Search Results per Claim",
        min_value=2,
        max_value=5,
        value=3,
        help="Number of top search result snippets to collect as verification evidence."
    )
    
    st.markdown("---")
    st.markdown("""
        <div style="font-size: 0.8rem; color: #64748b; line-height: 1.4;">
            <strong>How it works:</strong><br>
            1. Extracts raw text from uploaded PDF.<br>
            2. Identifies concrete statistics, dates, percentages, and financial claims using Gemini.<br>
            3. Verifies each claim via live web search queries.<br>
            4. Determines credibility (Verified, Inaccurate, False) with complete evidence logs.
        </div>
    """, unsafe_allow_html=True)

st.markdown('<h1 class="main-header">TruthLayer AI</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Automated Fact-Checking & Claim Verification Engine</p>', unsafe_allow_html=True)

if not gemini_key:
    st.warning("⚠️ Google Gemini API Key is required. Please enter your API key in the sidebar to get started.")

uploaded_file = st.file_uploader(
    "Drag and drop your PDF document here",
    type=["pdf"],
    help="Support PDF files up to 10MB.",
    disabled=not gemini_key
)

if uploaded_file is not None:
    if uploaded_file.name != st.session_state.current_file_name:
        st.session_state.extracted_text = ""
        st.session_state.pdf_metadata = {}
        st.session_state.claims = []
        st.session_state.verification_results = []
        st.session_state.current_file_name = uploaded_file.name
        
    file_bytes = uploaded_file.getvalue()
    file_size_mb = len(file_bytes) / (1024 * 1024)
    
    if file_size_mb > 10.0:
        st.error(f"❌ File size exceeds the 10MB limit (Uploaded: {file_size_mb:.2f}MB). Please upload a smaller PDF.")
    else:
        if not st.session_state.extracted_text:
            with st.spinner("📄 Extracting text and parsing PDF structure..."):
                pdf_stream = BytesIO(file_bytes)
                parse_result = extract_text_from_pdf(pdf_stream)
                
                if parse_result["success"]:
                    st.session_state.extracted_text = parse_result["text"]
                    st.session_state.pdf_metadata = {
                        "pages": parse_result["page_count"],
                        "filename": uploaded_file.name,
                        "size_mb": f"{file_size_mb:.2f} MB",
                        "metadata": parse_result["metadata"]
                    }
                    st.success("✅ PDF parsing complete! Ready for claim analysis.")
                else:
                    if parse_result["is_scanned"]:
                        st.warning(f"⚠️ {parse_result['error']}")
                    else:
                        st.error(f"❌ {parse_result['error']}")
                        
        if st.session_state.extracted_text:
            meta = st.session_state.pdf_metadata
            st.markdown(f"""
                <div class="evidence-card" style="margin-bottom: 2rem;">
                    <h4 style="margin: 0 0 10px 0; color: #818cf8;">📄 Document Loaded</h4>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; font-size: 0.9rem;">
                        <div><strong>Filename:</strong> {meta['filename']}</div>
                        <div><strong>Total Pages:</strong> {meta['pages']}</div>
                        <div><strong>File Size:</strong> {meta['size_mb']}</div>
                        <div><strong>Title:</strong> {meta['metadata'].get('title', 'Unknown')}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if not st.session_state.verification_results:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🛡️ Start Automated Fact-Checking Process", use_container_width=True):
                        st.session_state.processing = True
                        st.session_state.claims = []
                        st.session_state.verification_results = []
                        
            if st.session_state.processing:
                try:
                    status_placeholder = st.empty()
                    progress_bar = st.progress(0.0)
                    
                    status_placeholder.markdown("🔍 **Step 1/3: Extracting factual claims...**")
                    claims = extract_claims(
                        text=st.session_state.extracted_text,
                        api_key=gemini_key,
                        max_claims=max_claims
                    )
                    
                    if not claims:
                        st.warning("⚠️ No specific factual claims (statistics, dates, percentages, financial, technical) were detected in the document text.")
                        st.session_state.processing = False
                    else:
                        st.session_state.claims = claims
                        total_found = len(claims)
                        progress_bar.progress(0.3)
                        
                        results = []
                        for idx, item in enumerate(claims):
                            claim_text = item["claim"]
                            claim_type = item["type"]
                            
                            status_placeholder.markdown(
                                f"🌐 **Step 2/3: Live verifying claim {idx+1}/{total_found}...**<br>"
                                f"<code style='color: #a855f7;'>[{claim_type.upper()}]</code> {claim_text}",
                                unsafe_allow_html=True
                            )
                            
                            search_res = search_claim(
                                claim=claim_text,
                                tavily_api_key=tavily_key,
                                max_results=search_depth
                            )
                            
                            verification = verify_claim(
                                claim=claim_text,
                                evidence=search_res["results"],
                                api_key=gemini_key
                            )
                            
                            results.append({
                                "claim": claim_text,
                                "type": claim_type,
                                "status": verification["status"],
                                "reason": verification["reason"],
                                "correct_fact": verification["correct_fact"],
                                "confidence": verification["confidence"],
                                "evidence": search_res["results"],
                                "search_engine": search_res["engine_used"]
                            })
                            
                            current_progress = 0.3 + (0.7 * ((idx + 1) / total_found))
                            progress_bar.progress(min(current_progress, 1.0))
                            
                        st.session_state.verification_results = results
                        st.session_state.processing = False
                        status_placeholder.empty()
                        progress_bar.empty()
                        st.balloons()
                        st.rerun()
                        
                except Exception as ex:
                    st.session_state.processing = False
                    st.error(f"❌ Fact-Checking Failed: {str(ex)}")

if st.session_state.verification_results:
    results = st.session_state.verification_results
    
    total_claims = len(results)
    verified_count = sum(1 for r in results if r["status"] == "VERIFIED")
    inaccurate_count = sum(1 for r in results if r["status"] == "INACCURATE")
    false_count = sum(1 for r in results if r["status"] == "FALSE")
    
    verified_pct = (verified_count / total_claims) * 100 if total_claims > 0 else 0
    inaccurate_pct = (inaccurate_count / total_claims) * 100 if total_claims > 0 else 0
    false_pct = (false_count / total_claims) * 100 if total_claims > 0 else 0
    
    render_metric_cards(verified_pct, inaccurate_pct, false_pct, total_claims)
    
    tab1, tab2, tab3 = st.tabs([
        "📊 Dashboard Overview", 
        "🔍 Detailed Evidence Logs", 
        "📥 Export Report"
    ])
    
    with tab1:
        st.subheader("Factual Claims Audit Report")
        
        markdown_table = """| Claim | Category | Status | Confidence | Correct Fact |\n| :--- | :--- | :---: | :---: | :--- |\n"""
        
        for item in results:
            status_upper = item["status"].upper().strip()
            if status_upper == "VERIFIED":
                status_val = "🟢 **Verified**"
            elif status_upper == "INACCURATE":
                status_val = "🟡 **Inaccurate**"
            else:
                status_val = "🔴 **False**"
                
            type_lbl = get_type_icon(item["type"])
            correct_fact = item["correct_fact"] if item["correct_fact"] else "*N/A (Verified)*"
            
            markdown_table += f"| {item['claim']} | {type_lbl} | {status_val} | **{item['confidence']}%** | {correct_fact} |\n"
            
        st.markdown(markdown_table)
        
    with tab2:
        st.subheader("Deep Audit & Verification Logs")
        st.write("Browse specific sources, search engine diagnostics, and LLM verification reasoning logs for each claim.")
        
        for idx, item in enumerate(results, 1):
            status = item["status"]
            badge_color = "#10b981" if status == "VERIFIED" else ("#f59e0b" if status == "INACCURATE" else "#ef4444")
            
            with st.expander(f"Claim #{idx}: [{status}] - {item['claim'][:80]}...", expanded=(idx==1)):
                st.markdown(f"""
                    <div style="border-left: 4px solid {badge_color}; padding-left: 15px; margin-bottom: 15px;">
                        <h4 style="margin: 0 0 5px 0; color: #f1f5f9;">{item['claim']}</h4>
                        <span class="type-badge">{get_type_icon(item['type'])}</span>
                        <span style="margin-left: 10px;">Confidence Score: <strong>{item['confidence']}%</strong></span>
                        <span style="margin-left: 10px;">Verified using: <strong>{item['search_engine']}</strong></span>
                    </div>
                """, unsafe_allow_html=True)
                
                if status in {"INACCURATE", "FALSE"} and item["correct_fact"]:
                    st.markdown(f"""
                        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.2); border-radius: 8px; padding: 12px; margin-bottom: 15px;">
                            <strong style="color: #ef4444;">🛡️ Corrected Fact:</strong><br>
                            <span style="color: #fca5a5;">{item['correct_fact']}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    
                st.markdown(f"""
                    <div style="margin-bottom: 15px;">
                        <strong style="color: #cbd5e1;">🤖 Verification Reasoning:</strong><br>
                        <p style="color: #94a3b8; font-size: 0.92rem; line-height: 1.5; margin-top: 5px;">{item['reason']}</p>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown("🌐 **Search Sources Collected:**")
                evidence_list = item.get("evidence", [])
                
                if not evidence_list:
                    st.write("No external web snippets could be parsed for this claim.")
                else:
                    for e_idx, ev in enumerate(evidence_list, 1):
                        st.markdown(f"""
                            <div class="evidence-card" style="padding: 10px; margin-bottom: 8px; background: rgba(255, 255, 255, 0.02);">
                                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                                    <span style="font-size: 0.85rem; color: #818cf8; font-weight: 600;">[{e_idx}] <a href="{ev['url']}" target="_blank" style="color: #818cf8; text-decoration: none;">{ev['title']}</a></span>
                                    <span style="font-size: 0.75rem; color: #64748b;">Source: {ev.get('source', 'Web')}</span>
                                </div>
                                <p style="margin: 0; font-size: 0.82rem; color: #cbd5e1; line-height: 1.4;">"{ev['snippet']}"</p>
                            </div>
                        """, unsafe_allow_html=True)

    with tab3:
        st.subheader("Generate & Download Audit Records")
        st.write("Generate a standardized CSV report containing claims, categorization types, verification statuses, confidence levels, and all source URLs.")
        
        csv_data = generate_csv_report(results)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 Download CSV Fact-Checking Report",
                data=csv_data,
                file_name=f"TruthLayer_Fact_Check_{st.session_state.pdf_metadata.get('filename', 'report').replace('.pdf', '')}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
        st.markdown("""
            <div style="background: rgba(30, 41, 59, 0.2); padding: 15px; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05); margin-top: 2rem;">
                <h5 style="margin: 0 0 8px 0; color: #f1f5f9;">🔒 Data Privacy Statement</h5>
                <p style="margin: 0; font-size: 0.85rem; color: #94a3b8; line-height: 1.4;">
                    TruthLayer AI processes your document files in-memory. Extracted text, generated claims, and search cache logs are held in temporary session states and are cleared immediately upon closing or refreshing your browser tab.
                </p>
            </div>
        """, unsafe_allow_html=True)
