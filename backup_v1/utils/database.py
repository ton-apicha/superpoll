"""
QuickPoll Database Module
SQLite database operations for campaigns, questions, options, and responses
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, List, Dict, Any
from contextlib import contextmanager

# Database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'quickpoll.db')

# Default demographic options (Thai)
DEMOGRAPHIC_OPTIONS = {
    "age_group": {
        "label": "ช่วงอายุ",
        "options": [
            "ต่ำกว่า 18 ปี",
            "18-24 ปี (Gen Z)",
            "25-40 ปี (Millennials)",
            "41-56 ปี (Gen X)",
            "57 ปีขึ้นไป (Baby Boomers)"
        ]
    },
    "education": {
        "label": "ระดับการศึกษา",
        "options": [
            "ต่ำกว่ามัธยมศึกษา",
            "มัธยมศึกษา/ปวช.",
            "อนุปริญญา/ปวส.",
            "ปริญญาตรี",
            "สูงกว่าปริญญาตรี"
        ]
    },
    "region": {
        "label": "ภูมิภาค",
        "options": [
            "กรุงเทพมหานคร",
            "ภาคกลาง",
            "ภาคเหนือ",
            "ภาคตะวันออกเฉียงเหนือ (อีสาน)",
            "ภาคใต้",
            "ภาคตะวันออก",
            "ภาคตะวันตก"
        ]
    },
    "occupation": {
        "label": "อาชีพ",
        "options": [
            "นักเรียน/นักศึกษา",
            "พนักงานบริษัทเอกชน",
            "ข้าราชการ/รัฐวิสาหกิจ",
            "ธุรกิจส่วนตัว/อาชีพอิสระ",
            "เกษตรกร",
            "แม่บ้าน/พ่อบ้าน",
            "ว่างงาน/เกษียณ",
            "อื่นๆ"
        ]
    },
    "income": {
        "label": "รายได้เฉลี่ยต่อเดือน",
        "options": [
            "ต่ำกว่า 15,000 บาท",
            "15,000 - 30,000 บาท",
            "30,001 - 50,000 บาท",
            "50,001 - 100,000 บาท",
            "มากกว่า 100,000 บาท"
        ]
    }
}


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize database with required tables"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Campaigns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                show_results INTEGER DEFAULT 0,
                demographics_config TEXT DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                question_text TEXT NOT NULL,
                question_type TEXT DEFAULT 'single',
                max_selections INTEGER DEFAULT 1,
                order_index INTEGER DEFAULT 0,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
            )
        ''')
        
        # Options table with image and color support
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS options (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_id INTEGER NOT NULL,
                option_text TEXT NOT NULL,
                image_url TEXT,
                bg_color TEXT,
                order_index INTEGER DEFAULT 0,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE
            )
        ''')
        
        # Responses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                campaign_id INTEGER NOT NULL,
                age_group TEXT,
                education TEXT,
                region TEXT,
                occupation TEXT,
                income TEXT,
                voter_token TEXT,
                ip_address TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE
            )
        ''')
        
        # Response details table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS response_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                response_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                option_id INTEGER NOT NULL,
                FOREIGN KEY (response_id) REFERENCES responses(id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
                FOREIGN KEY (option_id) REFERENCES options(id) ON DELETE CASCADE
            )
        ''')
        
        conn.commit()


# ==================== Campaign Operations ====================

def create_campaign(title: str, description: str = "", demographics_config: dict = None) -> int:
    """Create a new campaign and return its ID"""
    if demographics_config is None:
        demographics_config = {key: True for key in DEMOGRAPHIC_OPTIONS.keys()}
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO campaigns (title, description, demographics_config)
            VALUES (?, ?, ?)
        ''', (title, description, json.dumps(demographics_config)))
        conn.commit()
        return cursor.lastrowid


def get_campaign(campaign_id: int) -> Optional[Dict[str, Any]]:
    """Get a campaign by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM campaigns WHERE id = ?', (campaign_id,))
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result['demographics_config'] = json.loads(result.get('demographics_config', '{}'))
            return result
        return None


def get_all_campaigns() -> List[Dict[str, Any]]:
    """Get all campaigns"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM campaigns ORDER BY created_at DESC')
        rows = cursor.fetchall()
        campaigns = []
        for row in rows:
            campaign = dict(row)
            campaign['demographics_config'] = json.loads(campaign.get('demographics_config', '{}'))
            campaigns.append(campaign)
        return campaigns


def update_campaign(campaign_id: int, **kwargs) -> bool:
    """Update campaign fields"""
    allowed_fields = ['title', 'description', 'is_active', 'show_results', 'demographics_config']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    
    if not updates:
        return False
    
    if 'demographics_config' in updates and isinstance(updates['demographics_config'], dict):
        updates['demographics_config'] = json.dumps(updates['demographics_config'])
    
    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [campaign_id]
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f'''
            UPDATE campaigns SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', values)
        conn.commit()
        return cursor.rowcount > 0


def delete_campaign(campaign_id: int) -> bool:
    """Delete a campaign and all related data"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM campaigns WHERE id = ?', (campaign_id,))
        conn.commit()
        return cursor.rowcount > 0


def toggle_campaign_status(campaign_id: int) -> bool:
    """Toggle campaign active status"""
    campaign = get_campaign(campaign_id)
    if campaign:
        new_status = 0 if campaign['is_active'] else 1
        return update_campaign(campaign_id, is_active=new_status)
    return False


# ==================== Question Operations ====================

def create_question(campaign_id: int, question_text: str, question_type: str = 'single', 
                   max_selections: int = 1, options: List = None) -> int:
    """Create a question with options
    
    Args:
        options: Can be list of strings OR list of dicts with keys:
                 - text (required)
                 - image_url (optional)
                 - bg_color (optional)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get max order index
        cursor.execute('SELECT MAX(order_index) FROM questions WHERE campaign_id = ?', (campaign_id,))
        max_order = cursor.fetchone()[0] or 0
        
        cursor.execute('''
            INSERT INTO questions (campaign_id, question_text, question_type, max_selections, order_index)
            VALUES (?, ?, ?, ?, ?)
        ''', (campaign_id, question_text, question_type, max_selections, max_order + 1))
        question_id = cursor.lastrowid
        
        # Add options if provided
        if options:
            for idx, opt in enumerate(options):
                # Support both string and dict format
                if isinstance(opt, dict):
                    opt_text = opt.get('text', '')
                    image_url = opt.get('image_url', None)
                    bg_color = opt.get('bg_color', None)
                else:
                    opt_text = str(opt)
                    image_url = None
                    bg_color = None
                
                cursor.execute('''
                    INSERT INTO options (question_id, option_text, image_url, bg_color, order_index)
                    VALUES (?, ?, ?, ?, ?)
                ''', (question_id, opt_text, image_url, bg_color, idx))
        
        conn.commit()
        return question_id


def get_questions(campaign_id: int) -> List[Dict[str, Any]]:
    """Get all questions for a campaign with their options"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM questions WHERE campaign_id = ? ORDER BY order_index
        ''', (campaign_id,))
        questions = [dict(row) for row in cursor.fetchall()]
        
        for question in questions:
            cursor.execute('''
                SELECT * FROM options WHERE question_id = ? ORDER BY order_index
            ''', (question['id'],))
            question['options'] = [dict(row) for row in cursor.fetchall()]
        
        return questions


def update_question(question_id: int, question_text: str = None, question_type: str = None,
                   max_selections: int = None, options: List[str] = None) -> bool:
    """Update a question and its options"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        updates = {}
        if question_text is not None:
            updates['question_text'] = question_text
        if question_type is not None:
            updates['question_type'] = question_type
        if max_selections is not None:
            updates['max_selections'] = max_selections
        
        if updates:
            set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
            values = list(updates.values()) + [question_id]
            cursor.execute(f'UPDATE questions SET {set_clause} WHERE id = ?', values)
        
        # Update options if provided
        if options is not None:
            cursor.execute('DELETE FROM options WHERE question_id = ?', (question_id,))
            for idx, opt in enumerate(options):
                # Support both string and dict format
                if isinstance(opt, dict):
                    opt_text = opt.get('text', '')
                    image_url = opt.get('image_url', None)
                    bg_color = opt.get('bg_color', None)
                else:
                    opt_text = str(opt)
                    image_url = None
                    bg_color = None

                cursor.execute('''
                    INSERT INTO options (question_id, option_text, image_url, bg_color, order_index)
                    VALUES (?, ?, ?, ?, ?)
                ''', (question_id, opt_text, image_url, bg_color, idx))
        
        conn.commit()
        return True


def delete_question(question_id: int) -> bool:
    """Delete a question and its options"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM questions WHERE id = ?', (question_id,))
        conn.commit()
        return cursor.rowcount > 0


# ==================== Response Operations ====================

def has_voted(campaign_id: int, voter_token: str) -> bool:
    """Check if a voter has already voted"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM responses 
            WHERE campaign_id = ? AND voter_token = ?
        ''', (campaign_id, voter_token))
        return cursor.fetchone()[0] > 0


def submit_vote(campaign_id: int, demographics: Dict[str, str], 
                answers: Dict[int, List[int]], voter_token: str, ip_address: str = None) -> int:
    """Submit a vote response"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Insert response
        cursor.execute('''
            INSERT INTO responses (campaign_id, age_group, education, region, occupation, income, voter_token, ip_address)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            campaign_id,
            demographics.get('age_group'),
            demographics.get('education'),
            demographics.get('region'),
            demographics.get('occupation'),
            demographics.get('income'),
            voter_token,
            ip_address
        ))
        response_id = cursor.lastrowid
        
        # Insert response details
        for question_id, option_ids in answers.items():
            for option_id in option_ids:
                cursor.execute('''
                    INSERT INTO response_details (response_id, question_id, option_id)
                    VALUES (?, ?, ?)
                ''', (response_id, question_id, option_id))
        
        conn.commit()
        return response_id


def get_response_count(campaign_id: int) -> int:
    """Get total response count for a campaign"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM responses WHERE campaign_id = ?', (campaign_id,))
        return cursor.fetchone()[0]


def get_responses(campaign_id: int, filters: Dict[str, str] = None) -> List[Dict[str, Any]]:
    """Get all responses for a campaign with optional demographic filters"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = 'SELECT * FROM responses WHERE campaign_id = ?'
        params = [campaign_id]
        
        if filters:
            for field, value in filters.items():
                if value and field in ['age_group', 'education', 'region', 'occupation', 'income']:
                    query += f' AND {field} = ?'
                    params.append(value)
        
        cursor.execute(query + ' ORDER BY submitted_at DESC', params)
        responses = [dict(row) for row in cursor.fetchall()]
        
        # Get response details for each response
        for response in responses:
            cursor.execute('''
                SELECT rd.*, q.question_text, o.option_text
                FROM response_details rd
                JOIN questions q ON rd.question_id = q.id
                JOIN options o ON rd.option_id = o.id
                WHERE rd.response_id = ?
            ''', (response['id'],))
            response['answers'] = [dict(row) for row in cursor.fetchall()]
        
        return responses


def get_vote_statistics(campaign_id: int, filters: Dict[str, str] = None) -> Dict[str, Any]:
    """Get vote statistics for a campaign with optional filters"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Build filter clause
        filter_clause = ''
        params = [campaign_id]
        if filters:
            for field, value in filters.items():
                if value and field in ['age_group', 'education', 'region', 'occupation', 'income']:
                    filter_clause += f' AND r.{field} = ?'
                    params.append(value)
        
        # Get questions
        questions = get_questions(campaign_id)
        
        stats = {
            'total_votes': 0,
            'questions': []
        }
        
        # Get total votes with filters
        cursor.execute(f'''
            SELECT COUNT(*) FROM responses r WHERE r.campaign_id = ? {filter_clause}
        ''', params)
        stats['total_votes'] = cursor.fetchone()[0]
        
        # Get stats per question
        for question in questions:
            q_stats = {
                'id': question['id'],
                'text': question['question_text'],
                'type': question['question_type'],
                'options': []
            }
            
            for option in question['options']:
                cursor.execute(f'''
                    SELECT COUNT(*) FROM response_details rd
                    JOIN responses r ON rd.response_id = r.id
                    WHERE rd.question_id = ? AND rd.option_id = ? AND r.campaign_id = ? {filter_clause}
                ''', [question['id'], option['id'], campaign_id] + params[1:])
                
                count = cursor.fetchone()[0]
                q_stats['options'].append({
                    'id': option['id'],
                    'text': option['option_text'],
                    'count': count,
                    'percentage': round(count / stats['total_votes'] * 100, 1) if stats['total_votes'] > 0 else 0
                })
            
            stats['questions'].append(q_stats)
        
        return stats


def get_demographic_breakdown(campaign_id: int, demographic_field: str, question_id: int = None) -> Dict[str, Any]:
    """Get breakdown of votes by demographic field"""
    if demographic_field not in ['age_group', 'education', 'region', 'occupation', 'income']:
        return {}
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get unique demographic values
        cursor.execute(f'''
            SELECT DISTINCT {demographic_field} FROM responses 
            WHERE campaign_id = ? AND {demographic_field} IS NOT NULL
        ''', (campaign_id,))
        demo_values = [row[0] for row in cursor.fetchall()]
        
        breakdown = {
            'field': demographic_field,
            'label': DEMOGRAPHIC_OPTIONS[demographic_field]['label'],
            'data': []
        }
        
        for demo_value in demo_values:
            cursor.execute(f'''
                SELECT COUNT(*) FROM responses 
                WHERE campaign_id = ? AND {demographic_field} = ?
            ''', (campaign_id, demo_value))
            count = cursor.fetchone()[0]
            breakdown['data'].append({
                'value': demo_value,
                'count': count
            })
        
        return breakdown


def export_responses_data(campaign_id: int) -> List[Dict[str, Any]]:
    """Export all responses with details for CSV/Excel export"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get all responses
        cursor.execute('''
            SELECT * FROM responses WHERE campaign_id = ? ORDER BY submitted_at
        ''', (campaign_id,))
        responses = [dict(row) for row in cursor.fetchall()]
        
        # Get questions for column headers
        questions = get_questions(campaign_id)
        
        export_data = []
        for response in responses:
            row = {
                'ID': response['id'],
                'ช่วงอายุ': response['age_group'],
                'ระดับการศึกษา': response['education'],
                'ภูมิภาค': response['region'],
                'อาชีพ': response['occupation'],
                'รายได้': response['income'],
                'IP Address': response['ip_address'],
                'วันที่ตอบ': response['submitted_at']
            }
            
            # Get answers for this response
            cursor.execute('''
                SELECT rd.question_id, o.option_text
                FROM response_details rd
                JOIN options o ON rd.option_id = o.id
                WHERE rd.response_id = ?
            ''', (response['id'],))
            answers = cursor.fetchall()
            
            # Group answers by question
            answer_dict = {}
            for ans in answers:
                q_id = ans[0]
                if q_id not in answer_dict:
                    answer_dict[q_id] = []
                answer_dict[q_id].append(ans[1])
            
            # Add question answers to row
            for q in questions:
                q_answers = answer_dict.get(q['id'], [])
                row[q['question_text']] = ', '.join(q_answers)
            
            export_data.append(row)
        
        return export_data


# Initialize database on module import
init_database()
