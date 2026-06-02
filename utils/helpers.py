import streamlit as st
from typing import Dict

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
        
        .stApp {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Space Grotesk', sans-serif;
            font-weight: 700 !important;
            letter-spacing: -0.02em;
        }
        
        .main-header {
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800 !important;
            text-align: center;
            font-size: 2.8rem;
            margin-bottom: 0.5rem;
            letter-spacing: -0.03em;
        }
        
        .sub-header {
            color: #94a3b8;
            text-align: center;
            font-size: 1.1rem;
            margin-bottom: 2.5rem;
            font-weight: 400;
        }
        
        .metric-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1.25rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: rgba(30, 41, 59, 0.4);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 1.25rem;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        }
        
        .metric-card:hover {
            transform: translateY(-4px);
            border-color: rgba(99, 102, 241, 0.3);
            box-shadow: 0 10px 30px rgba(99, 102, 241, 0.08);
        }
        
        .metric-val {
            font-size: 2rem;
            font-weight: 700;
            color: #f8fafc;
            font-family: 'Space Grotesk', sans-serif;
            margin-bottom: 0.25rem;
        }
        
        .metric-label {
            font-size: 0.85rem;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            font-weight: 600;
        }
        
        .evidence-card {
            background: rgba(15, 23, 42, 0.35);
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.06);
            padding: 1.25rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .status-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            padding: 0.35rem 0.8rem;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            border-width: 1px;
            border-style: solid;
        }
        
        .badge-verified {
            background-color: rgba(16, 185, 129, 0.1) !important;
            color: #10b981 !important;
            border-color: rgba(16, 185, 129, 0.2) !important;
        }
        
        .badge-inaccurate {
            background-color: rgba(245, 158, 11, 0.1) !important;
            color: #f59e0b !important;
            border-color: rgba(245, 158, 11, 0.2) !important;
        }
        
        .badge-false {
            background-color: rgba(239, 68, 68, 0.1) !important;
            color: #ef4444 !important;
            border-color: rgba(239, 68, 68, 0.2) !important;
        }
        
        .type-badge {
            background-color: rgba(99, 102, 241, 0.1);
            color: #818cf8;
            border: 1px solid rgba(99, 102, 241, 0.15);
            padding: 0.15rem 0.5rem;
            border-radius: 6px;
            font-size: 0.7rem;
            text-transform: uppercase;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 0.5rem;
        }
        
        .stButton>button {
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1.8rem;
            font-weight: 600;
            font-size: 0.95rem;
            transition: all 0.2s ease;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.25);
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(99, 102, 241, 0.4);
            background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
            border: none;
            color: white;
        }
        
        .streamlit-expanderHeader {
            background-color: rgba(30, 41, 59, 0.3) !important;
            border: 1px solid rgba(255, 255, 255, 0.05) !important;
            border-radius: 8px !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }
        
        .dashboard-table-container {
            margin-top: 1.5rem;
            margin-bottom: 2rem;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(255, 255, 255, 0.06);
        }
        
        </style>
    """, unsafe_allow_html=True)

def render_metric_cards(verified_pct: float, inaccurate_pct: float, false_pct: float, total_claims: int):
    verified_color = "#10b981" if verified_pct > 0 else "#94a3b8"
    inaccurate_color = "#f59e0b" if inaccurate_pct > 0 else "#94a3b8"
    false_color = "#ef4444" if false_pct > 0 else "#94a3b8"
    
    st.markdown(f"""
        <div class="metric-container">
            <div class="metric-card">
                <div class="metric-val" style="color: #6366f1;">{total_claims}</div>
                <div class="metric-label">Claims Analyzed</div>
            </div>
            <div class="metric-card">
                <div class="metric-val" style="color: {verified_color};">{verified_pct:.0f}%</div>
                <div class="metric-label">Verified</div>
            </div>
            <div class="metric-card">
                <div class="metric-val" style="color: {inaccurate_color};">{inaccurate_pct:.0f}%</div>
                <div class="metric-label">Inaccurate</div>
            </div>
            <div class="metric-card">
                <div class="metric-val" style="color: {false_color};">{false_pct:.0f}%</div>
                <div class="metric-label">False</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def get_status_badge_html(status: str) -> str:
    status = status.upper().strip()
    if status == "VERIFIED":
        return '<span class="status-badge badge-verified">Verified</span>'
    elif status == "INACCURATE":
        return '<span class="status-badge badge-inaccurate">Inaccurate</span>'
    else:
        return '<span class="status-badge badge-false">False</span>'

def get_type_icon(claim_type: str) -> str:
    mapping = {
        "statistic": "📊 Statistic",
        "date": "📅 Date",
        "percentage": "📈 Percentage",
        "financial": "💰 Financial",
        "technical": "⚙️ Technical"
    }
    return mapping.get(claim_type.lower().strip(), "📝 Claim")
