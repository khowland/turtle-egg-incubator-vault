"""
=============================================================================
Module:     pages/1_dashboard.py
Project:    Incubator Vault v6.0 — Wildlife In Need Center (WINC)
Purpose:    Main command center showing KPIs, biological alerts, and 
            real-time incubation analytics.
Author:     Agent Zero (Automated Build)
Created:    2026-04-06
=============================================================================
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from utils.db import get_supabase_client
from utils.session import render_sidebar
from utils.css import BASE_CSS

# Configure Page
st.set_page_config(page_title="Dashboard | Vault Pro", page_icon="📊", layout="wide")
st.markdown(BASE_CSS, unsafe_allow_html=True)

# Persistent Sidebar
render_sidebar()

# =============================================================================
# SECTION: Data Fetching
# =============================================================================

def load_kpis(supabase):
    """Calculates system-wide KPIs for active hatching season."""
    try:
        res = supabase.table("egg").select("status, current_stage").eq("is_deleted", False).execute()
        df = pd.DataFrame(res.data)
        if df.empty: return 0, 0, 0, 0
        
        active = len(df[df['status'] == 'Active'])
        pipping = len(df[df['current_stage'] == 'Pipping'])
        hatched = len(df[df['status'] == 'Hatched'])
        lost = len(df[df['status'] == 'Dead'])
        
        return active, pipping, hatched, lost
    except Exception as e:
        # Surface connection errors instead of silently returning zeros
        print(f"KPI load error: {e}")
        return 0, 0, 0, 0

def load_alerts(supabase):
    """Implementation of Biological Guardrails G1-G7 per Requirements §8."""
    # 1. Mature Eggs > 60 Days (G1)
    # 2. Critical Health Flags (G2/G3 - Molding/Leaking)
    try:
        res = supabase.table("egg").select(
            "egg_id, current_stage, bin:bin_id(harvest_date, bin_label)"
        ).eq("status", "Active").eq("is_deleted", False).execute()
        
        alerts = []
        for egg in res.data:
            harvest = datetime.fromisoformat(egg['bin']['harvest_date'].split('+')[0])
            days = (datetime.now().date() - harvest.date()).days
            
            if egg['current_stage'] == 'Mature' and days > 60:
                alerts.append({"id": egg['egg_id'], "type": "CRITICAL", "msg": f"Mature for {days} days (Potential Stall)"})
            
            # Check latest observation for health flags
            obs = supabase.table("EggObservation").select("molding, leaking").eq("egg_id", egg['egg_id']).order("timestamp", desc=True).limit(1).execute()
            if obs.data and (obs.data[0]['molding'] or obs.data[0]['leaking']):
                alerts.append({"id": egg['egg_id'], "type": "HEALTH", "msg": "Active Molding/Leaking detected"})
        
        return alerts
    except Exception as e:
        # Surface guardrail query errors instead of hiding them
        print(f"Alert load error: {e}")
        return []

# =============================================================================
# SECTION: UI Layout
# =============================================================================

st.markdown("<h1>Hatchery Command Center</h1>", unsafe_allow_html=True)

supabase = get_supabase_client()
active, pipping, hatched, lost = load_kpis(supabase)

# --- KPI ROW ---
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f"<div class='glass-card'><div style='color:#10B981; font-weight:800;'>ACTIVE</div><div style='font-size:3rem; font-weight:800;'>{active}</div></div>", unsafe_allow_html=True)
with c2: st.markdown(f"<div class='glass-card'><div style='color:#3B82F6; font-weight:800;'>PIPPING</div><div style='font-size:3rem; font-weight:800;'>{pipping}</div></div>", unsafe_allow_html=True)
with c3: st.markdown(f"<div class='glass-card'><div style='color:#F59E0B; font-weight:800;'>HATCHED</div><div style='font-size:3rem; font-weight:800;'>{hatched}</div></div>", unsafe_allow_html=True)
with c4: st.markdown(f"<div class='glass-card'><div style='color:#EF4444; font-weight:800;'>LOST</div><div style='font-size:3rem; font-weight:800;'>{lost}</div></div>", unsafe_allow_html=True)

# --- ALERT CENTER ---
st.markdown("### 🚨 Biological Guardrails")
alerts = load_alerts(supabase)
if alerts:
    for a in alerts:
        color = "#EF4444" if a['type'] == "CRITICAL" else "#F59E0B"
        st.markdown(f"""
        <div class='glass-card' style='border-left: 5px solid {color}; padding: 15px; margin-bottom: 10px;'>
            <span style='font-weight:800; color:{color};'>{a['type']}</span> | 
            <b>{a['id']}</b>: {a['msg']}
        </div>
        """, unsafe_allow_html=True)
else:
    st.success("✅ All systems nominal. No biological anomalies detected.")

# --- ANALYTICS ROW ---
st.markdown("### 📈 Season Analytics")
c_left, c_right = st.columns(2)

# Distribution Chart
try:
    res = supabase.table("egg").select("current_stage").eq("status", "Active").execute()
    if res.data:
        df_stage = pd.DataFrame(res.data)['current_stage'].value_counts().reset_index()
        fig = px.pie(df_stage, values='count', names='current_stage', title="Stage Distribution", hole=0.4, 
                     color_discrete_sequence=px.colors.sequential.Emrld)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        c_left.plotly_chart(fig, use_container_width=True)
    else:
        c_left.info("No data for distribution analysis.")
except Exception as e:
    # Surface chart rendering errors — don't silently hide them
    c_left.error(f"⚠️ Chart error: {e}")

# Success Trends Placeholder
c_right.markdown("<div class='glass-card' style='height:350px; display:flex; align-items:center; justify-content:center;'><h4>Hatch Rate Trends coming in Phase D</h4></div>", unsafe_allow_html=True)
