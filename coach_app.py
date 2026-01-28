from st_aggrid import AgGrid, GridOptionsBuilder
import pandas as pd
import streamlit as st
import requests
from datetime import date
from typing import List, Dict, Optional

# ==================== API 設定 ====================
import os
import socket

def get_api_base_url():
    """動態取得 API Base URL，支援手機訪問"""
    # 優先使用環境變數
    if os.getenv("API_BASE_URL"):
        return os.getenv("API_BASE_URL")
    
    # 自動偵測主機 IP（適用於區域網路訪問）
    try:
        # 取得本機 IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        host_ip = s.getsockname()[0]
        s.close()
        return f"http://{host_ip}:8000"
    except:
        # 備用方案：使用 localhost
        return "http://127.0.0.1:8000"

API_BASE_URL = get_api_base_url()


# ==================== 導航輔助函數 ====================
def navigate_to(page: str):
    """導航到指定頁面，同步更新 session state 和 URL"""
    st.session_state.page = page
    st.query_params["page"] = page
    st.rerun()



# ==================== API 呼叫函數 ====================
def get_teachers() -> List[Dict]:
    """從 API 取得所有教練"""
    try:
        response = requests.get(f"{API_BASE_URL}/teachers/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"無法取得教練資料: {e}")
        return []


def get_courses() -> List[Dict]:
    """從 API 取得所有課程"""
    try:
        response = requests.get(f"{API_BASE_URL}/courses/")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"無法取得課程資料: {e}")
        return []


def create_attendance(data: Dict) -> bool:
    """建立上課紀錄"""
    try:
        response = requests.post(f"{API_BASE_URL}/attendances/", json=data)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"提交失敗: {e}")
        return False


def create_sales(data: Dict) -> bool:
    """建立賣課紀錄"""
    try:
        response = requests.post(f"{API_BASE_URL}/sales/", json=data)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"提交失敗: {e}")
        return False


def get_salary_rules() -> List[Dict]:
    """取得薪資規則"""
    try:
        response = requests.get(f"{API_BASE_URL}/admin/rules")
        response.raise_for_status()
        return response.json()
    except Exception:
        return []


def update_salary_rules(tiers: List[Dict]) -> bool:
    """更新薪資規則"""
    try:
        payload = {"tiers": tiers}
        response = requests.post(f"{API_BASE_URL}/admin/rules", json=payload)
        response.raise_for_status()
        return True
    except Exception as e:
        st.error(f"更新失敗: {e}")
        return False


def get_monthly_stats() -> Dict:
    """取得月度統計"""
    try:
        response = requests.get(f"{API_BASE_URL}/admin/stats")
        response.raise_for_status()
        return response.json()
    except Exception:
        return {}


def get_all_attendances() -> List[Dict]:
    try:
        response = requests.get(f"{API_BASE_URL}/attendances/")
        return response.json()
    except:
        return []

def get_all_sales() -> List[Dict]:
    try:
        response = requests.get(f"{API_BASE_URL}/sales/")
        return response.json()
    except:
        return []


# ==================== 教練薪資頁面邏輯 ====================
def get_historical_rules(year: int, month: int) -> List[Dict]:
    """取得特定年月的薪資規則"""
    try:
        response = requests.get(f"{API_BASE_URL}/admin/rules/history", params={"year": year, "month": month})
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_attendances_by_date_range(start_date: str, end_date: str) -> List[Dict]:
    try:
        response = requests.get(f"{API_BASE_URL}/attendances/date-range/", params={"start_date": start_date, "end_date": end_date})
        return response.json()
    except:
        return []

def get_sales_by_date_range(start_date: str, end_date: str) -> List[Dict]:
    try:
        response = requests.get(f"{API_BASE_URL}/sales/date-range/", params={"start_date": start_date, "end_date": end_date})
        return response.json()
    except:
        return []

def calculate_dynamic_salary(student_count: int, rules: List[Dict]) -> float:
    """根據傳入的規則計算薪資 (Client-side recalculation)"""
    for tier in rules:
        if tier["min"] <= student_count <= tier["max"]:
            return float(tier["amount"])
    
    # 預設：如果沒有匹配的規則，返回最高級別薪資 (或最後一個規則)
    if rules:
        return float(rules[-1]["amount"])
    return 0.0

def show_coach_salary_page():
    st.markdown("### 💰 教練月薪統計表")
    
    # 1. 月份選擇器
    c1, c2 = st.columns([1, 3])
    with c1:
        current_year = date.today().year
        year_options = [str(y) for y in range(current_year - 2, current_year + 3)]
        # Default index matches current_year
        selected_year_str = custom_select("年份", year_options, key="salary_year", default_index=2)
        selected_year = int(selected_year_str)
    with c2:
        current_month = date.today().month
        month_options = [str(m) for m in range(1, 13)]
        selected_month_str = custom_select("月份", month_options, key="salary_month", default_index=current_month - 1)
        selected_month = int(selected_month_str)
    
    # 計算日期範圍
    import calendar
    last_day = calendar.monthrange(selected_year, selected_month)[1]
    start_date = f"{selected_year}-{selected_month:02d}-01"
    end_date = f"{selected_year}-{selected_month:02d}-{last_day}"
    
    # 2. 取得資料
    with st.spinner("正在重新計算薪資資料..."):
        # A. 取得該月規則
        monthly_rules = get_historical_rules(selected_year, selected_month)
        
        # B. 取得上課紀錄
        attendances = get_attendances_by_date_range(start_date, end_date)
        
        # C. 取得賣課紀錄
        sales = get_sales_by_date_range(start_date, end_date)
        
        # D. 取得所有教練名稱 (Mapping用)
        teachers = get_teachers()
        teacher_map = {t['id']: t['name'] for t in teachers}
    
    if not monthly_rules:
        st.warning("⚠️ 查無該月薪資規則設定，將使用目前系統預設規則計算。")
        # Fallback logic is handled by API returning current rules, but warning is good.
    
    # 3. 計算薪資 (Aggregation)
    salary_data = {} # teacher_id -> {base: 0, commission: 0, name: ""}
    
    # 初始化
    for tid, tname in teacher_map.items():
        salary_data[tid] = {"name": tname, "base_salary": 0, "commission": 0, "total": 0}
        
    # 計算上課薪資 (Base Salary) - 使用 monthly_rules 重算
    for record in attendances:
        tid = record['teacher_id']
        if tid not in salary_data: continue # 略過未知教練
        
        # 重算薪資
        count = record['student_count']
        salary = calculate_dynamic_salary(count, monthly_rules)
        salary_data[tid]['base_salary'] += salary
        
    # 計算賣課提成 (Commission) - 直接使用紀錄中的 commission (因為提成通常是當下決定的，還是也要重算？)
    # 需求說：「內部資料就是根據salary_rule以及提成等 算出的...」
    # 提成部分：需求沒特別說要重算提成規則，且提成規則比較死 (固定金額)，但 models 裡有存 commission。
    # 通常提成是跟隨當下銷售的，若要重算可能需要歷史提成規則。
    # 為了簡單與安全，這裡假設銷售提成沿用當時紀錄的值 (因為 Database 已經存了 commission)。
    # 如果使用者希望提成也重算，需要另外存提成規則歷史。目前需求重點似乎在於 "salary_rule" (上課人數級距)。
    # "也就是說當調用前月的資料時 會用儲存的那份rule重新計算" -> 指 salary_rule.
    for record in sales:
        tid = record['teacher_id']
        if tid not in salary_data: continue
        
        if record.get('commission'):
            salary_data[tid]['commission'] += float(record['commission'])
    
    # 彙整總額
    for tid in salary_data:
        salary_data[tid]['total'] = salary_data[tid]['base_salary'] + salary_data[tid]['commission']
        
    # 轉為 DataFrame
    df_salary = pd.DataFrame(list(salary_data.values()))
    
    # 過濾掉 0 元的教練 (可選)
    df_salary = df_salary[df_salary['total'] > 0]
    
    if df_salary.empty:
        st.info("該月份尚無薪資資料。")
    else:
        # 格式化顯示
        df_display = df_salary.copy()
        df_display = df_display.rename(columns={
            "name": "教練姓名",
            "base_salary": "上課薪資 (Base)",
            "commission": "銷售提成 (Commission)",
            "total": "總薪資 (Total)"
        })
        
        # 排序
        df_display = df_display.sort_values("總薪資 (Total)", ascending=False)
        
        # 4. 顯示表格
        st.markdown(f"#### 📊 {selected_year}年{selected_month}月 薪資統計表")
        st.dataframe(
            df_display, 
            column_config={
                "上課薪資 (Base)": st.column_config.NumberColumn(format="$%d"),
                "銷售提成 (Commission)": st.column_config.NumberColumn(format="$%d"),
                "總薪資 (Total)": st.column_config.NumberColumn(format="$%d"),
            },
            use_container_width=True,
            hide_index=True
        )
        
        # 5. 匯出功能
        csv = df_display.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="⬇️ 匯出 Excel (CSV)",
            data=csv,
            file_name=f"coach_salary_{selected_year}_{selected_month}.csv",
            mime="text/csv",
            type="primary"
        )


# ==================== 自訂選擇器（解決 selectbox 文字不可見問題）====================
def custom_select(label: str, options: List[str], key: str, default_index: int = 0) -> str:
    """自訂選擇器，使用 radio 實作以確保文字可見"""
    st.markdown(f'<div style="color: white; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;">{label}</div>', unsafe_allow_html=True)
    
    # 使用 expander 模擬下拉選單
    if f"{key}_selected" not in st.session_state:
        st.session_state[f"{key}_selected"] = options[default_index] if options else ""
    
    with st.expander(f"✓ {st.session_state[f'{key}_selected']}", expanded=False):
        selected = st.radio(
            "選項",
            options=options,
            index=options.index(st.session_state[f"{key}_selected"]) if st.session_state[f"{key}_selected"] in options else 0,
            key=f"{key}_radio",
            label_visibility="collapsed"
        )
        if selected != st.session_state[f"{key}_selected"]:
            st.session_state[f"{key}_selected"] = selected
            st.rerun()
    
    return st.session_state[f"{key}_selected"]


def tel_number_input(label: str, key: str, min_value: int = 0, max_value: int = 999, value: int = 0) -> int:
    """自訂數字輸入框 - 強制使用九宮格電話鍵盤 (type=tel)"""
    
    # 初始化 session state
    if key not in st.session_state:
        st.session_state[key] = value
    
    # 顯示標籤
    st.markdown(f'<div style="color: white; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem;">{label}</div>', unsafe_allow_html=True)
    
    # 使用 text_input（稍後用 JS 改為 type="tel"）
    current_val = st.session_state[key]
    display_val = str(current_val) if current_val != 0 else ""
    
    val_str = st.text_input(
        label,
        value=display_val,
        key=f"{key}_tel",
        label_visibility="collapsed",
        placeholder="0"
    )
    
    # 解析輸入值
    if val_str and val_str.isdigit():
        new_val = int(val_str)
        if new_val != st.session_state[key]:
            final_val = max(min_value, min(max_value, new_val))
            st.session_state[key] = final_val
            st.rerun()
    elif val_str == "":
        if st.session_state[key] != 0:
            st.session_state[key] = 0
            st.rerun()
    elif val_str != display_val:
        st.rerun()

    # JavaScript: 強制將 input type 改為 tel (唯一能觸發九宮格的方法)
    js = f"""
    <script>
        (function() {{
            const targetKey = "{key}_tel";
            
            function forceTelType() {{
                // 使用 data-testid 定位到正確的 input
                const inputs = document.querySelectorAll('input[aria-label="{label}"]');
                inputs.forEach(input => {{
                    // 強制改為 type="tel" (這是觸發九宮格的關鍵)
                    if (input.type !== 'tel') {{
                        input.type = 'tel';
                    }}
                    // 確保只能輸入數字
                    input.addEventListener('input', function(e) {{
                        this.value = this.value.replace(/[^0-9]/g, '');
                    }});
                }});
            }}
            
            // 初次執行
            setTimeout(forceTelType, 100);
            
            // 監控 DOM 變化
            const observer = new MutationObserver(forceTelType);
            const targetNode = document.querySelector('.stApp');
            if (targetNode) {{
                observer.observe(targetNode, {{ childList: true, subtree: true }});
            }}
        }})();
    </script>
    """
    st.markdown(js, unsafe_allow_html=True)

    return st.session_state[key]




# ==================== 自訂 CSS 樣式（手機優先）====================
def apply_custom_style():
    """套用 Mobile First 設計與黑色主題"""
    st.markdown("""
        <style>
        /* 配色變數 */
        :root {
            --dance-orange: #FF7F50;
            --dance-blue: #4A90E2;
            --dance-yellow: #F9ED69;
            --dance-purple: #B088F9;
            --black-bg: #000000;
            --dark-gray: #2B2B2B;
            --input-gray: #3D3D3D;
            --border-white: #FFFFFF;
            --text-white: #FFFFFF;
        }
        
        /* 全域設定 - 黑色背景 */
        .stApp {
            background-color: var(--black-bg) !important;
            color: var(--text-white) !important;
            max-width: 100%;
        }
        
        /* 主容器也是黑色 */
        .main {
            background-color: var(--black-bg) !important;
        }
        
        /* 隱藏 Streamlit 預設元素 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        /* header {visibility: hidden;}  <-- 不要隱藏 header，否則漢堡選單會不見 */
        
        /* 容器設定 - 手機優先 */
        .block-container {
            max-width: 800px;
            padding-top: 2rem;
            padding-bottom: 5rem;
        }
        
        /* 大按鈕樣式 */
        .big-button {
            background: linear-gradient(135deg, #FFE5D9, #FFF);
            border: none;
            border-radius: 20px;
            padding: 2rem 1.5rem;
            margin: 1rem 0;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 4px 12px rgba(255,255,255,0.1);
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .big-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(255,255,255,0.15);
        }
        
        .big-button.orange {
            background: linear-gradient(135deg, #FFE5D9, #FFCDB2);
        }
        
        .big-button.blue {
            background: linear-gradient(135deg, #D4E8FF, #B8D8FF);
        }
        
        .big-button.dark {
            background: linear-gradient(135deg, #2B2B2B, #1E1E1E);
            color: white;
        }
        
        /* 圖示區塊 */
        .icon-box {
            width: 60px;
            height: 60px;
            border-radius: 15px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
        }
        
        .icon-box.orange {
            background: #FF7F50;
        }
        
        .icon-box.blue {
            background: #4A90E2;
        }
        
        .icon-box.yellow {
            background: #F9C74F;
        }
        
        /* 標題樣式 - 白色文字 */
        .page-title {
            font-size: 1.8rem;
            font-weight: bold;
            color: var(--text-white) !important;
            margin-bottom: 0.5rem;
            text-align: center;
        }
        
        .page-subtitle {
            font-size: 1rem;
            color: #CCC !important;
            margin-bottom: 2rem;
            text-align: center;
        }
        
        /* 表單標籤 - 白色文字 */
        .stSelectbox > label,
        .stDateInput > label,
        .stNumberInput > label,
        .stTextInput > label,
        .stTextArea > label {
            color: var(--text-white) !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            margin-bottom: 0.5rem;
        }
        
        /* 所有輸入框 - 灰色背景 + 白邊 + 白色文字 */
        .stSelectbox [data-baseweb="select"] > div,
        .stDateInput > div > div > input,
        .stNumberInput > div > div > input,
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            background-color: var(--input-gray) !important;
            color: var(--text-white) !important;
            border: 2px solid var(--border-white) !important;
            border-radius: 12px !important;
            font-size: 1rem !important;
            padding: 0.75rem !important;
        }
        
        /* Selectbox 修正 */
        .stSelectbox [data-baseweb="select"],
        .stSelectbox [data-baseweb="select"] > div {
            background-color: var(--input-gray) !important;
            color: var(--text-white) !important;
            border-color: var(--border-white) !important;
        }
        
        /* 下拉選單文字顏色 - 強制覆蓋所有子元素 */
        .stSelectbox [data-baseweb="select"] * {
             color: var(--text-white) !important;
             -webkit-text-fill-color: var(--text-white) !important;
             caret-color: var(--text-white) !important;
        }
        
        /* 確保選單選項也是黑底白字 */
        .stSelectbox [data-baseweb="popover"] div, 
        .stSelectbox [data-baseweb="menu"] div {
            background-color: var(--input-gray) !important;
            color: var(--text-white) !important;
        }
        
        /* 隱藏 NumberInput 的增減按鈕 (隱藏所有 Streamlit 產生的按鈕) */
        .stNumberInput button {
            display: none !important;
        }
        div[data-testid="stNumberInput"] > div > div > button {
            display: none !important;
        }
        
        /* 針對 Mobile 瀏覽器隱藏原生 spin button */
        input[type="number"]::-webkit-inner-spin-button,
        input[type="number"]::-webkit-outer-spin-button {
             -webkit-appearance: none;
             margin: 0;
        }

        /* 輸入框樣式優化 */
        .stNumberInput input {
            inputmode: numeric !important; /* 強制數字鍵盤 (Android/iOS) */
            pattern: "[0-9]*" !important;  /* 確保鍵盤樣式正確 */
            /* text-align: center !important;  <-- 移除置中，回復預設靠左或瀏覽器預設 */
            border-radius: 12px !important;
            -moz-appearance: textfield; /* Firefox */
        }
        
        /* 主要按鈕 (Primary) - 漸層大按鈕 */
        .stButton button[data-testid="stBaseButton-primary"] {
            background: linear-gradient(135deg, var(--dance-purple), var(--dance-yellow)) !important;
            color: #000 !important;
            font-weight: bold;
            border: none;
            padding: 1rem 2rem !important;
            border-radius: 15px !important;
            width: 100%;
            font-size: 1.2rem !important;
            margin-top: 1rem;
            box-shadow: 0 4px 12px rgba(255,255,255,0.15);
        }
        
        .stButton button[data-testid="stBaseButton-primary"]:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(255,255,255,0.2);
        }

        /* 次要按鈕 (Secondary) - 簡潔小按鈕 (用於計數器) */
        .stButton button[data-testid="stBaseButton-secondary"] {
            background-color: var(--dark-gray) !important;
            color: var(--text-white) !important;
            border: 1px solid var(--border-white) !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            min-height: 45px;
        }
        
        .stButton button[data-testid="stBaseButton-secondary"]:hover {
            border-color: var(--dance-blue) !important;
            color: var(--dance-blue) !important;
        }

        /* 統計卡片 */
        .stat-card {
            background: var(--dark-gray);
            border-radius: 15px;
            padding: 1.5rem;
            border-left: 5px solid var(--dance-blue);
            margin-bottom: 1rem;
        }
        
        .stat-title {
            color: #AAA;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }
        
        .stat-value {
            color: #FFF;
            font-size: 1.8rem;
            font-weight: bold;
        }
        
        .positive { color: #4CAF50 !important; }
        .negative { color: #FF5252 !important; }

        </style>
        
        <script>
        // 通用行動裝置優化：確保所有數字輸入框都使用正確的鍵盤類型
        // 適用於 Android 與 iOS
        document.addEventListener('DOMContentLoaded', function() {
            function enforcePhonePad() {
                const numberInputs = document.querySelectorAll('input[type="number"]');
                numberInputs.forEach(input => {
                    // 通用設定：inputmode=numeric 和 pattern=[0-9]* 是標準做法
                    if (input.getAttribute('pattern') !== '[0-9]*') {
                        input.setAttribute('pattern', '[0-9]*');
                        input.setAttribute('inputmode', 'numeric');
                    }
                });
            }
            
            // 初次執行
            enforcePhonePad();
            
            // 使用 MutationObserver 監控動態渲染
            const targetNode = document.querySelector('.stApp');
            if (targetNode) {
                const observer = new MutationObserver((mutations) => {
                     enforcePhonePad();
                });
                observer.observe(targetNode, { childList: true, subtree: true });
            }
        });
        </script>
    """, unsafe_allow_html=True)


# ==================== 頁面：首頁 ====================
def show_homepage():
    """顯示首頁 - 三個大按鈕"""
    st.markdown('<div class="page-title">Dance DEX 2025</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Hi 教練，今天想紀錄什麼？</div>', unsafe_allow_html=True)
    
    # 紀錄上課按鈕
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown('<div class="icon-box orange">📝</div>', unsafe_allow_html=True)
    with col2:
        if st.button("**紀錄上課**\n\nClass Record", key="btn_class", type="primary", use_container_width=True):
            st.session_state.form_data = {}
            navigate_to("class_form")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 紀錄收入按鈕
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown('<div class="icon-box blue">💰</div>', unsafe_allow_html=True)
    with col2:
        if st.button("**紀錄收入（賣課）**\n\nSales Record", key="btn_sales", type="primary", use_container_width=True):
            st.session_state.form_data = {}
            navigate_to("sales_form")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 老闆面板按鈕
    col1, col2 = st.columns([1, 5])
    with col1:
        st.markdown('<div class="icon-box yellow">👑</div>', unsafe_allow_html=True)
    with col2:
        if st.button("**我是老闆**\n\nBoss Dashboard", key="btn_boss", type="primary", use_container_width=True):
            # 如果已經登入過，直接進儀表板
            if st.session_state.get("is_boss_logged_in", False):
                navigate_to("boss_dashboard")
            else:
                navigate_to("boss_login")


# ==================== 頁面：老闆登入 ====================
def show_boss_login():
    """老闆登入頁面"""
    st.markdown('<div class="page-title">👑 老闆登入</div>', unsafe_allow_html=True)
    
    password = st.text_input("請輸入管理密碼", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回", key="login_back"):
            navigate_to("home")
            
    with col2:
        if st.button("登入 →", key="login_submit", type="primary"):
            if password == "0000":
                st.session_state.is_boss_logged_in = True
                navigate_to("boss_dashboard")
            else:
                st.error("密碼錯誤！")


# ==================== 頁面：老闆儀表板 ====================
def show_boss_dashboard():
    """老闆管理面板"""
    # 檢查登入狀態
    if not st.session_state.get("is_boss_logged_in", False):
        navigate_to("boss_login")
        return

    # 側邊欄導航 (漢堡選單)
    with st.sidebar:
        st.markdown("### 👑 管理員選單")
        st.write(f"歡迎回來，老闆！")
        st.markdown("---")
        if st.button("🚪 登出系統", type="primary", use_container_width=True):
            st.session_state.is_boss_logged_in = False
            navigate_to("home")

    # --- 主內容區域 ---
    # 使用 Radio Button 代替 Tabs 以避免渲染問題
    st.markdown('<div class="page-title">📊 管理面板</div>', unsafe_allow_html=True)
    
    dashboard_mode = st.radio(
        "功能切換", 
        ["數據總覽", "資料檢視", "教練薪資", "規則設定"], 
        horizontal=True,
        label_visibility="collapsed",
        key="boss_dashboard_nav"
    )
    
    st.markdown("---")

    # --- Mode 1: 數據總覽 ---
    if dashboard_mode == "數據總覽":
        with st.container():
            st.markdown("### 📅 本月財務概況")
            
            stats = get_monthly_stats()
            # 若無數據，插入模擬數據以展示介面效果
            if not stats: 
                # MOCK DATA
                stats = {
                    "total_revenue": 1250000, 
                    "total_expenses": 860000, 
                    "net_income": 390000
                }
                st.info("💡 目前顯示為模擬數據 (Mock Data)，真實數據累積後將自動替換。")

            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class="stat-card" style="border-left-color: #4CAF50;">
                    <div class="stat-title">總收入 (Revenue)</div>
                    <div class="stat-value">NT$ {stats.get('total_revenue', 0):,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
                
            with c2:
                st.markdown(f"""
                <div class="stat-card" style="border-left-color: #FF5252;">
                    <div class="stat-title">總支出 (Expenses)</div>
                    <div class="stat-value">NT$ {stats.get('total_expenses', 0):,.0f}</div>
                </div>
                """, unsafe_allow_html=True)
                
            net = stats.get('net_income', 0)
            color = "#4CAF50" if net >= 0 else "#FF5252"
            st.markdown(f"""
            <div class="stat-card" style="border-left-color: {color};">
                <div class="stat-title">淨利 (Net Income)</div>
                <div class="stat-value" style="color: {color} !important;">
                    NT$ {net:,.0f}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # --- Mode 3: 教練薪資 (New) ---
    elif dashboard_mode == "教練薪資":
        show_coach_salary_page()

    # --- Mode 2: 資料檢視 ---
    elif dashboard_mode == "資料檢視":
        with st.container():
            st.markdown("### 📝 資料紀錄")
            view_type = st.radio("選擇檢視資料", ["上課紀錄 (Attendance)", "賣課紀錄 (Sales)"], key="boss_data_view_type", horizontal=True)
            
            if view_type == "上課紀錄 (Attendance)":
                data = get_all_attendances()
                
                # MOCK DATA for Attendance
                if not data or len(data) == 0:
                    data = [
                        {"id": 1, "student_name": "Alice Wang", "course_name": "K-Pop 基礎", "teacher_name": "小美老師", "date": "2024-01-15", "points_deducted": 1},
                        {"id": 2, "student_name": "Bob Chen", "course_name": "HipHop 進階", "teacher_name": "阿豪老師", "date": "2024-01-16", "points_deducted": 1.5},
                        {"id": 3, "student_name": "Carol Li", "course_name": "Jazz入門", "teacher_name": "小美老師", "date": "2024-01-16", "points_deducted": 1},
                        {"id": 4, "student_name": "David Wu", "course_name": "Locking 專攻", "teacher_name": "大毛老師", "date": "2024-01-17", "points_deducted": 1},
                        {"id": 5, "student_name": "Eve Lin", "course_name": "MV 舞曲", "teacher_name": "小美老師", "date": "2024-01-18", "points_deducted": 1},
                    ]
                    st.info("💡 目前為模擬上課紀錄。")

                if data and len(data) > 0:
                    df = pd.DataFrame(data)
                    
                    # 取得教練和課程資料用於 ID 轉換
                    teachers = get_teachers()
                    courses = get_courses()
                    teacher_dict = {t['id']: t['name'] for t in teachers}
                    course_dict = {c['id']: c['name'] for c in courses}
                    
                    # 處理 nested object (如果有的話)
                    if "teacher" in df.columns:
                        df["teacher_name"] = df["teacher"].apply(lambda x: x.get("name", "") if isinstance(x, dict) else str(x))
                    if "course" in df.columns:
                        df["course_name"] = df["course"].apply(lambda x: x.get("name", "") if isinstance(x, dict) else str(x))
                    
                    # 將 teacher_id 和 course_id 轉換為名稱
                    if "teacher_id" in df.columns and "teacher_name" not in df.columns:
                        df["teacher_name"] = df["teacher_id"].map(teacher_dict).fillna("未知教練")
                    if "course_id" in df.columns and "course_name" not in df.columns:
                        df["course_name"] = df["course_id"].map(course_dict).fillna("未知課程")
                    
                    # 移除不需要的欄位
                    cols_to_drop = ['teacher', 'course', 'teacher_id', 'course_id']
                    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
                    
                    # 將欄位名稱改為中文（僅前端顯示,不影響資料庫）
                    column_mapping = {
                        'id': 'ID',
                        'date': '日期',
                        'student_count': '上課人數',
                        'calculated_salary': '計算薪資',
                        'student_name': '學生姓名',
                        'course_name': '課程名稱',
                        'teacher_name': '教練姓名',
                        'points_deducted': '扣點數'
                    }
                    df = df.rename(columns=column_mapping)

                    gb = GridOptionsBuilder.from_dataframe(df)
                    gb.configure_pagination(paginationAutoPageSize=True)
                    gb.configure_default_column(editable=False, groupable=True, wrapText=False, autoHeight=False, resizable=True, minWidth=120)
                    
                    # 為每個欄位設定合適的最小寬度
                    for col in df.columns:
                        if col == 'ID':
                            gb.configure_column(col, minWidth=80, maxWidth=100)
                        elif col in ['課程名稱', '教練姓名']:
                            gb.configure_column(col, minWidth=150)
                        elif col in ['日期']:
                            gb.configure_column(col, minWidth=120)
                        elif col in ['上課人數']:
                            gb.configure_column(col, minWidth=120)
                        elif col in ['計算薪資']:
                            gb.configure_column(col, minWidth=120)
                        else:
                            gb.configure_column(col, minWidth=120)
                    
                    grid_options = gb.build()
                    
                    # 加入可滾動容器的 CSS
                    st.markdown("""
                        <style>
                        .ag-theme-balham {
                            width: 100% !important;
                            overflow-x: auto !important;
                        }
                        .ag-header-cell-text {
                            overflow: visible !important;
                            text-overflow: clip !important;
                            white-space: normal !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    AgGrid(
                        df, 
                        gridOptions=grid_options, 
                        height=400, 
                        theme="balham", 
                        fit_columns_on_grid_load=False,
                        allow_unsafe_jscode=True,
                        key="aggrid_attendance_v2"
                    ) 
                else:
                    st.info("目前尚無上課資料，請先至前台新增紀錄。")
                    
            else:
                data = get_all_sales()
                # MOCK DATA for Sales
                if not data or len(data) == 0:
                    data = [
                        {"id": 1, "student_name": "Alice Wang", "item": "10堂課卡", "amount": 3500, "teacher_name": "櫃檯 - 小花", "date": "2024-01-10"},
                        {"id": 2, "student_name": "Bob Chen", "item": "20堂課卡", "amount": 6000, "teacher_name": "店長 - 大寶", "date": "2024-01-12"},
                        {"id": 3, "student_name": "New Student", "item": "體驗課", "amount": 400, "teacher_name": "櫃檯 - 小花", "date": "2024-01-15"},
                    ]
                    st.info("💡 目前為模擬銷售紀錄。")

                if data and len(data) > 0:
                    df = pd.DataFrame(data)
                    
                    # 取得教練資料用於 ID 轉換
                    teachers = get_teachers()
                    teacher_dict = {t['id']: t['name'] for t in teachers}
                    
                    # 處理 nested object (如果有的話)
                    if "teacher" in df.columns:
                        df["teacher_name"] = df["teacher"].apply(lambda x: x.get("name", "") if isinstance(x, dict) else str(x))
                    
                    # 將 teacher_id 轉換為名稱
                    if "teacher_id" in df.columns and "teacher_name" not in df.columns:
                        df["teacher_name"] = df["teacher_id"].map(teacher_dict).fillna("未知教練")
                    
                    # 移除不需要的欄位
                    cols_to_drop = ['teacher', 'teacher_id']
                    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns], errors='ignore')
                    
                    # 將欄位名稱改為中文（僅前端顯示,不影響資料庫）
                    column_mapping = {
                        'id': 'ID',
                        'date': '日期',
                        'plan_type': '方案類型',
                        'amount': '金額',
                        'student_name': '學生姓名',
                        'item': '項目',
                        'teacher_name': '教練姓名',
                        'payment_method': '付款方式',
                        'custom_amount': '自訂金額',
                        'note': '備注'
                    }
                    df = df.rename(columns=column_mapping)
                    
                    if '提成' in df.columns:
                        df = df.drop(columns=['提成'], errors='ignore')

                    gb = GridOptionsBuilder.from_dataframe(df)
                    gb.configure_pagination(paginationAutoPageSize=True)
                    gb.configure_default_column(editable=False, groupable=True, wrapText=False, autoHeight=False, resizable=True, minWidth=120)
                    
                    # 為每個欄位設定合適的最小寬度
                    for col in df.columns:
                        if col == 'ID':
                            gb.configure_column(col, minWidth=80, maxWidth=100)
                        elif col in ['學生姓名', '教練姓名', '項目', '備注']:
                            gb.configure_column(col, minWidth=150)
                        elif col in ['金額', '自訂金額']:
                            gb.configure_column(col, minWidth=100)
                        elif col in ['日期', '方案類型']:
                            gb.configure_column(col, minWidth=120)
                        else:
                            gb.configure_column(col, minWidth=120)
                    
                    grid_options = gb.build()
                    
                    # 加入可滾動容器的 CSS
                    st.markdown("""
                        <style>
                        .ag-theme-balham {
                            width: 100% !important;
                            overflow-x: auto !important;
                        }
                        .ag-header-cell-text {
                            overflow: visible !important;
                            text-overflow: clip !important;
                            white-space: normal !important;
                        }
                        </style>
                    """, unsafe_allow_html=True)
                    
                    AgGrid(
                        df, 
                        gridOptions=grid_options, 
                        height=400, 
                        theme="balham", 
                        fit_columns_on_grid_load=False,
                        allow_unsafe_jscode=True,
                        key="aggrid_sales_v2"
                    )
                else:
                    st.info("目前尚無賣課資料，請先至前台新增紀錄。")

    # --- Mode 3: 規則設定 ---
    elif dashboard_mode == "規則設定":
        with st.container():
            st.markdown("### ⚙️ 薪資計算規則")
            st.info("修改下方參數並按儲存，將即時更新後端計算邏輯。")
            
            current_rules = get_salary_rules()
            
            # 若讀取失敗或無規則，提供預設值以顯示表單
            if not current_rules:
                current_rules = [
                    {"min": 1, "max": 5, "amount": 500},
                    {"min": 6, "max": 10, "amount": 800},
                ]

            with st.form("rules_form"):
                new_rules = []
                
                for i, rule in enumerate(current_rules):
                    st.markdown(f"**級距 {i+1}**")
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        # 增加 unique key 避免 id 衝突
                        min_val = st.number_input(f"Min (人)", value=int(rule.get('min', 0)), min_value=0, key=f"rule_min_{i}")
                    with c2:
                        max_val = st.number_input(f"Max (人)", value=int(rule.get('max', 0)), min_value=0, key=f"rule_max_{i}")
                    with c3:
                        amt = st.number_input(f"薪資 ($)", value=float(rule.get('amount', 0)), min_value=0.0, key=f"rule_amt_{i}")
                    
                    new_rules.append({"min": min_val, "max": max_val, "amount": amt})
                
                if st.form_submit_button("💾 更新規則"):
                    if update_salary_rules(new_rules):
                        st.success("規則已更新！")
    
    st.markdown("---")


# ==================== 頁面：上課紀錄表單 ====================
def show_class_form():
    """上課紀錄填寫頁面"""
    st.markdown('<div class="page-title">📝 紀錄上課</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">請填寫上課資訊</div>', unsafe_allow_html=True)
    
    # 日期
    record_date = st.date_input(
        "📅 上課日期",
        value=date.today(),
        key="class_date"
    )
    
    # 教練
    teachers = get_teachers()
    teacher_options = {f"{t['name']}": t['id'] for t in teachers}
    teacher_names = ["請選擇教練"] + list(teacher_options.keys()) if teacher_options else ["暫無資料"]
    selected_teacher = custom_select(
        "👤 選擇教練",
        options=teacher_names,
        key="class_teacher",
        default_index=0
    )
    
    # 課程
    courses = get_courses()
    course_options = {f"{c['name']} ({c['course_type']})": c['id'] for c in courses}
    course_names = ["請選擇課程"] + list(course_options.keys()) if course_options else ["暫無資料"]
    selected_course = custom_select(
        "🎵 選擇課程",
        options=course_names,
        key="class_course",
        default_index=0
    )
    
    # 人數（使用自訂組件強制九宮格鍵盤）
    student_count = tel_number_input(
        "👥 上課人數",
        key="class_count",
        min_value=1,
        max_value=100,
        value=1
    )
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 按鈕
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回", key="class_back", use_container_width=True):
            navigate_to("home")
    
    with col2:
        # 驗證必填欄位
        is_valid = (
            selected_teacher != "請選擇教練" and 
            selected_course != "請選擇課程" and 
            student_count > 0
        )
        
        if st.button("下一步 →", key="class_next", use_container_width=True, disabled=not is_valid):
            # 儲存資料到 session
            st.session_state.form_data = {
                "type": "attendance",
                "date": record_date,
                "teacher_name": selected_teacher,
                "teacher_id": teacher_options.get(selected_teacher),
                "course_name": selected_course,
                "course_id": course_options.get(selected_course),
                "student_count": student_count
            }
            navigate_to("confirm")


# ==================== 頁面：賣課紀錄表單 ====================
def show_sales_form():
    """賣課紀錄填寫頁面"""
    st.markdown('<div class="page-title">💰 紀錄收入</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">請選擇方案與金額</div>', unsafe_allow_html=True)
    
    # 日期
    record_date = st.date_input(
        "📅 銷售日期",
        value=date.today(),
        key="sales_date"
    )
    
    # 教練
    teachers = get_teachers()
    teacher_options = {f"{t['name']}": t['id'] for t in teachers}
    teacher_names = ["請選擇教練"] + list(teacher_options.keys()) if teacher_options else ["暫無資料"]
    selected_teacher = custom_select(
        "👤 選擇教練",
        options=teacher_names,
        key="sales_teacher",
        default_index=0
    )
    
    st.markdown("---")
    st.markdown("### 📦 選擇方案")
    
    # 方案 A
    PLAN_A_PRICE = 3000
    st.markdown(f"#### 方案 A - 入門方案 (NT$ {PLAN_A_PRICE:,})")
    plan_a_qty = tel_number_input(
        "數量",
        key="plan_a_qty",
        min_value=0,
        max_value=50,
        value=0
    )
    
    # 方案 B
    PLAN_B_PRICE = 5000
    st.markdown(f"#### 方案 B - 進階方案 (NT$ {PLAN_B_PRICE:,})")
    plan_b_qty = tel_number_input(
        "數量",
        key="plan_b_qty",
        min_value=0,
        max_value=50,
        value=0
    )
    
    # 方案 C
    PLAN_C_PRICE = 8000
    st.markdown(f"#### 方案 C - 專業方案 (NT$ {PLAN_C_PRICE:,})")
    plan_c_qty = tel_number_input(
        "數量",
        key="plan_c_qty",
        min_value=0,
        max_value=50,
        value=0
    )
    
    st.markdown("---")
    
    # 特殊金額
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💵 特殊金額（選填）")
    special_amount = tel_number_input(
        "自訂金額 (NT$)",
        key="special_amount",
        min_value=0,
        max_value=999999,
        value=0
    )
    
    # 備註
    note = st.text_area(
        "📝 備註（選填）",
        placeholder="輸入備註說明...",
        key="sales_note"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 按鈕
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 返回", key="sales_back", use_container_width=True):
            navigate_to("home")
    
    with col2:
        # 驗證：至少要選一個方案或填特殊金額
        can_proceed = (plan_a_qty > 0 or plan_b_qty > 0 or plan_c_qty > 0 or special_amount > 0)
        
        if st.button("下一步 →", key="sales_next", type="primary", use_container_width=True, disabled=not can_proceed):
            # 計算總金額
            total_amount = (plan_a_qty * PLAN_A_PRICE) + (plan_b_qty * PLAN_B_PRICE) + (plan_c_qty * PLAN_C_PRICE) + special_amount
            
            # 儲存資料到 session
            st.session_state.form_data = {
                "type": "sales",
                "date": record_date,
                "teacher_name": selected_teacher,
                "teacher_id": teacher_options.get(selected_teacher),
                "plan_a_qty": plan_a_qty,
                "plan_b_qty": plan_b_qty,
                "plan_c_qty": plan_c_qty,
                "special_amount": special_amount,
                "note": note,
                "total_amount": total_amount
            }
            navigate_to("confirm")


# ==================== 頁面：確認頁面 ====================
def show_confirm_page():
    """確認頁面 - 顯示資料總表"""
    data = st.session_state.get("form_data", {})
    
    st.markdown('<div class="page-title">📊 資料確認</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">請仔細核對以下資訊</div>', unsafe_allow_html=True)
    
    # 根據類型顯示不同內容
    if data.get("type") == "attendance":
        st.markdown(f"""
        <div class="confirm-card">
            <div class="confirm-item">
                <div class="confirm-label">📅 日期</div>
                <div class="confirm-value">{data.get('date')}</div>
            </div>
            <div class="confirm-item">
                <div class="confirm-label">👤 教練</div>
                <div class="confirm-value">{data.get('teacher_name')}</div>
            </div>
            <div class="confirm-item">
                <div class="confirm-label">🎵 課程</div>
                <div class="confirm-value">{data.get('course_name')}</div>
            </div>
            <div class="confirm-item">
                <div class="confirm-label">👥 人數</div>
                <div class="confirm-value">{data.get('student_count')} 人</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    elif data.get("type") == "sales":
        items = []
        if data.get('plan_a_qty', 0) > 0:
            items.append(f"方案 A × {data['plan_a_qty']}")
        if data.get('plan_b_qty', 0) > 0:
            items.append(f"方案 B × {data['plan_b_qty']}")
        if data.get('plan_c_qty', 0) > 0:
            items.append(f"方案 C × {data['plan_c_qty']}")
        if data.get('special_amount', 0) > 0:
            items.append(f"特殊金額 NT$ {data['special_amount']:,.0f}")
        
        items_text = "<br>".join(items)
        
        # 處理備註文字 - 只保留純文字，換行轉為 <br>
        note_raw = data.get('note', '').strip()
        note_display = note_raw.replace('\n', '<br>') if note_raw else ""
        
        # 組合確認卡片HTML - 注意：不要縮排 HTML 字串，以免被當成 code block
        confirm_html = f"""
<div class="confirm-card">
    <div class="confirm-item">
        <div class="confirm-label">📅 日期</div>
        <div class="confirm-value">{data.get('date')}</div>
    </div>
    <div class="confirm-item">
        <div class="confirm-label">👤 教練</div>
        <div class="confirm-value">{data.get('teacher_name')}</div>
    </div>
    <div class="confirm-item">
        <div class="confirm-label">📦 方案內容</div>
        <div class="confirm-value">{items_text}</div>
    </div>
    <div class="confirm-item">
        <div class="confirm-label">💵 總金額</div>
        <div class="confirm-value">NT$ {data.get('total_amount', 0):,.0f}</div>
    </div>"""

        if note_display:
            confirm_html += f"""
    <div class="confirm-item">
        <div class="confirm-label">📝 備註</div>
        <div class="confirm-value">{note_display}</div>
    </div>"""

        confirm_html += """
</div>"""

        st.markdown(confirm_html, unsafe_allow_html=True)
    
    # 電子簽名預留
    st.markdown("### ✍️ 電子簽名")
    st.markdown("""
    <div class="signature-area">
        此區域預留給 Stage 2 電子簽名功能<br>
        敬請期待...
    </div>
    """, unsafe_allow_html=True)
    
    # 確認勾選
    confirmed = st.checkbox("✅ 我已確認資料無誤", key="final_confirm")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 按鈕
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← 重新填寫", key="confirm_back", use_container_width=True):
            st.session_state.form_data = {}
            navigate_to("home")
    
    with col2:
        if st.button("🚀 送出", key="confirm_submit", type="primary", use_container_width=True, disabled=not confirmed):
            # 提交資料
            success = False
            
            if data.get("type") == "attendance":
                api_data = {
                    "date": str(data['date']),
                    "teacher_id": data['teacher_id'],
                    "course_id": data['course_id'],
                    "student_count": data['student_count']
                }
                success = create_attendance(api_data)
            
            elif data.get("type") == "sales":
                # 這裡簡化處理，實際需要根據方案計算金額
                # 暫時使用總金額提交

                # Determine plan type
                plans = []
                if data.get('plan_a_qty', 0) > 0:
                    plans.append("方案A")
                if data.get('plan_b_qty', 0) > 0:
                    plans.append("方案B")
                if data.get('plan_c_qty', 0) > 0:
                    plans.append("方案C")
                if data.get('special_amount', 0) > 0:
                    plans.append("特殊金額")
                
                plan_type_str = " + ".join(plans) if plans else "方案A"

                # Calculate commission (Fixed Amount)
                # 方案A: 100, 方案B: 200, 方案C: 300
                comm_a = data.get('plan_a_qty', 0) * 100
                comm_b = data.get('plan_b_qty', 0) * 200
                comm_c = data.get('plan_c_qty', 0) * 300
                total_commission = comm_a + comm_b + comm_c

                api_data = {
                    "date": str(data['date']),
                    "teacher_id": data['teacher_id'],
                    "plan_type": plan_type_str,
                    "amount": data['total_amount'],
                    "note": data.get('note'),
                    "custom_amount": data.get('special_amount', 0),
                    "commission": total_commission
                }
                success = create_sales(api_data)
            
            if success:
                navigate_to("success")


# ==================== 頁面：成功頁面 ====================
def show_success_page():
    """顯示提交成功頁面"""
    st.markdown("""
    <div class="success-message">
        <div class="success-icon">✅</div>
        <div class="success-text">提交成功！</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.balloons()
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    if st.button("🏠 返回首頁", key="success_home", use_container_width=True):
        st.session_state.form_data = {}
        navigate_to("home")


# ==================== 主應用程式 ====================
def main():
    # 頁面設定
    st.set_page_config(
        page_title="Dance DEX - 教練端",
        page_icon="💃",
        layout="centered",
        initial_sidebar_state="collapsed"
    )
    
    # 套用樣式
    apply_custom_style()
    
    # 從 URL 讀取頁面參數
    query_params = st.query_params
    url_page = query_params.get("page", "home")
    
    # 有效頁面列表
    valid_pages = ["home", "class_form", "sales_form", "confirm", "success", "boss_login", "boss_dashboard"]
    
    # 初始化或同步 session state
    if 'page' not in st.session_state:
        # 首次訪問，使用 URL 參數或預設主頁
        if url_page in valid_pages:
            st.session_state.page = url_page
        else:
            st.session_state.page = "home"
            st.query_params["page"] = "home"
    elif st.session_state.page != url_page:
        # URL 改變（例如瀏覽器返回），同步 session state
        if url_page in valid_pages:
            st.session_state.page = url_page
        else:
            # 無效頁面，重定向到主頁
            st.session_state.page = "home"
            st.query_params["page"] = "home"
    
    # 路由邏輯 - 使用 empty container 強制清除舊內容
    main_container = st.empty()
    with main_container.container():
        if st.session_state.page == "home":
            show_homepage()
        elif st.session_state.page == "class_form":
            show_class_form()
        elif st.session_state.page == "sales_form":
            show_sales_form()
        elif st.session_state.page == "confirm":
            show_confirm_page()
        elif st.session_state.page == "success":
            show_success_page()
        elif st.session_state.page == "boss_login":
            show_boss_login()
        elif st.session_state.page == "boss_dashboard":
            show_boss_dashboard()
        else:
            # 未知頁面，重定向到主頁
            navigate_to("home")

if __name__ == "__main__":
    main()
