import pandas as pd
import os
from datetime import datetime
import pytz

# 处理旧的csv中没有带时区信息的时间戳字段
DATA_DIR = "C:\csg_Folder\MyProject\Airi\data"  # csv 文件夹
LOCAL_TZ = pytz.timezone("Asia/Singapore")  # SG

# 把 tz-naive 的字符串转换为 tz-aware（SG时间）
def fix_timestamp(ts_str):
    # 解析没有时区的时间
    naive_dt = datetime.fromisoformat(ts_str)

    # 补上 SG 时区
    aware_dt = LOCAL_TZ.localize(naive_dt)

    return aware_dt.isoformat()  # 返回带时区的 ISO8601 字符串

def process_file(path):
    print(f"📄 Fixing {path}")
    df = pd.read_csv(path)

    # 修复 timestamp 列
    df["timestamp"] = df["timestamp"].apply(fix_timestamp)

    # 保存
    df.to_csv(path, index=False)
    print(f"✅ Saved fixed file: {path}")

def fix_all_csv():
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".csv"):
            process_file(os.path.join(DATA_DIR, filename))

if __name__ == "__main__":
    fix_all_csv()
