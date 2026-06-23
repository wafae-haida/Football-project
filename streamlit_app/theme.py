import streamlit as st


def apply_theme():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

    :root {
        --bg: #A9B8A6;
        --card: #F8FBF7;
        --primary: #4E9A8A;
        --primary-dark: #2F5D50;
        --hover: #62A96F;
        --accent: #D9D957;
        --title: #16352F;
        --text: #2E3B35;
        --muted: #68786F;
        --border: #B7C5B5;
    }

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 8% 12%, rgba(217,217,87,0.20), transparent 30%),
            radial-gradient(circle at 90% 18%, rgba(78,154,138,0.16), transparent 28%),
            linear-gradient(135deg, #A9B8A6 0%, #B7C5B5 48%, #EEF3EA 100%);
        color: var(--text);
    }

    header[data-testid="stHeader"] {
        background: rgba(238,243,234,0.95) !important;
        backdrop-filter: blur(12px);
        box-shadow: none !important;
        border-bottom: 1px solid rgba(47,93,80,0.12);
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    footer {
        visibility: hidden;
    }

    section[data-testid="stSidebar"],
    section[data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #F4F7F1 0%, #E7EFE4 100%) !important;
        border-right: 1px solid rgba(47,93,80,0.16);
    }

    [data-testid="stSidebar"] * {
        color: var(--title) !important;
        font-weight: 700;
    }

    [data-testid="stSidebarContent"] {
        padding-top: 5rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
    }

    .block-container {
        padding-top: 6rem !important;
        padding-bottom: 6rem !important;
        padding-left: 3rem !important;
        padding-right: 3rem !important;
        max-width: 1280px;
    }

    [data-testid="collapsedControl"] {
        display: block !important;
        visibility: visible !important;
        z-index: 999999 !important;
    }

    .sidebar-logo {
        background: rgba(248,251,247,0.95);
        border: 1px solid rgba(47,93,80,0.14);
        border-radius: 22px;
        padding: 18px;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px rgba(22,53,47,0.08);
    }

    .sidebar-title {
        font-size: 20px;
        font-weight: 900;
        color: var(--title);
    }

    .sidebar-subtitle {
        font-size: 12px;
        color: var(--muted);
        margin-top: 6px;
    }

    .hero-card {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, rgba(248,251,247,0.97), rgba(238,243,234,0.94));
        padding: 38px;
        border-radius: 32px;
        border: 1px solid rgba(47,93,80,0.18);
        box-shadow: 0 24px 70px rgba(22,53,47,0.18);
        margin-bottom: 28px;
        z-index: 2;
    }

    .hero-card::after {
        content: "⚽";
        position: absolute;
        right: 30px;
        top: 20px;
        font-size: 130px;
        opacity: 0.18;
        animation: heroBall 8s infinite ease-in-out;
    }

    @keyframes heroBall {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-15px) rotate(180deg); }
        100% { transform: translateY(0px) rotate(360deg); }
    }

    .hero-title {
        font-size: 46px;
        font-weight: 900;
        color: var(--title);
        margin-bottom: 10px;
        letter-spacing: -0.06em;
        line-height: 1.05;
    }

    .hero-subtitle {
        font-size: 17px;
        color: var(--text);
        line-height: 1.65;
        max-width: 900px;
    }

    .small-badge {
        display: inline-block;
        padding: 8px 15px;
        border-radius: 999px;
        background: rgba(217,217,87,0.45);
        color: var(--title);
        border: 1px solid rgba(47,93,80,0.16);
        font-weight: 900;
        font-size: 12px;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 14px;
    }

    .content-section {
        background: rgba(248,251,247,0.94);
        border: 1px solid rgba(47,93,80,0.14);
        border-radius: 26px;
        padding: 28px 30px;
        margin: 30px 0 24px 0;
        box-shadow: 0 18px 45px rgba(22,53,47,0.10);
    }

    .content-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 20px;
    }

    .content-kicker {
        display: inline-block;
        padding: 8px 14px;
        border-radius: 999px;
        background: rgba(217,217,87,0.35);
        border: 1px solid rgba(47,93,80,0.12);
        color: var(--primary-dark);
        font-size: 12px;
        font-weight: 900;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        margin-bottom: 12px;
    }

    .content-header h2 {
        color: var(--title);
        font-size: 30px;
        font-weight: 900;
        margin: 0 0 8px 0;
    }

    .content-header p {
        color: var(--text);
        font-size: 15px;
        line-height: 1.6;
        margin: 0;
    }

    .content-icon {
        width: 64px;
        height: 64px;
        border-radius: 22px;
        background: linear-gradient(135deg, rgba(78,154,138,0.18), rgba(217,217,87,0.32));
        border: 1px solid rgba(47,93,80,0.14);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 31px;
        flex-shrink: 0;
    }

    .metrics-block-title {
        color: var(--title);
        font-size: 20px;
        font-weight: 850;
        margin: 28px 0 14px 0;
    }

    .metric-card {
        background: linear-gradient(135deg, #F8FBF7, #EEF5EC);
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 22px 18px;
        min-height: 120px;
        box-shadow: 0 12px 28px rgba(22, 53, 47, 0.08);
    }

    .metric-label {
        color: var(--muted);
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 16px;
    }

    .metric-value {
        color: var(--primary-dark);
        font-size: 34px;
        font-weight: 900;
        line-height: 1;
    }

    .table-title {
        color: var(--title);
        font-size: 18px;
        font-weight: 850;
        margin: 22px 0 12px 0;
        padding: 10px 14px;
        display: inline-block;
        border-radius: 14px;
        background: rgba(248,251,247,0.90);
        border: 1px solid rgba(47,93,80,0.14);
    }

    [data-testid="stDataFrame"] {
        background: rgba(248,251,247,0.96);
        border-radius: 22px;
        border: 1px solid rgba(47,93,80,0.14);
        padding: 10px;
        box-shadow: 0 14px 35px rgba(22,53,47,0.10);
    }

    textarea,
    input {
        background-color: #F8FBF7 !important;
        color: var(--title) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(47,93,80,0.25) !important;
    }

    div[data-baseweb="select"] > div {
        background-color: #F8FBF7 !important;
        color: var(--title) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(47,93,80,0.25) !important;
    }

    .stTextArea textarea {
        min-height: 420px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        line-height: 1.7 !important;
    }

    .stAlert {
        border-radius: 18px;
    }

    h1, h2, h3 {
        color: var(--title);
        font-weight: 900;
    }

    .stButton > button {
        background: linear-gradient(135deg, #2F5D50, #4E9A8A);
        color: white;
        border: none;
        border-radius: 16px;
        padding: 0.82rem 1.35rem;
        font-weight: 900;
        box-shadow: 0 16px 35px rgba(47,93,80,0.25);
    }

    .stButton > button:hover {
        background: linear-gradient(135deg, #4E9A8A, #62A96F);
        color: white;
        border: none;
        transform: translateY(-1px);
    }
    .metrics-block-title {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        color: var(--title);
        font-size: 20px;
        font-weight: 900;
        margin: 32px 0 16px 0;
        padding: 11px 18px;
        border-radius: 18px;
        background: rgba(248,251,247,0.94);
        border: 1px solid rgba(47,93,80,0.14);
        box-shadow: 0 12px 28px rgba(22,53,47,0.08);
    }
    .feature-card,
    .section-box,
    .custom-card {
        background: rgba(248,251,247,0.96);
        padding: 24px;
        border-radius: 24px;
        border: 1px solid rgba(47,93,80,0.14);
        box-shadow: 0 16px 38px rgba(22,53,47,0.12);
    }

    .feature-title {
        font-size: 19px;
        font-weight: 850;
        color: var(--title);
        margin-bottom: 8px;
    }

    .feature-text {
        font-size: 14px;
        color: var(--text);
        line-height: 1.55;
    }

    .badge,
    .badge-event {
        display: inline-block;
        margin: 6px;
        padding: 10px 14px;
        border-radius: 12px;
        background: rgba(78,154,138,0.10);
        border: 1px solid rgba(78,154,138,0.20);
        color: var(--title);
        font-weight: 700;
        font-size: 14px;
    }

    .badge-event {
        background: rgba(217,217,87,0.18);
        border: 1px solid rgba(217,217,87,0.40);
    }

    .section-box .services-title {
        display: inline-block !important;
        font-size: 15px !important;
        font-weight: 850 !important;
        color: var(--title) !important;
        margin-bottom: 14px !important;
        padding: 8px 14px !important;
        border-radius: 14px !important;
        background: rgba(217,217,87,0.35) !important;
        border: 1px solid rgba(47,93,80,0.14) !important;
    }
    .matrix-card-title,
    .report-label {
        display: inline-block;
        color: var(--title);
        font-size: 16px;
        font-weight: 850;
        margin: 16px 0 12px 0;
        padding: 10px 15px;
        border-radius: 15px;
        background: rgba(217,217,87,0.28);
        border: 1px solid rgba(47,93,80,0.14);
    }

    .report-box {
        margin-top: 18px;
    }

    .metric-card {
        background: linear-gradient(135deg, #F8FBF7, #EEF5EC);
        border: 1px solid var(--border);
        border-radius: 22px;
        padding: 22px 18px;
        min-height: 120px;
        box-shadow: 0 12px 28px rgba(22,53,47,0.08);
    }

    .metric-label {
        color: var(--muted);
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 16px;
    }

    .metric-value {
        color: var(--primary-dark);
        font-size: 34px;
        font-weight: 900;
        line-height: 1;
    }

    div[data-baseweb="select"] > div {
        background-color: #F8FBF7 !important;
        color: var(--title) !important;
        border-radius: 16px !important;
        border: 1px solid rgba(47,93,80,0.22) !important;
        box-shadow: 0 10px 25px rgba(22,53,47,0.07);
    }

    .stTextArea textarea {
        background-color: #F8FBF7 !important;
        color: var(--title) !important;
        border-radius: 18px !important;
        border: 1px solid rgba(47,93,80,0.22) !important;
        box-shadow: 0 12px 30px rgba(22,53,47,0.08);
        font-size: 14px !important;
        line-height: 1.7 !important;
    }
    .stApp::before {
        content: "⚽";
        position: fixed;
        top: 18%;
        right: 5%;
        font-size: 105px;
        opacity: 0.12;
        z-index: 0;
        animation: floatBall 12s infinite ease-in-out;
        pointer-events: none;
    }

    .stApp::after {
        content: "⚽";
        position: fixed;
        bottom: 10%;
        left: 4%;
        font-size: 70px;
        opacity: 0.08;
        z-index: 0;
        animation: floatBallReverse 16s infinite ease-in-out;
        pointer-events: none;
    }

    @keyframes floatBall {
        0% { transform: translateY(0px) rotate(0deg); }
        50% { transform: translateY(-38px) rotate(180deg); }
        100% { transform: translateY(0px) rotate(360deg); }
    }

    @keyframes floatBallReverse {
        0% { transform: translateY(0px) rotate(360deg); }
        50% { transform: translateY(32px) rotate(180deg); }
        100% { transform: translateY(0px) rotate(0deg); }
    }

    ul {
        color: var(--text);
        line-height: 1.8;
    }
    </style>
    """, unsafe_allow_html=True)