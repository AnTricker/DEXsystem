from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from . import models, schemas
from .salary_rules import calculate_salary, calculate_commission


# ========== Teacher CRUD ==========
def create_teacher(db: Session, teacher: schemas.TeacherCreate) -> models.Teacher:
    """建立新教練"""
    db_teacher = models.Teacher(name=teacher.name)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher


def get_teacher(db: Session, teacher_id: int) -> Optional[models.Teacher]:
    """取得單一教練"""
    return db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()


def get_teachers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Teacher]:
    """取得教練列表"""
    return db.query(models.Teacher).offset(skip).limit(limit).all()


def update_teacher(db: Session, teacher_id: int, teacher: schemas.TeacherCreate) -> Optional[models.Teacher]:
    """更新教練資料"""
    db_teacher = get_teacher(db, teacher_id)
    if db_teacher:
        db_teacher.name = teacher.name
        db.commit()
        db.refresh(db_teacher)
    return db_teacher


def delete_teacher(db: Session, teacher_id: int) -> bool:
    """刪除教練"""
    db_teacher = get_teacher(db, teacher_id)
    if db_teacher:
        db.delete(db_teacher)
        db.commit()
        return True
    return False


# ========== Course CRUD ==========
def create_course(db: Session, course: schemas.CourseCreate) -> models.Course:
    """建立新課程"""
    db_course = models.Course(name=course.name, course_type=course.course_type)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def get_course(db: Session, course_id: int) -> Optional[models.Course]:
    """取得單一課程"""
    return db.query(models.Course).filter(models.Course.id == course_id).first()


def get_courses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Course]:
    """取得課程列表"""
    return db.query(models.Course).offset(skip).limit(limit).all()


def update_course(db: Session, course_id: int, course: schemas.CourseCreate) -> Optional[models.Course]:
    """更新課程資料"""
    db_course = get_course(db, course_id)
    if db_course:
        db_course.name = course.name
        db_course.course_type = course.course_type
        db.commit()
        db.refresh(db_course)
    return db_course


def delete_course(db: Session, course_id: int) -> bool:
    """刪除課程"""
    db_course = get_course(db, course_id)
    if db_course:
        db.delete(db_course)
        db.commit()
        return True
    return False


# ========== Attendance CRUD ==========
def create_attendance(db: Session, attendance: schemas.AttendanceCreate) -> models.Attendance:
    """建立上課紀錄（自動計算薪資）"""
    # 自動計算薪資
    calculated_salary = calculate_salary(attendance.student_count)
    
    db_attendance = models.Attendance(
        date=attendance.date,
        teacher_id=attendance.teacher_id,
        course_id=attendance.course_id,
        student_count=attendance.student_count,
        calculated_salary=calculated_salary
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


def get_attendance(db: Session, attendance_id: int) -> Optional[models.Attendance]:
    """取得單一上課紀錄"""
    return db.query(models.Attendance).filter(models.Attendance.id == attendance_id).first()


def get_attendances(db: Session, skip: int = 0, limit: int = 100) -> List[models.Attendance]:
    """取得上課紀錄列表"""
    return db.query(models.Attendance).offset(skip).limit(limit).all()


def get_attendances_by_teacher(db: Session, teacher_id: int) -> List[models.Attendance]:
    """取得特定教練的上課紀錄"""
    return db.query(models.Attendance).filter(models.Attendance.teacher_id == teacher_id).all()


def get_attendances_by_date_range(db: Session, start_date: date, end_date: date) -> List[models.Attendance]:
    """取得特定日期範圍的上課紀錄"""
    return db.query(models.Attendance).filter(
        models.Attendance.date >= start_date,
        models.Attendance.date <= end_date
    ).all()


def delete_attendance(db: Session, attendance_id: int) -> bool:
    """刪除上課紀錄"""
    db_attendance = get_attendance(db, attendance_id)
    if db_attendance:
        db.delete(db_attendance)
        db.commit()
        return True
    return False


# ========== Sales CRUD ==========
def create_sales(db: Session, sales: schemas.SalesCreate) -> models.Sales:
    """建立賣課紀錄（自動計算提成）"""
    # 自動計算提成 (如果前端有傳 commission 則使用，否則嘗試計算)
    commission = sales.commission if sales.commission is not None and sales.commission > 0 else calculate_commission(sales.plan_type, sales.amount)
    
    db_sales = models.Sales(
        date=sales.date,
        teacher_id=sales.teacher_id,
        plan_type=sales.plan_type,
        amount=sales.amount,
        commission=commission,
        note=sales.note,
        custom_amount=sales.custom_amount
    )
    db.add(db_sales)
    db.commit()
    db.refresh(db_sales)
    return db_sales


def get_sales(db: Session, sales_id: int) -> Optional[models.Sales]:
    """取得單一賣課紀錄"""
    return db.query(models.Sales).filter(models.Sales.id == sales_id).first()


def get_all_sales(db: Session, skip: int = 0, limit: int = 100) -> List[models.Sales]:
    """取得賣課紀錄列表"""
    return db.query(models.Sales).offset(skip).limit(limit).all()


def get_sales_by_teacher(db: Session, teacher_id: int) -> List[models.Sales]:
    """取得特定教練的賣課紀錄"""
    return db.query(models.Sales).filter(models.Sales.teacher_id == teacher_id).all()


def get_sales_by_date_range(db: Session, start_date: date, end_date: date) -> List[models.Sales]:
    """取得特定日期範圍的賣課紀錄"""
    return db.query(models.Sales).filter(
        models.Sales.date >= start_date,
        models.Sales.date <= end_date
    ).all()


def delete_sales(db: Session, sales_id: int) -> bool:
    """刪除賣課紀錄"""
    db_sales = get_sales(db, sales_id)
    if db_sales:
        db.delete(db_sales)
        db.commit()
        return True
    return False


# ========== Monthly Salary Rule CRUD ==========
def get_monthly_salary_rule(db: Session, year: int, month: int) -> Optional[models.MonthlySalaryRule]:
    """取得特定月份的薪資規則快照"""
    return db.query(models.MonthlySalaryRule).filter(
        models.MonthlySalaryRule.year == year,
        models.MonthlySalaryRule.month == month
    ).first()


def upsert_monthly_salary_rule(db: Session, year: int, month: int, rules_data: List[dict]):
    """新增或更新特定月份的薪資規則快照"""
    import json
    rules_json = json.dumps(rules_data, ensure_ascii=False)
    
    db_rule = get_monthly_salary_rule(db, year, month)
    if db_rule:
        db_rule.rules_json = rules_json
    else:
        db_rule = models.MonthlySalaryRule(year=year, month=month, rules_json=rules_json)
        db.add(db_rule)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule
