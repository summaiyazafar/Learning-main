from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/input")
def input_page():
    return render_template("input.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form['username']
    return f"Hello, {name}!"

if __name__ == "__main__":
    app.run(debug=True)