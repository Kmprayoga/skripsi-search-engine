from flask import Flask
from app.routes import routes

def create_app():
    app = Flask(__name__)

    # tambahkan prefix /api
    app.register_blueprint(routes, url_prefix="/api")

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
