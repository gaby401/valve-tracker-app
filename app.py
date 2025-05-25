from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

specimens = []
tests = []
results = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/specimens")
def specimen_list():
    return render_template("specimens.html", specimens=specimens)

@app.route("/specimens/add", methods=["GET", "POST"])
def specimen_add():
    if request.method == "POST":
        specimen = {
            "id": len(specimens) + 1,
            "name": request.form["name"],
            "type": request.form["type"],
            "status": "Received"
        }
        specimens.append(specimen)
        return redirect(url_for("specimen_list"))
    return render_template("specimen_add.html")

@app.route("/results/upload/<int:specimen_id>", methods=["POST"])
def upload_result(specimen_id):
    file = request.files["result_file"]
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)
    results.append({"specimen_id": specimen_id, "file": filename})
    return redirect(url_for("specimen_list"))

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)