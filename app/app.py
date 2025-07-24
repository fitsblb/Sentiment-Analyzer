from flask import Flask, render_template, request
from model import predict  # <- new import

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        user_input = request.form["text_input"]
        label, score = predict(user_input)
        return render_template("result.html", input_text=user_input, prediction=label, confidence=score)
    return render_template("home.html")

if __name__ == "__main__":
    app.run(debug=True)
