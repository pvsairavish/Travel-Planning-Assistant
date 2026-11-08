"""
Streamlit Web Application: Agentic AI-Based Travel Planning Assistant.
Featuring a luxury cyber-modern sidebar, interactive Plotly flight trajectory maps,
high-definition destination imagery, Open-Meteo live weather radar, and autonomous ReAct reasoning.
"""

import json
from datetime import date, datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import importlib
import config
importlib.reload(config)
import data_loader
importlib.reload(data_loader)
import tools
importlib.reload(tools)
import agent
importlib.reload(agent)
from config import CITY_COORDINATES

# Page Configuration
st.set_page_config(
    page_title="Wanderlust AI • Smart Travel Assistant",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Curated High-Definition Destination Imagery
DESTINATION_IMAGES = {
    "Goa": "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?w=1400&auto=format&fit=crop&q=80",
    "Delhi": "https://images.unsplash.com/photo-1587474260584-136574528ed5?w=1400&auto=format&fit=crop&q=80",
    "Mumbai": "https://images.unsplash.com/photo-1570168007204-dfb528c6958f?w=1400&auto=format&fit=crop&q=80",
    "Jaipur": "https://images.unsplash.com/photo-1477587458883-47145ed94245?w=1400&auto=format&fit=crop&q=80",
    "Bangalore": "https://images.unsplash.com/photo-1596176530529-78163a4f7af2?w=1400&auto=format&fit=crop&q=80",
    "Hyderabad": "https://images.unsplash.com/photo-1605649487212-47bdab064df8?w=1400&auto=format&fit=crop&q=80",
    "Kolkata": "https://images.unsplash.com/photo-1558431382-27e303142255?w=1400&auto=format&fit=crop&q=80",
    "Chennai": "https://images.unsplash.com/photo-1582510003544-4d00b7f74220?w=1400&auto=format&fit=crop&q=80",
}

# Inject Custom Google Font and Vibrant Luxury UI Theme
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet" />

<style>
    /* ==========================================================================
       ICON LIGATURE PRESERVATION (Fixes arrow_down and keyboard_double bugs)
       ========================================================================== */
    [data-testid="stIconMaterial"],
    [data-testid="stExpanderToggleIcon"],
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] span,
    .material-symbols-rounded,
    .material-symbols-outlined,
    details summary [data-testid="stIconMaterial"],
    details summary span:first-child {
        font-family: 'Material Symbols Rounded', 'Material Icons' !important;
        font-weight: normal !important;
        font-style: normal !important;
        line-height: 1 !important;
        display: inline-block !important;
        white-space: nowrap !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        -webkit-font-feature-settings: 'liga' 1 !important;
        font-feature-settings: 'liga' 1 !important;
    }

    /* Target content typography explicitly without overriding icon font spans */
    h1, h2, h3, h4, h5, h6,
    .brand-hero *, .hero-container *, .kpi-card *,
    .summary-card *, .day-slot-card *, .weather-radar-box *, .sight-card *,
    .boarding-pass *, .hotel-card *, .transit-card *,
    div[data-testid="stSidebar"] label,
    div[data-testid="stSidebar"] p,
    div[data-testid="stSidebar"] span[data-baseweb="tag"],
    .stMarkdown p, .stMarkdown li, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
    }

    /* Consistent Title & Heading Alignment */
    h1, h2, h3, h4, h5, h6 {
        letter-spacing: -0.4px !important;
        line-height: 1.3 !important;
    }
    h1 {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }
    h2 {
        font-size: 1.7rem !important;
        font-weight: 800 !important;
    }
    h3 {
        font-size: 1.35rem !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        margin: 14px 0 12px 0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }
    h4 {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        color: #f1f5f9 !important;
        margin: 10px 0 6px 0 !important;
    }

    .stApp {
        background: radial-gradient(circle at 15% 10%, #1e1b4b 0%, #090d16 60%, #030712 100%);
        color: #f8fafc;
    }

    /* Segmented Tab Navigation Bar Alignment */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background: rgba(15, 23, 42, 0.75) !important;
        padding: 6px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        display: flex !important;
        align-items: center !important;
        margin-bottom: 22px !important;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 10px 18px !important;
        color: #94a3b8 !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        border: none !important;
        background: transparent !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #f8fafc !important;
        background: rgba(255, 255, 255, 0.05) !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(2, 132, 199, 0.35) 0%, rgba(99, 102, 241, 0.35) 100%) !important;
        color: #38bdf8 !important;
        border: 1px solid rgba(56, 189, 248, 0.5) !important;
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25) !important;
    }
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        display: none !important;
    }

    /* Expander header styling without breaking expander chevron */
    [data-testid="stExpander"] details summary {
        padding: 12px 16px !important;
        border-radius: 10px !important;
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
    }
    [data-testid="stExpander"] details summary p {
        font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        color: #f1f5f9 !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
    }

    /* ==========================================================================
       SIDEBAR HIGH-END REDESIGN
       ========================================================================== */
    /* Sidebar Base Background & Border */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e1a 0%, #0f172a 40%, #090d16 100%) !important;
        border-right: 1px solid rgba(56, 189, 248, 0.15) !important;
        box-shadow: 10px 0 30px rgba(0, 0, 0, 0.6) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem !important;
    }

    /* Brand Header Box */
    .brand-hero {
        background: linear-gradient(135deg, rgba(30, 27, 75, 0.6) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 16px;
        padding: 18px 14px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
    }
    .brand-icon-halo {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 58px;
        height: 58px;
        border-radius: 16px;
        background: linear-gradient(135deg, #0284c7 0%, #6366f1 100%);
        box-shadow: 0 0 25px rgba(56, 189, 248, 0.5);
        font-size: 1.9rem;
        margin-bottom: 8px;
    }
    .brand-name {
        font-size: 1.35rem;
        font-weight: 800;
        letter-spacing: -0.5px;
        background: linear-gradient(135deg, #ffffff 0%, #38bdf8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .brand-subtitle {
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 600;
        margin-top: 2px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .brand-status-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(16, 185, 129, 0.12);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #34d399;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 3px 10px;
        border-radius: 9999px;
        margin-top: 10px;
    }
    .pulse-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #34d399;
        box-shadow: 0 0 8px #34d399;
    }

    /* Section Category Headings */
    .sidebar-section-tag {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.72rem;
        font-weight: 800;
        color: #38bdf8;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 18px 0 8px 2px;
    }
    .sidebar-section-tag hr {
        flex: 1;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, rgba(56, 189, 248, 0.4) 0%, transparent 100%);
        margin: 0;
    }

    /* Sidebar Form Controls Customization */
    [data-testid="stSidebar"] label {
        font-size: 0.82rem !important;
        font-weight: 700 !important;
        color: #cbd5e1 !important;
        margin-bottom: 4px !important;
    }

    /* Inputs, Dropdowns & Date Pickers (Forces Deep Slate Navy across both Localhost & Cloud) */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div,
    [data-testid="stSidebar"] div[data-baseweb="select"] div,
    [data-testid="stSidebar"] div[data-baseweb="input"],
    [data-testid="stSidebar"] div[data-baseweb="input"] > div,
    [data-testid="stSidebar"] div[data-baseweb="input"] input,
    [data-testid="stSidebar"] div[data-testid="stDateInput"] input,
    [data-testid="stSidebar"] div[data-testid="stDateInput"] div[data-baseweb="input"],
    [data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        background-color: #131c2e !important;
        background: #131c2e !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4) !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div:hover,
    [data-testid="stSidebar"] div[data-baseweb="input"]:hover,
    [data-testid="stSidebar"] div[data-testid="stDateInput"] div[data-baseweb="input"]:hover {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 14px rgba(56, 189, 248, 0.4) !important;
    }
    /* Dropdown Menus & Popover Options */
    ul[data-baseweb="menu"],
    div[data-baseweb="popover"],
    div[data-baseweb="calendar"] {
        background-color: #0f172a !important;
        background: #0f172a !important;
        border: 1px solid rgba(56, 189, 248, 0.35) !important;
        border-radius: 12px !important;
        color: #f8fafc !important;
    }
    li[data-baseweb="menu-item"]:hover {
        background: rgba(56, 189, 248, 0.18) !important;
        color: #38bdf8 !important;
    }

    /* Fix Slider Aesthetics: Cyan/Indigo Gradient Track & Cyan Glowing Thumb */
    [data-testid="stSidebar"] div[data-baseweb="slider"] {
        margin-top: 6px !important;
    }
    [data-testid="stSidebar"] div[data-testid="stThumbValue"] {
        color: #38bdf8 !important;
        font-weight: 800 !important;
        font-size: 0.88rem !important;
        background: #0f172a !important;
        padding: 2px 8px !important;
        border-radius: 6px !important;
        border: 1px solid rgba(56, 189, 248, 0.4) !important;
    }
    [data-testid="stSidebar"] div[role="slider"] {
        background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%) !important;
        box-shadow: 0 0 12px rgba(56, 189, 248, 0.8) !important;
        border: 2px solid #ffffff !important;
        width: 18px !important;
        height: 18px !important;
    }

    /* Multiselect Tags (Vibrant Cyan/Indigo Chips) */
    [data-testid="stSidebar"] span[data-baseweb="tag"] {
        background: linear-gradient(135deg, rgba(2, 132, 199, 0.25) 0%, rgba(99, 102, 241, 0.3) 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.45) !important;
        border-radius: 8px !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
        padding: 4px 10px !important;
    }
    [data-testid="stSidebar"] span[data-baseweb="tag"] svg {
        fill: #38bdf8 !important;
    }

    /* Expander styling in Sidebar */
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        background: #131c2e !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 12px !important;
        margin-top: 14px !important;
    }

    /* Primary Generate Button (Vibrant Glow Action) */
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #0284c7 0%, #6366f1 50%, #d946ef 100%) !important;
        color: #ffffff !important;
        font-size: 1.05rem !important;
        font-weight: 800 !important;
        letter-spacing: 0.5px !important;
        padding: 14px 20px !important;
        border-radius: 12px !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.5) !important;
        border: none !important;
        width: 100% !important;
        margin-top: 14px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 12px 30px rgba(217, 70, 239, 0.6) !important;
    }

    /* ==========================================================================
       MAIN CONTENT CARD STYLES
       ========================================================================== */
    /* Destination Hero Card */
    .hero-container {
        position: relative;
        border-radius: 20px;
        overflow: hidden;
        margin-bottom: 24px;
        border: 1px solid rgba(255, 255, 255, 0.12);
        box-shadow: 0 20px 40px -10px rgba(0, 0, 0, 0.7);
        background: #0f172a;
    }
    .hero-img {
        width: 100%;
        height: 270px;
        object-fit: cover;
        opacity: 0.65;
        filter: brightness(0.9) contrast(1.1);
        transition: transform 0.6s ease;
    }
    .hero-container:hover .hero-img {
        transform: scale(1.02);
    }
    .hero-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 30px;
        background: linear-gradient(180deg, rgba(15, 23, 42, 0) 0%, rgba(9, 13, 22, 0.95) 85%);
    }
    .hero-title {
        font-size: 2.7rem;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
        letter-spacing: -1px;
        text-shadow: 0 3px 8px rgba(0,0,0,0.8);
    }
    .hero-subtitle {
        color: #38bdf8;
        font-size: 1.05rem;
        font-weight: 600;
        margin-top: 6px;
    }

    /* Badges & Pills */
    .pill-cyan {
        background: rgba(56, 189, 248, 0.18);
        color: #38bdf8;
        border: 1px solid rgba(56, 189, 248, 0.4);
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 8px;
        margin-bottom: 6px;
    }
    .pill-green {
        background: rgba(16, 185, 129, 0.18);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 8px;
    }
    .pill-amber {
        background: rgba(245, 158, 11, 0.18);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 4px 14px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 8px;
    }
    .pill-savings {
        background: rgba(16, 185, 129, 0.25);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.6);
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 800;
        display: inline-flex;
        align-items: center;
        gap: 4px;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.25);
    }

    /* KPI Cards - Uniform Height & Alignment */
    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px 16px;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        transition: transform 0.25s ease, border-color 0.25s ease;
        height: 100%;
        min-height: 175px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.5);
    }
    .kpi-icon {
        font-size: 1.6rem;
        margin-bottom: 4px;
        line-height: 1;
    }
    .kpi-label {
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }
    .kpi-val {
        font-size: 1.85rem;
        font-weight: 800;
        margin: 4px 0;
        color: #ffffff;
        line-height: 1.1;
    }
    .kpi-badge {
        font-size: 0.8rem;
        color: #cbd5e1;
        font-weight: 600;
        line-height: 1.2;
    }

    /* Multi-Modal Comparison Cards - Equalized Height & Alignment */
    .transit-card {
        background: #1e293b;
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 22px;
        height: 100%;
        min-height: 275px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        transition: transform 0.25s ease, border-color 0.25s ease;
    }
    .transit-card:hover {
        transform: translateY(-3px);
    }
    .transit-card.active-choice {
        border: 2px solid #38bdf8 !important;
        box-shadow: 0 0 20px rgba(56, 189, 248, 0.3) !important;
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 100%) !important;
    }
    .transit-mode-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    /* Boarding Pass / Ticket Card */
    .boarding-pass {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        border: 1px solid rgba(139, 92, 246, 0.3);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 12px 25px -5px rgba(0, 0, 0, 0.5);
        color: #ffffff;
        height: 100%;
        min-height: 330px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
    }
    .boarding-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px dashed rgba(255, 255, 255, 0.15);
        padding-bottom: 16px;
        margin-bottom: 18px;
    }
    .airline-brand {
        font-size: 1.3rem;
        font-weight: 800;
        color: #38bdf8;
    }
    .flight-price-glow {
        font-size: 1.5rem;
        font-weight: 800;
        color: #34d399;
    }
    .flight-nodes {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 16px 0;
    }
    .node-code {
        font-size: 2rem;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: -0.5px;
    }
    .node-city {
        font-size: 0.85rem;
        color: #94a3b8;
        font-weight: 600;
    }
    .node-time {
        font-size: 0.95rem;
        color: #38bdf8;
        font-weight: 700;
        margin-top: 4px;
    }
    .flight-mid {
        text-align: center;
        flex: 1;
        padding: 0 20px;
    }
    .flight-duration-tag {
        font-size: 0.8rem;
        color: #94a3b8;
        font-weight: 600;
    }
    .flight-plane-track {
        color: #38bdf8;
        font-size: 1.2rem;
        margin: 4px 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
    }
    .flight-plane-track hr {
        flex: 1;
        border-color: rgba(56, 189, 248, 0.3);
        margin: 0;
    }

    /* Luxury Hotel Listing Card */
    .hotel-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(251, 191, 36, 0.25);
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 12px 25px -5px rgba(0, 0, 0, 0.5);
        color: #ffffff;
        height: 100%;
        min-height: 330px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .hotel-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding-bottom: 14px;
        margin-bottom: 16px;
    }
    .hotel-name {
        font-size: 1.35rem;
        font-weight: 800;
        color: #ffffff;
    }
    .hotel-stars {
        color: #fbbf24;
        font-size: 1.1rem;
        letter-spacing: 2px;
        margin: 4px 0;
    }
    .tariff-amount {
        font-size: 1.5rem;
        font-weight: 800;
        color: #34d399;
        text-align: right;
    }
    .tariff-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-align: right;
    }
    .amenity-chip {
        display: inline-block;
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #e2e8f0;
        padding: 5px 12px;
        border-radius: 8px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* Day Schedule Cards */
    .day-slot-card {
        background: #1e293b;
        border-radius: 12px;
        padding: 18px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        height: 100%;
        min-height: 140px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    .slot-tag {
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.8px;
        margin-bottom: 8px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    .slot-desc {
        font-size: 0.92rem;
        color: #e2e8f0;
        line-height: 1.55;
    }

    /* Modern Itemized Expense Table (High Contrast Guaranteed) */
    .summary-card {
        background: #1e293b !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        border-radius: 16px !important;
        padding: 24px !important;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5) !important;
        color: #ffffff !important;
        height: 320px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: space-between !important;
    }
    .summary-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        font-size: 0.95rem;
    }
    .summary-label {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
    }
    .summary-val {
        color: #38bdf8 !important;
        font-weight: 800 !important;
        font-size: 1.1rem !important;
    }
    .summary-total {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 14px;
        margin-top: 4px;
    }
    .total-title {
        font-size: 1.15rem;
        font-weight: 800;
        color: #ffffff !important;
    }
    .total-glow {
        font-size: 1.6rem;
        font-weight: 900;
        color: #34d399 !important;
        text-shadow: 0 0 15px rgba(52, 211, 153, 0.5);
    }

    /* Weather Radar Box */
    .weather-radar-box {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        padding: 20px 14px;
        text-align: center;
        height: 100%;
        min-height: 215px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: center;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .weather-radar-box:hover {
        transform: translateY(-4px);
        border-color: #38bdf8;
        box-shadow: 0 10px 20px -5px rgba(56, 189, 248, 0.3);
    }

    /* Attraction showcase */
    .sight-card {
        background: #1e293b;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px;
        height: 100%;
        min-height: 145px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .sight-card:hover {
        transform: translateY(-3px);
        border-color: #818cf8;
    }

    /* Download Buttons Alignment & Design */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%) !important;
        border: 1px solid rgba(56, 189, 248, 0.3) !important;
        color: #38bdf8 !important;
        font-weight: 700 !important;
        font-size: 0.92rem !important;
        border-radius: 10px !important;
        padding: 12px 18px !important;
        transition: all 0.25s ease !important;
        width: 100% !important;
    }
    .stDownloadButton > button:hover {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.4) !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
    }
</style>
""", unsafe_allow_html=True)


def build_route_map(origin_name: str, dest_name: str, transit_mode: str = "flight"):
    """Builds an interactive geographic trajectory map of the transit route across India."""
    c1 = CITY_COORDINATES.get(origin_name, CITY_COORDINATES.get("Delhi"))
    c2 = CITY_COORDINATES.get(dest_name, CITY_COORDINATES.get("Goa"))

    fig = go.Figure()

    # Route line with styling depending on mode
    dash_style = 'dot' if transit_mode == 'bus' else ('dash' if transit_mode == 'cab' else 'solid')
    line_color = '#38bdf8' if transit_mode == 'flight' else ('#34d399' if transit_mode == 'bus' else '#fbbf24')
    mode_icon = "✈️" if transit_mode == "flight" else ("🚌" if transit_mode == "bus" else "🚗")

    fig.add_trace(go.Scattergeo(
        locationmode='country names',
        lon=[c1['longitude'], c2['longitude']],
        lat=[c1['latitude'], c2['latitude']],
        mode='lines+markers',
        line=dict(width=3.5, color=line_color, dash=dash_style),
        marker=dict(size=[12, 16], color=['#fbbf24', '#34d399'], symbol=['circle', 'star']),
        text=[f"Departure: {origin_name}", f"Arrival: {dest_name}"],
        hoverinfo='text'
    ))

    title_text = (
        f"{mode_icon} Flight Trajectory: {origin_name} ➔ {dest_name}"
        if transit_mode == "flight"
        else f"{mode_icon} Interstate {transit_mode.capitalize()} Route: {origin_name} ➔ {dest_name}"
    )

    fig.update_layout(
        geo=dict(
            scope='asia',
            projection_type='natural earth',
            showland=True,
            landcolor='#1e293b',
            showcountries=True,
            countrycolor='#475569',
            showocean=True,
            oceancolor='#090d16',
            showlakes=True,
            lakecolor='#090d16',
            center=dict(lat=21.5, lon=79.0),
            projection_scale=3.8
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=30, b=0),
        height=320,
        title=dict(text=title_text, font=dict(color="#38bdf8", size=15, family="Plus Jakarta Sans"))
    )
    return fig


def main():
    # =========================================================================
    # SIDEBAR: LUXURY CYBER-MODERN DESIGN
    # =========================================================================
    st.sidebar.markdown("""
    <div class="brand-hero">
        <div class="brand-icon-halo">
            <span>✈️</span>
        </div>
        <h2 class="brand-name">Wanderlust AI</h2>
        <div class="brand-subtitle">Agentic Travel Concierge</div>
        <div class="brand-status-chip">
            <span class="pulse-dot"></span> LangChain Agent Active
        </div>
    </div>
    """, unsafe_allow_html=True)

    cities = data_loader.get_all_cities()
    if not cities:
        cities = ["Bangalore", "Chennai", "Delhi", "Goa", "Hyderabad", "Jaipur", "Kolkata", "Mumbai"]

    origin_default = "Delhi" if "Delhi" in cities else cities[0]
    dest_default = "Jaipur" if "Jaipur" in cities else cities[1]

    # Section 1: Route Setup & Transit Preference
    st.sidebar.markdown("""
    <div class="sidebar-section-tag">
        <span>🛫 Route & Transit Preference</span><hr>
    </div>
    """, unsafe_allow_html=True)

    col_orig, col_dest = st.sidebar.columns(2)
    with col_orig:
        origin_city = st.selectbox("From (Origin)", cities, index=cities.index(origin_default))
    with col_dest:
        dest_candidates = [c for c in cities if c != origin_city]
        dest_idx = dest_candidates.index(dest_default) if dest_default in dest_candidates else 0
        destination_city = st.selectbox("To (Destination)", dest_candidates, index=dest_idx)

    transit_mode_labels = [
        "🤖 Smart Mode (Budget-Optimized)",
        "🚌 AC Sleeper Bus (Budget Friendly)",
        "✈️ Flight (Fastest)",
        "🚗 Private Cab (Road Trip)"
    ]
    transit_mode_map = {
        transit_mode_labels[0]: "any",
        transit_mode_labels[1]: "bus",
        transit_mode_labels[2]: "flight",
        transit_mode_labels[3]: "cab"
    }
    selected_transit_label = st.sidebar.selectbox("Transit Mode Preference", transit_mode_labels, index=0)
    preferred_transit_mode = transit_mode_map[selected_transit_label]

    # Section 2: Timeline & Duration
    st.sidebar.markdown("""
    <div class="sidebar-section-tag">
        <span>📅 Schedule & Duration</span><hr>
    </div>
    """, unsafe_allow_html=True)

    today = date.today()
    default_start = today + timedelta(days=7)
    travel_date = st.sidebar.date_input("Travel Date", value=default_start, min_value=today)
    num_days = st.sidebar.slider("Trip Duration", min_value=1, max_value=7, value=3, format="%d Days")

    # Section 3: Budget & Travel Style
    st.sidebar.markdown("""
    <div class="sidebar-section-tag">
        <span>💎 Budget & Style Tier</span><hr>
    </div>
    """, unsafe_allow_html=True)

    travel_style = st.sidebar.select_slider(
        "Travel Style",
        options=["budget", "moderate", "luxury"],
        value="budget",
        format_func=lambda x: f"{x.capitalize()} (₹{'800' if x=='budget' else ('1,500' if x=='moderate' else '3,000')}/day)"
    )

    # Section 4: Attractions & Interests
    st.sidebar.markdown("""
    <div class="sidebar-section-tag">
        <span>🎯 Activity Interests</span><hr>
    </div>
    """, unsafe_allow_html=True)

    interest_options = ["Beaches", "Heritage & Forts", "Temples & Culture", "Museums", "Parks & Nature", "Water Sports", "Local Food"]
    selected_interests = st.sidebar.multiselect(
        "Interests",
        options=interest_options,
        default=["Heritage & Forts", "Local Food"],
        label_visibility="collapsed"
    )

    # Section 5: LLM Configuration (Optional)
    with st.sidebar.expander("⚙️ AI Model Engine (Optional)", expanded=False):
        llm_provider = st.selectbox(
            "Agent Mode",
            ["Autonomous Built-in Engine (Instant & Guaranteed)", "Groq (Llama-3.3-70B)", "OpenAI (GPT-4o-mini)", "Google Gemini (Gemini-1.5)"],
            index=0
        )
        api_key = ""
        if "Groq" in llm_provider:
            api_key = st.text_input("Groq API Key", type="password")
        elif "OpenAI" in llm_provider:
            api_key = st.text_input("OpenAI API Key", type="password")
        elif "Gemini" in llm_provider:
            api_key = st.text_input("Gemini API Key", type="password")

    generate_btn = st.sidebar.button("🚀 Plan My Trip With AI", type="primary", use_container_width=True)

    # State Handling
    if "itinerary_result" not in st.session_state:
        st.session_state.itinerary_result = None

    if generate_btn or st.session_state.itinerary_result is None:
        provider_slug = "heuristic"
        if "Groq" in llm_provider:
            provider_slug = "groq"
        elif "OpenAI" in llm_provider:
            provider_slug = "openai"
        elif "Gemini" in llm_provider:
            provider_slug = "google"

        with st.spinner("🤖 Autonomous Agent is analyzing flights, buses, cabs, hotels, weather & budgeting..."):
            plan = agent.plan_trip(
                origin=origin_city,
                destination=destination_city,
                start_date=travel_date.strftime("%Y-%m-%d"),
                num_days=num_days,
                travel_style=travel_style,
                preferred_transit=preferred_transit_mode,
                interests=selected_interests,
                llm_provider=provider_slug,
                api_key=api_key if api_key else None
            )
            st.session_state.itinerary_result = plan

    res = st.session_state.itinerary_result
    if not res:
        st.info("Select your destination and click 'Plan My Trip With AI' to begin.")
        return

    # Extract Data Safely
    b_down = res.get("budget_breakdown", {}).get("breakdown", {})
    total_budget = float(res.get("budget_breakdown", {}).get("total_estimated_budget", 0) or 0)
    selected_transit = res.get("transit_selected") or {
        "mode": "flight", "icon": "✈️", "price": 4800, "provider": "IndiGo", "duration_str": "2.5h", "title": "IndiGo Flight"
    }
    selected_ht = res.get("hotel_selected") or {}
    transit_price = float(selected_transit.get("price", 0) or 0)
    hotel_total = float((b_down.get("hotel") or {}).get("total", 0) or 0)
    daily_total = float((b_down.get("food_and_local_transit") or {}).get("total", 0) or 0)
    hero_img = DESTINATION_IMAGES.get(res["destination"], DESTINATION_IMAGES["Goa"])
    savings_vs_flight = float(selected_transit.get("savings_vs_flight", 0) or 0)

    # HERO BANNER
    st.markdown(f"""
    <div class="hero-container">
        <img class="hero-img" src="{hero_img}" alt="{res['destination']}" />
        <div class="hero-overlay">
            <span class="pill-green">● Verified Agent Plan</span>
            <span class="pill-cyan">🌤️ Live Open-Meteo REST API</span>
            <span class="pill-amber">⚡ Multi-Modal Budget Smart</span>
            <h1 class="hero-title">{res['destination']} Journey</h1>
            <div class="hero-subtitle">
                {selected_transit.get('icon', '✈️')} {res['origin']} ➔ {res['destination']} • {res['num_days']} Days ({res['trip_dates']}) • {travel_style.capitalize()} Experience
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # TOP KPI METRICS STRIP
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #38bdf8;">
            <div class="kpi-icon">📍</div>
            <div class="kpi-label">DESTINATION</div>
            <div class="kpi-val">{res.get('destination', 'N/A')}</div>
            <div class="kpi-badge">📅 {res.get('trip_dates', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    with k2:
        badge_text = (
            f"💰 Saves ₹{savings_vs_flight:,.0f} vs Flight!"
            if savings_vs_flight > 0
            else f"{selected_transit.get('provider', 'Transit')}"
        )
        badge_color = "#34d399" if savings_vs_flight > 0 else "#cbd5e1"
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #818cf8;">
            <div class="kpi-icon">{selected_transit.get('icon', '🧳')}</div>
            <div class="kpi-label">TRANSIT ({selected_transit.get('mode', 'transit').upper()})</div>
            <div class="kpi-val" style="color:#38bdf8;">₹{transit_price:,.0f}</div>
            <div class="kpi-badge" style="color:{badge_color}; font-weight:700;">{badge_text}</div>
        </div>
        """, unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #34d399;">
            <div class="kpi-icon">🏨</div>
            <div class="kpi-label">ACCOMMODATION</div>
            <div class="kpi-val" style="color:#34d399;">₹{hotel_total:,.0f}</div>
            <div class="kpi-badge">{res.get('num_nights', 0)} Nights Stay</div>
        </div>
        """, unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="kpi-card" style="border-top: 3px solid #fbbf24;">
            <div class="kpi-icon">💰</div>
            <div class="kpi-label">TOTAL BUDGET</div>
            <div class="kpi-val" style="color:#fbbf24;">₹{total_budget:,.0f}</div>
            <div class="kpi-badge">All-Inclusive Estimate</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")

    # INTERACTIVE NAVIGATION TABS
    tab_itinerary, tab_analytics, tab_weather, tab_places, tab_transit, tab_trace = st.tabs([
        "📅 Day-Wise Schedule",
        "📊 Visual Budget & Geographic Map",
        "🌤️ Live Weather Forecast",
        "🏛️ Top Attractions Showcase",
        "🚆 Multi-Modal Transit & Stays",
        "🧠 Agent Reasoning & Trace",
    ])

    # TAB 1: ITINERARY
    with tab_itinerary:
        st.markdown(f"### 📍 Curated Day-Wise Schedule for {res['destination']}")
        st.markdown(f"<span style='color:#94a3b8; font-size:0.95rem;'>Dynamically optimized for <b>{travel_style.capitalize()}</b> travel with weather-smart scheduling and {selected_transit.get('mode', 'transit')} connectivity.</span>", unsafe_allow_html=True)
        st.write("")

        itinerary_items = res.get("day_wise_itinerary", [])
        for item in itinerary_items:
            day_w = item.get("weather", {})
            cond = day_w.get("condition", "Sunny ☀️")
            high_t = day_w.get("temp_max_c", 30)
            sched = item.get("schedule", {})

            with st.expander(f"🗓️ {item.get('day_label')} — {cond} (High: {high_t}°C)", expanded=True):
                c_m, c_a, c_e = st.columns(3)
                with c_m:
                    st.markdown(f"""
                    <div class="day-slot-card" style="border-left: 3px solid #38bdf8;">
                        <div class="slot-tag" style="color:#38bdf8;">🌅 MORNING</div>
                        <div class="slot-desc">{sched.get('morning')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c_a:
                    st.markdown(f"""
                    <div class="day-slot-card" style="border-left: 3px solid #fbbf24;">
                        <div class="slot-tag" style="color:#fbbf24;">☀️ AFTERNOON</div>
                        <div class="slot-desc">{sched.get('afternoon')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with c_e:
                    st.markdown(f"""
                    <div class="day-slot-card" style="border-left: 3px solid #c084fc;">
                        <div class="slot-tag" style="color:#c084fc;">🌙 EVENING</div>
                        <div class="slot-desc">{sched.get('evening')}</div>
                    </div>
                    """, unsafe_allow_html=True)

    # TAB 2: VISUAL ANALYTICS & GEOGRAPHIC MAP
    with tab_analytics:
        st.markdown("### 📊 Visual Analytics & Geographic Route Map")

        v_col1, v_col2 = st.columns([1.1, 1])

        with v_col1:
            # Geographic Route Map
            map_fig = build_route_map(res["origin"], res["destination"], transit_mode=selected_transit.get("mode", "flight"))
            st.plotly_chart(map_fig, use_container_width=True)

        with v_col2:
            # Budget Gauge Chart
            gauge_max = 35000 if travel_style == "luxury" else (22000 if travel_style == "moderate" else 15000)
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=total_budget,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Budget Gauge ({travel_style.capitalize()} Limit: ₹{gauge_max:,})", 'font': {'size': 14, 'color': '#f8fafc', 'family': 'Plus Jakarta Sans'}},
                number={'prefix': "₹", 'font': {'color': '#38bdf8', 'size': 26, 'family': 'Plus Jakarta Sans'}},
                gauge={
                    'axis': {'range': [None, gauge_max], 'tickcolor': "#94a3b8", 'tickfont': {'color': "#94a3b8"}},
                    'bar': {'color': "#38bdf8", 'thickness': 0.3},
                    'bgcolor': "#1e293b",
                    'borderwidth': 1,
                    'bordercolor': "#334155",
                    'steps': [
                        {'range': [0, gauge_max * 0.6], 'color': 'rgba(16, 185, 129, 0.25)'},
                        {'range': [gauge_max * 0.6, gauge_max * 0.85], 'color': 'rgba(245, 158, 11, 0.25)'},
                        {'range': [gauge_max * 0.85, gauge_max], 'color': 'rgba(239, 68, 68, 0.25)'}
                    ]
                }
            ))
            fig_gauge.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font={'color': "#f8fafc"},
                height=320,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_gauge, use_container_width=True)

        st.markdown("---")

        # Donut Chart & High-Contrast Table
        b_col_donut, b_col_table = st.columns([1.1, 1])

        with b_col_donut:
            mode_title = f"{selected_transit.get('icon', '🧳')} {selected_transit.get('mode', 'transit').capitalize()} Fare"
            labels = [mode_title, "Hotel Accommodation", "Food & Local Transit"]
            values = [transit_price, hotel_total, daily_total]
            colors = ["#38bdf8", "#34d399", "#fbbf24"]

            fig_donut = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=0.6,
                marker=dict(colors=colors, line=dict(color='#0b1120', width=2)),
                textinfo="label+percent",
                hovertemplate="<b>%{label}</b><br>Amount: ₹%{value:,.0f}<br>Share: %{percent}<extra></extra>"
            )])
            fig_donut.update_layout(
                title=dict(text="Expense Distribution", font=dict(color="#f8fafc", size=15, family="Plus Jakarta Sans")),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f8fafc", family="Plus Jakarta Sans"),
                showlegend=False,
                height=320,
                margin=dict(l=20, r=20, t=40, b=20),
                annotations=[dict(text=f"₹{total_budget:,.0f}", x=0.5, y=0.5, font_size=18, font_color="#38bdf8", showarrow=False)]
            )
            st.plotly_chart(fig_donut, use_container_width=True)

        with b_col_table:
            st.markdown(f"""
            <div class="summary-card">
                <div style="font-size:1.15rem; font-weight:800; color:#38bdf8; margin-bottom:12px;">💰 Itemized Expense Summary</div>
                <div class="summary-row">
                    <span class="summary-label">{selected_transit.get('icon', '🧳')} {selected_transit.get('mode', 'Transit').capitalize()} ({selected_transit.get('provider')})</span>
                    <span class="summary-val">₹{transit_price:,.0f}</span>
                </div>
                <div class="summary-row">
                    <span class="summary-label">🏨 Hotel ({res['num_nights']} Nights @ ₹{selected_ht.get('price_per_night', 0):,}/night)</span>
                    <span class="summary-val">₹{hotel_total:,.0f}</span>
                </div>
                <div class="summary-row">
                    <span class="summary-label">🍛 Food & Local Transit ({res['num_days']} Days @ ₹{daily_total/res['num_days']:,.0f}/day)</span>
                    <span class="summary-val">₹{daily_total:,.0f}</span>
                </div>
                <div class="summary-total">
                    <span class="total-title">Total Estimated Cost</span>
                    <span class="total-glow">₹{total_budget:,.0f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # TAB 3: LIVE WEATHER FORECAST
    with tab_weather:
        st.markdown(f"### 🌤️ Live Open-Meteo Weather Center — {res['destination']}")
        forecast = res.get("weather_forecast", [])

        if forecast:
            w_cols = st.columns(min(len(forecast), 5))
            for idx, fc in enumerate(forecast[:5]):
                with w_cols[idx]:
                    st.markdown(f"""
                    <div class="weather-radar-box">
                        <div style="font-size:0.8rem; font-weight:700; color:#38bdf8; text-transform:uppercase;">{fc.get('day')}</div>
                        <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:6px;">{fc.get('date')}</div>
                        <div style="font-size:1.8rem; margin:8px 0;">{fc.get('condition').split()[-1] if ' ' in fc.get('condition') else '☀️'}</div>
                        <div style="font-size:1.25rem; font-weight:800; color:#ffffff;">{fc.get('temp_max_c')}°C</div>
                        <div style="font-size:0.75rem; color:#94a3b8;">Low: {fc.get('temp_min_c')}°C</div>
                        <div style="font-size:0.8rem; color:#cbd5e1; margin-top:8px; font-weight:500;">{fc.get('condition')}</div>
                    </div>
                    """, unsafe_allow_html=True)

            st.write("")
            chart_df = pd.DataFrame(forecast)
            fig_weather = px.line(
                chart_df,
                x="day",
                y=["temp_max_c", "temp_min_c"],
                markers=True,
                labels={"value": "Temperature (°C)", "day": "Day", "variable": "Metric"},
                color_discrete_map={"temp_max_c": "#38bdf8", "temp_min_c": "#34d399"}
            )
            fig_weather.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f8fafc", family="Plus Jakarta Sans"),
                legend=dict(orientation="h", y=1.1, x=0.3),
                height=260,
                margin=dict(l=10, r=10, t=30, b=10)
            )
            st.plotly_chart(fig_weather, use_container_width=True)

    # TAB 4: ATTRACTIONS SHOWCASE
    with tab_places:
        st.markdown(f"### 🏛️ Top Attractions & Highlights in {res['destination']}")
        places = res.get("places_recommended") or []
        if not places:
            places = data_loader.find_places(res["destination"], top_n=6)

        p_cols = st.columns(3)
        type_icons = {
            "beach": "🏖️",
            "fort": "🏛️",
            "temple": "🛕",
            "museum": "🖼️",
            "lake": "🌊",
            "park": "🌳",
            "church": "⛪"
        }

        for idx, p in enumerate(places[:6]):
            p_type = str(p.get("type", "sight")).lower()
            icon = type_icons.get(p_type, "📍")
            rating = float(p.get("rating", 4.5))

            with p_cols[idx % 3]:
                st.markdown(f"""
                <div class="sight-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <span style="font-size:1.1rem; font-weight:700; color:#ffffff;">{p.get('name')}</span>
                        <span style="color:#fbbf24; font-weight:800; font-size:0.95rem;">★ {rating}</span>
                    </div>
                    <div style="margin-top:10px;">
                        <span class="pill-cyan">{icon} {p_type.capitalize()}</span>
                        <span class="pill-green">Rank #{idx+1}</span>
                    </div>
                    <div style="font-size:0.85rem; color:#94a3b8; margin-top:8px;">
                        City: {p.get('city')} • Prime Sightseeing
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.write("")

    # TAB 5: MULTI-MODAL TRANSIT & ACCOMMODATION
    with tab_transit:
        st.markdown("### 🔄 Multi-Modal Transit Intelligence")
        st.markdown(f"<span style='color:#94a3b8; font-size:0.95rem;'>Compare **Flights vs AC Sleeper Buses vs Private Cabs** on the {res['origin']} ➔ {res['destination']} route to maximize budget savings.</span>", unsafe_allow_html=True)
        st.write("")

        # 3-Way Transit Comparison Cards
        t_comp = res.get("transit_comparison") or {}
        best_fl = t_comp.get("best_flight") or res.get("flight_selected") or {}
        best_bs = t_comp.get("best_bus") or res.get("bus_selected") or {}
        best_cb = t_comp.get("best_cab") or res.get("cab_selected") or {}
        current_mode = selected_transit.get("mode", "flight")

        tc_col1, tc_col2, tc_col3 = st.columns(3)

        # 1. Flight Card
        with tc_col1:
            is_active = current_mode == "flight"
            active_cls = "active-choice" if is_active else ""
            st.markdown(f"""
            <div class="transit-card {active_cls}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="transit-mode-badge" style="background:rgba(56,189,248,0.2); color:#38bdf8;">✈️ FLIGHT</span>
                    {'<span class="pill-green">● Active Choice</span>' if is_active else '<span style="font-size:0.75rem; color:#94a3b8;">Alternative</span>'}
                </div>
                <div style="font-size:1.15rem; font-weight:800; color:#ffffff; margin-top:10px;">{best_fl.get('airline', 'Scheduled Flight')}</div>
                <div style="font-size:0.8rem; color:#94a3b8;">Flight ID: {best_fl.get('flight_id', 'FL-01')}</div>
                <div style="margin:12px 0;">
                    <div style="font-size:1.6rem; font-weight:900; color:#38bdf8;">₹{best_fl.get('price', 4800):,}</div>
                    <div style="font-size:0.78rem; color:#94a3b8;">Duration: {best_fl.get('duration_str', '2.5h')} • Fastest Option</div>
                </div>
                <div style="margin-bottom:8px;">
                    <span class="pill-cyan">⚡ Fastest Transit Mode</span>
                </div>
                <div style="font-size:0.82rem; color:#cbd5e1; border-top:1px solid rgba(255,255,255,0.08); padding-top:10px;">
                    🛫 Dep: {best_fl.get('departure_time', '14:00')} ➔ Arr: {best_fl.get('arrival_time', '16:30')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 2. Bus Card
        with tc_col2:
            is_active = current_mode == "bus"
            active_cls = "active-choice" if is_active else ""
            bus_price = best_bs.get('price', 850)
            fl_price = best_fl.get('price', 4800)
            bus_savings = max(0, fl_price - bus_price)
            st.markdown(f"""
            <div class="transit-card {active_cls}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="transit-mode-badge" style="background:rgba(16,185,129,0.2); color:#34d399;">🚌 AC SLEEPER BUS</span>
                    {'<span class="pill-green">● Active Choice</span>' if is_active else '<span style="font-size:0.75rem; color:#94a3b8;">Alternative</span>'}
                </div>
                <div style="font-size:1.15rem; font-weight:800; color:#ffffff; margin-top:10px;">{best_bs.get('operator', 'Smart Sleeper Bus')}</div>
                <div style="font-size:0.8rem; color:#94a3b8;">{best_bs.get('bus_type', 'BharatBenz AC Sleeper')}</div>
                <div style="margin:12px 0;">
                    <div style="font-size:1.6rem; font-weight:900; color:#34d399;">₹{bus_price:,}</div>
                    <div style="font-size:0.78rem; color:#94a3b8;">Duration: {best_bs.get('duration', '9h')} • Overnight Comfort</div>
                </div>
                <div style="margin-bottom:8px;">
                    <span class="pill-savings">💰 Saves ₹{bus_savings:,} vs Flight!</span>
                </div>
                <div style="font-size:0.82rem; color:#cbd5e1; border-top:1px solid rgba(255,255,255,0.08); padding-top:10px;">
                    🚏 Dep: {best_bs.get('departure_time', '21:30')} ➔ Arr: {best_bs.get('arrival_time', '07:30')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # 3. Cab Card
        with tc_col3:
            is_active = current_mode == "cab"
            active_cls = "active-choice" if is_active else ""
            cab_price = best_cb.get('price', 2800)
            cab_savings = max(0, fl_price - cab_price)
            st.markdown(f"""
            <div class="transit-card {active_cls}">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="transit-mode-badge" style="background:rgba(245,158,11,0.2); color:#fbbf24;">🚗 OUTSTATION CAB</span>
                    {'<span class="pill-green">● Active Choice</span>' if is_active else '<span style="font-size:0.75rem; color:#94a3b8;">Alternative</span>'}
                </div>
                <div style="font-size:1.15rem; font-weight:800; color:#ffffff; margin-top:10px;">{best_cb.get('service', 'Outstation Cab')}</div>
                <div style="font-size:0.8rem; color:#94a3b8;">{best_cb.get('car_type', 'AC Sedan')} • {best_cb.get('seating', 4)} Seater</div>
                <div style="margin:12px 0;">
                    <div style="font-size:1.6rem; font-weight:900; color:#fbbf24;">₹{cab_price:,}</div>
                    <div style="font-size:0.78rem; color:#94a3b8;">Duration: {best_cb.get('duration', '6h')} • Door-to-Door</div>
                </div>
                <div style="margin-bottom:8px;">
                    <span class="pill-savings">💰 Saves ₹{cab_savings:,} vs Flight!</span>
                </div>
                <div style="font-size:0.82rem; color:#cbd5e1; border-top:1px solid rgba(255,255,255,0.08); padding-top:10px;">
                    🚪 Doorstep Pickup • Fuel Included
                </div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.markdown("---")

        # Dynamic Booking Pass & Hotel Details
        t_col, h_col = st.columns(2)

        with t_col:
            # Dynamic Boarding Pass / Ticket depending on selected mode
            if current_mode == "bus":
                ticket_title = f"{selected_transit.get('provider')} • AC Sleeper"
                ticket_badge = "CONFIRMED BUS TICKET"
                seat_label = "Berth: L-12 (AC Lower)"
                icon_line = "🚌"
            elif current_mode == "cab":
                ticket_title = f"{selected_transit.get('provider')} • Doorstep Cab"
                ticket_badge = "CAB BOOKING VOUCHER"
                seat_label = "Vehicle: Dedicated AC Sedan"
                icon_line = "🚗"
            else:
                ticket_title = f"{selected_transit.get('provider')} • Flight {selected_transit.get('id')}"
                ticket_badge = "ELECTRONIC BOARDING PASS"
                seat_label = "Seat: 14B (Standard Economy)"
                icon_line = "✈️"

            st.markdown(f"""
            <div class="boarding-pass">
                <div class="boarding-header">
                    <div>
                        <div class="airline-brand">{ticket_title}</div>
                        <div style="font-size:0.8rem; color:#94a3b8;">Status: {ticket_badge}</div>
                    </div>
                    <div class="flight-price-glow">₹{transit_price:,.0f}</div>
                </div>
                <div class="flight-nodes">
                    <div>
                        <div class="node-code">{res['origin'][:3].upper()}</div>
                        <div class="node-city">{res['origin']}</div>
                        <div class="node-time">Dep: {selected_transit.get('departure_time', 'Flexible')}</div>
                    </div>
                    <div class="flight-mid">
                        <div class="flight-duration-tag">{selected_transit.get('duration_str', 'Direct')}</div>
                        <div class="flight-plane-track">
                            <hr><span>{icon_line}</span><hr>
                        </div>
                        <div style="font-size:0.75rem; color:#34d399; font-weight:600;">Direct Journey</div>
                    </div>
                    <div style="text-align:right;">
                        <div class="node-code">{res['destination'][:3].upper()}</div>
                        <div class="node-city">{res['destination']}</div>
                        <div class="node-time">Arr: {selected_transit.get('arrival_time', 'Flexible')}</div>
                    </div>
                </div>
                <div style="font-size:0.85rem; color:#cbd5e1; margin-top:14px; border-top:1px dashed rgba(255,255,255,0.12); padding-top:12px;">
                    <b>Booking Details:</b> {seat_label} • {selected_transit.get('details', '')}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with h_col:
            # Luxury Hotel Card
            stars_count = int(selected_ht.get("stars", 3) or 3)
            stars_render = "★" * stars_count
            amenities = selected_ht.get("amenities") or []
            if not isinstance(amenities, list):
                amenities = [str(amenities)]
            amenity_chips = "".join([f'<span class="amenity-chip">{a.title()}</span>' for a in amenities])

            st.markdown(f"""
            <div class="hotel-card">
                <div class="hotel-header">
                    <div>
                        <div class="hotel-stars">{stars_render}</div>
                        <div class="hotel-name">{selected_ht.get('name', 'Hotel')}</div>
                        <div style="font-size:0.85rem; color:#94a3b8; margin-top:2px;">📍 {res['destination']} • {stars_count}-Star Stay</div>
                    </div>
                    <div>
                        <div class="tariff-amount">₹{selected_ht.get('price_per_night', 0):,}</div>
                        <div class="tariff-label">per night</div>
                    </div>
                </div>
                <div style="margin:14px 0;">
                    {amenity_chips}
                </div>
                <div style="background:rgba(255,255,255,0.04); border-radius:10px; padding:12px; display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.88rem; color:#94a3b8;">Total Stay ({res['num_nights']} Nights):</span>
                    <span style="font-size:1.15rem; font-weight:800; color:#34d399;">₹{hotel_total:,.0f}</span>
                </div>
                <div style="font-size:0.85rem; color:#cbd5e1; margin-top:12px;">
                    <b>Agent Justification:</b> Top guest rating and amenities matching your {travel_style} preference.
                </div>
            </div>
            """, unsafe_allow_html=True)

    # TAB 6: AGENT REASONING TRACE
    with tab_trace:
        st.markdown("### 🧠 Autonomous Agent Reasoning & Execution Trace")
        st.markdown("""
        The LangChain ReAct agent executes a sequential decision graph:
        1. Multi-modal route transit evaluation (Flights, Buses, Cabs) & savings calculation ➔ 
        2. Filter hotel candidates by star-rating & budget cap ➔ 
        3. Fetch live Open-Meteo REST API weather forecast ➔ 
        4. Select outdoor/indoor sights matching daily climate ➔ 
        5. Balance itemized budget.
        """)

        traces = res.get("execution_trace", [])
        for t in traces:
            st.markdown(f"""
            <div style="background:#1e293b; border-left:3px solid #38bdf8; padding:12px 16px; margin-bottom:10px; border-radius:8px; font-size:0.88rem;">
                <span style="color:#38bdf8; font-weight:700;">[{t.get('timestamp')}] {t.get('step')}</span> 
                <span class="pill-cyan">tool: {t.get('tool')}</span>
                <div style="color:#cbd5e1; margin-top:4px;">{t.get('output_summary')}</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.markdown("#### Selection Justification Summary:")
        st.info(res.get("agent_reasoning"))

    st.write("")
    st.markdown("---")

    # Export Section
    st.markdown("### 📥 Download & Export Itinerary")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        json_data = json.dumps(res, indent=2, default=str)
        st.download_button(
            label="📄 Download Structured JSON Itinerary",
            data=json_data,
            file_name=f"itinerary_{res['destination'].lower()}_{res['num_days']}days.json",
            mime="application/json",
            use_container_width=True
        )
    with col_d2:
        st.download_button(
            label="📝 Download Formatted Markdown Plan",
            data=res.get("markdown_output", ""),
            file_name=f"itinerary_{res['destination'].lower()}_{res['num_days']}days.md",
            mime="text/markdown",
            use_container_width=True
        )


if __name__ == "__main__":
    main()
