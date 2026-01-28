from pydantic import BaseModel, Field
from datetime import date as Date
from typing import Optional


# ========== Teacher Schemas ==========
class TeacherBase(BaseModel):
    name: str = Field(..., description="教練姓名")


class TeacherCreate(TeacherBase):
    pass


class Teacher(TeacherBase):
    id: int
    
    class Config:
        from_attributes = True


# ========== Course Schemas ==========
class CourseBase(BaseModel):
    name: str = Field(..., description="課程名稱")
    course_type: str = Field(..., description="課程類型：常態 或 額外")


class CourseCreate(CourseBase):
    pass


class Course(CourseBase):
    id: int
    
    class Config:
        from_attributes = True


# ========== Attendance Schemas ==========
class AttendanceBase(BaseModel):
    date: Date = Field(..., description="上課日期")
    teacher_id: int = Field(..., description="教練 ID")
    course_id: int = Field(..., description="課程 ID")
    student_count: int = Field(..., ge=0, description="上課人數")


class AttendanceCreate(AttendanceBase):
    pass


class Attendance(AttendanceBase):
    id: int
    calculated_salary: float = Field(..., description="計算後的薪資")
    
    class Config:
        from_attributes = True


# ========== Sales Schemas ==========
class SalesBase(BaseModel):
    date: Date = Field(..., description="銷售日期")
    teacher_id: int = Field(..., description="教練 ID")
    plan_type: str = Field(..., description="方案類型：方案A 或 方案B")
    amount: float = Field(..., ge=0, description="銷售金額")
    note: Optional[str] = Field(None, description="備註")
    custom_amount: Optional[float] = Field(0, description="自訂金額")
    commission: Optional[float] = Field(0, description="教練提成")


class SalesCreate(SalesBase):
    pass


class Sales(SalesBase):
    id: int
    commission: float = Field(..., description="教練提成")
    
    
    class Config:
        from_attributes = True


# ========== Admin Schemas ==========
class SalaryTier(BaseModel):
    min: int = Field(..., ge=0, description="最小人數")
    max: int = Field(..., ge=0, description="最大人數")
    amount: float = Field(..., ge=0, description="薪資金額")


class SalaryRulesUpdate(BaseModel):
    tiers: list[SalaryTier] = Field(..., description="薪資級距列表")


class MonthlyStats(BaseModel):
    year: int
    month: int
    total_revenue: float
    total_expenses: float
    net_income: float
