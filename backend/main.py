from fastapi import FastAPI, Request
import pandas as pd
import os
from contextlib import asynccontextmanager
import asyncio
from models import Base
from db import engine
from uploader import upload_all_csv, schedule_daily_upload

@asynccontextmanager
async def lifespan(app: FastAPI):
    APP_ENV = os.getenv("APP_ENV", "development")
    print(f"🚀 Backend starting, ENV = {APP_ENV}")
    # Startup
    # 初始化数据库
    for i in range(10):  # 最多尝试 10 次，每次间隔 1 秒
        try:
            async with engine.begin() as conn:
                print("====Connected to DB, creating tables...====")
                await conn.run_sync(Base.metadata.create_all)
                print("✅ Database initialized.")
                break
        except Exception as e:
            print(f"⚠️ DB not ready yet (attempt {i+1}/10). Error: {e}")
            await asyncio.sleep(1)
    else:
        print("❌ Failed to connect to DB after 10 attempts")
        raise

    if APP_ENV == "production":
        # 1. 容器启动后立即上传一次
        print("Running immediate upload (production mode)...")
        asyncio.create_task(upload_all_csv())

        # 2. 同时启动定时调度任务
        print("Starting daily upload scheduler...")
        asyncio.create_task(schedule_daily_upload(0, 0))

    else:
        # 开发模式下，不自动上传
        print("Development mode: uploader auto-run disabled.")

    yield

    # Shutdown
    await engine.dispose()
    print("🛑 Database engine disposed.")

app = FastAPI(title="Airi Backend", lifespan=lifespan)

DATABASE_URL = os.getenv('APP_DATABASE_URL')
DATABASE_ASYNC_URL = os.getenv('APP_DATABASE_ASYNC_URL')

@app.get("/")
def root():
    return {"message": "Airi Backend is running!"}

# @app.post("/api/upload_activity")
# async def upload_activity(request: Request):
#     data = await request.json()
#     df = pd.DataFrame(data)

#     df.to_sql("activity_logs", con=engine, if_exists="append", index=False)
#     return {"status": "ok", "records_saved": len(df)}