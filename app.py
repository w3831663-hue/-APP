import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime, timedelta
import random

# --- 页面配置 ---
st.set_page_config(page_title="极简自律助手", page_icon="🍅", layout="centered")

# --- 核心数据逻辑 ---
DATA_FILE = "study_log.csv"

def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["日期", "类型", "科目", "时长", "学了什么", "卡在哪里", "改进措施"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# 计算连续打卡天数
def calculate_streak(df):
    if df.empty: return 0
    # 转换日期格式并去重
    dates = pd.to_datetime(df["日期"]).dt.date.unique()
    dates.sort()
    
    streak = 0
    today = datetime.now().date()
    
    # 从最近的一天开始倒推
    check_date = today
    # 如果今天还没打卡，就从昨天算起，不算断签
    if today not in dates:
        check_date = today - timedelta(days=1)
        
    while check_date in dates:
        streak += 1
        check_date -= timedelta(days=1)
    return streak

# --- 侧边栏：内容库与计划 ---
st.sidebar.header("🗂️ 学习内容库")
# 这里对应第9点：内容库
subjects = st.sidebar.multiselect(
    "我的常驻科目", 
    ["Python", "金字塔原理", "ERP维护", "英语单词", "数据分析"],
    default=["Python", "金字塔原理"]
)

st.sidebar.markdown("---")
st.sidebar.header("📅 今日计划")
if st.sidebar.button("🎲 生成今日计划"):
    if subjects:
        task = random.choice(subjects)
        st.sidebar.success(f"今天重点攻克：**{task}**")
        st.sidebar.info("建议时长：45 分钟")
    else:
        st.sidebar.warning("请先在上方选择科目")

# --- 主界面 ---
df = load_data()
streak_days = calculate_streak(df)

# 顶部数据看板（对应第3点：热力图/连胜）
col1, col2, col3 = st.columns(3)
col1.metric("🔥 连续自律", f"{streak_days} 天")
today_minutes = df[df["日期"] == datetime.now().strftime("%Y-%m-%d")]["时长"].sum()
col2.metric("⏳ 今日专注", f"{today_minutes} 分钟")
col3.metric("📅 累计天数", f"{len(df['日期'].unique())} 天")

st.markdown("---")

# === 功能区 1：专注计时器 (对应第2点) ===
st.subheader("⏱️ 沉浸时刻")

# 使用 Session State 管理计时器状态
if 'start_time' not in st.session_state:
    st.session_state.start_time = None

c1, c2 = st.columns(2)
with c1:
    if st.button("▶️ 开始学习", use_container_width=True):
        st.session_state.start_time = time.time()
        st.toast("计时开始！保持专注，不要看手机哦~")

with c2:
    if st.button("⏹️ 结束并结算", use_container_width=True):
        if st.session_state.start_time:
            end_time = time.time()
            duration = int((end_time - st.session_state.start_time) / 60)
            st.session_state.duration_cache = duration # 暂存时长
            st.session_state.start_time = None
            st.success(f"本次专注：{duration} 分钟")
        else:
            st.warning("请先点击开始")

# === 功能区 2：打卡与复盘 (对应第5、6点) ===
st.markdown("### 📝 结营打卡")

tab1, tab2 = st.tabs(["✅ 完成学习", "🛌 今日请假"])

with tab1:
    with st.form("normal_log"):
        # 自动填入刚才计时器的时长，如果没有就是0
        default_min = st.session_state.get('duration_cache', 60)
        
        pick_sub = st.selectbox("学习科目", subjects if subjects else ["默认"])
        mins = st.number_input("专注时长(分钟)", value=default_min, step=5)
        
        # 对应第5点：三句复盘法
        st.markdown("**三句复盘法：**")
        q1 = st.text_input("1. 今天学了什么关键内容？", placeholder="例如：Streamlit 的 session_state 用法")
        q2 = st.text_input("2. 哪里卡住了/遇到了困难？", placeholder="例如：对 GitHub 的提交逻辑还有点晕")
        q3 = st.text_input("3. 明天如何改进？", placeholder="例如：明天要把部署流程画个图")
        
        if st.form_submit_button("提交打卡"):
            new_row = {
                "日期": datetime.now().strftime("%Y-%m-%d"),
                "类型": "学习",
                "科目": pick_sub,
                "时长": mins,
                "学了什么": q1,
                "卡在哪里": q2,
                "改进措施": q3
            }
            df = pd.concat([pd.DataFrame([new_row]), df], ignore_index=True)
            save_data(df)
            st.balloons()
            st.rerun() # 刷新页面更新顶部数据

with tab2:
    st.info("对应功能 6：‘一键合法摆烂’。状态不好的时候，允许自己休息，不会断掉连续打卡记录。")
    with st.form("skip_day"):
        reason = st.text_input("休息原因 (选填)", placeholder="身体不舒服 / 朋友聚会 / 纯粹想躺")
        if st.form_submit_button("🛌 批准今日休息"):
            new_row = {
                "日期": datetime.now().strftime("%Y-%m-%d"),
                "类型": "休息",
                "科目": "无",
                "时长": 0,
                "学了什么": "休息充电",
                "卡在哪里": reason,
                "改进措施": "明天满血复活"
            }
            df = pd.concat([pd.DataFrame([new_row]), df], ignore_index=True)
            save_data(df)
            st.success("休息是为了走更远的路！")
            st.rerun()

# === 底部：近期记录 ===
with st.expander("🗃️ 查看近期日记"):
    st.dataframe(df, use_container_width=True)
