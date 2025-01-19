FROM python:3.11-slim

WORKDIR /app

# Copy application files
COPY ./api ./api
COPY requirements.txt .
COPY query_gpt.py .
COPY .env .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Add PYTHONPATH to include /app
ENV PYTHONPATH=/app

# Run the application
CMD ["python", "query_gpt.py"]
