# Base image with Python 3.12 on Windows Server Core
# Note: Windows Containers are required for pywin32 and local printer access.
FROM python:3.12-windowsservercore-ltsc2022

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=utf-8 \
    PORTA_API=5000 \
    API_KEY=minha_chave_segura_123

# Install uv (modern python package manager)
ADD https://astral.sh/uv/install.ps1 install.ps1
RUN powershell -ExecutionPolicy Bypass -File install.ps1; \
    Remove-Item install.ps1

# Copy project configuration
COPY pyproject.toml .

# Install dependencies via pip (simplest for a single image layer)
# pywin32 is critical and needs to be installed in the system python
RUN pip install fastapi[standard] pywin32 python-dotenv jinja2 uvicorn

# Copy application code and templates
COPY main.py .
COPY templates/ ./templates/

# Expose the API port
EXPOSE 5000

# Start the Gateway
CMD ["python", "main.py"]
