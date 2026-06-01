import streamlit as st
import sqlite3
import pandas as pd

# 1. إعداد قاعدة البيانات والاتصال بها
conn = sqlite3.connect('volunteer_system.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    tasks TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS volunteers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    email TEXT,
    phone TEXT,
    department_id INTEGER,
    score INTEGER DEFAULT 0,
    FOREIGN KEY(department_id) REFERENCES departments(id)
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    date TEXT
)''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS attendance (
    volunteer_id INTEGER,
    event_id INTEGER,
    PRIMARY KEY(volunteer_id, event_id),
    FOREIGN KEY(volunteer_id) REFERENCES volunteers(id),
    FOREIGN KEY(event_id) REFERENCES events(id)
)''')
conn.commit()

# --- إعدادات واجهة المطور التفاعلية ---
st.set_page_config(page_title="نظام إدارة الفريق التطوعي", layout="wide")
st.title("📊 نظام إدارة الفريق التطوعي الذكي")

menu = ["🏠 الرئيسية ورفع البيانات", "🏢 الأقسام والمهام", "🙋‍♂️ المتطوعون والإحصائيات", "📅 الفعاليات والمشاركين"]
choice = st.sidebar.selectbox("اختر الجزء المُراد إدارته:", menu)

# --- الجزء الأول: الرئيسية ورفع البيانات ---
if choice == "🏠 الرئيسية ورفع البيانات":
    st.header("📥 إدخال البيانات إلى النظام")
    
    uploaded_file = st.file_uploader("اختر ملف إكسل جاهز (شيت المتطوعين مثلاً)", type=["xlsx", "xls"])
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file)
            st.write("معاينة البيانات المرفوعة:")
            st.dataframe(df.head())
            
            if st.button("تأكيد حفظ ملف الإكسل في قاعدة البيانات"):
                for index, row in df.iterrows():
                    cursor.execute('''
                        INSERT OR IGNORE INTO volunteers (name, email, phone, score) 
                        VALUES (?, ?, ?, ?)
                    ''', (str(row['الاسم']), str(row['الإيميل']), str(row['الهاتف']), int(row['المؤشر'])))
                conn.commit()
                st.success("تم استيراد بيانات المتطوعين بنجاح والتزامن فوري!")
        except Exception as e:
            st.error(f"حدث خطأ أثناء قراءة الملف، تأكد من مطابقة أسماء الأعمدة: {e}")

    st.divider()
    st.subheader("📝 إضافة متطوع جديد يدوياً")
    with st.form("add_volunteer_form"):
        v_name = st.text_input("اسم المتطوع كاملاً")
        v_email = st.text_input("البريد الإلكتروني")
        v_phone = st.text_input("رقم الهاتف")
        v_score = st.number_input("المؤشر الحالي للمتطوع", min_value=0, value=10)
        
        deps = pd.read_sql_query("SELECT id, name FROM departments", conn)
        dep_choice = st.selectbox("اختر قسم المتطوع", deps['name'].tolist() if not deps.empty else ["لا توجد أقسام بعد"])
        
        submitted = st.form_submit_button("إضافة للمنظومة")
        if submitted:
            if v_name:
                dep_id = int(deps[deps['name'] == dep_choice]['id'].values[0]) if not deps.empty and dep_choice != "لا توجد أقسام بعد" else None
                cursor.execute("INSERT OR IGNORE INTO volunteers (name, email, phone, department_id, score) VALUES (?, ?, ?, ?, ?)", 
                               (v_name, v_email, v_phone, dep_id, v_score))
                conn.commit()
                st.success(f"تم إضافة {v_name} وتحديث قاعدة البيانات فوراً!")
            else:
                st.warning("يرجى إدخال اسم المتطوع")

# --- الجزء الثاني: الأقسام والمهام ---
elif choice == "🏢 الأقسام والمهام":
    st.header("🏢 إدارة أقسام الفريق وتعديل بياناتها")
    
    with st.expander("➕ إضافة قسم جديد بالفريق"):
        new_dep = st.text_input("اسم القسم (مثال: الإعلام، التنظيم)")
        dep_tasks = st.text_area("مهام هذا القسم")
        if st.button("حفظ القسم الجديد"):
            if new_dep:
                cursor.execute("INSERT OR IGNORE INTO departments (name, tasks) VALUES (?, ?)", (new_dep, dep_tasks))
                conn.commit()
                st.success(f"تم إنشاء قسم {new_dep}")
                st.rerun()

    st.subheader("🗂️ الأقسام الحالية وتحديث مهامها")
    departments_df = pd.read_sql_query("SELECT * FROM departments", conn)
    if not departments_df.empty:
        for idx, row in departments_df.iterrows():
            st.markdown(f"### 🎯 قسم: {row['name']}")
            new_tasks = st.text_area(f"تعديل مهام قسم {row['name']}", value=row['tasks'], key=f"task_{row['id']}")
            if st.button(f"تحديث مهام {row['name']}", key=f"btn_{row['id']}"):
                cursor.execute("UPDATE departments SET tasks = ? WHERE id = ?", (new_tasks, row['id']))
                conn.commit()
                st.success("تم تحديث قاعدة البيانات بنجاح!")
    else:
        st.info("لا توجد أقسام مسجلة حتى الآن.")

# --- الجزء الثالث: المتطوعون والإحصائيات والترتيب ---
elif choice == "🙋‍♂️ المتطوعون والإحصائيات":
    st.header("🙋‍♂️ لوحة تحكم ومؤشرات المتطوعين")
    
    query = "SELECT v.id, v.name AS 'اسم المتطوع', d.name AS 'القسم', v.score AS 'المؤشر الرقمي', COUNT(a.event_id) AS 'عدد الفعاليات المشارك بها', RANK() OVER (ORDER BY v.score DESC, COUNT(a.event_id) DESC) AS 'الترتيب العام' FROM volunteers v LEFT JOIN departments d ON v.department_id = d.id LEFT JOIN attendance a ON v.id = a.volunteer_id GROUP BY v.id ORDER BY [الترتيب العام] ASC"
    volunteers_stats = pd.read_sql_query(query, conn)
    
    if not volunteers_stats.empty:
        st.subheader("🏆 جدول الترتيب العام للمتطوعين (تحديث تلقائي ولحظي)")
        st.dataframe(volunteers_stats, use_container_width=True)
        
        st.divider()
        st.subheader("🔍 استعلام مخصص لملف متطوع")
        search_volunteer = st.selectbox("اختر اسم المتطوع لمعرفة تفاصيله والفعاليات التي حضرها:", volunteers_stats['اسم المتطوع'].tolist())
        
        if search_volunteer:
            v_id = int(volunteers_stats[volunteers_stats['اسم المتطوع'] == search_volunteer]['id'].values[0])
            
            events_query = f"SELECT e.name AS 'اسم الفعالية', e.date AS 'تاريخ الفعالية' FROM events e JOIN attendance a ON e.id = a.event_id WHERE a.volunteer_id = {v_id}"
            v_events = pd.read_sql_query(events_query, conn)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("الترتيب الحالي للفريق", f"#{volunteers_stats[volunteers_stats['id'] == v_id]['الترتيب العام'].values[0]}")
            col2.metric("مؤشر الأداء الرقمي", int(volunteers_stats[volunteers_stats['id'] == v_id]['المؤشر الرقمي'].values[0]))
            col3.metric("مجموع الفعاليات", int(volunteers_stats[volunteers_stats['id'] == v_id]['عدد الفعاليات المشارك بها'].values[0]))
            
            st.markdown(f"#### 📅 قائمة الفعاليات التي شارك بها ({search_volunteer}):")
            if not v_events.empty:
                st.table(v_events)
            else:
                st.info("هذا المتطوع لم يشارك في أي فعاليات حتى الآن.")
    else:
        st.info("لا يوجد متطوعين في النظام حالياً، يرجى إدخال بيانات أو رفع ملف إكسل من الصفحة الرئيسية.")

# --- الجزء الرابع: الفعاليات والمشاركين ---
elif choice == "📅 الفعاليات والمشاركين":
    st.header("📅 إدارة فعاليات الفريق التطوعي")
    
    col_ev1, col_ev2 = st.columns(2)
    with col_ev1:
        st.subheader("➕ تسجيل فعالية جديدة")
        with st.form("event_form"):
            ev_name = st.text_input("اسم الفعالية التطوعية")
            ev_date = st.date_input("تاريخ الفعالية")
            submitted_ev = st.form_submit_button("إنشاء الفعالية")
            if submitted_ev and ev_name:
                cursor.execute("INSERT OR IGNORE INTO events (name, date) VALUES (?, ?)", (ev_name, str(ev_date)))
                conn.commit()
                st.success(f"تم تسجيل فعالية '{ev_name}' بنجاح!")
                st.rerun()
                
    with col_ev2:
        st.subheader("🔗 تسجيل حضور المتطوعين في فعالية")
        all_v = pd.read_sql_query("SELECT id, name FROM volunteers", conn)
        all_e = pd.read_sql_query("SELECT id, name FROM events", conn)
        
        if not all_v.empty and not all_e.empty:
            with st.form("attendance_form"):
                select_v = st.selectbox("اسم المتطوع", all_v['name'].tolist())
                select_e = st.selectbox("اسم الفعالية", all_e['name'].tolist())
                if st.form_submit_button("تسجيل مشاركة الحضور"):
                    vid = int(all_v[all_v['name'] == select_v]['id'].values[0])
                    eid = int(all_e[all_e['name'] == select_e]['id'].values[0])
                    try:
                        cursor.execute("INSERT INTO attendance (volunteer_id, event_id) VALUES (?, ?)", (vid, eid))
                        conn.commit()
                        st.success(f"تم تسجيل حضور {select_v} في {select_e}!")
                    except:
                        st.warning("هذا المتطوع مسجل بالفعل في هذه الفعالية.")
        else:
            st.info("يجب إضافة متطوعين وفعاليات أولاً لتتمكن من ربطهم.")

    st.divider()
    st.subheader("📋 كشف الفعاليات المقامة وأسماء المشاركين بها")
    events_list = pd.read_sql_query("SELECT * FROM events", conn)
    if not events_list.empty:
        for idx, ev_row in events_list.iterrows():
            st.markdown(f"### 📊 الفعالية: **{ev_row['name']}** | 🗓️ بتاريخ: `{ev_row['date']}`")
            part_query = f"SELECT v.name AS 'اسم المتطوع المشارك', d.name AS 'قسمه' FROM volunteers v JOIN attendance a ON v.id = a.volunteer_id LEFT JOIN departments d ON v.department_id = d.id WHERE a.event_id = {int(ev_row['id'])}"
            participants_df = pd.read_sql_query(part_query, conn)
            if not participants_df.empty:
                st.dataframe(participants_df, use_container_width=True)
            else:
                st.caption("لا يوجد مشاركين مسجلين في هذه الفعالية بعد.")
    else:
        st.info("لا توجد فعاليات مسجلة.")
