import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta

# --- 1. 页面配置 ---
st.set_page_config(page_title="我的进化之路", page_icon="⚔️", layout="centered")

# --- 2. 核心设置与数据处理 ---
DATA_FILE = "study_log.csv"

# 自动处理新旧数据兼容问题
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # 确保新字段存在（如果读取旧文件，自动补全列，防止报错）
        expected_cols = ["日期", "是否学习", "学习时长", "学习科目", "核心结论", "复盘_S", "复盘_C", "复盘_Q", "复盘_A"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = "" 
        return df
    else:
        return pd.DataFrame(columns=["日期", "是否学习", "学习时长", "学习科目", "核心结论", "复盘_S", "复盘_C", "复盘_Q", "复盘_A"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- 3. RPG 游戏化算法 ---
def calculate_status(df):
    # 只计算真正学习了的记录
    study_df = df[df["是否学习"] == "是"]
    
    # 1. 计算总经验 (XP) = 总分钟数
    total_xp = study_df["学习时长"].sum() if not study_df.empty else 0
    
    # 2. 计算等级 (每 60 分钟升 1 级)
    level = int(total_xp // 60) + 1
    
    # 3. 计算称号
    if level <= 5: title = "🌱 萌新小白"
    elif level <= 10: title = "🔨 进阶学徒"
    elif level <= 20: title = "🛡️ 坚毅行者"
    elif level <= 50: title = "⚔️ 知识骑士"
    elif level <= 100: title = "🧙‍♂️ 智慧贤者"
    else: title = "👑 绝世学霸"
    
    # 4. 计算当前进度条 (距离下一级还差多少)
    next_level_xp = level * 60
    current_progress = (total_xp % 60) / 60
    
    return level, title, total_xp, current_progress

# --- 4. 界面 UI ---

# === 顶部：玩家状态栏 ===
df = load_data()
level, title, xp, progress = calculate_status(df)

st.title(f"⚔️ Lv.{level} {title}")
st.caption(f"当前总经验值 (XP): {xp} | 距离升级还需: {60 - (xp % 60)} 分钟")
st.progress(progress)
st.markdown("---")

# === 中部：打卡操作台 ===
st.header("📝 今日任务结算")

with st.form("study_form"):
    col1, col2 = st.columns(2)
    with col1:
        date_pick = st.date_input("📅 日期", datetime.now())
    with col2:
        # 增加科目选择，方便以后做ERP式分析
        subject = st.selectbox("📚 学习科目", ["Python 编程", "金字塔原理", "ERP 系统维护", "英语", "其他"])
    
    study_minutes = st.number_input("⏰ 投入时长 (分钟/XP)", min_value=0, step=30, value=60)
    did_study = st.checkbox("✅ 任务完成确认")

    st.markdown("### 🧠 金字塔深度复盘 (S.C.Q.A)")
    st.info("用结构化思维，把知识刻进脑子里！")
    
    # 金字塔原理结构化输入
    col_conclusion, col_dummy = st.columns([3, 1]) # 布局调整
    conclusion = st.text_input("💡 核心结论 (一句话总结今天学到了什么？)", placeholder="例如：掌握了Streamlit的布局技巧")
    
    with st.expander("点击展开详细复盘 (S.C.Q.A 模型)", expanded=True):
        s_text = st.text_area("S (情境 - 背景是什么？)", placeholder="例如：我想把工具移植到手机上...")
        c_text = st.text_area("C (冲突 - 遇到了什么困难？)", placeholder="例如：但是局域网配置总是报错...")
        q_text = st.text_area("Q (疑问 - 核心问题是什么？)", placeholder="例如：如何通过命令行正确启动？")
        a_text = st.text_area("A (答案 - 解决方案/行动)", placeholder="例如：使用了 python -m 命令并关闭了防火墙。")

    submitted = st.form_submit_button("🚀 提交结算，获取经验！")

# === 逻辑处理 ===
if submitted:
    if did_study and study_minutes > 0:
        st.balloons() # 只有真的学了才放气球庆祝！
        st.success(f"恭喜！获得 {study_minutes} 点经验值！")
    else:
        st.info("休息是为了走更远的路，明天见！")
        study_minutes = 0 # 没学就是0分

    # 构建新数据
    new_record = {
        "日期": date_pick,
        "是否学习": "是" if did_study else "否",
        "学习时长": study_minutes,
        "学习科目": subject,
        "核心结论": conclusion,
        "复盘_S": s_text,
        "复盘_C": c_text,
        "复盘_Q": q_text,
        "复盘_A": a_text
    }
    
    # 保存
    new_df = pd.DataFrame([new_record])
    df = pd.concat([new_df, df], ignore_index=True)
    save_data(df)
    
    # 强制刷新页面以更新顶部的等级条
    st.rerun()

# === 底部：历史数据 (简单展示) ===
with st.expander("📊 查看历史档案"):
    if not df.empty:
        # 只展示关键列，显得整洁
        st.dataframe(df[["日期", "学习科目", "学习时长", "核心结论"]], use_container_width=True)
    else:
        st.write("暂无记录，快开始你的第一次冒险吧！")