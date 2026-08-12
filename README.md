# 🚢 VibeTitanic

A small, end-to-end data science project that explores the [Kaggle Titanic dataset](https://www.kaggle.com/c/titanic) and predicts which passengers survived the sinking of the RMS Titanic.

Built as a learning exercise for **Claude Code** and "vibe coding" — see the [roadmap.sh Titanic EDA project](https://roadmap.sh/projects/titanic-eda-python) for the original challenge.

---

## 🎯 Goal

Train a model on the labeled training set (`train.csv`, 891 passengers) and predict survival for the unlabeled test set (`test.csv`, 418 passengers).

The final deliverable is a CSV with two columns:

| Column        | Description                          |
| ------------- | ------------------------------------ |
| `PassengerId` | ID of the passenger in the test set  |
| `Survived`    | `0` = did not survive, `1` = survived |

The output file matches the schema of the Kaggle `gender_submission.csv` sample.

---

## 🧰 Tech Stack

- **Language:** Python 3.10+
- **Data Analysis:** pandas, numpy
- **Visualization:** matplotlib, seaborn
- **Machine Learning:** xgboost
- **Interactive:** Jupyter notebooks

---

## 📁 Project Structure

```
VibeTitanic/
├── notebooks/          # EDA + modeling notebooks (one per stage)
│   └── .gitkeep
├── src/                # Reusable Python modules / helper scripts
│   └── .gitkeep
├── outputs/            # Generated figures and the final submission.csv
│   └── .gitkeep
├── data/               # Local data cache (raw CSVs live in csvs/, gitignored)
│   └── .gitkeep
├── csvs/               # Raw Kaggle CSVs — gitignored
│   ├── train.csv
│   ├── test.csv
│   └── gender_submission.csv
├── .gitignore
├── CLAUDE.md           # Project context & instructions for Claude
└── README.md
```

---

## ⚙️ Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/crx-21/VibeTitanic.git
   cd VibeTitanic
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # macOS / Linux
   source .venv/bin/activate
   ```

3. **Install dependencies** (once `requirements.txt` is added)
   ```bash
   pip install -r requirements.txt
   ```

4. **Drop the Kaggle CSVs** into `csvs/` (already gitignored):
   - `train.csv`
   - `test.csv`
   - `gender_submission.csv`

---

## 🚀 Usage

Open the project as a Jupyter notebook:

```bash
jupyter notebook notebooks/
```

Run the notebooks in order — they walk through EDA, feature engineering, model training, and the final prediction written to `outputs/submission.csv`.

---

## 📤 Output

After the prediction step runs, you should see:

```
outputs/
├── figures/            # Saved plots from the EDA
└── submission.csv      # Final predictions — ready for Kaggle upload
```

A correctly-formatted `submission.csv` has 418 data rows plus a header:

```csv
PassengerId,Survived
892,0
893,1
...
```

---

## 📚 References

- [roadmap.sh — Titanic EDA (Python)](https://roadmap.sh/projects/titanic-eda-python)
- [Kaggle — Titanic: Machine Learning from Disaster](https://www.kaggle.com/c/titanic)

---

## 📝 License

This is a personal learning project. The underlying Titanic dataset is © its respective owners on Kaggle.
