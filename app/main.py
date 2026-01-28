from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from datetime import date
from sqlalchemy import func, extract
from . import salary_rules

from .database import engine, get_db, Base
from . import crud, schemas, models

# 建立資料表
Base.metadata.create_all(bind=engine)

# 建立 FastAPI 應用
app = FastAPI(
    title="DEXsystem API",
    description="數位化管理系統 - 薪資計算與課程管理",
    version="1.0.0"
)


# ========== Teacher API ==========
@app.post("/teachers/", response_model=schemas.Teacher, tags=["Teachers"])
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    """建立新教練"""
    return crud.create_teacher(db=db, teacher=teacher)


@app.get("/teachers/", response_model=List[schemas.Teacher], tags=["Teachers"])
def read_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """取得教練列表"""
    return crud.get_teachers(db, skip=skip, limit=limit)


@app.get("/teachers/{teacher_id}", response_model=schemas.Teacher, tags=["Teachers"])
def read_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """取得單一教練"""
    db_teacher = crud.get_teacher(db, teacher_id=teacher_id)
    if db_teacher is None:
        raise HTTPException(status_code=404, detail="教練不存在")
    return db_teacher


@app.put("/teachers/{teacher_id}", response_model=schemas.Teacher, tags=["Teachers"])
def update_teacher(teacher_id: int, teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    """更新教練資料"""
    db_teacher = crud.update_teacher(db, teacher_id=teacher_id, teacher=teacher)
    if db_teacher is None:
        raise HTTPException(status_code=404, detail="教練不存在")
    return db_teacher


@app.delete("/teachers/{teacher_id}", tags=["Teachers"])
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """刪除教練"""
    success = crud.delete_teacher(db, teacher_id=teacher_id)
    if not success:
        raise HTTPException(status_code=404, detail="教練不存在")
    return {"message": "刪除成功"}


# ========== Course API ==========
@app.post("/courses/", response_model=schemas.Course, tags=["Courses"])
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    """建立新課程"""
    return crud.create_course(db=db, course=course)


@app.get("/courses/", response_model=List[schemas.Course], tags=["Courses"])
def read_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """取得課程列表"""
    return crud.get_courses(db, skip=skip, limit=limit)


@app.get("/courses/{course_id}", response_model=schemas.Course, tags=["Courses"])
def read_course(course_id: int, db: Session = Depends(get_db)):
    """取得單一課程"""
    db_course = crud.get_course(db, course_id=course_id)
    if db_course is None:
        raise HTTPException(status_code=404, detail="課程不存在")
    return db_course


@app.put("/courses/{course_id}", response_model=schemas.Course, tags=["Courses"])
def update_course(course_id: int, course: schemas.CourseCreate, db: Session = Depends(get_db)):
    """更新課程資料"""
    db_course = crud.update_course(db, course_id=course_id, course=course)
    if db_course is None:
        raise HTTPException(status_code=404, detail="課程不存在")
    return db_course


@app.delete("/courses/{course_id}", tags=["Courses"])
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """刪除課程"""
    success = crud.delete_course(db, course_id=course_id)
    if not success:
        raise HTTPException(status_code=404, detail="課程不存在")
    return {"message": "刪除成功"}


# ========== Attendance API ==========
@app.post("/attendances/", response_model=schemas.Attendance, tags=["Attendances"])
def create_attendance(attendance: schemas.AttendanceCreate, db: Session = Depends(get_db)):
    """建立上課紀錄（自動計算薪資）"""
    return crud.create_attendance(db=db, attendance=attendance)


@app.get("/attendances/", response_model=List[schemas.Attendance], tags=["Attendances"])
def read_attendances(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """取得上課紀錄列表"""
    return crud.get_attendances(db, skip=skip, limit=limit)


@app.get("/attendances/{attendance_id}", response_model=schemas.Attendance, tags=["Attendances"])
def read_attendance(attendance_id: int, db: Session = Depends(get_db)):
    """取得單一上課紀錄"""
    db_attendance = crud.get_attendance(db, attendance_id=attendance_id)
    if db_attendance is None:
        raise HTTPException(status_code=404, detail="上課紀錄不存在")
    return db_attendance


@app.get("/attendances/teacher/{teacher_id}", response_model=List[schemas.Attendance], tags=["Attendances"])
def read_attendances_by_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """取得特定教練的所有上課紀錄"""
    return crud.get_attendances_by_teacher(db, teacher_id=teacher_id)


@app.get("/attendances/date-range/", response_model=List[schemas.Attendance], tags=["Attendances"])
def read_attendances_by_date_range(
    start_date: date = Query(..., description="起始日期"),
    end_date: date = Query(..., description="結束日期"),
    db: Session = Depends(get_db)
):
    """取得特定日期範圍的上課紀錄"""
    return crud.get_attendances_by_date_range(db, start_date=start_date, end_date=end_date)


@app.delete("/attendances/{attendance_id}", tags=["Attendances"])
def delete_attendance(attendance_id: int, db: Session = Depends(get_db)):
    """刪除上課紀錄"""
    success = crud.delete_attendance(db, attendance_id=attendance_id)
    if not success:
        raise HTTPException(status_code=404, detail="上課紀錄不存在")
    return {"message": "刪除成功"}


# ========== Sales API ==========
@app.post("/sales/", response_model=schemas.Sales, tags=["Sales"])
def create_sales(sales: schemas.SalesCreate, db: Session = Depends(get_db)):
    """建立賣課紀錄（自動計算提成）"""
    return crud.create_sales(db=db, sales=sales)


@app.get("/sales/", response_model=List[schemas.Sales], tags=["Sales"])
def read_all_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """取得賣課紀錄列表"""
    return crud.get_all_sales(db, skip=skip, limit=limit)


@app.get("/sales/{sales_id}", response_model=schemas.Sales, tags=["Sales"])
def read_sales(sales_id: int, db: Session = Depends(get_db)):
    """取得單一賣課紀錄"""
    db_sales = crud.get_sales(db, sales_id=sales_id)
    if db_sales is None:
        raise HTTPException(status_code=404, detail="賣課紀錄不存在")
    return db_sales


@app.get("/sales/teacher/{teacher_id}", response_model=List[schemas.Sales], tags=["Sales"])
def read_sales_by_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """取得特定教練的所有賣課紀錄"""
    return crud.get_sales_by_teacher(db, teacher_id=teacher_id)


@app.get("/sales/date-range/", response_model=List[schemas.Sales], tags=["Sales"])
def read_sales_by_date_range(
    start_date: date = Query(..., description="起始日期"),
    end_date: date = Query(..., description="結束日期"),
    db: Session = Depends(get_db)
):
    """取得特定日期範圍的賣課紀錄"""
    return crud.get_sales_by_date_range(db, start_date=start_date, end_date=end_date)


@app.delete("/sales/{sales_id}", tags=["Sales"])
def delete_sales(sales_id: int, db: Session = Depends(get_db)):
    """刪除賣課紀錄"""
    success = crud.delete_sales(db, sales_id=sales_id)
    if not success:
        raise HTTPException(status_code=404, detail="賣課紀錄不存在")
    return {"message": "刪除成功"}





# ========== Admin API ==========
@app.get("/admin/rules", response_model=List[schemas.SalaryTier], tags=["Admin"])
def get_salary_rules(db: Session = Depends(get_db)):
    """取得目前薪資門檻規則 (並確保當月規則快照存在)"""
    current_rules = salary_rules.load_rules()
    
    # Side Effect: 檢查當月是否已有規則快照，若無則存檔
    today = date.today()
    if not crud.get_monthly_salary_rule(db, today.year, today.month):
        crud.upsert_monthly_salary_rule(db, today.year, today.month, current_rules)
        
    return current_rules


@app.get("/admin/rules/history", tags=["Admin"])
def get_historical_rules(
    year: int = Query(..., description="年份"),
    month: int = Query(..., description="月份"),
    db: Session = Depends(get_db)
):
    """取得特定月份的薪資規則 (若該月無紀錄，則回傳目前規則)"""
    db_rule = crud.get_monthly_salary_rule(db, year, month)
    if db_rule:
        import json
        return json.loads(db_rule.rules_json)
    
    # Fallback: 若無歷史紀錄，回傳目前規則 (或你要回傳空列表/錯誤)
    # 這裡依照需求：若調用前月資料時，用儲存的那份 rule... 若沒存到，這也是個 fallback
    return salary_rules.load_rules()


@app.post("/admin/rules", tags=["Admin"])
def update_salary_rules(rules: schemas.SalaryRulesUpdate, db: Session = Depends(get_db)):
    """更新薪資門檻規則 (同步更新當月快照)"""
    # 轉換為 dict list 儲存
    tiers_data = [tier.dict() for tier in rules.tiers]
    salary_rules.save_rules(tiers_data)
    
    # Side Effect: 更新當月規則快照
    today = date.today()
    crud.upsert_monthly_salary_rule(db, today.year, today.month, tiers_data)
    
    return {"message": "規則更新成功"}


@app.get("/admin/stats", response_model=schemas.MonthlyStats, tags=["Admin"])
def get_monthly_stats(
    year: int = date.today().year, 
    month: int = date.today().month, 
    db: Session = Depends(get_db)
):
    """取得月度統計（總收入 vs 總支出）"""
    # 計算總收入 (Sales.amount)
    total_revenue = db.query(func.sum(models.Sales.amount)).filter(
        extract('year', models.Sales.date) == year,
        extract('month', models.Sales.date) == month
    ).scalar() or 0.0
    
    # 計算總支出 (Attendance.calculated_salary + Sales.commission)
    salary_expense = db.query(func.sum(models.Attendance.calculated_salary)).filter(
        extract('year', models.Attendance.date) == year,
        extract('month', models.Attendance.date) == month
    ).scalar() or 0.0
    
    commission_expense = db.query(func.sum(models.Sales.commission)).filter(
        extract('year', models.Sales.date) == year,
        extract('month', models.Sales.date) == month
    ).scalar() or 0.0
    
    total_expenses = salary_expense + commission_expense
    
    return {
        "year": year,
        "month": month,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_income": total_revenue - total_expenses
    }
