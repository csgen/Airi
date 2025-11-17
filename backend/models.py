from sqlalchemy import (
    Column, Integer, String, Text, Float, Date, TIMESTAMP, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import UniqueConstraint

Base = declarative_base()


# --------------------------------------------------------
# 1.原始日志表：raw_activity_logs
# --------------------------------------------------------
class RawActivityLog(Base):
    __tablename__ = "raw_activity_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # 事件发生时本地时间（带时区）
    local_timestamp = Column(TIMESTAMP(timezone=True), nullable=False)

    # UTC 时间（统一用于排序/分析）
    timestamp_utc = Column(TIMESTAMP(timezone=True), nullable=False)

    # 当时的本地时区（时区偏移，例如 "+08:00" 或 "-05:00"）
    timezone_name = Column(String(50), nullable=False)

    duration_seconds = Column(Integer, nullable=False)
    application = Column(Text, nullable=False)
    activity_type = Column(String(50), nullable=False)
    input_count = Column(Integer, nullable=False)

    imported_at = Column(TIMESTAMP(timezone=True))

    __table_args__ = (
        UniqueConstraint("local_timestamp", "application", "duration_seconds",
                         name="uq_raw_log_unique_record"),
    )


# --------------------------------------------------------
# 2.处理后的分类表：processed_activity
# --------------------------------------------------------
class ProcessedActivity(Base):
    __tablename__ = "processed_activity"

    id = Column(Integer, primary_key=True, autoincrement=True)

    raw_id = Column(Integer, ForeignKey("raw_activity_logs.id"))
    raw_log = relationship("RawActivityLog")

    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    duration_seconds = Column(Integer, nullable=False)

    application = Column(Text)
    category = Column(String(50))          # 工作/学习/娱乐/休息
    sub_category = Column(String(100))      # Chrome:Wikipedia / VSCode 等

    input_count = Column(Integer)
    focus_score = Column(Float)

    processed_at = Column(TIMESTAMP(timezone=True))


# --------------------------------------------------------
# 3.每日汇总表：daily_summary
# --------------------------------------------------------
class DailySummary(Base):
    __tablename__ = "daily_summary"

    date = Column(Date, primary_key=True)

    work_seconds = Column(Integer, default=0)
    study_seconds = Column(Integer, default=0)
    entertainment_seconds = Column(Integer, default=0)
    rest_seconds = Column(Integer, default=0)
    communication_seconds = Column(Integer, default=0)

    total_input_count = Column(Integer, default=0)
    average_focus_score = Column(Float)

    created_at = Column(TIMESTAMP(timezone=True))
