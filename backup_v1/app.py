"""
QuickPoll - Public Opinion Polling Application
Main entry point for Streamlit app
"""

import streamlit as st
from pages.voter import render_voter_page
from pages.admin import render_admin_page
from utils.database import init_database

# Page configuration
st.set_page_config(
    page_title="QuickPoll - แบบสำรวจความคิดเห็น",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize database
init_database()


def main():
    """Main application entry point"""
    # Get query parameters
    query_params = st.query_params
    
    # Route based on query parameters
    if 'poll' in query_params:
        # Voter interface - accessed via ?poll=<campaign_id>
        try:
            campaign_id = int(query_params['poll'])
            render_voter_page(campaign_id)
        except (ValueError, TypeError):
            st.error("❌ ลิงก์ไม่ถูกต้อง กรุณาตรวจสอบอีกครั้ง")
    
    elif 'admin' in query_params or 'page' in query_params and query_params.get('page') == 'admin':
        # Admin interface - accessed via ?admin or ?page=admin
        render_admin_page()
    
    else:
        # Default landing page
        render_home_page()


def render_home_page():
    """Render the default home/landing page"""
    st.markdown("""
    <style>
        .hero-section {
            text-align: center;
            padding: 80px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 24px;
            color: white;
            margin-bottom: 40px;
        }
        
        .hero-title {
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 16px;
        }
        
        .hero-subtitle {
            font-size: 20px;
            opacity: 0.9;
            margin-bottom: 32px;
        }
        
        .feature-card {
            background: white;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
            text-align: center;
            height: 100%;
        }
        
        .feature-icon {
            font-size: 48px;
            margin-bottom: 16px;
        }
        
        .feature-title {
            font-size: 20px;
            font-weight: bold;
            color: #2d3436;
            margin-bottom: 8px;
        }
        
        .feature-desc {
            color: #636e72;
            font-size: 14px;
        }
        
        /* Hide Streamlit elements for cleaner look */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    
    <div class="hero-section">
        <div class="hero-title">📊 QuickPoll</div>
        <div class="hero-subtitle">
            ระบบสำรวจความคิดเห็นสาธารณะ<br>
            สร้างโพล แชร์ลิงก์ รับผลทันที
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🚀</div>
            <div class="feature-title">สร้างง่าย รวดเร็ว</div>
            <div class="feature-desc">
                สร้างแบบสอบถามได้ภายในไม่กี่นาที<br>
                ไม่ต้องมีความรู้ทางเทคนิค
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📱</div>
            <div class="feature-title">ตอบง่าย ไม่ต้องพิมพ์</div>
            <div class="feature-desc">
                ใช้งานง่ายบนมือถือ<br>
                แค่จิ้มเลือก ไม่ต้องสมัครสมาชิก
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-title">ผลแบบ Real-time</div>
            <div class="feature-desc">
                ดูผลโหวตได้ทันที<br>
                วิเคราะห์เชิงลึกตามกลุ่มประชากร
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Action buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("---")
        st.markdown("### 🔐 สำหรับผู้ดูแลระบบ")
        
        if st.button("เข้าสู่ระบบจัดการ", type="primary", use_container_width=True):
            st.query_params['admin'] = 'true'
            st.rerun()
        
        st.markdown("""
        <p style="text-align: center; color: #636e72; font-size: 14px; margin-top: 16px;">
            💡 เพิ่ม <code>?admin</code> ที่ URL เพื่อเข้าหน้าจัดการ<br>
            หรือเพิ่ม <code>?poll=ID</code> เพื่อเข้าทำแบบสอบถาม
        </p>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
