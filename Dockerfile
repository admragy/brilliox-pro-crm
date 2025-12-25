FROM python:3.10-slim

WORKDIR /app

# تثبيت التبعيات
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ الكود
COPY . .

# إنشاء المجلدات
RUN mkdir -p data uploads static/css static/js static/images

# تشغيل التطبيق
EXPOSE 5000
CMD ["python", "main.py"]
