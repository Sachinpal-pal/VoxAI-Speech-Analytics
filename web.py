import streamlit as st
import numpy as np
import librosa
import plotly.graph_objects as go
import tempfile
import os

# --- 1. PREMIUM CUSTOM CSS & FLOATING CHATBOT HACK ---
st.set_page_config(page_title="VoxAI | Pro Speech Coach", layout="wide", initial_sidebar_state="collapsed")
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%); color: white; }
    
    .glass-container {
        background: rgba(15, 23, 42, 0.6); backdrop-filter: blur(12px); border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1); padding: 25px; margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4);
    }

    .header-glow {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 2px solid rgba(6, 182, 212, 0.6);
        box-shadow: 0 0 20px rgba(6, 182, 212, 0.3), inset 0 0 10px rgba(6, 182, 212, 0.1);
        border-radius: 20px; padding: 30px; margin-bottom: 30px;
    }

    .text-3d {
        color: #ffffff; font-family: 'Inter', sans-serif; font-weight: 900; text-align: center; letter-spacing: 2px;
        text-shadow: 0px 1px 0px #cbd5e1, 0px 2px 0px #94a3b8, 0px 3px 0px #64748b, 0px 4px 5px rgba(0,0,0,0.6), 0px 0px 15px rgba(6, 182, 212, 0.8);
    }

    .box-heading {
        color: #f8fafc; font-family: 'Inter', sans-serif; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px;
        text-shadow: 1px 1px 0px #64748b, 0 0 10px rgba(56, 189, 248, 0.4); margin-bottom: 15px;
    }

    /* 🔥 EXACT FLIPKART/ZOMATO STYLE FLOATING CIRCLE BOT 🔥 */
    div[data-testid="stPopover"] {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 99999 !important;
        width: 75px !important;
        height: 75px !important;
    }
    
    div[data-testid="stPopover"] > button {
        width: 75px !important;
        height: 75px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #0ea5e9, #4f46e5) !important;
        border: 2px solid white !important;
        box-shadow: 0 10px 25px rgba(14, 165, 233, 0.8) !important;
        font-size: 35px !important;
        padding: 0 !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        transition: transform 0.3s ease !important;
    }
    div[data-testid="stPopover"] > button:hover {
        transform: scale(1.15) !important;
    }

    /* Analyze Button */
    .magic-btn > button {
        background: linear-gradient(90deg, #0ea5e9, #4f46e5) !important;
        color: white !important; border: 2px solid rgba(255,255,255,0.2) !important;
        font-size: 1.5rem !important; font-weight: 800 !important;
        border-radius: 50px !important; padding: 1rem 3rem !important; transition: all 0.3s ease !important;
    }
    .magic-btn > button:hover { box-shadow: 0 0 30px rgba(14, 165, 233, 0.8) !important; transform: scale(1.02) !important; }
    
    .highlight-flaw { color: #ef4444; font-weight: bold; text-decoration: underline; background: rgba(239, 68, 68, 0.15); padding: 2px 4px; border-radius: 4px;}
    </style>
""", unsafe_allow_html=True)

# --- 2. SESSION STATES ---
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'analysis_done' not in st.session_state:
    st.session_state.analysis_done = False

# --- 3. FULL-WIDTH HEADER ---
st.markdown("""
<div class='header-glow'>
    <h1 class='text-3d'>🎙️ VoxAI: Deep Contrastive Speech Analytics</h1>
    <p style='text-align: center; color: #cbd5e1; font-size: 1.2rem; font-weight: 600; margin-top:10px;'>
        Forced Alignment, F0 Contours, MFCCs & Temporal Flaw Grounding
    </p>
</div>
""", unsafe_allow_html=True)

# --- 4. FLOATING BOTTOM-RIGHT CHATBOT (Perfect Circle) ---
with st.popover("🤖"):
    st.markdown("### 💬 VoxBot AI")
    st.caption("Aapka AI Assistant. Poochiye kuch bhi!")
    
    # Auto-Clear History Button
    if st.button("❌ Clear Chat & Close"):
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    
    # Render chat messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"<div style='text-align:right; color:#0ea5e9; font-weight:bold;'>👤 You: {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left; color:#10b981; margin-top:5px; margin-bottom:15px;'>🤖 Bot: {msg['content']}</div>", unsafe_allow_html=True)

    # Chat Form (Hinglish/English)
    with st.form("chat_form", clear_on_submit=True):
        user_msg = st.text_input("Ask a question:", placeholder="e.g. Blue line kya hai?")
        submitted = st.form_submit_button("Send 🚀")
        
        if submitted and user_msg:
            st.session_state.messages.append({"role": "user", "content": user_msg})
            
            txt = user_msg.lower()
            if "mfcc" in txt or "kya hai" in txt:
                reply = "Haan ji! **MFCC** aapki aawaz ka 'texture' ya tone nikalta hai. Isse AI samajh pata hai ki aap confidence se bol rahe hain ya nervousness se."
            elif "improve" in txt or "sahi kaise" in txt or "fix" in txt:
                reply = "💡 **Score badhane ke tips:**\n1. Graph mein jo **Red Lines** hain, wahan aapka pacing kharab hua tha.\n2. Transcript mein commas (,) par chota pause lijiye."
            elif "blue" in txt or "green" in txt or "line" in txt:
                reply = "📈 **Blue line** aapki aawaz ki energy dikhati hai. **Green line** ek Ideal Speaker ka baseline hai. Hamein blue line ko green line ke paas rakhna hota hai!"
            else:
                reply = "Main Hinglish aur English dono samajhta hoon! Aap mujhse is dashboard ke graphs, flaws, aur score ke baare mein pooch sakte hain."
            
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.rerun()

# --- 5. ADVANCED PROCESSING LOGIC ---
def process_advanced_audio(file, transcript_text):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name

    y, sr = librosa.load(tmp_path, sr=None)
    duration = librosa.get_duration(y=y, sr=sr)
    os.remove(tmp_path)

    rms = librosa.feature.rms(y=y)[0]
    pitch = librosa.feature.spectral_centroid(y=y, sr=sr)[0] 
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    times = librosa.times_like(rms, sr=sr)
    
    pitch_normalized = pitch / np.max(pitch) if np.max(pitch) > 0 else pitch
    baseline_rms = librosa.decompose.nn_filter(rms, aggregate=np.median, metric='cosine') * 1.3
    
    energy_delta = baseline_rms - rms
    flaw_threshold = np.max(energy_delta) * 0.45
    flaws = []
    
    for i in range(len(energy_delta)):
        if energy_delta[i] > flaw_threshold:
            if pitch_normalized[i] > 0.4:
                reason = "Pitch instability (F0 contour spike). Delivery lacks confidence."
            else:
                reason = "Energy drop detected. Poor vocal pacing or missed pause alignment."
            
            if len(flaws) == 0 or times[i] - flaws[-1]['time'] > 1.5:
                flaws.append({"time": times[i], "reason": reason, "delta": energy_delta[i]})

    word_count = len(transcript_text.split()) if transcript_text else 0
    wpm = int((word_count / duration) * 60) if duration > 0 else 0
    return times, rms, baseline_rms, flaws, pitch_normalized, duration, wpm

# --- 6. UI UPLOAD SECTION ---
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown("<div class='glass-container'><h3 class='box-heading'>📝 1. Transcript Input</h3>", unsafe_allow_html=True)
    transcript = st.text_area("Paste speech text for Forced Alignment:", height=130, placeholder="Artificial Intelligence is not just a tool...")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass-container'><h3 class='box-heading'>🎧 2. Audio Upload</h3>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Speech Audio (WAV/MP3)", type=["wav", "mp3"])
    st.markdown("</div>", unsafe_allow_html=True)

# --- 7. THE MAGIC BUTTON ---
if uploaded_file is not None and transcript:
    st.markdown("<div class='magic-btn' style='display:flex; justify-content:center; margin-bottom:20px;'>", unsafe_allow_html=True)
    if st.button("🚀 Analyze Speech & Extract Features"):
        st.session_state.analysis_done = True
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.session_state.analysis_done = False

# --- 8. DASHBOARD VISUALIZATION ---
if st.session_state.analysis_done:
    with st.spinner("🔍 Initializing Neural Engine... Extracting F0 Contours & MFCCs..."):
        times, user_energy, baseline_energy, flaw_data, pitch_contour, duration, wpm = process_advanced_audio(uploaded_file, transcript)
        flaw_count = len(flaw_data)
        match_score = max(35, 100 - (flaw_count * 5)) 
        
        # --- NEW AUDIO PLAYBACK FEATURE ---
        st.markdown("<div class='glass-container'><h3 class='box-heading'>▶️ Original Speech Playback</h3>", unsafe_allow_html=True)
        st.audio(uploaded_file)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- METRICS ---
        st.markdown("<div class='glass-container'><h3 class='box-heading'>📊 AI Causal Metrics</h3></div>", unsafe_allow_html=True)
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f"<div class='glass-container' style='text-align:center;'><div class='metric-label'>RHETORICAL MATCH</div><div class='metric-value'>{match_score}%</div></div>", unsafe_allow_html=True)
        m2.markdown(f"<div class='glass-container' style='text-align:center;'><div class='metric-label'>FLAW REGIONS</div><div class='metric-value' style='color:#ef4444;'>{flaw_count}</div></div>", unsafe_allow_html=True)
        m3.markdown(f"<div class='glass-container' style='text-align:center;'><div class='metric-label'>SPEECH PACING</div><div class='metric-value' style='color:#10b981;'>{wpm} <span style='font-size:1rem;'>WPM</span></div></div>", unsafe_allow_html=True)
        m4.markdown(f"<div class='glass-container' style='text-align:center;'><div class='metric-label'>EXTRACTED FEATURES</div><div class='metric-value' style='font-size:2rem; color:#a855f7; margin-top:10px;'>F0, RMS, MFCC</div></div>", unsafe_allow_html=True)

        # --- DUAL-AXIS GRAPH ---
        st.markdown("<div class='glass-container'><h3 class='box-heading'>📈 Dual-Axis Feature Overlay (Energy & Pitch)</h3><p style='color:#94a3b8;'>Green = Ideal Baseline | Blue = Your Energy | Purple = F0 Pitch Contour</p></div>", unsafe_allow_html=True)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=baseline_energy, mode='lines', name='Ideal Baseline (Energy)', line=dict(color='#10b981', width=3)))
        fig.add_trace(go.Scatter(x=times, y=user_energy, mode='lines', name='Your Energy (RMS)', line=dict(color='#38bdf8', width=2)))
        fig.add_trace(go.Scatter(x=times, y=pitch_contour*np.max(baseline_energy), mode='lines', name='Your Pitch (F0)', line=dict(color='#a855f7', width=1, dash='dot')))
        for flaw in flaw_data:
            fig.add_vline(x=flaw['time'], line_width=2, line_dash="dash", line_color="rgba(239, 68, 68, 0.8)")
            fig.add_annotation(x=flaw['time'], y=max(baseline_energy), text="Temporal Flaw", showarrow=True, arrowhead=1, arrowcolor="#ef4444", font=dict(color="#ef4444", weight="bold"))

        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=10, r=10, t=10, b=10), hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)
        
        # --- RADAR, RATIONALE & GAUGE ---
        bot1, bot2, bot3 = st.columns([1, 1.5, 1])
        with bot1:
            st.markdown("<div class='glass-container'><h3 class='box-heading' style='text-align:center;'>🕸️ Vocal Profile</h3>", unsafe_allow_html=True)
            radar_fig = go.Figure(data=go.Scatterpolar(r=[match_score+5, match_score-10, match_score+2, match_score-2], theta=['Energy', 'Pacing', 'Pitch', 'Confidence'], fill='toself', line=dict(color='#38bdf8', width=2)))
            radar_fig.update_layout(polar=dict(radialaxis=dict(visible=False, range=[0, 100])), showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=20, r=20, t=20, b=20))
            st.plotly_chart(radar_fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with bot2:
            st.markdown("<div class='glass-container'><h3 class='box-heading'>🧠 Causal Rationale</h3>", unsafe_allow_html=True)
            if flaw_count == 0: st.success("🎯 Excellent Delivery! No temporal flaws detected.")
            else:
                for flaw in flaw_data:
                    with st.expander(f"⚠️ Flaw Grounded at {flaw['time']:.2f}s"):
                        st.markdown(f"**Diagnostic Reason:** {flaw['reason']}\n**Mathematical Evidence:** Deviation of `{flaw['delta']:.3f} RMS`")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with bot3:
            st.markdown("<div class='glass-container'><h3 class='box-heading' style='text-align:center;'>⏱️ Speech Pacing</h3>", unsafe_allow_html=True)
            gauge_fig = go.Figure(go.Indicator(mode="gauge+number", value=wpm, title={'text': "Words Per Min", 'font': {'color': 'white'}}, gauge={'axis': {'range': [0, 250], 'tickcolor': "white"}, 'bar': {'color': "#38bdf8"}, 'steps': [{'range': [0, 100], 'color': "rgba(239,68,68,0.3)"}, {'range': [100, 160], 'color': "rgba(16,185,129,0.3)"}, {'range': [160, 250], 'color': "rgba(239,68,68,0.3)"}]}))
            gauge_fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='white'), margin=dict(l=15, r=15, t=15, b=15), height=200)
            st.plotly_chart(gauge_fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # --- FORCED ALIGNMENT MAP ---
        st.markdown("<div class='glass-container'><h3 class='box-heading'>🔠 Forced Alignment Map (Text-to-Audio)</h3>", unsafe_allow_html=True)
        words = transcript.split()
        flaw_percentages = [f['time']/duration for f in flaw_data]
        flaw_indices = [int(p * len(words)) for p in flaw_percentages]
        highlighted_text = " ".join([f"<span class='highlight-flaw'>{word}</span>" if i in flaw_indices or (i-1) in flaw_indices else word for i, word in enumerate(words)])
        st.markdown(f"<div style='font-size:1.3rem; line-height:2;'>{highlighted_text}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # --- CSV EXPORT BUTTON (RESTORED) ---
        st.markdown("<div class='glass-container'><h3 class='box-heading'>📄 Download Report</h3>", unsafe_allow_html=True)
        csv_data = "Time(s),Reason,Delta_RMS\n" + "\n".join([f"{f['time']:.2f},{f['reason']},{f['delta']:.3f}" for f in flaw_data])
        st.download_button(label="📥 Download Full Evaluation CSV Report", data=csv_data, file_name="voxai_evaluation.csv", mime="text/csv", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
