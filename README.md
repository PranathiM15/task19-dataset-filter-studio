# FilterLab — Task 19: Filter Dataset Records

A small, polished web app for filtering CSV datasets with Python and Pandas. Built to complete the Veda Technology Task 19 brief without Jupyter Notebook.

## Features
- Two instant demo datasets: Student Performance and Titanic-style passenger data.
- Upload your own CSV (up to 10 MB).
- Up to five conditions with AND / OR logic.
- Numeric comparisons, equals / not-equals, text contains, and empty-value checks.
- Live result counts, a responsive table preview, and CSV export.
- All filtering uses Pandas Boolean masks.

## Requirements
- Python 3.10 or newer
- Terminal / Command Prompt
- Internet is only needed once to install dependencies.

## Run locally

### Windows
```powershell
cd task19_dataset_filter_studio
py -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

### macOS / Linux
```bash
cd task19_dataset_filter_studio
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser. Keep the terminal running while you use the app. Press `Ctrl+C` in the terminal to stop it.

## Quick demo
1. Open the site; Student Performance is loaded by default.
2. Click **Score ≥ 75** or choose columns/operators/values manually.
3. Add a second rule and use AND or OR to combine conditions.
4. Try the Titanic sample or upload a CSV.
5. Select **Export CSV** to save the filtered rows.

## Pandas examples (the task deliverable)
```python
# 1. One condition
high_scores = df[df["Score"] >= 75]

# 2. Two conditions combined with AND (parentheses are important)
high_attendance = df[(df["Score"] >= 75) & (df["Attendance"] >= 85)]

# 3. Multiple conditions combined with OR
strong_or_attending = df[(df["Score"] >= 90) | (df["Attendance"] >= 95)]
```
Pandas returns a filtered DataFrame containing only rows where the Boolean condition is true. Parentheses ensure each comparison is evaluated before `&` or `|`.

## Troubleshooting
- **`python` not found:** install Python 3.10+ and enable “Add Python to PATH” on Windows. Try `py app.py` if `python app.py` does not work.
- **`pip` not found:** run `python -m pip install -r requirements.txt`.
- **Activation blocked in PowerShell:** use Command Prompt and run `.venv\\Scripts\\activate.bat`, or continue without activating and run `.venv\\Scripts\\python.exe -m pip install -r requirements.txt` followed by `.venv\\Scripts\\python.exe app.py`.
- **Port 5000 busy:** change `port=5000` at the bottom of `app.py` to `port=5001`, then open `http://127.0.0.1:5001`.
- **Upload error:** save the file as a standard UTF-8 CSV and ensure it is under 10 MB.
- **GitHub push rejected:** use the exact sequence in the task guide; if the repo was initialized with a README online, use `git pull --rebase origin main` before pushing.

## Project structure
```text
task19_dataset_filter_studio/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
└── uploads/
    └── .gitkeep
```

## GitHub
Create a new empty repository at https://github.com/new. Suggested name: `task19-dataset-filter-studio`. Do not initialize it with a README, .gitignore, or license because those files are already in this project.
