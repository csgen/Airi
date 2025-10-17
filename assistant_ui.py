# assistant_ui.py
import streamlit as st
import pandas as pd
from datetime import datetime

# 页面配置
st.set_page_config(page_title="我的AI助手", layout="wide")

# 侧边栏 - 导航
st.sidebar.title("导航")
page = st.sidebar.radio("选择功能", ["数据统计", "智能对话", "日程管理", "个性化推荐"])

if page == "数据统计":
    st.title("📊 我的电脑使用统计")
    # 这里放数据可视化代码
    
elif page == "智能对话":
    st.title("💬 与助手对话")
    # 这里放聊天界面代码
    
elif page == "日程管理":
    st.title("📅 我的日程")
    # 这里放日历集成代码