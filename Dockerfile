FROM python:3.11-slim

# Install system dependencies including git
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    xvfb \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files first
COPY pyproject.toml .
COPY requirements.txt .
COPY src/ ./src/
COPY run_server.py .
COPY main_codes/ ./main_codes/

# Install Python dependencies and the project itself
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -e .

# Create sessions directory
RUN mkdir -p sessions

# Set environment variables
ENV PYTHONPATH=/app
ENV DISPLAY=:99

# Run the MCP server
CMD ["python", "run_server.py"] 