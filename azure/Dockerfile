FROM python:3.11-slim

WORKDIR /app

# Copy project files
COPY data/ ./data/
COPY schemas/ ./schemas/
COPY rulebound/ ./rulebound/
COPY run.py ./
COPY azure/ ./azure/

# Standard Python server configuration
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
EXPOSE 8080

CMD ["python", "run.py", "--input", "data", "--output", "OUTPUT"]
