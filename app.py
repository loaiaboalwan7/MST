%%writefile app.py
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
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("https://postimg.co", width=180, use_container_width=False)
        st.markdown('<div class="title-main">فريق روح مردك التطوعي</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle-main">بوابة تسجيل الدخول الآمنة</div>', unsafe_allow_html=True)
        
        with st.form("login_gate_form"):
            login_email = st.text_input("📧 الرجاء إدخال البريد الإلكتروني المعتمد بالسجلات:", placeholder="username@gmail.com").strip().lower()
            submit_login = st.form_submit_button("🔓 تسجيل الدخول للمنظومة")
            
            if submit_login:
                allowed_masters = ["2024.12.16.mst@gmail.com", "murduksoulteam@gmail.com"]
                cursor.execute("SELECT status FROM volunteers WHERE email=? AND status='حالي'", (login_email,))
                is_active_volunteer = cursor.fetchone()
                
                if login_email in allowed_masters or is_active_volunteer:
                    st.session_state.logged_in = True
Use code with caution.st.session_state.user_email = login_emailst.success("✨ تم التحقق من الهوية الرقمية، جارٍ فتح النظام...")st.rerun()else:st.error("🚫 عذراً! هذا البريد الإلكتروني غير مسجل حالياً أو تم إلغاء وصوله من قبل إدارة الموارد البشرية.")st.stop()==============================================================================5. إدارة لوحة السحب والإطار الجانبي للتنقل (يخفى تماماً بالرئيسية)==============================================================================if st.session_state.current_view == "🏠 الواجهة الرئيسية":# إخفاء قائمة التصفح الجانبية تماماً في الواجهة الرئيسية لراحة بصرية فائقةst.sidebar.markdown("### 🔒 نظام الحماية النشط")st.sidebar.info(f"👤 مرحباً بك:\n\n{st.session_state.user_email}")if st.sidebar.button("🚪 تسجيل الخروج الآمن"):st.session_state.logged_in = Falsest.session_state.user_email = ""st.session_state.current_view = "🏠 الواجهة الرئيسية"st.rerun()else:# إظهار إطار السحب الجانبي فقط عند الدخول للأقسام الفرعية لسهولة العودة والتنقلst.sidebar.markdown("### 🧭 لوحة التصفح الذكية")nav_choice = st.sidebar.radio("انتقل سريعاً بين الأقسام المتاحة لك:", ["🏠 الواجهة الرئيسية","🕊️ نافذة المتطوعين والفعاليات","🛠️ لوحة تحكم الأقسام المتقدمة"])if nav_choice != st.session_state.current_view:st.session_state.current_view = nav_choicest.rerun()st.sidebar.divider()if st.sidebar.button("🚪 تسجيل الخروج"):st.session_state.logged_in = Falsest.session_state.user_email = ""st.session_state.current_view = "🏠 الواجهة الرئيسية"st.rerun()==============================================================================6. شاشة العرض الأولى: 🏠 الواجهة الرئيسية (التصميم المربع العصري)==============================================================================if st.session_state.current_view == "🏠 الواجهة الرئيسية":# الجزء العلوي الثابت للهوية البصرية المتناسقة تماماً مع ألوان اللوغو البني الدافئst.markdown("", unsafe_allow_html=True)st.image("postimg.co", width=180)st.markdown('روح مردك', unsafe_allow_html=True)st.markdown('روح واحدة بأكثر من جسد', unsafe_allow_html=True)st.markdown("", unsafe_allow_html=True)# معرض الفريق - عرض الشرائح (Carousel) المميز المبني برمجياً للتصفح فقطst.markdown(" معرض نبضات فريق روح مردك", unsafe_allow_html=True)cursor.execute("SELECT type, url FROM gallery ORDER BY id DESC")media_items = cursor.fetchall()if media_items:cols_gallery = st.columns(min(len(media_items), 4))for idx, item in enumerate(media_items[:4]):with cols_gallery[idx % 4]:if item[0] == 'صورة':st.image(item[1], use_container_width=True)else:st.video(item[1])else:st.caption("المعرض فارغ حالياً، بانتظار ومضات القسم الإعلامي الموثقة...", unsafe_allow_html=True)st.divider()# الأزرار المربعة الثلاثة المتناسقة الجذابة للتنقلst.markdown("""المتطوعون والفعالياتلوحة تحكم الأقسام""", unsafe_allow_html=True)# معالجة الضغطات البرمجية البديلة للأزرار المربعة داخل Streamlitcol_b1, col_b2, col_b3 = st.columns([1, 1, 1])with col_b1:if st.button("✨ الدخول لـ نافذة المتطوعين والفعاليات", use_container_width=True):st.session_state.current_view = "🕊️ نافذة المتطوعين والفعاليات"st.rerun()with col_b2:if st.button("⚙️ الدخول لـ لوحة تحكم الأقسام", use_container_width=True):st.session_state.current_view = "🛠️ لوحة تحكم الأقسام المتقدمة"st.rerun()==============================================================================7. شاشة العرض الثانية: 🕊️ نافذة المتطوعين والفعاليات المدمجة (للاستعلام والتصفح)==============================================================================elif st.session_state.current_view == "🕊️ نافذة المتطوعين والفعاليات":st.markdown(" واجهة الاستعلامات المفتوحة للمنظومة", unsafe_allow_html=True)tab_vol, tab_eve = st.tabs(["🙋‍♂️ لوحة المتطوعين الشخصية", "📅 أرشيف وبحث الفعاليات المقامة"])# تفعيل الجزء الأول: نافذة البحث والاستعلام الشخصي للمتطوعwith tab_vol:st.subheader("🔍 استعلام ذكي وبحث عن ملف متطوع")search_type = st.radio("اختر وسيلة البحث السريعة المتاحة:", ["البحث بالاسم الثلاثي كاملاً", "البحث بواسطة رقم السجل التسلسلي"])cursor.execute("SELECT serial_number, name FROM volunteers WHERE status='حالي'")all_actives = cursor.fetchall()search_query = ""if search_type == "البحث بالاسم الثلاثي كاملاً":search_query = st.selectbox("اختر أو اكتب الاسم المراد الاستعلام عن مؤشراته:", [x[1] for x in all_actives])else:search_query = st.selectbox("اختر رقم السجل التسلسلي المستهدف للتأكد من هويته:", [x[0] for x in all_actives])if search_query:if search_type == "البحث بالاسم الثلاثي كاملاً":cursor.execute("SELECT * FROM volunteers WHERE name=?", (search_query,))else:cursor.execute("SELECT * FROM volunteers WHERE serial_number=?", (search_query,))v_res = cursor.fetchone()if v_res:v_id, s_num, name, m_name, b_date, qual, branch, phone, email, exp, j_date, status, _, _, _, _, _, _, _ = v_res# جلب القسم الحالي التابع له برمجياً من التشكيلة الحالية المعتمدةcursor.execute("SELECT role FROM current_assignment WHERE volunteer_email=? OR coordinator_email=?", (email, email))assigned_role = cursor.fetchone()current_dep_name = assigned_role[0] if assigned_role else "عضو ميداني عام"# جلب البرنامج الحالي المسكن بداخل سجلاته المتطوعcursor.execute("SELECT p.title FROM programs p JOIN program_members pm ON p.id=pm.program_id WHERE pm.volunteer_email=?", (email,))prog_name = cursor.fetchone()current_prog_name = prog_name[0] if prog_name else "غير مسكن ببرنامج حالي"# جلب الفعاليات التي حضرها بدقة ومطابقة التواريخ والبرامج الفرعيةcursor.execute('''SELECT e.title, e.type, e.start_date FROM events eJOIN event_participants ep ON e.id = ep.event_idWHERE ep.volunteer_email=?''', (email,))v_events_list = cursor.fetchall()# حساب الرتب والمؤشرات التنافسية الذكية المطلوبة بدقة من نواحٍ مختلفةcursor.execute("SELECT email FROM volunteers")all_v_emails = [x[0] for x in cursor.fetchall()]# ترتيب 1: بناءً على نقاط مؤشر الأداء الكلي المعقدscores_dict = {em: calculate_volunteer_score(em) for em in all_v_emails}sorted_by_score = sorted(scores_dict.items(), key=lambda item: item[1], reverse=True)rank_by_score = [x[0] for x in sorted_by_score].index(email) + 1# ترتيب 2: بناءً على عدد مرات حضور المشاركات الفعلية الميدانية للفعالياتattendance_dict = {}for em in all_v_emails:cursor.execute("SELECT COUNT(*) FROM event_participants WHERE volunteer_email=?", (em,))attendance_dict[em] = cursor.fetchone()[0]sorted_by_attendance = sorted(attendance_dict.items(), key=lambda item: item[1], reverse=True)rank_by_attendance = [x[0] for x in sorted_by_attendance].index(email) + 1# عرض كرت المتطوع الشخصي المطور بأيقونات عصرية فائقة المظهرst.markdown(f"### 🪪 الملف الرقمي الموثق: {name}")c1, c2, c3 = st.columns(3)c1.markdown(f"📌 رقم السجل: {s_num}\n\n🎂 تاريخ الميلاد: {b_date}")c2.markdown(f"🏢 القسم الإداري: {current_dep_name}\n\n🌿 البرنامج النشط: {current_prog_name}")c3.markdown(f"📱 رقم الجوال: {phone}\n\n📅 تاريخ الانضمام: {j_date}")st.divider()# عدادات ومقاييس الأداء التنافسية الثنائية الذكيةm1, m2, m3 = st.columns(3)m1.metric("🏅 مؤشر الأداء التراكمي الكلي", f"{scores_dict[email]} نقطة")m2.metric("🏆 الترتيب العام بمؤشر الأداء", f"#{rank_by_score} من الفريق")m3.metric("🏃‍♂️ الترتيب كمشارك ميداني بالفعاليات", f"#{rank_by_attendance} من الفريق")st.markdown("#### 📅 قائمة الفعاليات الميدانية التي شارك بها:")if v_events_list:df_v_ev = pd.DataFrame(v_events_list, columns=["عنوان الفعالية الميدانية", "نوع الفعالية الموثق", "تاريخ الانعقاد"])st.dataframe(df_v_ev, use_container_width=True)else:st.info("💡 هذا المتطوع لم يسجل حضوراً في أي فعالية للفريق حتى هذه اللحظة.")# تفعيل الجزء الثاني: شاشة عرض وبحث الفعاليات لعموم المستخدمين (للتصفح فقط)with tab_eve:st.subheader("🔍 محرك بحث الأرشيف الشامل لفعاليات روح مردك")f_title = st.text_input("📝 اكتب جزءاً من عنوان الفعالية للبحث الفوري:")f_place = st.text_input("📍 اكتب اسم مكان الفعالية لتصفيتها:")# جلب الفعاليات المطابقة لمعايير الفلترة والبحث المتقدمةq_ev = "SELECT * FROM events WHERE 1=1"params = []if f_title:q_ev += " AND title LIKE ?"params.append(f"%{f_title}%")if f_place:q_ev += " AND location LIKE ?"params.append(f"%{f_place}%")q_ev += " ORDER BY id DESC"cursor.execute(q_ev, tuple(params))searched_events = cursor.fetchall()if searched_events:for ev in searched_events:ev_id, title, ev_type, s_date, e_date, loc, b_count, a_group, cost, partners, challenges, sub_acts, e_dt = ev# جلب المتطوعين المشاركين في تنفيذ هذه الفعالية بالتحديد لعرضهم للأرشيفcursor.execute('''SELECT v.name FROM volunteers vJOIN event_participants ep ON v.email = ep.volunteer_emailWHERE ep.event_id=?''', (ev_id,))parts_names = [x[0] for x in cursor.fetchall()]with st.expander(f"📊 الفعالية: {title} | 🗓️ التاريخ: {s_date} | 📍 المكان: {loc}"):col_ev1, col_ev2 = st.columns(2)with col_ev1:st.markdown(f"🔹 نوع الفعالية: {ev_type}")st.markdown(f"🔹 المدى الزمني: من {s_date} إلى {e_date}")st.markdown(f"🔹 عدد المستفيدين الكلي: {b_count} مستفيد ({a_group})")st.markdown(f"🔹 التكلفة النهائية: {cost}")with col_ev2:st.markdown(f"🔹 الجهات التنسيقية والمشاركة: {partners}")st.markdown(f"🔹 الأنشطة الميدانية الفرعية: {sub_acts}")st.markdown(f"🔹 التحديات والصعوبات الموثقة:  {challenges}")st.markdown("👥 فريق العمل المتطوع المشارك بالتنفيذ:")st.write(" ، ".join(parts_names) if parts_names else "لا يوجد مشاركين مسجلين بالملف.")else:st.warning("⚠️ لا توجد فعاليات مسجلة تطابق محددات البحث المكتوبة حالياً.")==============================================================================8. شاشة العرض الثالثة: 🛠️ لوحة تحكم الأقسام المتقدمة (حماية الصلاحيات الصارمة)==============================================================================elif st.session_state.current_view == "🛠️ لوحة تحكم الأقسام المتقدمة":st.markdown(" لوحة تحكم الصلاحيات وإدارة الهياكل التنظيمية", unsafe_allow_html=True)# اختيار القسم المراد الدخول إليه وفحص الصلاحيات المرتبطة بالبريد الإلكتروني الموثقdep_selected = st.selectbox("اختر الواجهة التنظيمية التي تود إدارتها وتحديث بياناتها:", ["👑 واجهة مسؤول الفريق (القيادة العليا)","🏢 قسم الموارد البشرية","💰 قسم الشؤون المالية","📸 قسم الإنتاج الإعلامي","📈 قسم الإحصاء والتوثيق الميداني"])# 🌟 1. معالجة وتأمين واجهة مسؤول الفريق (حماية بكلمة مرور + حظر الموارد البشرية)if dep_selected == "👑 واجهة مسؤول الفريق (القيادة العليا)":st.markdown("### 👑 لوحة تحكم وإدارة مسؤول الفريق والنائب")# شرط أمني صارم: حظر كامل لأعضاء الموارد البشرية من فتح هذه الواجهة حتى لو امتلكوا الباسوردcursor.execute("SELECT * FROM current_assignment WHERE role='الموارد البشرية' AND (volunteer_email=? OR coordinator_email=?)", (st.session_state.user_email, st.session_state.user_email))is_hr_agent = cursor.fetchone()if is_hr_agent:st.error("🚫 عذراً! يمنع نظام الصلاحيات الصارم لروح مردك أعضاء ومنسقي قسم الموارد البشرية من دخول واجهة المسؤول لضمان فصل السلطات الإدارية والرقابية.")else:admin_pass_input = st.text_input("🔐 يرجى إدخال كلمة المرور القيادية الحالية للوصول:", type="password")cursor.execute("SELECT value FROM system_config WHERE key='admin_password'")real_admin_pass = cursor.fetchone()[0]if admin_pass_input == real_admin_pass or st.session_state.user_email in ["2024.12.16.mst@gmail.com", "murduksoulteam@gmail.com"]:st.success("🔓 تم فتح صلاحيات الإدارة العليا بنجاح.")sub_tab_admin_1, sub_tab_admin_2 = st.tabs(["🗂️ التشكيلات الإدارية الحالية والسابقة", "🌿 إدارة وتسكين البرامج الزمنية"])# إدارة الصلاحيات والتشكيلات الإدارية المتزامنة مع التاريخ المؤتمت لروح مردكwith sub_tab_admin_1:st.subheader("➕ تعيين تشكيلة إدارية دورية جديدة للفريق")cursor.execute("SELECT email, name FROM volunteers WHERE status='حالي'")v_options = cursor.fetchall()v_map_opts = {x[0]: x[1] for x in v_options}v_list_emails = list(v_map_opts.keys())with st.form("new_assignment_form"):m_leader = st.selectbox("👤 مسؤول الفريق العام:", v_list_emails, format_func=lambda x: v_map_opts[x])m_deputy = st.selectbox("👤 نائب مسؤول الفريق:", v_list_emails, format_func=lambda x: v_map_opts[x])st.divider()m_hr = st.selectbox("🏢 المسؤول عن قسم الموارد البشرية:", v_list_emails, format_func=lambda x: v_map_opts[x])c_hr = st.selectbox("🤝 المنسق المساعد لقسم الموارد البشرية:", v_list_emails, format_func=lambda x: v_map_opts[x])m_media = st.selectbox("📸 المسؤول عن قسم الإنتاج الإعلامي:", v_list_emails, format_func=lambda x: v_map_opts[x])c_media = st.selectbox("🤝 المنسق المساعد لقسم الإنتاج الإعلامي:", v_list_emails, format_func=lambda x: v_map_opts[x])m_stats = st.selectbox("📈 المسؤول عن قسم الإحصاء والتوثيق الميداني:", v_list_emails, format_func=lambda x: v_map_opts[x])c_stats = st.selectbox("🤝 المنسق المساعد لقسم الإحصاء والتوثيق الميداني:", v_list_emails, format_func=lambda x: v_map_opts[x])m_finance = st.selectbox("💰 المسؤول عن قسم الشؤون المالية:", v_list_emails, format_func=lambda x: v_map_opts[x])c_finance = st.selectbox("🤝 المنسق المساعد لقسم الشؤون المالية:", v_list_emails, format_func=lambda x: v_map_opts[x])
