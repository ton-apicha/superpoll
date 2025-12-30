import sqlite3
import os
import json
import pandas as pd
from datetime import datetime

# DB Config
DB_DIR = 'data'
DB_NAME = 'quickpoll.db'
DB_PATH = os.path.join(DB_DIR, DB_NAME)

DEMOGRAPHIC_OPTIONS = {
    "age_group": {
        "label": "ช่วงอายุ",
        "options": ["18-25 ปี", "26-35 ปี", "36-45 ปี", "46-60 ปี", "60 ปีขึ้นไป"]
    },
    "gender": {
        "label": "เพศ",
        "options": ["ชาย", "หญิง", "LGBTQ+", "ไม่ระบุ"]
    },
    "occupation": {
        "label": "อาชีพ",
        "options": ["นักเรียน/นักศึกษา", "ข้าราชการ/รัฐวิสาหกิจ", "พนักงานเอกชน", "เจ้าของธุรกิจ/ค้าขาย", "รับจ้างทั่วไป", "ว่างงาน/เกษียณ"]
    },
    "location": {
        "label": "พื้นที่อาศัย",
        "options": ["กรุงเทพฯ/ปริมณฑล", "ภาคกลาง", "ภาคเหนือ", "ภาคตะวันออกเฉียงเหนือ", "ภาคตะวันออก", "ภาคใต้"]
    }
}

def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Campaigns
    c.execute('''CREATE TABLE IF NOT EXISTS campaigns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        demographics_config TEXT DEFAULT '{}',
        show_results INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Questions
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER,
        question_text TEXT NOT NULL,
        question_type TEXT DEFAULT 'single',
        max_selections INTEGER DEFAULT 1,
        order_index INTEGER DEFAULT 0,
        FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE CASCADE
    )''')
    
    # Options
    c.execute('''CREATE TABLE IF NOT EXISTS options (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER,
        option_text TEXT NOT NULL,
        image_url TEXT,
        bg_color TEXT,
        order_index INTEGER DEFAULT 0,
        FOREIGN KEY (question_id) REFERENCES questions (id) ON DELETE CASCADE
    )''')
    
    # Responses
    c.execute('''CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER,
        demographic_data TEXT,
        ip_address TEXT,
        user_agent TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (campaign_id) REFERENCES campaigns (id) ON DELETE CASCADE
    )''')
    
    # Response Details
    c.execute('''CREATE TABLE IF NOT EXISTS response_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        response_id INTEGER,
        question_id INTEGER,
        option_id INTEGER,
        FOREIGN KEY (response_id) REFERENCES responses (id) ON DELETE CASCADE
    )''')
    
    conn.commit()
    conn.close()

# --- Campaigns ---
def get_all_campaigns():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM campaigns ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_campaign(campaign_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM campaigns WHERE id = ?", (campaign_id,))
    row = c.fetchone()
    conn.close()
    if row:
        d = dict(row)
        d['demographics_config'] = json.loads(d['demographics_config']) if d['demographics_config'] else {}
        return d
    return None

def create_campaign(title, description, demographics_config=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO campaigns (title, description, demographics_config) VALUES (?, ?, ?)",
              (title, description, json.dumps(demographics_config or {})))
    new_id = c.lastrowid
    conn.commit()
    conn.close()
    return new_id

def toggle_campaign_status(campaign_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE campaigns SET is_active = NOT is_active WHERE id = ?", (campaign_id,))
    conn.commit()
    conn.close()

def delete_campaign(campaign_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM campaigns WHERE id = ?", (campaign_id,))
    conn.commit()
    conn.close()

def update_campaign(campaign_id, title, description, demographics_config=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE campaigns SET title = ?, description = ?, demographics_config = ? WHERE id = ?",
              (title, description, json.dumps(demographics_config or {}), campaign_id))
    conn.commit()
    conn.close()

# --- Questions & Options ---
def get_questions(campaign_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM questions WHERE campaign_id = ? ORDER BY order_index", (campaign_id,))
    questions = [dict(row) for row in c.fetchall()]
    
    for q in questions:
        c.execute("SELECT * FROM options WHERE question_id = ? ORDER BY id", (q['id'],))
        q['options'] = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return questions

def create_question(campaign_id, text, q_type='single', max_select=1, options=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO questions (campaign_id, question_text, question_type, max_selections) VALUES (?, ?, ?, ?)",
              (campaign_id, text, q_type, max_select))
    q_id = c.lastrowid
    
    if options:
        for opt in options:
            # opt can be dict (advanced) or string (simple)
            if isinstance(opt, dict):
                c.execute("INSERT INTO options (question_id, option_text, image_url, bg_color) VALUES (?, ?, ?, ?)",
                          (q_id, opt['text'], opt.get('image_url'), opt.get('bg_color')))
            else:
                c.execute("INSERT INTO options (question_id, option_text) VALUES (?, ?)", (q_id, opt))
                
    conn.commit()
    conn.close()

def update_question(q_id, text, q_type, max_selections, options):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Update question info
    c.execute("UPDATE questions SET question_text = ?, question_type = ?, max_selections = ? WHERE id = ?", 
              (text, q_type, max_selections, q_id))
    
    # Re-create options (simplest way to handle edits)
    c.execute("DELETE FROM options WHERE question_id = ?", (q_id,))
    
    for opt in options:
        if isinstance(opt, dict):
             c.execute("INSERT INTO options (question_id, option_text, image_url, bg_color) VALUES (?, ?, ?, ?)",
                      (q_id, opt['text'], opt.get('image_url'), opt.get('bg_color')))
        else:
             c.execute("INSERT INTO options (question_id, option_text) VALUES (?, ?)", (q_id, opt))
             
    conn.commit()
    conn.close()

def delete_question(q_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM questions WHERE id = ?", (q_id,))
    conn.commit()
    conn.close()

def reorder_question(q_id, direction):
    """Move question up or down by swapping positions (if position field exists)"""
    # For now, let's keep it simple: Swap with next/prev ID 
    # (In a real app, we'd use a 'sort_order' column, but for this scale, ID-based is tricky)
    # Let's add 'sort_order' to the table if we want real reordering.
    pass # I will prioritize the UI fixing for now as requested.

# --- Responses ---
def submit_response(campaign_id, demographic_data, answers, ip_address=None, user_agent=None, location_data=None):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute("INSERT INTO responses (campaign_id, demographic_data, ip_address, user_agent, location_data) VALUES (?, ?, ?, ?, ?)",
              (campaign_id, json.dumps(demographic_data), ip_address, user_agent, json.dumps(location_data)))
    response_id = c.lastrowid
    
    for q_id, option_ids in answers.items():
        if not isinstance(option_ids, list):
            option_ids = [option_ids]
        for opt_id in option_ids:
            c.execute("INSERT INTO response_details (response_id, question_id, option_id) VALUES (?, ?, ?)",
                      (response_id, int(q_id), int(opt_id)))
                      
    conn.commit()
    conn.close()
    return True

def get_response_count(campaign_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM responses WHERE campaign_id = ?", (campaign_id,))
    count = c.fetchone()[0]
    conn.close()
    return count

def reset_responses(campaign_id):
    """Delete all responses for a specific campaign"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Delete response details first (Foreign Key relationship)
    # Get all response IDs for this campaign
    c.execute("SELECT id FROM responses WHERE campaign_id = ?", (campaign_id,))
    resp_ids = [r[0] for r in c.fetchall()]
    
    if resp_ids:
        # Delete details for these responses
        placeholders = ', '.join(['?'] * len(resp_ids))
        c.execute(f"DELETE FROM response_details WHERE response_id IN ({placeholders})", resp_ids)
        # Delete the responses themselves
        c.execute("DELETE FROM responses WHERE campaign_id = ?", (campaign_id,))
    
    conn.commit()
    conn.close()
    return True

def get_voter_logs(campaign_id):
    """Retrieve detailed logs for all voters"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, ip_address, user_agent, location_data, demographic_data, created_at FROM responses WHERE campaign_id = ? ORDER BY created_at DESC", (campaign_id,))
    rows = c.fetchall()
    
    logs = []
    for r in rows:
        loc = {}
        try:
            if r['location_data']: loc = json.loads(r['location_data'])
        except: pass
        
        demo = {}
        try:
            if r['demographic_data']: demo = json.loads(r['demographic_data'])
        except: pass
        
        logs.append({
            "id": r['id'],
            "ip": r['ip_address'],
            "ua": r['user_agent'],
            "location": loc,
            "demo": demo,
            "timestamp": r['created_at']
        })
    conn.close()
    return logs

def export_responses_data(campaign_id):
    """Export all response data for CSV"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get Responses
    c.execute("SELECT * FROM responses WHERE campaign_id = ?", (campaign_id,))
    responses = c.fetchall()
    
    # Get Questions
    questions = get_questions(campaign_id)
    q_map = {q['id']: q['question_text'] for q in questions}
    
    data = []
    for r in responses:
        row = {
            "Response ID": r['id'],
            "Timestamp": r['created_at'],
            "IP Address": r['ip_address']
        }
        
        # Demographics
        demos = json.loads(r['demographic_data']) if r['demographic_data'] else {}
        for k, v in demos.items():
            row[f"Demo: {k}"] = v
            
        # Answers
        c.execute("""
            SELECT q.question_text, o.option_text 
            FROM response_details rd
            JOIN questions q ON rd.question_id = q.id
            JOIN options o ON rd.option_id = o.id
            WHERE rd.response_id = ?
        """, (r['id'],))
        answers = c.fetchall()
        for ans in answers:
            row[ans['question_text']] = ans['option_text']
            
        data.append(row)
        
    conn.close()
    return data

def get_demographic_breakdown(campaign_id, field):
    """Get breakdown stats for a demographic field"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # This is tricky with JSON storage in SQLite
    # We fetch all and process in python for simplicity (not efficient for big data, but OK for this scale)
    c.execute("SELECT demographic_data FROM responses WHERE campaign_id = ?", (campaign_id,))
    rows = c.fetchall()
    conn.close()
    
    counts = {}
    total = 0
    for r in rows:
        # Safety Check: handle None or empty string
        raw_data = r['demographic_data']
        if not raw_data:
            data = {}
        else:
            try:
                data = json.loads(raw_data)
            except:
                data = {}
                
        val = data.get(field, 'Unknown')
        counts[val] = counts.get(val, 0) + 1
        total += 1
        
    return {
        'total': total,
        'data': [{'value': k, 'count': v} for k, v in counts.items()]
    }

def get_vote_statistics(campaign_id):
    """Alias for get_results but matches old interface name"""
    return {'questions': get_results(campaign_id)}

def get_results(campaign_id):
    # ... existing get_results implementation ...
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    questions = get_questions(campaign_id)
    results = []
    
    for q in questions:
        q_data = {'id': q['id'], 'text': q['question_text'], 'options': []}
        
        # Get total votes for this question
        c.execute("""
            SELECT COUNT(*) as total 
            FROM response_details 
            WHERE question_id = ?
        """, (q['id'],))
        total_votes = c.fetchone()['total']
        
        for opt in q['options']:
            c.execute("""
                SELECT COUNT(*) as count 
                FROM response_details 
                WHERE option_id = ?
            """, (opt['id'],))
            count = c.fetchone()['count']
            q_data['options'].append({
                'text': opt['option_text'],
                'count': count,
                'percentage': round((count / total_votes * 100) if total_votes > 0 else 0, 1)
            })
        
        results.append(q_data)
        
    conn.close()
    return results
