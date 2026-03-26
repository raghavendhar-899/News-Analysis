import logging

from app import create_app

# Reduce noisy HTTP client logs (httpx/urllib3) — set to WARNING so INFO requests are not printed.
# If you later need httpx request logs for debugging, raise this back to logging.INFO.
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)