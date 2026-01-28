"""
初始化測試資料
建立範例教練與課程
"""
import requests

API_BASE_URL = "http://127.0.0.1:8000"

# 建立教練
teachers = [
    {"name": "教練A"},
    {"name": "教練B"},
    {"name": "教練C"}
]

print("建立教練資料...")
for teacher in teachers:
    try:
        response = requests.post(f"{API_BASE_URL}/teachers/", json=teacher)
        if response.status_code == 200:
            print(f"✅ 已建立: {teacher['name']}")
        else:
            print(f"⚠️ {teacher['name']} 可能已存在")
    except Exception as e:
        print(f"❌ 建立 {teacher['name']} 失敗: {e}")

# 建立課程
courses = [
    {"name": "HipHop", "course_type": "常態"},
    {"name": "Breaking", "course_type": "常態"},
    {"name": "Popping", "course_type": "常態"},
    {"name": "Locking", "course_type": "常態"},
    {"name": "House", "course_type": "常態"},
    {"name": "Waacking", "course_type": "額外"},
    {"name": "Urban", "course_type": "額外"}
]

print("\n建立課程資料...")
for course in courses:
    try:
        response = requests.post(f"{API_BASE_URL}/courses/", json=course)
        if response.status_code == 200:
            print(f"✅ 已建立: {course['name']} ({course['course_type']})")
        else:
            print(f"⚠️ {course['name']} 可能已存在")
    except Exception as e:
        print(f"❌ 建立 {course['name']} 失敗: {e}")

print("\n✨ 初始化完成！")
