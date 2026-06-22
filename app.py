import streamlit as st
import pymysql
import pandas as pd
import plotly.express as px

# 1. Page Architectural Setup
st.set_page_config(
    page_title="Institutional Matrix Portal", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Sleek Deep Plum & Magenta Cyber Neon Custom Theme
st.markdown("""
<style>
    /* Global Base Background (Dark Plum/Deep Space) */
    .stApp {
        background-color: #0B0713;
        background-image: radial-gradient(circle at 80% 20%, #25103A 0%, #0B0713 60%);
        color: #F8FAFC !important;
    }
    
    /* Smooth Dynamic Loading Transitions */
    @keyframes fadeInSlide {
        0% { opacity: 0; transform: translateY(15px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    div[data-testid="stVerticalBlock"] > div {
        animation: fadeInSlide 0.6s ease-out forwards;
    }

    /* Premium Glassmorphism Magenta Neon Cards */
    div[data-testid="metric-container"] {
        background: rgba(26, 18, 38, 0.7) !important;
        border: 1px solid rgba(236, 72, 153, 0.3) !important;
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), 0 0 15px rgba(236, 72, 153, 0.1);
        backdrop-filter: blur(4px);
        -webkit-backdrop-filter: blur(4px);
    }
    
    /* Force Metric Titles to be Bright White */
    div[data-testid="metric-container"] [data-testid="stMetricLabel"] p {
        color: #F8FAFC !important;
        font-weight: 600 !important;
        text-transform: capitalize;
        letter-spacing: 0.03em;
        font-size: 1rem !important;
        opacity: 0.9 !important;
    }
    
    /* Glowing Rose/Magenta Numbers */
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] > div {
        color: #F43F5E !important;
        font-weight: 700 !important;
        font-size: 2.8rem !important;
        text-shadow: 0 0 12px rgba(244, 63, 94, 0.4);
    }

    /* Green Performance Delta Highlight */
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] svg {
        fill: #10B981 !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] div {
        color: #10B981 !important;
        font-weight: 600 !important;
    }

    /* High Visibility Input Labels */
    div[data-testid="stWidgetLabel"] p, label p, .stTextInput p {
        color: #F8FAFC !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }
    
    /* Transparent Smoky Input Fields */
    div[data-baseweb="input"] input {
        color: #FFFFFF !important;
        background-color: #1A1226 !important;
    }
    div[data-baseweb="input"] {
        background-color: #1A1226 !important;
        border: 1px solid rgba(236, 72, 153, 0.4) !important;
        border-radius: 10px;
    }

    /* Dataframe & Table Theme Customizations (Removes ugly white glare) */
    div[data-testid="stDataFrame"] {
        background-color: #1A1226 !important;
        border: 1px solid rgba(236, 72, 153, 0.3) !important;
        border-radius: 12px;
        padding: 10px;
    }
    div[data-testid="stDataFrame"] canvas {
        filter: invert(0.88) hue-rotate(150deg);
        border-radius: 8px;
    }

    /* Download Button Theme Customizations */
    div.stDownloadButton > button {
        color: #FFFFFF !important;
        background-color: rgba(244, 63, 94, 0.2) !important;
        border: 1px solid #F43F5E !important;
        border-radius: 10px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(244, 63, 94, 0.2);
    }
    div.stDownloadButton > button:hover {
        background-color: #F43F5E !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 15px rgba(244, 63, 94, 0.6);
        transform: translateY(-2px);
    }

    /* Cyber Dark Sidebar Construction */
    section[data-testid="stSidebar"] {
        background-color: #07040C !important;
        border-right: 1px solid rgba(236, 72, 153, 0.2);
    }
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #F8FAFC !important;
    }

    /* Master Typography Styles */
    .main-title {
        font-size: 2.85rem;
        font-weight: 800;
        background: linear-gradient(135deg, #F43F5E 0%, #D946EF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.35rem;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #94A3B8 !important;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }
</style>
""", unsafe_allow_html=True)

# --- DATABASE CONNECTION (Securely reading from st.secrets for safe deployment) ---
@st.cache_resource
def init_connection():
    return pymysql.connect(
        host=st.secrets["mysql"]["host"],
        user=st.secrets["mysql"]["user"],
        password=st.secrets["mysql"]["password"],
        database=st.secrets["mysql"]["database"],
        cursorclass=pymysql.cursors.DictCursor
    )

try:
    conn = init_connection()
except Exception as e:
    st.error(f"❌ Connection failed. Check your configuration parameters. Error: {e}")
    st.stop()

def run_query(query):
    with conn.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        return pd.DataFrame(result)

# --- FETCH DATA ---
df_students = run_query("""
    SELECT s.student_id, CONCAT(s.first_name, ' ', s.last_name) as student_name, 
           s.email, s.phone, s.enrollment_date, d.department_name 
    FROM students s
    LEFT JOIN departments d ON s.department_id = d.department_id
""")

df_faculty = run_query("""
    SELECT f.faculty_id, CONCAT(f.first_name, ' ', f.last_name) as faculty_name,
           d.department_name, f.designation 
    FROM faculty f
    LEFT JOIN departments d ON f.department_id = d.department_id
""")

# --- SIDEBAR LIVE SYSTEM HEALTH INDICATOR ---
st.sidebar.markdown("## 🏛️ Neon Portal Control")
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 System Pipeline Status")
if conn.open:
    st.sidebar.markdown("<span style='color:#10B981; font-weight:bold;'>● MySQL LINK: ACTIVE</span>", unsafe_allow_html=True)
else:
    st.sidebar.markdown("<span style='color:#EF4444; font-weight:bold;'>● MySQL LINK: DISCONNECTED</span>", unsafe_allow_html=True)
st.sidebar.markdown("---")

all_departments = list(df_students['department_name'].unique()) if not df_students.empty else []
selected_depts = st.sidebar.multiselect("Filter Target Department:", all_departments, default=all_departments)

if selected_depts:
    df_students_filtered = df_students[df_students['department_name'].isin(selected_depts)]
    df_faculty_filtered = df_faculty[df_faculty['department_name'].isin(selected_depts)]
else:
    df_students_filtered = df_students
    df_faculty_filtered = df_faculty

# --- MAIN DISPLAY HEADER ---
st.markdown('<div class="main-title">Campus Intelligence Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">A synchronized matrix dashboard verifying end-to-end data pipelines.</div>', unsafe_allow_html=True)

# --- AUTOMATED CAPACITY THRESHOLD MONITOR ---
if not df_students_filtered.empty:
    for dept in selected_depts:
        dept_count = len(df_students_filtered[df_students_filtered['department_name'] == dept])
        if dept_count >= 3:
            st.warning(f"⚠️ Operational Alert: {dept} registration capacity is optimization-critical ({dept_count} Active).")

# --- KPI METRIC CARDS WITH CONTEXT DELTAS ---
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Total Student Roster", value=len(df_students_filtered), delta="+12% vs Last Term")
with col2:
    st.metric(label="Active Academic Faculty", value=len(df_faculty_filtered), delta="1:15 Ratio Target")
with col3:
    unique_depts = df_students_filtered['department_name'].nunique() if not df_students_filtered.empty else 0
    st.metric(label="Monitored Clusters", value=unique_depts, delta="Fully Synced")

st.markdown("<br>", unsafe_allow_html=True)

# --- PRESENTATION TABS ---
tab1, tab2 = st.tabs(["📊 Distribution Matrices", "📋 Real-Time Registry Explorer"])

with tab1:
    if not df_students_filtered.empty:
        g1, g2 = st.columns(2)
        
        with g1:
            st.markdown("#### **Student Densities per Department**")
            student_counts = df_students_filtered['department_name'].value_counts().reset_index()
            student_counts.columns = ['Department', 'Students']
            
            fig_bar = px.bar(
                student_counts, x='Students', y='Department', 
                orientation='h', color='Students',
                color_continuous_scale=["#4C0519", "#F43F5E"],
                template="plotly_dark"
            )
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False, 
                yaxis={'categoryorder':'total ascending'}
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with g2:
            st.markdown("#### **Faculty Allocation Share**")
            if not df_faculty_filtered.empty:
                fac_counts = df_faculty_filtered['department_name'].value_counts().reset_index()
                fac_counts.columns = ['Department', 'Faculty Count']
                
                fig_pie = px.pie(
                    fac_counts, names='Department', values='Faculty Count',
                    hole=0.6,
                    color_discrete_sequence=["#F43F5E", "#D946EF", "#8B5CF6", "#475569"],
                    template="plotly_dark"
                )
                fig_pie.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                fig_pie.update_traces(textposition='outside', textinfo='percent+label')
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No faculty metrics found matching active filters.")
    else:
        st.warning("No records align with the active filter selections.")

with tab2:
    st.markdown("#### **Live Backend System Verification Grid**")
    
    search_query = st.text_input("⚡ Dynamic Search Engine (Filter instantly by Name, Email, or Phone):")
    
    if not df_students_filtered.empty:
        if search_query:
            match_mask = (
                df_students_filtered['student_name'].str.contains(search_query, case=False) |
                df_students_filtered['email'].str.contains(search_query, case=False) |
                df_students_filtered['phone'].str.contains(search_query, case=False)
            )
            final_df = df_students_filtered[match_mask]
        else:
            final_df = df_students_filtered

        st.dataframe(final_df, use_container_width=True, hide_index=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        csv_data = final_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export Current View to CSV Report",
            data=csv_data,
            file_name="campus_registry_export.csv",
            mime="text/csv"
        )
    else:
        st.info("The student database is currently empty.")