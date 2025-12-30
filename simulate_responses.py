"""
Simulation script to add 120 mock responses to the พังงา เขต 2 poll
Distributed according to realistic sampling:
- ตะกั่วป่า: 50 samples
- ท้ายเหมือง: 30 samples
- คุระบุรี: 25 samples
- กะปง: 15 samples
"""

import sys
import os
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.database import get_db_connection, get_questions, init_database

# Initialize
init_database()

# Campaign ID for พังงา poll
CAMPAIGN_ID = 3

# Distribution settings
DISTRICT_DISTRIBUTION = {
    "อ.ตะกั่วป่า": 50,
    "อ.ท้ายเหมือง": 30,
    "อ.คุระบุรี": 25,
    "อ.กะปง": 15
}

# Voting probabilities (realistic simulation)
# เบอร์ 3 ฉกาจ (ภูมิใจไทย) leads, followed by เบอร์ 4 กุศล (ประชาธิปัตย์)
VOTE_WEIGHTS = {
    "เบอร์ 1 น.ส.พิจิกา - พรรคเพื่อไทย": 15,
    "เบอร์ 2 นายสมควร - พรรคกล้าธรรม": 8,
    "เบอร์ 3 นายฉกาจ - พรรคภูมิใจไทย": 35,
    "เบอร์ 4 นายกุศล - พรรคประชาธิปัตย์": 25,
    "เบอร์ 5 นายธีรุตม์ - พรรคประชาชน": 12,
    "ยังไม่ตัดสินใจ": 5
}

# Reason weights (correlate with vote choice)
REASON_WEIGHTS = {
    "เลือกที่ \"ตัวบุคคล\" (ผลงาน/ความดี/คนพื้นที่)": 45,
    "เลือกที่ \"พรรคการเมือง\" (นโยบาย/หัวหน้าพรรค)": 35,
    "ต้องการ \"ความเปลี่ยนแปลง\"": 20
}

GENDER_WEIGHTS = {
    "ชาย": 48,
    "หญิง": 48,
    "LGBTQ+ / ไม่ระบุ": 4
}

AGE_WEIGHTS = {
    "ต่ำกว่า 18 ปี": 2,
    "18-24 ปี (Gen Z)": 18,
    "25-40 ปี (Millennials)": 35,
    "41-56 ปี (Gen X)": 30,
    "57 ปีขึ้นไป (Baby Boomers)": 15
}


def weighted_choice(weights_dict):
    """Choose random item based on weights"""
    items = list(weights_dict.keys())
    weights = list(weights_dict.values())
    return random.choices(items, weights=weights, k=1)[0]


def get_option_id_by_text(options, text_fragment):
    """Find option ID that contains the text fragment"""
    for opt in options:
        if text_fragment in opt['option_text']:
            return opt['id']
    return options[0]['id']


def simulate_responses():
    """Generate 120 simulated responses"""
    
    # Get questions for campaign
    questions = get_questions(CAMPAIGN_ID)
    
    if not questions:
        print("❌ No questions found for campaign. Run setup_phangnga_poll.py first!")
        return
    
    print(f"📊 Found {len(questions)} questions")
    for q in questions:
        print(f"   - {q['question_text'][:50]}...")
    
    # Map question texts to their IDs and options
    q_gender = None
    q_district = None
    q_vote = None
    q_reason = None
    
    for q in questions:
        if "เพศ" in q['question_text']:
            q_gender = q
        elif "อำเภอ" in q['question_text'] or "พื้นที่" in q['question_text']:
            q_district = q
        elif "กาคะแนน" in q['question_text'] or "เลือกตั้ง" in q['question_text']:
            q_vote = q
        elif "เหตุผล" in q['question_text']:
            q_reason = q
    
    if not all([q_gender, q_district, q_vote, q_reason]):
        print(f"❌ Missing questions: gender={q_gender is not None}, district={q_district is not None}, vote={q_vote is not None}, reason={q_reason is not None}")
        return
    
    print("\n🔄 Generating 120 simulated responses...")
    
    responses_added = 0
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for district, count in DISTRICT_DISTRIBUTION.items():
            print(f"   📍 {district}: {count} responses")
            
            for i in range(count):
                # Generate random demographics
                age_group = weighted_choice(AGE_WEIGHTS)
                gender = weighted_choice(GENDER_WEIGHTS)
                
                # Generate vote choice
                vote_choice = weighted_choice(VOTE_WEIGHTS)
                
                # Reason correlates somewhat with vote
                reason_choice = weighted_choice(REASON_WEIGHTS)
                
                # Create unique voter token
                voter_token = f"sim_{district}_{i}_{random.randint(1000, 9999)}"
                
                # Insert response
                cursor.execute('''
                    INSERT INTO responses (campaign_id, age_group, education, region, occupation, income, voter_token, ip_address)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (CAMPAIGN_ID, age_group, None, None, None, None, voter_token, f"192.168.1.{random.randint(1, 254)}"))
                
                response_id = cursor.lastrowid
                
                # Insert response details for each question
                # Gender
                gender_opt_id = get_option_id_by_text(q_gender['options'], gender.split()[0])
                cursor.execute('INSERT INTO response_details (response_id, question_id, option_id) VALUES (?, ?, ?)',
                             (response_id, q_gender['id'], gender_opt_id))
                
                # District
                district_opt_id = get_option_id_by_text(q_district['options'], district)
                cursor.execute('INSERT INTO response_details (response_id, question_id, option_id) VALUES (?, ?, ?)',
                             (response_id, q_district['id'], district_opt_id))
                
                # Vote
                vote_opt_id = get_option_id_by_text(q_vote['options'], vote_choice.split(" - ")[0])
                cursor.execute('INSERT INTO response_details (response_id, question_id, option_id) VALUES (?, ?, ?)',
                             (response_id, q_vote['id'], vote_opt_id))
                
                # Reason
                reason_opt_id = get_option_id_by_text(q_reason['options'], reason_choice.split("\"")[1] if "\"" in reason_choice else reason_choice[:10])
                cursor.execute('INSERT INTO response_details (response_id, question_id, option_id) VALUES (?, ?, ?)',
                             (response_id, q_reason['id'], reason_opt_id))
                
                responses_added += 1
        
        conn.commit()
    
    print(f"\n✅ Successfully added {responses_added} simulated responses!")
    print("\n📊 Expected results approximation:")
    print(f"   🥇 เบอร์ 3 นายฉกาจ (ภูมิใจไทย): ~35%")
    print(f"   🥈 เบอร์ 4 นายกุศล (ประชาธิปัตย์): ~25%")
    print(f"   🥉 เบอร์ 1 น.ส.พิจิกา (เพื่อไทย): ~15%")
    print(f"   #4 เบอร์ 5 นายธีรุตม์ (ประชาชน): ~12%")
    print(f"   #5 เบอร์ 2 นายสมควร (กล้าธรรม): ~8%")


if __name__ == "__main__":
    simulate_responses()
