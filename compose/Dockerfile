FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Copy application code
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Expose the port FastAPI runs on
EXPOSE 8000

# Run the application with hot reload
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]