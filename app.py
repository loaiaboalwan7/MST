import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import io

# ==============================================================================
# 1. إعداد قاعدة البيانات والاتصال المزامَن
# ==============================================================================
conn = sqlite3.connect('volunteer_system.db', check_same_thread=False)
cursor = conn.cursor()

# إنشاء الجداول المتكاملة المتوافقة مع كافة التعديلات الأمنية والإدارية
cursor.execute('''
CREATE TABLE IF NOT EXISTS system_config (
    key TEXT PRIMARY KEY,
    value TEXT
)''')

# وضع كلمة المرور الافتراضية للمسؤول إذا لم تكن موجودة
cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('admin_password', 'mst162026')")
cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('spending_limit', '1000')")
cursor.execute("INSERT OR IGNORE INTO system_config (key, value) VALUES ('emergency_fund', '0')")

cursor.execute('''
CREATE TABLE IF NOT EXISTS volunteers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    serial_number TEXT UNIQUE,
    name TEXT NOT NULL,
    mother_name TEXT,
    birth_date TEXT,
    qualification TEXT,
    branch TEXT,
    phone TEXT,
    email TEXT UNIQUE,
    experience TEXT,
    join_date TEXT,
    status TEXT DEFAULT 'حالي', -- حالي / انسحاب / إيقاف عمل
    exit_date TEXT,
    exit_reason TEXT,
    exit_notes TEXT,
    ideas_radical INTEGER DEFAULT 0,
    ideas_important INTEGER DEFAULT 0,
    impact_level TEXT DEFAULT 'ضعيف' -- جيد / متوسط / ضعيف
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS current_assignment (
    role TEXT PRIMARY KEY, -- مسؤول الفريق / النائب / الموارد البشرية / الإعلامي / الإحصاء والتوثيق / المالي
    volunteer_email TEXT,
    coordinator_email TEXT,
    start_date TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS assignment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    role TEXT,
    volunteer_email TEXT,
    coordinator_email TEXT,
    start_date TEXT,
    end_date TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS financial_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT, -- استلام / صرف
    date TEXT,
    party TEXT,
    receiver TEXT,
    amount REAL
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS gallery (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT, -- صورة / فيديو
    url TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    type TEXT, -- أصلية / خارجية
    start_date TEXT,
    end_date TEXT,
    location TEXT,
    beneficiaries_count INTEGER,
    age_group TEXT,
    cost REAL,
    partners TEXT,
    challenges TEXT,
    sub_activities TEXT,
    entry_date TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS event_participants (
    event_id INTEGER,
    volunteer_email TEXT,
    is_leader INTEGER DEFAULT 0, -- 1 إذا كان مسؤولاً أو نائباً للفعالية
    PRIMARY KEY(event_id, volunteer_email)
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS disciplinary_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    volunteer_email TEXT,
    type TEXT, -- تنبيه شفوي / تجميد عضوية
    reason TEXT,
    start_date TEXT,
    end_date TEXT,
    notes TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS programs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT UNIQUE,
    coordinators_limit INTEGER,
    volunteers_limit INTEGER,
    fields TEXT,
    manager_email TEXT,
     توثيق_email TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS program_members (
    program_id INTEGER,
    volunteer_email TEXT,
    role TEXT, -- عضو / منسق أنشطة
    PRIMARY KEY(program_id, volunteer_email)
)''')
conn.commit()

# ==============================================================================
# 2. الهوية البصرية، التصميم الاحترافي، والخطوط العصرية
# ==============================================================================
st.set_page_config(page_title="روح مردك | إدارة المنظومة", layout="wide", initial_sidebar_state="expanded")

# تخصيص ثيم الألوان المتناسق مع اللوغو (درجات البني الدافئ والخطوط الاحترافية)
st.markdown("""
<style>
    @import url('https://googleapis.com');
    
    html, body, [data-testid="stSidebar"], .stApp {
        font-family: 'Cairo', sans-serif;
        background-color: #FDFBF7;
        color: #4A3E3D;
        direction: rtl;
        text-align: right;
    }
    
    /* تصميم الأزرار المربعة الكبرى الفاخرة في الصفحة الرئيسية */
    .main-btn-container {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 40px;
        flex-wrap: wrap;
    }
    .main-box-btn {
        background: linear-gradient(135deg, #8C6A5C 0%, #5F473E 100%);
        color: white !important;
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        width: 240px;
        height: 240px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.08);
        cursor: pointer;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        text-decoration: none;
        border: 2px solid #E6DCD2;
    }
    .main-box-btn:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 30px rgba(140, 106, 92, 0.25);
        border-color: #8C6A5C;
    }
    .main-box-btn i {
        font-size: 50px;
        margin-bottom: 15px;
    }
    .main-box-btn span {
        font-size: 22px;
        font-weight: bold;
    }
    
    /* تنسيق العناوين المخصصة لروح مردك */
    .title-main {
        font-size: 52px;
        color: #5F473E;
        font-weight: bold;
        text-align: center;
        margin-top: 10px;
        margin-bottom: 0px;
    }
    .subtitle-main {
        font-size: 24px;
        color: #8C6A5C;
        text-align: center;
        margin-top: 5px;
        margin-bottom: 30px;
        font-style: italic;
    }
</style>
<!-- تضمين مكتبة أيقونات عصرية FontAwesome -->
<link rel="stylesheet" href="https://cloudflare.com">
""", unsafe_allow_allowed_html=True)

# ==============================================================================
# 3. معادلات احتساب مؤشر الأداء والترتيبات الإحصائية
# ==============================================================================
def calculate_volunteer_score(email):
    # جلب بيانات المتطوع الأساسية والأفكار والتأثير
    cursor.execute("SELECT status, ideas_radical, ideas_important, impact_level FROM volunteers WHERE email=?", (email,))
    v_data = cursor.fetchone()
    if not v_data: return 0
    status, radical, important, impact = v_data
    
    if status == 'إيقاف عمل':
        return 0
        
    # 1. عدد الفعاليات الكلي التي شارك بها
    cursor.execute("SELECT COUNT(*) FROM event_participants WHERE volunteer_email=?", (email,))
    events_count = cursor.fetchone()[0]
    
    # 2. عدد المرات التي كان فيها مسؤولاً أو نائباً في الفعالية
    cursor.execute("SELECT COUNT(*) FROM event_participants WHERE volunteer_email=? AND is_leader=1", (email,))
    leader_count = cursor.fetchone()[0]
    
    # 3. عدد تشكيلات الأقسام المشارك بها تاريخياً (حالية وسابقة)
    cursor.execute("SELECT COUNT(*) FROM assignment_history WHERE volunteer_email=? OR coordinator_email=?", (email, email))
    history_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM current_assignment WHERE volunteer_email=? OR coordinator_email=?", (email, email))
    current_count = cursor.fetchone()[0]
    total_assignments = history_count + current_count

    # تطبيق المعادلة الحسابية الدقيقة المعتمدة لروح مردك
    base_score = events_count + (leader_count * 9) + (total_assignments * 2) + (radical * 6) + (important * 3)
    
    # حساب قيمة معامل التأثير الميداني
    if impact == 'جيد':
        final_score = base_score + (base_score * 0.5)
    elif impact == 'متوسط':
        final_score = base_score + (base_score * 0.25)
    else:
        final_score = base_score
        
    # معامل الخروج بسبب الانسحاب (يأخذ 75% فقط من الجهد)
    if status == 'انسحاب':
        final_score = final_score * 0.75
        
    return round(final_score, 2)

# ==============================================================================
# 4. بوابة تسجيل الدخول الموحدة (Login Gate) وحماية الصلاحيات
# ==============================================================================
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'current_view' not in st.session_state:
    st.session_state.current_view = "🏠 الواجهة الرئيسية"

# شاشة تسجيل الدخول الموحدة للفريق لحجب أي وصول خارجي غير مصرح به
# --- بوابة تسجيل الدخول (Login Gate) ---
if not st.session_state.get('user_email'):
    st.markdown("<h2 style='text-align: center; color: #5D4037;'>🔐 تسجيل الدخول للنظام</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        login_email = st.text_input("البريد الإلكتروني المعتمد للفريق", placeholder="example@gmail.com").strip().lower()
        submit_login = st.form_submit_button("دخول وآمن")
        
        if submit_login:
            # 1. التحقق من الحسابات القيادية الافتراضية
            allowed_admin_emails = ["2024.12.16.mst@gmail.com", "murduksoulteam@gmail.com"]
            
            # 2. التحقق من المتطوعين الحاليين في قاعدة البيانات
            is_volunteer = False
            try:
                check_query = "SELECT COUNT(*) FROM volunteers WHERE LOWER(email) = ?"
                cursor.execute(check_query, (login_email,))
                if cursor.fetchone()[0] > 0:
                    is_volunteer = True
            except:
                pass
            
            # اتخاذ قرار الدخول
            if login_email in allowed_admin_emails or is_volunteer:
                st.session_state.user_email = login_email
                st.success("✨ تم التحقق من الهوية الرقمية، جارٍ فتح النظام...")
                st.rerun()
            else:
                st.error("🚫 عذراً! هذا البريد الإلكتروني غير مسجل حالياً أو تم إلغاء وصوله من قبل إدارة الموارد البشرية.")
                st.stop()
    st.stop()

# --- إدارة لوحة السحب والإطار الجانبي للتنقل (يخفى تماماً بالرئيسية) ---
if st.session_state.get('current_view') == "🏠 الواجهة الرئيسية":
    st.sidebar.markdown("### 🔒 نظام الحماية النشط")
    st.sidebar.info(f"👤 مرحباً بك:\n\n{st.session_state.get('user_email', 'غير مسجل')}")
r_email}")
