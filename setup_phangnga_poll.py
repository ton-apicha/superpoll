"""
Setup script for พังงา เขต 2 Election Poll
Creates the poll with OFFICIAL candidates from กกต.
Election Date: 8 Feb 2569 (2026)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import (
    init_database, create_campaign, create_question, update_campaign,
    delete_campaign, get_all_campaigns
)

def setup_phangnga_poll():
    """Create the พังงา เขต 2 election poll with official candidates"""
    
    # Initialize database
    init_database()
    
    # Delete existing poll ID 2 if exists (to refresh)
    existing = get_all_campaigns()
    for c in existing:
        if "พังงา" in c['title']:
            print(f"🗑️ Deleting old campaign: {c['title']}")
            delete_campaign(c['id'])
    
    # Create the campaign
    campaign_id = create_campaign(
        title="🗳️ สำรวจ เขต 2 พังงา (8 ก.พ. 69)",
        description="📊 แบบสำรวจความคิดเห็นของประชาชน\n\n📍 พื้นที่: ตะกั่วป่า, ท้ายเหมือง, คุระบุรี, กะปง\n\n⚠️ ผลสำรวจนี้ไม่ใช่ผลเลือกตั้งจริง",
        demographics_config={
            "age_group": True,
            "education": False,
            "region": False,  # We use custom district question
            "occupation": False,
            "income": False
        }
    )
    
    # Enable showing results after voting
    update_campaign(campaign_id, show_results=1, is_active=1)
    
    print(f"✅ Created campaign ID: {campaign_id}")
    
    # Question 0: Gender (เพศ)
    q0_id = create_question(
        campaign_id=campaign_id,
        question_text="👤 เพศของท่าน",
        question_type="single",
        max_selections=1,
        options=[
            "ชาย",
            "หญิง",
            "LGBTQ+ / ไม่ระบุ"
        ]
    )
    print(f"✅ Created question 0 (gender): ID {q0_id}")
    
    # Question 1: District (อำเภอ)
    q1_id = create_question(
        campaign_id=campaign_id,
        question_text="📍 ท่านมีสิทธิโหวตในอำเภอใด?",
        question_type="single",
        max_selections=1,
        options=[
            "อ.ตะกั่วป่า",
            "อ.ท้ายเหมือง",
            "อ.คุระบุรี",
            "อ.กะปง"
        ]
    )
    print(f"✅ Created question 1 (district): ID {q1_id}")
    
    # Question 2: Main voting question with OFFICIAL candidates
    q2_id = create_question(
        campaign_id=campaign_id,
        question_text="🗳️ หากวันนี้เป็นวันเลือกตั้ง ท่านจะกาคะแนนให้ใคร?",
        question_type="single",
        max_selections=1,
        options=[
            "เบอร์ 1 น.ส.พิจิกา - พรรคเพื่อไทย",
            "เบอร์ 2 นายสมควร - พรรคกล้าธรรม",
            "เบอร์ 3 นายฉกาจ - พรรคภูมิใจไทย",
            "เบอร์ 4 นายกุศล - พรรคประชาธิปัตย์",
            "เบอร์ 5 นายธีรุตม์ - พรรคประชาชน",
            "ยังไม่ตัดสินใจ"
        ]
    )
    print(f"✅ Created question 2 (main vote): ID {q2_id}")
    
    # Question 3: Reason for voting (Tie-breaker)
    q3_id = create_question(
        campaign_id=campaign_id,
        question_text="📋 เหตุผลหลักที่ท่านเลือกหมายเลขนี้?",
        question_type="single",
        max_selections=1,
        options=[
            "เลือกที่ \"ตัวบุคคล\" (ผลงาน/ความดี/คนพื้นที่)",
            "เลือกที่ \"พรรคการเมือง\" (นโยบาย/หัวหน้าพรรค)",
            "ต้องการ \"ความเปลี่ยนแปลง\""
        ]
    )
    print(f"✅ Created question 3 (reason): ID {q3_id}")
    
    print("\n" + "="*60)
    print(f"🎉 Poll created successfully!")
    print(f"")
    print(f"📱 Voter URL: http://localhost:8501?poll={campaign_id}")
    print(f"🔧 Admin URL: http://localhost:8501?admin")
    print(f"")
    print(f"📊 ผู้สมัคร เขต 2 พังงา:")
    print(f"   เบอร์ 1: น.ส.พิจิกา (เพื่อไทย)")
    print(f"   เบอร์ 2: นายสมควร (กล้าธรรม)")
    print(f"   เบอร์ 3: นายฉกาจ (ภูมิใจไทย)")
    print(f"   เบอร์ 4: นายกุศล (ประชาธิปัตย์)")
    print(f"   เบอร์ 5: นายธีรุตม์ (ประชาชน)")
    print("="*60)
    
    return campaign_id


if __name__ == "__main__":
    setup_phangnga_poll()
