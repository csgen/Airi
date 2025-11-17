from sqlalchemy.exc import IntegrityError, OperationalError
import asyncio
import os
import pandas as pd
import re
from datetime import datetime, timedelta
from db import AsyncSessionLocal
from models import RawActivityLog

DATA_DIR = "/app/data"

# 把 timedelta 转成 +08:00 这样可读的偏移字符串
def format_offset(offset):
    total_seconds = int(offset.total_seconds())
    sign = "+" if total_seconds >= 0 else "-"
    total_seconds = abs(total_seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{sign}{hours:02d}:{minutes:02d}"

async def upload_record(row, max_retries=3):
    '''
    上传一条记录：
    - 数据重复 → 忽略
    - 数据库连接失败 → 最多重试 max_retries 次
    - 超过重试次数 → 返回 False（让下次定时任务再尝试）
    '''

    attempt = 0

    # 本地 timestamp(tz-aware)
    local_ts = row["timestamp"]
    # 转为UTC
    timestamp_utc = local_ts.tz_convert("UTC")
    # 提取时区偏移，如 +08:00
    timezone_name = format_offset(local_ts.utcoffset())

    while attempt < max_retries:
        try:
            async with AsyncSessionLocal() as session:
                log = RawActivityLog(
                    local_timestamp=local_ts,
                    timestamp_utc=timestamp_utc,
                    timezone_name=timezone_name,
                    duration_seconds=row["duration_seconds"],
                    application=row["application"],
                    activity_type=row["activity_type"],
                    input_count=row["input_count"],
                )

                session.add(log)
                await session.commit()

                print(f"✅ Uploaded: {local_ts.isoformat()}")
                return True

        except IntegrityError:
            # 已存在，跳过
            print(f"⚠️ Duplicate skipped: {local_ts.isoformat()}")
            return True  # 也算成功，不需要下次再上传

        except OperationalError as e:
            # 数据库没开 / 网络错误
            attempt += 1
            print(
                f"❌ DB connection failed（尝试 {attempt}/{max_retries}）：{e}\n"
                f"⏳ Retrying in 10 seconds..."
            )
            await asyncio.sleep(10)

    # 三次失败 → 放弃本次，等下次定时任务再尝试
    print(f"❗ Upload failed after {max_retries} retries. Will try again next scheduled upload.")
    return False

async def upload_csv_file(csv_path):
    '''
    上传一个 CSV 文件中的所有记录
    - 失败不会中断
    - 已存在记录不会插入
    '''
    print(f"Uploading file: {csv_path}")

    df = pd.read_csv(csv_path, parse_dates=["timestamp"])

    for _, row in df.iterrows():
        await upload_record(row)

    print(f"File completed: {csv_path}")

# 从文件名中提取 YYYY-MM-DD 日期并转换为 datetime 对象
def extract_date(filename):
    match = re.search(r"(\d{4}-\d{2}-\d{2})", filename)
    if match:
        return datetime.strptime(match.group(1), "%Y-%m-%d")
    return datetime.min  # 确保无日期的文件排在最前或忽略

# 扫描 data/ 下的全部 csv，并按日期排序上传
async def upload_all_csv():
    files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]

    if not files:
        print("⚠️ No CSV files found.")
        return
    
    # 按日期排序（基于 YYYY-MM-DD）
    files.sort(key=extract_date)

    for f in files:
        path = os.path.join(DATA_DIR, f)
        await upload_csv_file(path)

    print("All files uploaded!")

async def schedule_daily_upload(hour=0, minute=0):
    while True:
        now = datetime.now()
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if target <= now:
            target += timedelta(days=1)

        wait_sec = (target - now).total_seconds()
        print(f"⏳ Next upload at {target}")

        await asyncio.sleep(wait_sec)
        await upload_all_csv()