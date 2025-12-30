"""
QuickPoll Voter Interface - Visual Ballot Edition
Mobile-focused voting experience with candidate photos and party colors
"""

import streamlit as st
import uuid
from utils.database import (
    get_campaign, get_questions, has_voted, submit_vote,
    get_vote_statistics, DEMOGRAPHIC_OPTIONS
)


def get_voter_token() -> str:
    """Get or create a unique voter token for anti-spam protection"""
    if 'voter_token' not in st.session_state:
        st.session_state.voter_token = str(uuid.uuid4())
    return st.session_state.voter_token


def init_theme():
    """Initialize theme in session state"""
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True  # Default to dark mode


def toggle_theme():
    """Toggle between dark and light mode"""
    st.session_state.dark_mode = not st.session_state.dark_mode


# Party colors mapping
PARTY_COLORS = {
    "ภูมิใจไทย": ("#1D4ED8", "#1E40AF"),  # Royal Blue
    "เพื่อไทย": ("#DC2626", "#B91C1C"),  # Red
    "ก้าวไกล": ("#F97316", "#EA580C"),  # Orange
    "ประชาธิปัตย์": ("#3B82F6", "#2563EB"),  # Blue
    "พลังประชารัฐ": ("#1E3A8A", "#1E3A8A"),  # Dark blue
    "รวมไทยสร้างชาติ": ("#7C3AED", "#6D28D9"),  # Purple
    "ชาติไทยพัฒนา": ("#059669", "#047857"),  # Green
    "ประชาชาติ": ("#10B981", "#059669"),  # Emerald
    "ประชาชน": ("#14B8A6", "#0D9488"),  # Teal
    "กล้าธรรม": ("#8B5CF6", "#7C3AED"),  # Violet
    "ไทยสร้างไทย": ("#EF4444", "#DC2626"),  # Red-orange
}


def get_party_colors(option_text: str) -> tuple:
    """Get gradient colors for a political party"""
    for party, colors in PARTY_COLORS.items():
        if party in option_text:
            return colors
    return ("#4B5563", "#374151")  # Default gray


def render_theme_toggle():
    """Render theme toggle button at top-right corner"""
    init_theme()
    is_dark = st.session_state.dark_mode
    
    # Theme toggle in top right
    col1, col2 = st.columns([6, 1])
    with col2:
        icon = "🌙" if is_dark else "☀️"
        label = "มืด" if is_dark else "สว่าง"
        if st.button(f"{icon}", key="theme_toggle", help=f"เปลี่ยนเป็นโหมด{'สว่าง' if is_dark else 'มืด'}"):
            toggle_theme()
            st.rerun()


def render_mobile_styles():
    """Apply mobile-optimized CSS styles with Standard Slate Design System"""
    init_theme()
    is_dark = st.session_state.dark_mode
    
    # Standard Design System Tokens (Slate Theme) - Consistent with Admin
    if is_dark:
        # DARK MODE
        c = {
            'bg_app': '#0f172a',        # Slate 900
            'bg_content': '#1e293b',    # Slate 800
            'bg_card': '#1e293b',       # Slate 800
            'bg_input': '#334155',      # Slate 700
            
            'text_main': '#f8fafc',     # Slate 50
            'text_sub': '#cbd5e1',      # Slate 300
            'text_muted': '#94a3b8',    # Slate 400
            
            'border': '#334155',        # Slate 700
            'primary': '#22c55e',       # Green 500 (Voter Main Action)
            'primary_hover': '#16a34a', # Green 600
            'secondary': '#475569',     # Slate 600
            
            'shadow': 'rgba(0,0,0,0.3)',
        }
    else:
        # LIGHT MODE
        c = {
            'bg_app': '#f1f5f9',        # Slate 100
            'bg_content': '#ffffff',    # White
            'bg_card': '#ffffff',       # White
            'bg_input': '#ffffff',      # White
            
            'text_main': '#0f172a',     # Slate 900
            'text_sub': '#334155',      # Slate 700
            'text_muted': '#64748b',    # Slate 500
            
            'border': '#e2e8f0',        # Slate 200
            'primary': '#22c55e',       # Green 500
            'primary_hover': '#15803d', # Green 700
            'secondary': '#64748b',     # Slate 500
            
            'shadow': 'rgba(0,0,0,0.05)',
        }
        
    st.markdown(f"""
    <style>
        /* --- GLOBAL & FONTS --- */
        @import url('https://fonts.googleapis.com/css2?family=Internal:wght@400;600&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif, 'Sarabun', sans-serif;
            color: {c['text_main']};
        }}
        
        h1, h2, h3, h4, h5, h6 {{
            color: {c['text_main']} !important;
            font-weight: 600 !important;
        }}
        
        p, label, span, div {{
            color: {c['text_sub']};
        }}

        /* --- BACKGROUND --- */
        .stApp, [data-testid="stAppViewContainer"] {{
            background-color: {c['bg_app']} !important;
            background-image: none !important;
        }}
        
        /* Toolbar & Header Styling */
        [data-testid="stToolbar"] {{
            background-color: transparent !important;
            color: {c['text_main']} !important;
        }}
        
        header[data-testid="stHeader"] {{
            background-color: transparent !important;
        }}

        [data-testid="stToolbar"] button {{
             color: {c['text_main']} !important;
        }}
        
        .main .block-container {{
            background-color: transparent !important;
            max-width: 600px !important; /* Mobile focus */
            padding-top: 1rem;
            padding-bottom: 4rem;
        }}

        /* --- BUTTONS (Mobile Optimized) --- */
        /* Main Action Buttons (Green) */
        .stButton > button {{
            width: 100%;
            min-height: 56px;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
            border-radius: 0.75rem !important;
            margin: 0.5rem 0;
            transition: all 0.2s;
            background-color: {c['primary']} !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        }}
        
        .stButton > button:hover:not(:disabled) {{
            transform: translateY(-2px);
            background-color: {c['primary_hover']} !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }}
        
        /* Secondary Buttons (Back/Cancel) - Not working directly via CSS class in Streamlit, 
           needs specific targeting or st.button type="secondary" if supported, or customized via key/container */
           
        /* Theme Toggle Button (Special) */
        div[data-testid="column"]:last-child .stButton > button {{
            min-height: 40px !important;
            width: auto !important;
            padding: 8px 16px !important;
            background-color: {c['bg_card']} !important;
            color: {c['text_sub']} !important;
            border: 1px solid {c['border']} !important;
            box-shadow: none !important;
        }}

        /* --- INPUTS & SELECTBOX --- */
        .stSelectbox > div > div {{
            background-color: {c['bg_input']} !important;
            color: {c['text_main']} !important;
            border: 1px solid {c['border']} !important;
            border-radius: 0.75rem !important;
        }}
        
        .stSelectbox div[data-baseweb="select"] {{
             color: {c['text_main']} !important;
        }}
        
        div[data-baseweb="popover"], ul[data-baseweb="menu"] {{
            background-color: {c['bg_card']} !important;
            border: 1px solid {c['border']} !important;
        }}
        
        li[data-baseweb="option"] {{
             color: {c['text_main']} !important;
        }}

        /* --- CARDS & CONTAINERS --- */
        .question-box {{
            background-color: {c['bg_card']};
            padding: 1.5rem;
            border-radius: 1rem;
            margin-bottom: 1rem;
            border: 1px solid {c['border']};
            box-shadow: 0 1px 3px 0 {c['shadow']};
        }}
        
        /* Hide default Streamlit elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        .stCaption, small {{
            color: {c['text_muted']} !important;
        }}
        
        /* Divider */
        hr {{
            border-color: {c['border']} !important;
        }}
        
        /* Success/Info/Warning boxes */
        .stSuccess, .stInfo, .stWarning {{
            background: {c['bg_card']} !important;
            color: {c['text_main']} !important;
        }}

        /* --- CLICKABLE CARD HACK --- */
        /* Large Card (Candidate) */
        .candidate-btn {{
            margin-top: -130px !important; 
            margin-bottom: 20px !important;
            position: relative;
            z-index: 5;
            height: 130px;
        }}
        
        /* Small Card (Undecided / Simple Option) */
        .small-btn {{
            margin-top: -70px !important; 
            margin-bottom: 10px !important;
            position: relative;
            z-index: 5;
            height: 70px;
        }}
        
        .candidate-btn button, .small-btn button {{
            height: 100% !important;
            width: 100% !important;
            opacity: 0 !important; /* Invisible */
            border: none !important;
            cursor: pointer !important;
        }}
        
        /* Adjust card spacing to account for negative margin */
        .clickable-card {{
            margin-bottom: 0px !important;
            padding-bottom: 0px !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def render_candidate_button(candidate_name: str, party_name: str, number: int, 
                           is_selected: bool, key: str, image_url: str = None, bg_color: str = None) -> bool:
    """Render a visual candidate card as a clickable button with improved readability"""
    
    # Use provided color or calculate from party
    if bg_color:
        background_style = f"background: {bg_color};"
        # Gradient overlay for depth if solid color
        overlay_style = "background: linear-gradient(180deg, rgba(255,255,255,0.1) 0%, rgba(0,0,0,0.1) 100%);"
    else:
        color1, color2 = get_party_colors(party_name)
        background_style = f"background: linear-gradient(135deg, {color1} 0%, {color2} 100%);"
        overlay_style = ""
    
    border_style = "3px solid #22c55e" if is_selected else "1px solid rgba(255,255,255,0.2)"
    shadow = "0 10px 15px -3px rgba(0, 0, 0, 0.2)" if is_selected else "0 4px 6px -1px rgba(0, 0, 0, 0.1)"
    transform = "transform: scale(1.02);" if is_selected else ""
    
    # Image or Placeholder
    if image_url:
        img_html = f"""
        <div style="
            width: 72px;
            height: 72px;
            min-width: 72px;
            border-radius: 50%;
            background-image: url('{image_url}');
            background-size: cover;
            background-position: center;
            border: 3px solid white;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        "></div>
        """
    else:
        img_html = """
        <div style="
            width: 56px;
            height: 56px;
            min-width: 56px;
            border-radius: 50%;
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(4px);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            border: 2px solid rgba(255,255,255,0.5);
        ">👤</div>
        """
    
    # Display the card
    st.markdown(f"""
    <div class="clickable-card" style="
        {background_style}
        border-radius: 16px;
        margin: 10px 0;
        position: relative;
        overflow: hidden;
        border: {border_style};
        box-shadow: {shadow};
        {transform}
        transition: all 0.2s ease;
    ">
        <div style="{overlay_style} position: absolute; top:0; left:0; right:0; bottom:0;"></div>
        
        <div style="
            position: relative;
            padding: 16px;
            display: flex;
            align-items: center;
            gap: 16px;
            z-index: 1;
        ">
            <!-- Number Badge -->
            <div style="
                background: white;
                color: #0f172a;
                width: 36px;
                height: 36px;
                min-width: 36px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                font-weight: 800;
                box-shadow: 0 2px 4px rgba(0,0,0,0.2);
            ">{number}</div>
            
            {img_html}
            
            <!-- Text Content with enhanced readability shadow -->
            <div style="flex: 1; min-width: 0;">
                <p style="
                    font-size: 1.1rem;
                    font-weight: 700;
                    color: white !important;
                    margin: 0 0 4px 0;
                    line-height: 1.3;
                    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
                    white-space: normal;
                ">{candidate_name}</p>
                <p style="
                    font-size: 0.9rem;
                    color: rgba(255,255,255,0.95) !important;
                    margin: 0;
                    font-weight: 500;
                    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
                ">{'🏛️ ' + party_name if party_name else ''}</p>
            </div>
            
            <!-- Selection Indicator -->
            {f'''<div style="
                background: #22c55e;
                color: white;
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 18px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
            ">✓</div>''' if is_selected else ""}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Invisible button for click handling - wrapped in container
    with st.container():
        st.markdown('<div class="small-btn">', unsafe_allow_html=True)
        clicked = st.button("เลือก", key=key, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return clicked


def render_undecided_button(is_selected: bool, key: str) -> bool:
    """Render the undecided option"""
    border_style = "3px solid #FFD700" if is_selected else "3px solid transparent"
    shadow = "0 0 20px rgba(255, 215, 0, 0.5)" if is_selected else "0 4px 15px rgba(0,0,0,0.3)"
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #4B5563 0%, #374151 100%);
        border-radius: 16px;
        padding: 16px 20px;
        margin: 8px 0;
        border: {border_style};
        box-shadow: {shadow};
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
    ">
        <span style="font-size: 24px;">❓</span>
        <p style="
            font-size: 16px;
            color: white !important;
            margin: 0;
        ">ยังไม่ตัดสินใจ / ไม่ออกความเห็น</p>
        {"<span style='color: #FFD700; font-size: 24px; margin-left: 12px;'>✓</span>" if is_selected else ""}
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="candidate-btn">', unsafe_allow_html=True)
        clicked = st.button("เลือก", key=key, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return clicked


def render_option_button(option_text: str, is_selected: bool, key: str) -> bool:
    """Render a standard option as a button"""
    border_style = "3px solid #FFD700" if is_selected else "3px solid transparent"
    bg_color = "#3B82F6" if is_selected else "#475569"
    
    st.markdown(f"""
    <div style="
        background: {bg_color};
        border-radius: 12px;
        padding: 14px 20px;
        margin: 6px 0;
        border: {border_style};
        display: flex;
        align-items: center;
        gap: 12px;
    ">
        <div style="
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 2px solid white;
            background: {'#FFD700' if is_selected else 'transparent'};
            display: flex;
            align-items: center;
            justify-content: center;
        ">{"✓" if is_selected else ""}</div>
        <p style="
            font-size: 15px;
            color: white !important;
            margin: 0;
            flex: 1;
        ">{option_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="small-btn">', unsafe_allow_html=True)
        clicked = st.button("เลือก", key=key, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        return clicked


def render_landing_page(campaign: dict):
    """Render the campaign landing page"""
    st.markdown(f"""
    <div style="text-align: center; padding: 40px 20px;">
        <div style="font-size: 72px; margin-bottom: 16px;">🗳️</div>
        <h1 style="margin-bottom: 12px; color: white !important; font-size: 26px;">{campaign['title']}</h1>
        <p style="color: #94a3b8 !important; font-size: 15px; margin-bottom: 32px; line-height: 1.6;">
            {campaign.get('description', 'ร่วมแสดงความคิดเห็นของคุณ').replace(chr(10), '<br>')}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🗳️ เริ่มทำแบบสอบถาม", type="primary", use_container_width=True):
            st.session_state.voter_step = 'demographics'
            st.rerun()


def render_demographics_page(campaign: dict):
    """Render the demographics selection page"""
    st.markdown("### 📋 ข้อมูลทั่วไป")
    st.markdown("กรุณาเลือกข้อมูลของท่าน (ข้อมูลจะถูกเก็บเป็นความลับ)")
    
    demographics_config = campaign.get('demographics_config', {})
    demographics = {}
    
    # Render each enabled demographic field
    for field_key, field_info in DEMOGRAPHIC_OPTIONS.items():
        if demographics_config.get(field_key, True):
            st.markdown(f"**{field_info['label']}**")
            demographics[field_key] = st.selectbox(
                field_info['label'],
                options=["-- เลือก --"] + field_info['options'],
                key=f"demo_{field_key}",
                label_visibility="collapsed"
            )
            st.markdown("")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ กลับ", use_container_width=True):
            st.session_state.voter_step = 'landing'
            st.rerun()
    
    with col2:
        if st.button("ถัดไป ➡️", type="primary", use_container_width=True):
            # Validate demographics
            valid = True
            for field_key in demographics_config:
                if demographics_config.get(field_key, True):
                    if demographics.get(field_key) == "-- เลือก --" or not demographics.get(field_key):
                        valid = False
                        break
            
            if valid:
                # Clean up demographics (remove placeholder)
                for key in demographics:
                    if demographics[key] == "-- เลือก --":
                        demographics[key] = None
                st.session_state.voter_demographics = demographics
                st.session_state.voter_step = 'voting'
                st.rerun()
            else:
                st.error("⚠️ กรุณาเลือกข้อมูลให้ครบทุกช่อง")


def render_voting_page(campaign: dict, questions: list):
    """Render the voting questions page with visual ballot"""
    st.markdown("### 🗳️ แบบสำรวจความคิดเห็น")
    
    # Initialize answers in session state
    if 'voter_answers' not in st.session_state:
        st.session_state.voter_answers = {}
    
    answers = st.session_state.voter_answers
    
    # Show progress
    total_questions = len(questions)
    answered = len([q for q in questions if q['id'] in answers and answers[q['id']]])
    progress = answered / total_questions if total_questions > 0 else 0
    st.progress(progress, text=f"ตอบแล้ว {answered}/{total_questions} ข้อ")
    
    st.markdown("")
    
    for q_idx, question in enumerate(questions):
        # Question header
        st.markdown(f"""
        <div style="
            background: rgba(255,255,255,0.05);
            padding: 16px 20px;
            border-radius: 12px;
            margin: 20px 0 12px 0;
            border-left: 4px solid #3B82F6;
        ">
            <p style="color: white !important; font-size: 17px; margin: 0; font-weight: 500;">
                {question['question_text']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        options = question.get('options', [])
        current_selection = answers.get(question['id'], [])
        
        # Check if this is an election-style question (has candidate + party)
        is_election_q = any(' - พรรค' in opt['option_text'] for opt in options)
        
        for opt_idx, option in enumerate(options):
            opt_text = option['option_text']
            opt_id = option['id']
            is_selected = opt_id in current_selection
            btn_key = f"q{question['id']}_opt{opt_id}"
            
            if is_election_q:
                # Election-style with candidate cards
                if "ยังไม่ตัดสินใจ" in opt_text or "ไม่ออกความเห็น" in opt_text:
                    if render_undecided_button(is_selected, btn_key):
                        answers[question['id']] = [opt_id]
                        st.session_state.voter_answers = answers
                        st.rerun()
                else:
                    # Parse candidate + party
                    if " - " in opt_text:
                        parts = opt_text.split(" - ", 1)
                        name = parts[0]
                        party = parts[1] if len(parts) > 1 else ""
                    else:
                        name = opt_text
                        party = ""
                    
                    # Get extra attributes
                    img_url = option.get('image_url')
                    bg_col = option.get('bg_color')
                    
                    if render_candidate_button(name, party, opt_idx + 1, is_selected, btn_key, img_url, bg_col):
                        answers[question['id']] = [opt_id]
                        st.session_state.voter_answers = answers
                        st.rerun()
            else:
                # Standard options
                if render_option_button(opt_text, is_selected, btn_key):
                    answers[question['id']] = [opt_id]
                    st.session_state.voter_answers = answers
                    st.rerun()
        
        st.markdown("")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ กลับ", use_container_width=True):
            st.session_state.voter_step = 'demographics'
            st.rerun()
    
    with col2:
        if st.button("📤 ส่งคำตอบ", type="primary", use_container_width=True):
            # Validate all questions answered
            all_answered = all(
                q['id'] in answers and len(answers[q['id']]) > 0 
                for q in questions
            )
            
            if all_answered:
                # Submit vote
                voter_token = get_voter_token()
                submit_vote(
                    campaign_id=campaign['id'],
                    demographics=st.session_state.voter_demographics,
                    answers=answers,
                    voter_token=voter_token
                )
                st.session_state.voter_step = 'thank_you'
                st.rerun()
            else:
                st.error("⚠️ กรุณาตอบคำถามให้ครบทุกข้อ")


def render_thank_you_page(campaign: dict):
    """Render the thank you page after submission"""
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #059669 0%, #10B981 100%);
        color: white;
        padding: 40px 24px;
        border-radius: 20px;
        text-align: center;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(16, 185, 129, 0.3);
    ">
        <div style="font-size: 72px; margin-bottom: 16px;">✅</div>
        <h2 style="color: white !important; margin-bottom: 8px;">ขอบคุณสำหรับความคิดเห็น!</h2>
        <p style="opacity: 0.9; color: white !important;">คำตอบของท่านได้ถูกบันทึกเรียบร้อยแล้ว</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show results preview if enabled
    if campaign.get('show_results', False):
        st.markdown("---")
        st.markdown("### 📊 ผลโหวตเบื้องต้น")
        
        stats = get_vote_statistics(campaign['id'])
        
        for q_stat in stats.get('questions', []):
            st.markdown(f"""
            <div style="
                background: rgba(255,255,255,0.05);
                padding: 16px;
                border-radius: 12px;
                margin: 16px 0 8px 0;
            ">
                <p style="color: white !important; font-weight: 500; margin: 0;">{q_stat['text']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Sort options by count descending
            sorted_options = sorted(q_stat['options'], key=lambda x: x['count'], reverse=True)
            
            for rank, opt in enumerate(sorted_options, 1):
                pct = opt['percentage']
                color1, color2 = get_party_colors(opt['text'])
                
                # Add ranking badge
                if rank == 1:
                    rank_badge = "🥇"
                elif rank == 2:
                    rank_badge = "🥈"
                elif rank == 3:
                    rank_badge = "🥉"
                else:
                    rank_badge = f"#{rank}"
                
                st.markdown(f"""
                <div style="
                    margin: 10px 0; 
                    background: rgba(255,255,255,0.08); 
                    border-radius: 12px; 
                    padding: 14px 16px;
                    border-left: 4px solid {color1};
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="color: white !important; font-size: 14px;">
                            <span style="font-size: 18px; margin-right: 8px;">{rank_badge}</span>
                            {opt['text'][:50]}{'...' if len(opt['text']) > 50 else ''}
                        </span>
                        <span style="color: #FFD700; font-weight: bold; font-size: 16px;">{pct}%</span>
                    </div>
                    <div style="background: rgba(255,255,255,0.15); border-radius: 8px; height: 20px; overflow: hidden;">
                        <div style="
                            background: linear-gradient(90deg, {color1}, {color2}); 
                            width: {pct}%; 
                            height: 100%; 
                            border-radius: 8px; 
                            transition: width 0.8s ease;
                        "></div>
                    </div>
                    <div style="text-align: right; color: #94a3b8; font-size: 12px; margin-top: 6px;">
                        {opt['count']} เสียง
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("")


def render_already_voted():
    """Render message for users who have already voted"""
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <div style="font-size: 72px; margin-bottom: 20px;">🗳️</div>
        <h2 style="color: white !important;">ท่านได้ทำแบบสอบถามนี้ไปแล้ว</h2>
        <p style="color: #94a3b8 !important;">
            ขอบคุณสำหรับการมีส่วนร่วม<br>
            ท่านสามารถโหวตได้เพียงครั้งเดียวต่อแบบสอบถาม
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_poll_closed():
    """Render message for closed polls"""
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <div style="font-size: 72px; margin-bottom: 20px;">🔒</div>
        <h2 style="color: white !important;">แบบสอบถามนี้ปิดรับคำตอบแล้ว</h2>
        <p style="color: #94a3b8 !important;">
            ขอบคุณสำหรับความสนใจ
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_poll_not_found():
    """Render message for polls that don't exist"""
    st.markdown("""
    <div style="text-align: center; padding: 60px 20px;">
        <div style="font-size: 72px; margin-bottom: 20px;">❓</div>
        <h2 style="color: white !important;">ไม่พบแบบสอบถาม</h2>
        <p style="color: #94a3b8 !important;">
            กรุณาตรวจสอบลิงก์อีกครั้ง
        </p>
    </div>
    """, unsafe_allow_html=True)


def render_voter_page(campaign_id: int):
    """Main voter page renderer"""
    render_mobile_styles()
    render_theme_toggle()  # Theme toggle at top right
    
    # Get campaign
    campaign = get_campaign(campaign_id)
    
    if not campaign:
        render_poll_not_found()
        return
    
    # Check if campaign is active
    if not campaign.get('is_active', False):
        render_poll_closed()
        return
    
    # Check if already voted
    voter_token = get_voter_token()
    if has_voted(campaign_id, voter_token):
        render_already_voted()
        return
    
    # Get questions
    questions = get_questions(campaign_id)
    
    if not questions:
        st.warning("⚠️ แบบสอบถามนี้ยังไม่มีคำถาม")
        return
    
    # Initialize voter step
    if 'voter_step' not in st.session_state:
        st.session_state.voter_step = 'landing'
    
    # Render appropriate step
    step = st.session_state.voter_step
    
    if step == 'landing':
        render_landing_page(campaign)
    elif step == 'demographics':
        render_demographics_page(campaign)
    elif step == 'voting':
        render_voting_page(campaign, questions)
    elif step == 'thank_you':
        render_thank_you_page(campaign)
