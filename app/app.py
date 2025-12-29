from flask import Flask
from flask_cors import CORS
from app.routes import routes

def create_app():
    app = Flask(__name__)

    # 🔥 CORS KONFIGURASI LENGKAP (NGROK SAFE)
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"]
    )

    app.register_blueprint(routes, url_prefix="/api")
    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=6000, debug=True)
