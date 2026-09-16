from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/")
def home():
    return jsonify(
        message="API Python hébergée sur Amazon EC2",
        status="OK"
    )


@app.get("/health")
def health():
    return jsonify(status="healthy")


@app.get("/hello/<name>")
def hello(name):
    return jsonify(message=f"Bonjour {name} depuis l'API Python sur EC2")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
