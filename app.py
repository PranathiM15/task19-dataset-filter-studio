from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import pandas as pd
import io, os, json
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "task19-local-demo-secret")
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"csv"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES

# In-memory demo datasets so the app works immediately without downloading anything.
def demo_data(kind):
    if kind == "students":
        return pd.DataFrame([
            {"Student":"Aarav","Department":"AI & ML","Score":91,"Attendance":96,"Hours_Studied":8,"Passed":True},
            {"Student":"Diya","Department":"Computer Science","Score":84,"Attendance":89,"Hours_Studied":6,"Passed":True},
            {"Student":"Kabir","Department":"AI & ML","Score":67,"Attendance":76,"Hours_Studied":4,"Passed":True},
            {"Student":"Meera","Department":"Electronics","Score":58,"Attendance":82,"Hours_Studied":3,"Passed":False},
            {"Student":"Ishaan","Department":"Computer Science","Score":73,"Attendance":91,"Hours_Studied":5,"Passed":True},
            {"Student":"Ananya","Department":"AI & ML","Score":96,"Attendance":98,"Hours_Studied":9,"Passed":True},
            {"Student":"Rohan","Department":"Electronics","Score":42,"Attendance":61,"Hours_Studied":2,"Passed":False},
            {"Student":"Sana","Department":"Computer Science","Score":79,"Attendance":85,"Hours_Studied":5,"Passed":True},
            {"Student":"Vihaan","Department":"AI & ML","Score":61,"Attendance":72,"Hours_Studied":3,"Passed":False},
            {"Student":"Tara","Department":"Electronics","Score":88,"Attendance":94,"Hours_Studied":7,"Passed":True},
        ])
    return pd.DataFrame([
        {"PassengerId":101,"Name":"Alex Morgan","Class":1,"Age":29,"Fare":72.50,"Sex":"female","Survived":1},
        {"PassengerId":102,"Name":"Sam Carter","Class":3,"Age":22,"Fare":7.25,"Sex":"male","Survived":0},
        {"PassengerId":103,"Name":"Jamie Lee","Class":2,"Age":35,"Fare":18.00,"Sex":"female","Survived":1},
        {"PassengerId":104,"Name":"Taylor Reed","Class":3,"Age":8,"Fare":12.40,"Sex":"male","Survived":1},
        {"PassengerId":105,"Name":"Jordan Blake","Class":1,"Age":54,"Fare":80.00,"Sex":"male","Survived":0},
        {"PassengerId":106,"Name":"Riley Quinn","Class":2,"Age":17,"Fare":16.00,"Sex":"female","Survived":1},
        {"PassengerId":107,"Name":"Casey Park","Class":3,"Age":41,"Fare":9.80,"Sex":"female","Survived":0},
        {"PassengerId":108,"Name":"Morgan Ellis","Class":1,"Age":31,"Fare":64.20,"Sex":"female","Survived":1},
        {"PassengerId":109,"Name":"Drew Hayes","Class":3,"Age":27,"Fare":8.05,"Sex":"male","Survived":0},
        {"PassengerId":110,"Name":"Avery Stone","Class":2,"Age":12,"Fare":20.00,"Sex":"male","Survived":1},
    ])

def get_df():
    kind = session.get("dataset_kind", "students")
    if kind in ("students", "titanic"):
        return demo_data(kind), kind.title() + " demo dataset"
    path = session.get("uploaded_path")
    if path and os.path.exists(path):
        try:
            return pd.read_csv(path), session.get("uploaded_name", "Uploaded dataset")
        except Exception:
            pass
    return demo_data("students"), "Students demo dataset"

def scalar(value, series):
    if pd.api.types.is_numeric_dtype(series):
        try: return float(value)
        except (ValueError, TypeError): return value
    if str(value).lower() in ("true", "false"):
        return str(value).lower() == "true"
    return str(value)

def apply_rule(df, rule):
    col, op, raw = rule.get("column"), rule.get("operator"), rule.get("value", "")
    if col not in df.columns:
        return pd.Series(False, index=df.index)
    s = df[col]
    val = scalar(raw, s)
    try:
        if op == "equals": return s.astype(str).str.lower() == str(raw).lower()
        if op == "not_equals": return s.astype(str).str.lower() != str(raw).lower()
        if op == "contains": return s.astype(str).str.contains(str(raw), case=False, na=False, regex=False)
        if op == "not_contains": return ~s.astype(str).str.contains(str(raw), case=False, na=False, regex=False)
        if op == "greater": return pd.to_numeric(s, errors="coerce") > float(raw)
        if op == "greater_equal": return pd.to_numeric(s, errors="coerce") >= float(raw)
        if op == "less": return pd.to_numeric(s, errors="coerce") < float(raw)
        if op == "less_equal": return pd.to_numeric(s, errors="coerce") <= float(raw)
        if op == "is_empty": return s.isna() | (s.astype(str).str.strip() == "")
        if op == "is_not_empty": return ~(s.isna() | (s.astype(str).str.strip() == ""))
    except (ValueError, TypeError):
        return pd.Series(False, index=df.index)
    return pd.Series(False, index=df.index)

def filter_frame(df, rules, joiner):
    if not rules:
        return df.copy()
    masks = [apply_rule(df, r) for r in rules]
    result = masks[0]
    for mask in masks[1:]:
        result = (result & mask) if joiner == "AND" else (result | mask)
    return df[result].copy()

def table_data(df, limit=100):
    clean = df.head(limit).copy()
    clean = clean.astype(object).where(pd.notna(clean), "")
    return clean.to_dict(orient="records"), list(clean.columns)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "dataset":
            kind = request.form.get("dataset_kind", "students")
            if kind in ("students", "titanic"):
                session["dataset_kind"] = kind
                session.pop("uploaded_path", None)
                session.pop("uploaded_name", None)
            flash("Dataset switched successfully.", "success")
            return redirect(url_for("index"))
        if action == "upload":
            file = request.files.get("dataset_file")
            if not file or not file.filename:
                flash("Choose a CSV file first.", "error")
                return redirect(url_for("index"))
            if not file.filename.lower().endswith(".csv"):
                flash("Only CSV files are supported for this task.", "error")
                return redirect(url_for("index"))
            name = secure_filename(file.filename)
            path = os.path.join(UPLOAD_FOLDER, name)
            try:
                file.save(path)
                test = pd.read_csv(path, nrows=5)
                if len(test.columns) == 0:
                    raise ValueError("No columns found")
                session["uploaded_path"] = path
                session["uploaded_name"] = name
                session["dataset_kind"] = "uploaded"
                flash(f"{name} loaded successfully.", "success")
            except Exception as exc:
                flash("Could not read this CSV. Check the file format and try again.", "error")
                if os.path.exists(path): os.remove(path)
            return redirect(url_for("index"))
        if action == "reset":
            session.pop("rules", None)
            session.pop("joiner", None)
            flash("Filters cleared.", "success")
            return redirect(url_for("index"))
        if action == "filter":
            rules = []
            cols = get_df()[0].columns.tolist()
            for i in range(5):
                col = request.form.get(f"column_{i}")
                op = request.form.get(f"operator_{i}")
                value = request.form.get(f"value_{i}", "")
                if col and op and (value.strip() or op in ("is_empty", "is_not_empty")):
                    if col in cols:
                        rules.append({"column": col, "operator": op, "value": value.strip()})
            session["rules"] = rules
            session["joiner"] = request.form.get("joiner", "AND")
            return redirect(url_for("index"))

    df, label = get_df()
    rules = session.get("rules", [])
    joiner = session.get("joiner", "AND")
    filtered = filter_frame(df, rules, joiner)
    records, columns = table_data(filtered)
    original_records, original_columns = table_data(df)
    numeric = df.select_dtypes(include="number").columns.tolist()
    return render_template("index.html", dataset_label=label, rows=len(df), filtered_rows=len(filtered),
        columns=df.columns.tolist(), records=records, table_columns=columns, rules=rules, joiner=joiner,
        numeric_columns=numeric, original_columns=original_columns, original_records=original_records,
        preview_limit=100, truncated=len(filtered)>100)

@app.route("/download")
def download():
    df, _ = get_df()
    filtered = filter_frame(df, session.get("rules", []), session.get("joiner", "AND"))
    buffer = io.BytesIO()
    filtered.to_csv(buffer, index=False)
    buffer.seek(0)
    return send_file(buffer, mimetype="text/csv", as_attachment=True, download_name="filtered_records.csv")

@app.errorhandler(413)
def too_large(_):
    flash("Upload limit is 10 MB. Please choose a smaller CSV file.", "error")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
