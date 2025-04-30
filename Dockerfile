##################################################
# Create production image
##################################################
FROM python:3.11-slim

# Set up the Python production environment
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN python -m pip install --upgrade pip pipenv && \
    pipenv install --system --deploy

# Install Firefox & Geckodriver
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        firefox-esr \
        ca-certificates \
        gnupg \
        libdbus-glib-1-2 \
        libgtk-3-0 \
        libx11-xcb1 \
        libxt6 \
        libxcomposite1 \
        libxdamage1 \
        libxrandr2 \
        libasound2 \
        libnss3 \
        libxss1 \
        libatk1.0-0 \
        libatk-bridge2.0-0 \
        libcups2 \
        libdrm2 \
        libgbm1 \
        libxshmfence1 \
        xdg-utils \
        unzip && \
    wget -q https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-linux64.tar.gz && \
    tar -xzf geckodriver-linux64.tar.gz -C /usr/local/bin && \
    chmod +x /usr/local/bin/geckodriver && \
    rm geckodriver-linux64.tar.gz && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the application contents
COPY wsgi.py .
COPY service/ ./service/

# Switch to a non-root user and set file ownership
RUN useradd --uid 1001 flask && \
    chown -R flask /app
USER flask

# Expose any ports the app is expecting in the environment
ENV FLASK_APP="wsgi:app"
ENV PORT=8080
EXPOSE $PORT

ENV GUNICORN_BIND=0.0.0.0:$PORT
ENTRYPOINT ["gunicorn"]
CMD ["--log-level=info", "wsgi:app"]