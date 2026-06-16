from flask import Flask
from flask_cors import CORS
from config import APP_NAME, FLASK_ENV
from routes.auth import auth_bp
from routes.cilindro import cilindro_bp
from routes.elemento import elemento_bp
from routes.leitura import leitura_bp

app = Flask(__name__)
CORS(app)

app.config["APP_NAME"] = APP_NAME
app.config["ENV"] = FLASK_ENV

app.register_blueprint(auth_bp)
app.register_blueprint(cilindro_bp)
app.register_blueprint(elemento_bp)
app.register_blueprint(leitura_bp)


@app.route("/")
def index():
    return {"message": f"{APP_NAME} API", "status": "running"}


@app.route("/health")
def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
