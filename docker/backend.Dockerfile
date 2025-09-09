FROM python:3.12.10-slim
WORKDIR /app

# ติดตั้ง system dependencies สำหรับ ML packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ติดตั้ง Python dependencies ในระบบ
COPY apps/backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# สร้าง directory สำหรับ data files
RUN mkdir -p /app/data

# คัดลอกโค้ด (ใน dev mode จะใช้ volume mount ทับ)
COPY apps/backend/ .

# คัดลอก data files
COPY apps/backend/data/ ./data/

# ตั้งค่า environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV GROQ_API_KEY=${GROQ_API_KEY}

# สร้าง non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
