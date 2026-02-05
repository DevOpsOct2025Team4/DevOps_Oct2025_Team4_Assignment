import os

from dotenv import load_dotenv
from flask import Flask, request
from flask_cors import CORS
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CollectorRegistry, REGISTRY
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from routes import api_bp


# Define Prometheus metrics
request_count = Counter(
    'flask_http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'flask_http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'flask_http_requests_active',
    'Active HTTP requests'
)


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)

    # Enable CORS for frontend
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    max_upload_mb = os.getenv("MAX_UPLOAD_MB")
    if max_upload_mb:
        try:
            app.config["MAX_CONTENT_LENGTH"] = int(max_upload_mb) * 1024 * 1024
        except ValueError:
            app.logger.warning("Invalid MAX_UPLOAD_MB=%s", max_upload_mb)

    app.register_blueprint(api_bp, url_prefix="/api")

    # Add Prometheus metrics middleware
    @app.before_request
    def before_request():
        active_requests.inc()

    @app.after_request
    def after_request(response):
        active_requests.dec()
        
        # Track metrics
        request_count.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown',
            status=response.status_code
        ).inc()
        
        # Track duration (simplified - using request context)
        return response

    # Add metrics endpoint
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {
        '/metrics': make_wsgi_app()
    })

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    host = os.getenv("HOST", "127.0.0.1")
    app.run(host=host, port=port)
