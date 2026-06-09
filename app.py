import streamlit as st
import pandas as pd
import joblib
import time
import io

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RecruitAI · Resume Screener",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,400&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #07090f; color: #dde1ec; }
.block-container { padding-top: 1.8rem !important; padding-bottom: 3rem !important; max-width: 1200px !important; }
#MainMenu, footer, header { visibility: hidden; }

/* ── Top nav bar ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.9rem 1.6rem; background: #0d1117;
    border: 1px solid rgba(255,255,255,0.06); border-radius: 14px;
    margin-bottom: 1.6rem;
}
.topbar-brand {
    font-family: 'Syne', sans-serif; font-size: 1.15rem; font-weight: 800;
    background: linear-gradient(135deg, #e2e8f0, #818cf8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.01em;
}
.topbar-badge {
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em;
    background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.28);
    color: #818cf8; padding: 0.25rem 0.75rem; border-radius: 99px;
}

/* ── Tab overrides ── */
div[data-testid="stTabs"] [role="tablist"] {
    background: #0d1117 !important; border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.06) !important; padding: 4px !important; gap: 4px !important;
}
div[data-testid="stTabs"] [role="tab"] {
    border-radius: 8px !important; font-family: 'Syne', sans-serif !important;
    font-size: 0.82rem !important; font-weight: 600 !important;
    color: #6b7280 !important; padding: 0.5rem 1.2rem !important;
    border: none !important;
}
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    background: rgba(99,102,241,0.18) !important; color: #818cf8 !important;
}

/* ── Cards ── */
.card {
    background: #0d1117; border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px; padding: 1.6rem 1.8rem; margin-bottom: 1rem;
}
.card-title {
    font-family: 'Syne', sans-serif; font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.14em; text-transform: uppercase; color: #4b5563;
    margin-bottom: 1.1rem; display: flex; align-items: center; gap: 0.5rem;
}
.card-title::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.04); }

/* ── Inputs ── */
div[data-testid="stTextInput"] label,
div[data-testid="stNumberInput"] label,
div[data-testid="stSlider"] label,
div[data-testid="stSelectbox"] label {
    font-size: 0.8rem !important; font-weight: 500 !important;
    color: #9ca3af !important; letter-spacing: 0.02em !important;
}
div[data-testid="stTextInput"] input,
div[data-testid="stNumberInput"] input {
    background: #111827 !important; border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important; color: #e2e8f0 !important;
    font-size: 0.9rem !important;
}
div[data-testid="stTextInput"] input:focus,
div[data-testid="stNumberInput"] input:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: #111827 !important; border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 10px !important; color: #e2e8f0 !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] { margin-top: 0.2rem; }

/* ── Score ring ── */
.score-ring-wrap {
    display: flex; flex-direction: column; align-items: center;
    justify-content: center; padding: 1.4rem 0;
}
.score-ring-label {
    font-size: 0.72rem; color: #6b7280; letter-spacing: 0.08em;
    text-transform: uppercase; margin-top: 0.5rem; font-weight: 500;
}

/* ── Score bars ── */
.bar-row { margin-bottom: 0.75rem; }
.bar-meta { display: flex; justify-content: space-between; font-size: 0.77rem; color: #9ca3af; margin-bottom: 0.3rem; }
.bar-track { background: rgba(255,255,255,0.05); border-radius: 99px; height: 5px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 99px; }

/* ── Verdict banner ── */
.verdict-pass {
    background: linear-gradient(135deg, #022c22 0%, #064e3b 100%);
    border: 1px solid rgba(52,211,153,0.25); border-radius: 14px;
    padding: 1.4rem 1.8rem; display: flex; align-items: center; gap: 1.2rem;
}
.verdict-fail {
    background: linear-gradient(135deg, #1a0a0a 0%, #2d1515 100%);
    border: 1px solid rgba(248,113,113,0.2); border-radius: 14px;
    padding: 1.4rem 1.8rem; display: flex; align-items: center; gap: 1.2rem;
}
.verdict-icon { font-size: 2rem; flex-shrink: 0; }
.verdict-pct {
    font-family: 'Syne', sans-serif; font-size: 2.4rem;
    font-weight: 800; line-height: 1;
}
.verdict-tag { font-family: 'Syne', sans-serif; font-size: 0.85rem; font-weight: 700; margin-bottom: 0.15rem; }
.verdict-sub { font-size: 0.75rem; color: #9ca3af; }

/* ── Tip rows ── */
.tip-row {
    display: flex; align-items: flex-start; gap: 0.7rem;
    padding: 0.6rem 0; border-bottom: 1px solid rgba(255,255,255,0.04);
    font-size: 0.82rem; color: #9ca3af; line-height: 1.5;
}
.tip-icon { flex-shrink: 0; }

/* ── Bulk stats ── */
.stat-box {
    background: #0d1117; border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px; padding: 1.1rem 1.4rem; text-align: center;
}
.stat-val { font-family: 'Syne', sans-serif; font-size: 2rem; font-weight: 800; line-height: 1; }
.stat-lbl { font-size: 0.72rem; color: #6b7280; margin-top: 0.3rem; font-weight: 500; }

/* ── Status pills ── */
.pill-pass {
    display: inline-block; background: rgba(52,211,153,0.12);
    border: 1px solid rgba(52,211,153,0.3); color: #34d399;
    font-size: 0.7rem; font-weight: 700; padding: 0.2rem 0.65rem; border-radius: 99px;
    letter-spacing: 0.06em;
}
.pill-fail {
    display: inline-block; background: rgba(248,113,113,0.1);
    border: 1px solid rgba(248,113,113,0.25); color: #f87171;
    font-size: 0.7rem; font-weight: 700; padding: 0.2rem 0.65rem; border-radius: 99px;
    letter-spacing: 0.06em;
}

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    padding: 0.7rem 1.6rem !important; font-family: 'Syne', sans-serif !important;
    font-size: 0.85rem !important; font-weight: 700 !important;
    letter-spacing: 0.04em !important; transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #4338ca, #4f46e5) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.3) !important;
    transform: translateY(-1px) !important;
}

/* ── File uploader ── */
div[data-testid="stFileUploader"] {
    background: #0d1117 !important; border: 1.5px dashed rgba(99,102,241,0.25) !important;
    border-radius: 14px !important;
}

/* ── Dataframe ── */
div[data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
EDU_MAP   = {"High School": 0, "Bachelors": 1, "Masters": 2, "PhD": 3}
EDU_LABELS = list(EDU_MAP.keys())

REQUIRED_COLS = [
    "years_experience", "skills_match_score", "education_level",
    "project_count", "resume_length", "github_activity"
]

def engineer(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived features expected by the model."""
    d = df.copy()
    # Map education strings to integers; leave alone if already numeric
    if d["education_level"].apply(lambda x: isinstance(x, str)).any():
        d["education_level"] = d["education_level"].map(EDU_MAP)
    d["education_level"]  = pd.to_numeric(d["education_level"], errors="coerce").fillna(0).astype(int)
    d["exp_x_skills"]    = d["years_experience"] * d["skills_match_score"]
    d["resume_per_proj"] = d["resume_length"]    / (d["project_count"] + 1)
    return d

def score_bars(yrs, skills, edu_idx, proj, github):
    return {
        "Skills Match":      min(skills, 100),
        "Experience":        min(yrs * 3.33, 100),
        "Education":         edu_idx * 33.3,
        "GitHub Activity":   min(github / 10, 100),
        "Project Portfolio": min(proj * 5, 100),
    }

def tips_for(yrs, skills, proj, github, rlen, edu_idx):
    t = []
    # ── Weaknesses ──
    if skills < 50:   t.append(("📚", f"Skills match is low at {skills:.0f}% — focus on role-specific certifications or upskilling."))
    elif skills < 70: t.append(("📚", f"Skills match is moderate at {skills:.0f}% — closing the gap with targeted training would help."))
    if yrs < 2:       t.append(("💼", f"Only {yrs} year(s) of experience — emphasise internships, freelance, or part-time work."))
    elif yrs < 4:     t.append(("💼", f"{yrs} years of experience is on the lower side for senior roles — consider applying to mid-level positions."))
    if github < 50:   t.append(("🐙", f"GitHub activity is low ({github} commits) — shortlisted candidates in our dataset average 393 commits."))
    elif github < 200:t.append(("🐙", f"GitHub activity ({github} commits) is below the shortlisted average of 393 commits — more public contributions would strengthen the profile."))
    if proj < 3:      t.append(("🛠", f"Only {proj} project(s) listed — adding side projects or open-source contributions would improve this."))
    if rlen > 2000:   t.append(("✂️", f"Resume is {rlen} words — most recruiters prefer 400–800 words; consider trimming."))
    elif rlen < 300:  t.append(("📄", f"Resume is very short at {rlen} words — expand with more detail on experience and projects."))
    # ── Strengths ──
    if skills >= 80:  t.append(("✅", f"Excellent skills match at {skills:.0f}% — strong alignment with the job requirements."))
    if yrs >= 5:      t.append(("✅", f"{yrs} years of experience is solid — candidate has substantial industry exposure."))
    if github >= 393: t.append(("✅", f"High GitHub activity ({github} commits) — above the shortlisted candidate average of 393 commits."))
    if proj >= 8:     t.append(("✅", f"{proj} projects demonstrates a strong, well-rounded portfolio."))
    if edu_idx >= 2:  t.append(("✅", f"Advanced degree ({EDU_LABELS[edu_idx]}) adds academic credibility to the profile."))
    if not t:         t.append(("🌟", "Solid profile with no major red flags — competitive candidate overall."))
    return t

@st.cache_resource
def load_model():
    return joblib.load("models/random_forest.pkl")

def run_model(df_engineered):
    model = load_model()
    cols  = ["years_experience","skills_match_score","education_level",
             "project_count","resume_length","github_activity",
             "exp_x_skills","resume_per_proj"]
    preds = model.predict(df_engineered[cols])
    probas = model.predict_proba(df_engineered[cols])[:,1]
    return preds, probas

# ── Top bar ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
  <div class="topbar-brand">⬡ RecruitAI</div>
  <div class="topbar-badge">Random Forest v1</div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_single, tab_bulk, tab_guide = st.tabs([
    "  🔍  Single Candidate  ",
    "  📂  Bulk Analysis  ",
    "  📋  CSV Guide  ",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SINGLE CANDIDATE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_single:
    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        # ── Identity ─────────────────────────────────────────────────────────
        st.markdown('<div class="card"><div class="card-title">Candidate Identity</div>', unsafe_allow_html=True)
        candidate_name = st.text_input("Full Name", placeholder="e.g. Budi Santoso")
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Qualifications ────────────────────────────────────────────────────
        st.markdown('<div class="card"><div class="card-title">Qualifications & Experience</div>', unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            years_experience = st.number_input("Years of Experience", 0, 30, 3,
                help="Total years of relevant professional experience")
        with c4:
            education_level = st.selectbox("Education Level", EDU_LABELS, index=1)

        skills_match_score = st.slider("Skills Match Score (%)", 0.0, 100.0, 65.0, 0.5,
            help="How well candidate's skills align with the job description (0 = no match, 100 = perfect match)")

        # Live skill bar
        clr = "#34d399" if skills_match_score >= 60 else "#fbbf24" if skills_match_score >= 35 else "#f87171"
        qual_label = "Strong match" if skills_match_score >= 60 else "Partial match" if skills_match_score >= 35 else "Weak match"
        st.markdown(f"""
        <div style="margin-top:-0.2rem; margin-bottom:0.5rem;">
          <div style="display:flex; justify-content:space-between; font-size:0.73rem; color:#6b7280; margin-bottom:0.3rem;">
            <span>{qual_label}</span><span style="color:{clr}; font-weight:600;">{skills_match_score:.0f}%</span>
          </div>
          <div class="bar-track"><div class="bar-fill" style="width:{skills_match_score}%; background:{clr};"></div></div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── Portfolio ─────────────────────────────────────────────────────────
        st.markdown('<div class="card"><div class="card-title">Portfolio & Digital Presence</div>', unsafe_allow_html=True)
        c5, c6 = st.columns(2)
        with c5:
            project_count = st.number_input("Number of Projects", 0, 50, 4,
                help="Completed projects (work, academic, or personal)")
        with c6:
            github_activity = st.number_input("GitHub Commits", 0, 2000, 60,
                help="Total public commits / contributions on GitHub. Benchmark: shortlisted candidates in the training dataset average 393 commits.")
        resume_length = st.number_input("Resume Word Count", 100, 5000, 850,
            help="Approximate word count — aim for 400–800 words for most roles")
        st.markdown('</div>', unsafe_allow_html=True)

        analyse_btn = st.button("🔍  Analyse Candidate", use_container_width=True)

    # ── Results ──────────────────────────────────────────────────────────────
    with right:
        edu_idx = EDU_MAP[education_level]
        exp_x_skills    = years_experience * skills_match_score
        resume_per_proj = resume_length / (project_count + 1)

        # Live computed metrics (always visible)
        st.markdown('<div class="card"><div class="card-title">Computed Signals</div>', unsafe_allow_html=True)
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#6366f1">{exp_x_skills:.0f}</div><div class="stat-lbl">Exp × Skills</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#6366f1">{resume_per_proj:.0f}</div><div class="stat-lbl">Words / Project</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if analyse_btn:
            with st.spinner("Running inference…"):
                time.sleep(0.3)
                try:
                    row = pd.DataFrame([[
                        years_experience, skills_match_score, edu_idx,
                        project_count, resume_length, github_activity,
                        exp_x_skills, resume_per_proj
                    ]], columns=[
                        "years_experience","skills_match_score","education_level",
                        "project_count","resume_length","github_activity",
                        "exp_x_skills","resume_per_proj"
                    ])
                    preds, probas = run_model(row)
                    prediction = preds[0]; probability = probas[0]
                    display_name = candidate_name.strip() or "Candidate"

                    if prediction == 1:
                        st.markdown(f"""
                        <div class="verdict-pass">
                          <div class="verdict-icon">✅</div>
                          <div>
                            <div class="verdict-tag" style="color:#34d399;">{display_name} — Shortlisted</div>
                            <div class="verdict-pct" style="color:#6ee7b7;">{probability:.1%}</div>
                            <div class="verdict-sub">Shortlist probability</div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="verdict-fail">
                          <div class="verdict-icon">❌</div>
                          <div>
                            <div class="verdict-tag" style="color:#f87171;">{display_name} — Not Shortlisted</div>
                            <div class="verdict-pct" style="color:#fca5a5;">{1-probability:.1%}</div>
                            <div class="verdict-sub">Rejection probability</div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Score breakdown
                    st.markdown('<br><div class="card-title" style="font-size:0.68rem; letter-spacing:0.14em; color:#4b5563; font-family:\'Syne\',sans-serif; font-weight:700; text-transform:uppercase;">Profile Score Breakdown</div>', unsafe_allow_html=True)
                    bars = score_bars(years_experience, skills_match_score, edu_idx, project_count, github_activity)
                    for lbl, pct in bars.items():
                        c = "#34d399" if pct >= 70 else "#fbbf24" if pct >= 40 else "#f87171"
                        st.markdown(f"""
                        <div class="bar-row">
                          <div class="bar-meta"><span>{lbl}</span><span style="color:{c}; font-weight:600;">{pct:.0f}%</span></div>
                          <div class="bar-track"><div class="bar-fill" style="width:{pct}%; background:{c};"></div></div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Tips
                    tips = tips_for(years_experience, skills_match_score, project_count, github_activity, resume_length, edu_idx)
                    st.markdown('<br><div class="card-title" style="font-size:0.68rem; letter-spacing:0.14em; color:#4b5563; font-family:\'Syne\',sans-serif; font-weight:700; text-transform:uppercase;">Recruiter Notes</div>', unsafe_allow_html=True)
                    for icon, tip in tips:
                        st.markdown(f'<div class="tip-row"><span class="tip-icon">{icon}</span><span>{tip}</span></div>', unsafe_allow_html=True)

                except FileNotFoundError:
                    st.warning("⚠️ Model not found at `models/random_forest.pkl` — place your trained model there and restart.")
        else:
            # Profile preview bars (always live)
            st.markdown('<div class="card"><div class="card-title">Live Profile Preview</div>', unsafe_allow_html=True)
            bars = score_bars(years_experience, skills_match_score, edu_idx, project_count, github_activity)
            for lbl, pct in bars.items():
                c = "#34d399" if pct >= 70 else "#fbbf24" if pct >= 40 else "#f87171"
                st.markdown(f"""
                <div class="bar-row">
                  <div class="bar-meta"><span>{lbl}</span><span style="color:{c}; font-weight:600;">{pct:.0f}%</span></div>
                  <div class="bar-track"><div class="bar-fill" style="width:{pct}%; background:{c};"></div></div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="text-align:center; padding:1.2rem 0; color:#4b5563; font-size:0.82rem;">
                Fill in the form and click <strong style="color:#6366f1;">Analyse Candidate</strong> for the full prediction.
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — BULK ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_bulk:

    up_col, info_col = st.columns([1.1, 0.9], gap="large")

    with up_col:
        st.markdown('<div class="card"><div class="card-title">Upload CSV File</div>', unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Drop your CSV here or click to browse",
            type=["csv"],
            help="CSV must contain the required columns. See the CSV Guide tab for format details."
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if uploaded:
            try:
                df_raw = pd.read_csv(uploaded)

                # ── Validation ────────────────────────────────────────────────
                missing = [c for c in REQUIRED_COLS if c not in df_raw.columns]
                if missing:
                    st.error(f"Missing columns: **{', '.join(missing)}** — check the CSV Guide tab.")
                    st.stop()

                st.success(f"✅ File loaded — **{len(df_raw):,} rows** detected.")

                # Preview
                with st.expander("Preview uploaded data", expanded=False):
                    st.dataframe(df_raw.head(10), use_container_width=True)

                run_bulk = st.button("⚡  Run Bulk Analysis", use_container_width=True)

                if run_bulk:
                    with st.spinner(f"Analysing {len(df_raw):,} candidates…"):
                        time.sleep(0.4)
                        df_eng = engineer(df_raw[REQUIRED_COLS].copy())
                        preds, probas = run_model(df_eng)

                    df_results = df_raw.copy()
                    df_results["shortlist_probability"] = (probas * 100).round(1)
                    df_results["prediction"]            = preds
                    df_results["verdict"]               = df_results["prediction"].map({1: "Shortlisted", 0: "Not Shortlisted"})
                    df_results = df_results.sort_values("shortlist_probability", ascending=False).reset_index(drop=True)
                    df_results.index += 1

                    st.session_state["bulk_results"] = df_results
                    st.session_state["bulk_ran"] = True

            except Exception as e:
                st.error(f"Error processing file: {e}")

    with info_col:
        if st.session_state.get("bulk_ran") and "bulk_results" in st.session_state:
            df_res = st.session_state["bulk_results"]
            total      = len(df_res)
            n_pass     = int(df_res["prediction"].sum())
            n_fail     = total - n_pass
            pass_rate  = n_pass / total * 100
            avg_prob   = df_res["shortlist_probability"].mean()

            # KPI row
            k1, k2, k3, k4 = st.columns(4)
            with k1: st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#6366f1">{total}</div><div class="stat-lbl">Total</div></div>', unsafe_allow_html=True)
            with k2: st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#34d399">{n_pass}</div><div class="stat-lbl">Shortlisted</div></div>', unsafe_allow_html=True)
            with k3: st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#f87171">{n_fail}</div><div class="stat-lbl">Rejected</div></div>', unsafe_allow_html=True)
            with k4: st.markdown(f'<div class="stat-box"><div class="stat-val" style="color:#fbbf24">{pass_rate:.0f}%</div><div class="stat-lbl">Pass Rate</div></div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Filter
            filter_opt = st.selectbox("Filter results", ["All Candidates", "Shortlisted Only", "Not Shortlisted Only"])
            df_show = df_res.copy()
            if filter_opt == "Shortlisted Only":    df_show = df_res[df_res["prediction"] == 1]
            elif filter_opt == "Not Shortlisted Only": df_show = df_res[df_res["prediction"] == 0]

        else:
            st.markdown("""
            <div style="border:1.5px dashed rgba(99,102,241,0.18); border-radius:14px; padding:3rem 2rem; text-align:center; color:#4b5563;">
                <div style="font-size:2.5rem; margin-bottom:0.8rem;">📂</div>
                <div style="font-family:'Syne',sans-serif; font-size:0.95rem; font-weight:700; color:#374151; margin-bottom:0.4rem;">Upload a CSV to begin</div>
                <div style="font-size:0.8rem; line-height:1.7;">Upload your candidates file on the left.<br>Results, stats, and export will appear here.</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Full results table (full width) ───────────────────────────────────────
    if st.session_state.get("bulk_ran") and "bulk_results" in st.session_state:
        df_res  = st.session_state["bulk_results"]
        filter_opt2 = st.session_state.get("_filter", "All Candidates")

        st.markdown('<div style="margin-top:1.5rem;"><div class="card-title" style="font-size:0.68rem; letter-spacing:0.14em; color:#4b5563; font-family:\'Syne\',sans-serif; font-weight:700; text-transform:uppercase;">Results Table</div></div>', unsafe_allow_html=True)

        # Build display df
        display_cols = ["verdict", "shortlist_probability"] + [c for c in df_res.columns if c not in ("verdict","shortlist_probability","prediction")]
        df_display = df_res[display_cols].copy()
        df_display.columns = [c.replace("_"," ").title() for c in df_display.columns]

        st.dataframe(
            df_display,
            use_container_width=True,
            height=420,
            column_config={
                "Verdict": st.column_config.TextColumn("Verdict", width="medium"),
                "Shortlist Probability": st.column_config.ProgressColumn(
                    "Shortlist %", format="%.1f%%", min_value=0, max_value=100, width="medium"
                ),
            }
        )

        # ── Export ────────────────────────────────────────────────────────────
        ex1, ex2, _ = st.columns([1, 1, 2])
        with ex1:
            csv_bytes = df_res.to_csv(index=False).encode()
            st.download_button(
                "⬇  Download Full CSV",
                data=csv_bytes,
                file_name="recruitai_results_all.csv",
                mime="text/csv",
                use_container_width=True,
            )
        with ex2:
            shortlisted_csv = df_res[df_res["prediction"] == 1].to_csv(index=False).encode()
            st.download_button(
                "⬇  Shortlisted Only",
                data=shortlisted_csv,
                file_name="recruitai_shortlisted.csv",
                mime="text/csv",
                use_container_width=True,
            )

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — CSV GUIDE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_guide:
    g1, g2 = st.columns([1, 1], gap="large")

    with g1:
        st.markdown('<div class="card"><div class="card-title">Required CSV Columns</div>', unsafe_allow_html=True)
        guide_data = {
            "Column": REQUIRED_COLS,
            "Type":   ["integer","float","string","integer","integer","integer"],
            "Range":  ["0 – ∞","0.0 – 100.0","High School / Bachelors / Masters / PhD","0 – ∞","0 – ∞","0 – ∞"],
            "Example":["5","72.5","Masters","8","950","140"],
        }
        st.dataframe(pd.DataFrame(guide_data), use_container_width=True, hide_index=True)
        st.markdown("""
        <div style="margin-top:1rem; font-size:0.8rem; color:#6b7280; line-height:1.7;">
            <strong style="color:#9ca3af;">Optional:</strong> You can include extra columns like <code>candidate_name</code>
            or <code>email</code> — they will be preserved in the output and not used by the model.
        </div>
        </div>
        """, unsafe_allow_html=True)

    with g2:
        st.markdown('<div class="card"><div class="card-title">Download Sample CSV</div>', unsafe_allow_html=True)
        sample = pd.DataFrame({
            "candidate_name":   ["Budi Santoso","Siti Rahayu","Ahmad Fauzi","Dewi Kusuma","Rizky Pratama"],
            "years_experience": [5, 3, 7, 2, 6],
            "skills_match_score":[78.5, 55.0, 91.0, 40.0, 83.5],
            "education_level":  ["Bachelors","Masters","Bachelors","Bachelors","Bachelors"],
            "project_count":    [8, 4, 12, 3, 9],
            "resume_length":    [750, 920, 640, 1100, 800],
            "github_activity":  [180, 60, 420, 15, 250],
        })
        st.dataframe(sample, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇  Download sample_candidates.csv",
            data=sample.to_csv(index=False).encode(),
            file_name="sample_candidates.csv",
            mime="text/csv",
            use_container_width=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card" style="margin-top:0;"><div class="card-title">Field Definitions</div>', unsafe_allow_html=True)
    defs = [
        ("years_experience",  "💼", "Total years in relevant professional or internship roles."),
        ("skills_match_score","🎯", "Recruiter-assigned score (0–100) for how well the candidate's skills match the job description."),
        ("education_level",   "🎓", "Highest qualification. Must be exactly one of: High School, Bachelors, Masters, PhD."),
        ("project_count",     "🛠", "Total completed projects — work, academic, personal, or open-source."),
        ("resume_length",     "📄", "Approximate word count of the submitted resume/CV."),
        ("github_activity",   "🐙", 'Total public GitHub commits. Benchmark: shortlisted candidates in the training dataset average 393 commits. Use 0 if no GitHub profile.'),
    ]
    for col, icon, desc in defs:
        st.markdown(f"""
        <div class="tip-row">
          <span class="tip-icon">{icon}</span>
          <span><strong style="color:#c4c9d8;">{col}</strong> — {desc}</span>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)