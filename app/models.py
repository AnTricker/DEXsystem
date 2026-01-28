from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


class Teacher(Base):
    """教練資料表"""
    __tablename__ = "teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    
    # 關聯
    attendances = relationship("Attendance", back_populates="teacher")
    sales = relationship("Sales", back_populates="teacher")


class Course(Base):
    """課程資料表"""
    __tablename__ = "courses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    course_type = Column(String, nullable=False)  # "常態" 或 "額外"
    
    # 關聯
    attendances = relationship("Attendance", back_populates="course")


class Attendance(Base):
    """上課紀錄表"""
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    student_count = Column(Integer, nullable=False)  # 上課人數
    calculated_salary = Column(Float, nullable=False)  # 計算後的薪資
    
    # 關聯
    teacher = relationship("Teacher", back_populates="attendances")
    course = relationship("Course", back_populates="attendances")


class Sales(Base):
    """賣課紀錄表"""
    __tablename__ = "sales"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    plan_type = Column(String, nullable=False)  # "方案A" 或 "方案B"
    amount = Column(Float, nullable=False)  # 銷售金額
    commission = Column(Float, nullable=False)  # 教練提成
    note = Column(String, nullable=True)  # 備註
    custom_amount = Column(Float, default=0)  # 自訂金額
    
    # 關聯
    teacher = relationship("Teacher", back_populates="sales")


class MonthlySalaryRule(Base):
    """月度薪資規則快照"""
    __tablename__ = "monthly_salary_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    rules_json = Column(String, nullable=False)  # JSON string of tiers
    
    # 複合唯一鍵 (確保每個月只有一份規則)
    # Note: SQLite 不支援 UniqueConstraint 直接寫在 class level 比較麻煩，這裡我們用 code 邏輯控制或者 index
    # 為了簡單，我們可以在 crud 層控制 upsert 邏輯，或者加上 Index
    
    __table_args__ = (
        # Index("ix_year_month", "year", "month", unique=True), # 需要 import Index
    )
