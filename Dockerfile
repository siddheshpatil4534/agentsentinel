FROM python:3.11-slim

# Hugging Face Spaces convention: run as non-root UID 1000
RUN useradd -m -u 1000 user

WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY --chown=user . .

USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1

EXPOSE 7860

CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "7860"]
