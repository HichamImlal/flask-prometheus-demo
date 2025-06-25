# Stage 1: Builder
FROM python:3.9-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.9-slim
WORKDIR /app

# Copy dependencies
COPY --from=builder /root/.local /root/.local
COPY . .

# Set PATH
ENV PATH=/root/.local/bin:$PATH

# Correct EXPOSE syntax (no quotes, no comments on same line)
EXPOSE 5000
EXPOSE 8000

# Non-root user
RUN useradd -m flaskuser && \
    chown -R flaskuser:flaskuser /app
USER flaskuser

CMD ["python", "app.py"]