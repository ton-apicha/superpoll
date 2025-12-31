# 🗳️ SuperPoll - Professional Field Operations Polling System

> **A production-ready, mobile-first polling application designed for professional field operations with real-time analytics and comprehensive demographic tracking.**

Built with Python + Streamlit | Deployed on Streamlit Cloud | SQLite Backend

[![Live Demo](https://img.shields.io/badge/Live-Demo-success)](https://andaman-2025.streamlit.app/)
[![GitHub](https://img.shields.io/badge/GitHub-SuperPoll-blue)](https://github.com/ton-apicha/superpoll)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Core Components](#core-components)
- [UI/UX Design Principles](#uiux-design-principles)
- [Installation & Setup](#installation--setup)
- [Deployment](#deployment)
- [API Reference](#api-reference)
- [Design Decisions & Lessons Learned](#design-decisions--lessons-learned)
- [Future Enhancements](#future-enhancements)

---

## 🎯 Overview

**SuperPoll** is a sophisticated public opinion polling system specifically designed for **political field operations** and **market research campaigns**. Unlike basic survey tools, SuperPoll provides:

- **Executive Dashboard** with real-time quota tracking
- **Geospatial voter analytics** with IP-based location tracking
- **Professional Question Builder** with visual card-based options
- **Zero-friction voter experience** optimized for mobile field workers
- **Comprehensive demographic profiling** aligned with field operation targets

### Use Cases

✅ Political campaign polling (e.g., Phang Nga District 2 election survey)  
✅ Market research with demographic segmentation  
✅ Event feedback collection with real-time dashboards  
✅ Academic research requiring quota sampling  

---

## ✨ Key Features

### 🗳️ Voter Interface

| Feature | Description |
|---------|-------------|
| **Mobile-First Design** | Touch-optimized card interface with large tap targets |
| **Invisible Button Overlay** | Custom CSS technique for seamless card selection UX |
| **Base64 Image Embedding** | Ensures reliable image display across all environments |
| **Demographic Collection** | Pre-voting survey (District, Area, Generation, Gender) |
| **Background Data Capture** | Automatic IP, User-Agent, and GeoIP location logging |
| **Zero Authentication** | Frictionless voting - no login required |

### 📊 Admin Dashboard

| Feature | Description |
|---------|-------------|
| **Executive Dashboard** | Real-time quota tracking with gauge charts (vs. N=360 targets) |
| **Question Builder 2.0** | Visual editor with image upload, color picker, and live preview |
| **Demographic Analytics** | Generation, Gender, District, and Area breakdown charts |
| **Voter Logs** | Detailed audit trail with IP, Location, ISP, Browser, and Map links |
| **Quality Control** | Manual data validation and vote reset capabilities |
| **CSV Export** | Full data export for external analysis |
| **Campaign Management** | Multi-campaign support with toggle activation |

---

## 🏗️ Architecture

### Tech Stack

```yaml
Language: Python 3.11+
Framework: Streamlit 1.40+
Database: SQLite 3
Charts: Plotly 5.x
External APIs:
  - ip-api.com (GeoIP lookup)
Deployment: Streamlit Community Cloud
```

### System Design

```
┌─────────────────────────────────────────────────────────────┐
│                         User Layer                          │
│  ┌──────────────────┐              ┌──────────────────┐    │
│  │  Voter UI        │              │   Admin UI       │    │
│  │  (Mobile-First)  │              │  (Desktop-Opt.)  │    │
│  └────────┬─────────┘              └────────┬─────────┘    │
│           │                                  │              │
└───────────┼──────────────────────────────────┼──────────────┘
            │                                  │
┌───────────▼──────────────────────────────────▼──────────────┐
│                    Application Layer                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │           app.py (Router & Initializer)             │   │
│  └────────┬────────────────────────────────────────────┘   │
│           │                                                  │
│      ┌────▼─────┐              ┌──────────────┐            │
│      │ views/   │              │   core/      │            │
│      │ - voter  │              │ - database   │            │
│      │ - admin  │◄────────────►│ - models     │            │
│      │ - charts │              │              │            │
│      └──────────┘              └──────────────┘            │
└──────────────────────────────────────────────────────────────┘
            │
┌───────────▼──────────────────────────────────────────────────┐
│                       Data Layer                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  SQLite Database (data/quickpoll.db)                   │ │
│  │  - campaigns, questions, options                       │ │
│  │  - responses, response_details                         │ │
│  │  - Demographic & Location JSON fields                 │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
SuperPoll/
├── 📄 app.py                      # Main router & DB initializer
│
├── 📂 core/                       # Business logic layer
│   └── database.py                # All database operations
│
├── 📂 views/                      # UI components
│   ├── admin_ui.py                # Admin dashboard & campaign management
│   ├── voter_ui.py                # Voter interface with card rendering
│   └── charts_helper.py           # Plotly chart generators
│
├── 📂 assets/                     # Static resources
│   └── styles.css                 # Custom CSS (invisible button overlays)
│
├── 📂 static/uploads/             # User-uploaded images (candidate photos)
│
├── 📂 data/                       # Database storage
│   └── quickpoll.db               # SQLite file (auto-created)
│
├── 📄 requirements.txt            # Python dependencies
├── 📄 migrate_db.py               # Schema migration script
├── 📄 DEPLOY_GUIDE.md             # Deployment instructions
└── 📄 README.md                   # You are here
```

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```
campaigns (1) ──< (N) questions ──< (N) options
    │
    └──< (N) responses ──< (N) response_details >──┐
                                                     │
                                          ┌──────────┘
                                          │
                              (references options)
```

### Table Definitions

#### `campaigns`
```sql
CREATE TABLE campaigns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `questions`
```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER,
    question_text TEXT NOT NULL,
    question_type TEXT,  -- 'single' or 'multi'
    max_selections INTEGER DEFAULT 1,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
);
```

#### `options`
```sql
CREATE TABLE options (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER,
    option_text TEXT NOT NULL,
    image_url TEXT,       -- Path to uploaded image
    bg_color TEXT,        -- Hex color for card background
    FOREIGN KEY (question_id) REFERENCES questions(id)
);
```

#### `responses`
```sql
CREATE TABLE responses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER,
    demographic_data TEXT,  -- JSON: {อำเภอ, พื้นที่, Gen, เพศ}
    ip_address TEXT,
    user_agent TEXT,
    location_data TEXT,     -- JSON: {city, country, isp, lat, lon}
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (campaign_id) REFERENCES campaigns(id)
);
```

#### `response_details`
```sql
CREATE TABLE response_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    response_id INTEGER,
    question_id INTEGER,
    option_id INTEGER,
    FOREIGN KEY (response_id) REFERENCES responses(id),
    FOREIGN KEY (question_id) REFERENCES questions(id),
    FOREIGN KEY (option_id) REFERENCES options(id)
);
```

---

## 🔧 Core Components

### 1. Voter UI (`views/voter_ui.py`)

**Key Functions:**

#### `render_card_html(opt, is_selected, q_type)`
Generates HTML for voting cards with two rendering modes:

- **Large Card**: For options with images (candidates)
  - Background image with gradient overlay
  - Checkmark indicator when selected
  - Green border (`#22c55e`) on selection
  
- **Small Card**: Text-only options
  - Clean white background
  - Compact layout for simple choices

**Invisible Button Technique:**
```python
# 1. Render visual card (HTML)
st.markdown(card_html, unsafe_allow_html=True)

# 2. Place CSS marker
st.markdown('<div class="btn-marker-large"></div>', unsafe_allow_html=True)

# 3. Invisible button (CSS positions it over the card)
if st.button("Select", key=f"btn_{opt['id']}"):
    # Selection logic
```

#### `render_voter_app(campaign_id)`
Main voter interface orchestrator:
1. Displays demographic collection form (District, Area, Gen, Gender)
2. Iterates through campaign questions
3. Renders cards for each option
4. Handles vote submission with background data collection:
   ```python
   # Automatic data capture on submit
   ip_addr = requests.get('https://api.ipify.org').text
   location_info = requests.get(f'http://ip-api.com/json/{ip_addr}').json()
   user_agent = st.context.headers.get("User-Agent")
   ```

---

### 2. Admin UI (`views/admin_ui.py`)

**Key Functions:**

#### `render_question_builder(campaign_id)`
Advanced visual question editor featuring:
- Large image preview thumbnails
- Color picker for card backgrounds
- Dynamic row addition/removal
- Edit mode with pre-filled data
- Real-time validation

**Question Card List:**
```python
# Professional card display with badges
for q in questions:
    type_badge = "Single" if q['type'] == 'single' else f"Multi (max {q['max_selections']})"
    # Colored badges: Blue (#3b82f6) for Single, Green (#10b981) for Multi
    # Option preview with colored dots matching bg_color
```

#### `render_results(campaign_id)`
Executive Dashboard with:

**Quota Tracking:**
```python
targets = {
    "ทั้งหมด": 360,
    "ตะกั่วป่า": 127,
    "ท้ายเหมือง": 124,
    # ... district targets
}
# Gauge charts showing current/target progress
create_gauge_chart("ตะกั่วป่า", current_count, target)
```

**Demographic Insights:**
- Generation breakdown (Gen Z, Y, X, Boomer)
- Gender distribution
- Geographic analysis (Municipality vs. Non-Municipality)

#### `render_voter_logs(campaign_id)`
Detailed audit trail:
```python
{
    "เวลา": "2025-12-31 16:30:45",
    "อำเภอ": "ตะกั่วป่า",
    "Gen": "Gen Y (26-45)",
    "ไอพี": "123.45.67.89",
    "ที่อยู่/จังหวัด": "Bangkok Thailand",
    "ISP": "TRUE Internet",
    "พิกัด": "https://www.google.com/maps?q=13.75,100.52"
}
```

---

### 3. Database Layer (`core/database.py`)

**Critical Functions:**

#### `submit_response(campaign_id, demographic_data, answers, ...)`
Atomic transaction for vote submission:
```python
# 1. Insert main response record
response_id = c.execute(
    "INSERT INTO responses (campaign_id, demographic_data, ip_address, ...) VALUES (...)"
).lastrowid

# 2. Insert individual question answers
for q_id, option_ids in answers.items():
    for opt_id in option_ids:
        c.execute("INSERT INTO response_details (...) VALUES (...)")

conn.commit()
```

#### `get_demographic_breakdown(campaign_id, field)`
Aggregates demographic data with safety checks:
```python
for row in responses:
    raw_data = row['demographic_data']
    # Safety check for legacy/null data
    if not raw_data:
        data = {}
    else:
        try:
            data = json.loads(raw_data)
        except:
            data = {}  # Prevent JSON parsing crashes
    
    value = data.get(field, 'Unknown')
    counts[value] += 1
```

---

## 🎨 UI/UX Design Principles

### 1. **Mobile-First Philosophy**
- Touch targets: Minimum 48px height
- Large, thumb-friendly buttons
- Vertical scrolling optimized
- No horizontal overflow

### 2. **Invisible Button Overlay Pattern**
**Problem:** Streamlit's default buttons don't integrate seamlessly with custom HTML.

**Solution:** CSS `:has()` selector technique
```css
/* Hide button container */
[data-testid="stElementContainer"]:has(div.btn-marker-large)+[data-testid="stElementContainer"] {
    height: 0px !important;
    overflow: visible !important;
}

/* Position button over previous card */
[...] button {
    position: absolute !important;
    bottom: 0px !important;
    opacity: 0 !important;  /* Invisible but clickable */
    height: 140px !important;
}
```

### 3. **Professional Color Palette**
```css
Primary (Blue):   #3b82f6  /* Single-select badges, active states */
Success (Green):  #22c55e  /* Selected cards, multi-select badges */
Warning (Yellow): #fef3c7  /* Quota warning zones */
Danger (Red):     #fee2e2  /* Quota danger zones */
Neutral (Gray):   #e2e8f0  /* Unselected card borders */
```

### 4. **Base64 Image Embedding**
To avoid static file serving issues across deployment platforms:
```python
def get_img_base64(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Embed directly in HTML
background-image: url('data:image/jpeg;base64,{get_img_base64(path)}');
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- pip
- (Optional) Git

### Local Development

```bash
# 1. Clone the repository
git clone https://github.com/ton-apicha/superpoll.git
cd superpoll

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database (automatic on first run)
# Database will be created at data/quickpoll.db

# 5. Run the application
streamlit run app.py --server.port=8501

# 6. Access the app
# Voter: http://localhost:8501/?poll=1
# Admin: http://localhost:8501/ (no parameters)
```

### Environment Variables (Optional)
```bash
# Not currently used, but reserved for future config
export ADMIN_PASSWORD="your_secure_password"
export DATABASE_PATH="data/quickpoll.db"
```

---

## 🌐 Deployment

### Streamlit Community Cloud (Recommended)

**Pros:**
✅ Free forever  
✅ Auto-deploys from GitHub  
✅ Custom subdomain (e.g., `andaman-2025.streamlit.app`)  
✅ HTTPS by default  

**Cons:**
⚠️ SQLite data resets on app restart (use for temporary polls)  
⚠️ Limited resources (1GB RAM)  

**Steps:**
1. Push code to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io/)
3. Connect GitHub repository
4. Select `app.py` as main file
5. Deploy!

**For persistent data:**
- Migrate to PostgreSQL (Supabase, Neon.tech)
- Or use Streamlit Cloud + external SQLite host

### Alternative Platforms

| Platform | Pros | Cons |
|----------|------|------|
| **Railway.app** | PostgreSQL support, paid plans | Not free tier |
| **Render** | Persistent disk, Docker support | Slower cold starts |
| **Heroku** | Enterprise-grade | Expensive |
| **DigitalOcean** | Full control, cheap VPS | Manual setup |

See [DEPLOY_GUIDE.md](DEPLOY_GUIDE.md) for detailed instructions.

---

## 📚 API Reference

### Database Module (`core/database.py`)

#### Campaign Management
```python
create_campaign(title: str, description: str = "") -> int
get_campaigns() -> List[Dict]
get_campaign(campaign_id: int) -> Dict
toggle_campaign_status(campaign_id: int) -> None
```

#### Question Management
```python
create_question(
    campaign_id: int,
    question_text: str,
    question_type: str,  # 'single' or 'multi'
    max_selections: int,
    options: List[Dict]  # [{'text': str, 'image_url': str, 'bg_color': str}]
) -> int

get_questions(campaign_id: int) -> List[Dict]
update_question(q_id: int, text: str, q_type: str, max_sel: int, options: List[Dict]) -> None
delete_question(q_id: int) -> None
```

#### Response Management
```python
submit_response(
    campaign_id: int,
    demographic_data: Dict,  # {'อำเภอ': str, 'พื้นที่': str, 'Gen': str}
    answers: Dict[int, List[int]],  # {question_id: [option_ids]}
    ip_address: str = None,
    user_agent: str = None,
    location_data: Dict = None
) -> int

get_response_count(campaign_id: int) -> int
get_voter_logs(campaign_id: int) -> List[Dict]
reset_responses(campaign_id: int) -> None  # Danger zone!
```

#### Analytics
```python
get_vote_statistics(campaign_id: int) -> Dict
# Returns: {'questions': [{'text': str, 'options': [{'text': str, 'count': int, 'percentage': float}]}]}

get_demographic_breakdown(campaign_id: int, field: str) -> Dict
# field: 'อำเภอ', 'พื้นที่', 'Gen', 'เพศ'
# Returns: {'total': int, 'data': [{'value': str, 'count': int}]}

export_responses_data(campaign_id: int) -> List[Dict]
# Full CSV-ready export
```

### Charts Module (`views/charts_helper.py`)

```python
create_bar_chart(question_text: str, options_data: List[Dict]) -> go.Figure
create_pie_chart(question_text: str, options_data: List[Dict]) -> go.Figure
create_gauge_chart(label: str, current: int, target: int) -> go.Figure
create_demographic_bar_chart(demographic_label: str, data: List[Dict]) -> go.Figure
```

---

## 💡 Design Decisions & Lessons Learned

### 1. **Why SQLite?**
**Decision:** Use SQLite instead of PostgreSQL for MVP.

**Rationale:**
- ✅ Zero configuration
- ✅ Single-file portability
- ✅ Perfect for < 10,000 responses
- ✅ Easy local development

**Limitation:** Not suitable for Streamlit Cloud in production (data loss on restart).

**Future:** Migrate to PostgreSQL for permanent deployments.

---

### 2. **Demographic Data as JSON**
**Decision:** Store demographic info in a single `TEXT` column as JSON.

**Rationale:**
- ✅ Schema flexibility (easy to add new demographic fields)
- ✅ Simplifies queries for small datasets
- ❌ Harder to index/query for large datasets

**Example:**
```json
{
  "อำเภอ": "ตะกั่วป่า",
  "พื้นที่": "ในเขตเทศบาล",
  "Gen": "Gen Y (26-45)",
  "เพศ": "หญิง"
}
```

**Lesson:** For scale, normalize demographics into separate `voter_demographics` table with foreign keys.

---

### 3. **Invisible Button Technique**
**Problem:** Streamlit doesn't support `on_click` handlers for custom HTML.

**Solution:** CSS `:has()` pseudo-class to position invisible buttons over cards.

**Trade-off:**
- ✅ Beautiful, seamless UX
- ❌ Complex CSS maintenance
- ❌ Browser compatibility (`:has()` requires modern browsers)

**Alternative considered:** `streamlit-clickable-images` component (rejected due to limited customization).

---

### 4. **Base64 vs. Static File Serving**
**Problem:** Deployed apps struggled with `static/uploads/` paths.

**Solution:** Convert all images to Base64 and embed in HTML.

**Impact:**
- ✅ 100% reliable image display
- ❌ Larger HTML payload
- ❌ No browser caching

**Lesson:** For heavy image usage, use CDN (Cloudinary, AWS S3).

---

### 5. **GeoIP via ip-api.com**
**Decision:** Use free `ip-api.com` instead of paid MaxMind.

**Rationale:**
- ✅ Free tier: 45 requests/min
- ✅ JSON API (no database download)
- ✅ Accurate for city-level data

**Limitation:** Rate limits for high-traffic polls.

**Future:** Implement caching or switch to MaxMind for production.

---

## 🔮 Future Enhancements

### Short-Term (v2.0)
- [ ] **PostgreSQL Migration**: Persistent data on cloud
- [ ] **User Authentication**: Admin login with roles (Viewer, Editor, Owner)
- [ ] **Question Reordering**: Drag-and-drop question sequence
- [ ] **Conditional Logic**: Show Q2 only if Q1 = "Yes"
- [ ] **Multi-language Support**: English, Thai, Chinese
- [ ] **Dark Mode**: For admin dashboard

### Medium-Term (v3.0)
- [ ] **Advanced Analytics**:
  - Cross-tabulation matrix
  - Statistical significance testing
  - Trend analysis over time
- [ ] **Quota Enforcement**: Auto-close poll when quota reached
- [ ] **Email Notifications**: Alert admins on milestones
- [ ] **API for External Tools**: REST API for integrations
- [ ] **Voter Verification**: SMS OTP for high-stakes polls

### Long-Term (v4.0)
- [ ] **AI-Powered Insights**: LLM-generated summary reports
- [ ] **Real-time Collaboration**: Multiple admins editing simultaneously
- [ ] **Advanced QC**: Anomaly detection (bot votes, IP clusters)
- [ ] **White-label**: Customizable branding per campaign
- [ ] **Mobile App**: Native iOS/Android with offline support

---

## 🙏 Credits & Acknowledgments

### Built With
- [Streamlit](https://streamlit.io/) - Frontend framework
- [Plotly](https://plotly.com/python/) - Interactive charts
- [SQLite](https://www.sqlite.org/) - Embedded database
- [IP-API](https://ip-api.com/) - Geolocation service

### Inspiration
This project was built for the **Phang Nga District 2 Election Poll** (2025), requiring:
- Field operation quota tracking (N=360)
- Mobile-first UX for canvassers
- Real-time monitoring for campaign managers

### Developer
**Developed by:** [Your Name/Team]  
**Repository:** [github.com/ton-apicha/superpoll](https://github.com/ton-apicha/superpoll)  
**Live Demo:** [andaman-2025.streamlit.app](https://andaman-2025.streamlit.app/)

---

## 📄 License

This project is open-source under the **MIT License**.

```
MIT License

Copyright (c) 2025 SuperPoll Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

See [LICENSE](LICENSE) file for full text.

---

## 🐛 Known Issues & Troubleshooting

### Issue: Images not displaying in deployed app
**Cause:** Static file path issues on Streamlit Cloud.  
**Solution:** Already resolved via Base64 embedding. Ensure `get_img_base64()` is used in `render_card_html()`.

### Issue: "JSON parsing error" in demographics
**Cause:** Legacy responses with `NULL` demographic_data.  
**Solution:** Already patched in `get_demographic_breakdown()` with try-except wrapper.

### Issue: Slow loading with 1000+ responses
**Cause:** Unindexed queries on large datasets.  
**Solution:** Add indexes:
```sql
CREATE INDEX idx_responses_campaign ON responses(campaign_id);
CREATE INDEX idx_response_details_response ON response_details(response_id);
```

---

## 📞 Support

- **GitHub Issues:** [Report a bug](https://github.com/ton-apicha/superpoll/issues)
- **Email:** support@superpoll.example.com (replace with your contact)
- **Documentation:** This README + inline code comments

---

**Made with ❤️ for better democracy through data**

*Last Updated: 2025-12-31*
