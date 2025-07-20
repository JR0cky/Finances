# 📊 Simple Bookkeeping App

This is a lightweight bookkeeping and finance tracking application built with [Streamlit](https://streamlit.io/). It provides a simple interface to log, view, and evaluate financial data — ideal for personal use, student projects, or small business prototypes.

---

## ✅ Features

- 💰 Track financial entries using a local CSV or SQLite database
- 📋 View transactions and summaries in a clean UI
- 📈 Visualize your data (e.g., charts, totals, categories)
- 🧾 Export records as CSV
- ⚡ Quick to launch, no login or setup required

---

## 🚀 How to Run

💡 Alternatively, you can simply double-click the `run_app.bat` file (on Windows) to automatically create the virtual environment, install requirements, and launch the app.


1. **Clone the repository**

```bash
git clone https://github.com/JR0cky/Finances.git
cd Finances
```

2. **Create a virtual environment**

```bash
python -m venv venv
```

3. **Activate the virtual environment**

- On **Windows**:
  ```bash
  venv\Scripts\activate
  ```

- On **macOS/Linux**:
  ```bash
  source venv/bin/activate
  ```

4. **Install the dependencies**

```bash
pip install -r requirements.txt
```

5. **Start the app**

```bash
streamlit run main.py
```

---

## 📁 File Overview

```plaintext
Finances/
├── main.py             # Streamlit app
├── db.py               # handles the database
├── db.py               # handles the database
├── requirements.txt    # Python dependencies
├── icon.ico            # Custom icon (optional)
├── README.md           # You're here!
├── pages/              # Streamlit sub-pages for modular app layout
    └── charts.py       # handles charts
    └── dashboard.py    # Dashboard with main overview of finances
    └── fixed.py        # handles fixed costs
    └── fonds.py        # handles fonds/shares
    └── ui.py           # handles input and appearance of the app
    └── vary.py         # handles variable costs
```

---

## 📝 Notes

- No user accounts or session state are used.
- All data is stored and read locally.
- Suitable for personal finance tracking, small team demos, or quick prototypes.

---

## 📬 Contact

Questions or suggestions?  
**Your Name** – your.email@example.com
