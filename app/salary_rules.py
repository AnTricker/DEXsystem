"""
薪資計算規則模組
========================
此模組包含所有薪資與提成計算邏輯
支援動態修改與持久化儲存 (JSON)
"""
import json
import os
from typing import List, Dict

RULES_FILE = "salary_rules.json"

# 預設規則
DEFAULT_TIERS = [
    {"min": 1, "max": 5, "amount": 500},    # 1-5 人：$500
    {"min": 6, "max": 10, "amount": 800},   # 6-10 人：$800
    {"min": 11, "max": 15, "amount": 1200}, # 11-15 人：$1200
    {"min": 16, "max": 99999, "amount": 1500}, # 16 人以上：$1500
]

# 固定提成金額（每個）
COMMISSION_RATES = {
    "方案A": 100,  # 固定 $100
    "方案B": 200,  # 固定 $200
    "方案C": 300,  # 固定 $300
}


def load_rules() -> List[Dict]:
    """讀取薪資規則 (如有 JSON 則讀取，否則回傳預設值)"""
    if os.path.exists(RULES_FILE):
        try:
            with open(RULES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return DEFAULT_TIERS
    return DEFAULT_TIERS


def save_rules(tiers: List[Dict]):
    """儲存薪資規則到 JSON"""
    with open(RULES_FILE, "w", encoding="utf-8") as f:
        json.dump(tiers, f, indent=2, ensure_ascii=False)


def calculate_salary(student_count: int) -> float:
    """
    根據上課人數計算薪資
    """
    if student_count < 1:
        raise ValueError("上課人數必須至少為 1 人")
    
    tiers = load_rules()
    
    for tier in tiers:
        if tier["min"] <= student_count <= tier["max"]:
            return float(tier["amount"])
    
    # 預設：如果沒有匹配的規則，返回最高級別薪資 (或最後一個規則)
    if tiers:
        return float(tiers[-1]["amount"])
    return 0.0


def calculate_commission(plan_type: str, amount: float) -> float:
    """根據方案類型與金額計算提成"""
    if plan_type not in COMMISSION_RATES:
        # 如果方案不在字典中，或者你可以選擇拋出錯誤，這裡做一個兼容
        # 暫時為了簡單，未知的方案回傳 0 或拋出錯誤
        # raise ValueError(f"未知的方案類型: {plan_type}")
        return 0.0
    
    rate = COMMISSION_RATES[plan_type]
    return amount * rate
