import json
from pathlib import Path

def create_cell(cell_type, source):
    cell = {
        "cell_type": cell_type,
        "metadata": {},
    }
    if cell_type == "code":
        cell["execution_count"] = None
        cell["outputs"] = []

    if isinstance(source, str):
        cell["source"] = [line + "\n" for line in source.split("\n")]
    else:
        cell["source"] = source
    return cell

# We combine everything into one giant code cell to prevent NameErrors
# from running cells out of order.
giant_code_block = (
    "import pandas as pd\n"
    "import numpy as np\n"
    "import matplotlib.pyplot as plt\n"
    "import seaborn as sns\n"
    "from pathlib import Path\n"
    "import sys\n"
    "sys.path.append('.')\n"
    "from src.data_loader import load_train, load_test\n\n"
    "# 1. Setup\n"
    "print('--- Setting up environment ---')\n"
    "Path('outputs/figures').mkdir(parents=True, exist_ok=True)\n"
    "sns.set_theme(style='whitegrid')\n\n"
    "# 2. Data Loading\n"
    "print('Loading data...')\n"
    "train_df = load_train()\n"
    "test_df = load_test()\n"
    "print(f'Train shape: {train_df.shape}, Test shape: {test_df.shape}')\n\n"
    "# 3. Profiling\n"
    "print('Profiling data...')\n"
    "print(train_df.info())\n"
    "print(train_df.describe(include='all'))\n"
    "print(train_df.isnull().sum())\n\n"
    "# 4. Visualizations\n"
    "print('Generating plots...')\n"
    "plt.figure(figsize=(6, 4))\n"
    "sns.countplot(data=train_df, x='Survived', hue='Survived', palette='viridis', legend=False)\n"
    "plt.title('Distribution of Survival')\n"
    "plt.savefig('outputs/figures/survival_distribution.png')\n"
    "plt.show()\n\n"
    "plt.figure(figsize=(8, 5))\n"
    "sns.histplot(train_df['Age'].dropna(), kde=True, color='blue')\n"
    "plt.title('Age Distribution')\n"
    "plt.savefig('outputs/figures/age_distribution.png')\n"
    "plt.show()\n\n"
    "plt.figure(figsize=(6, 4))\n"
    "sns.barplot(data=train_df, x='Sex', y='Survived', hue='Sex', palette='viridis', legend=False)\n"
    "plt.title('Survival Rate by Sex')\n"
    "plt.savefig('outputs/figures/survival_by_sex.png')\n"
    "plt.show()\n\n"
    "plt.figure(figsize=(6, 4))\n"
    "sns.barplot(data=train_df, x='Pclass', y='Survived', hue='Pclass', palette='viridis', legend=False)\n"
    "plt.title('Survival Rate by Pclass')\n"
    "plt.savefig('outputs/figures/survival_by_pclass.png')\n"
    "plt.show()\n\n"
    "plt.figure(figsize=(8, 5))\n"
    "sns.kdeplot(data=train_df[train_df['Survived'] == 0], x='Age', label='Not Survived', fill=True)\n"
    "sns.kdeplot(data=train_df[train_df['Survived'] == 1], x='Age', label='Survived', fill=True)\n"
    "plt.title('Age Distribution by Survival')\n"
    "plt.legend()\n"
    "plt.savefig('outputs/figures/age_survival_distribution.png')\n"
    "plt.show()\n\n"
    "plt.figure(figsize=(10, 8))\n"
    "numeric_df = train_df.select_dtypes(include=[np.number])\n"
    "sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')\n"
    "plt.title('Correlation Heatmap')\n"
    "plt.savefig('outputs/figures/correlation_heatmap.png')\n"
    "plt.show()\n\n"
    "print('--- EDA Complete! All figures saved to outputs/figures/ ---')"
)

cells = [
    create_cell("markdown", "# Milestone 1: Exploratory Data Analysis (EDA)\n\nThis notebook has been consolidated into a single cell to prevent NameErrors. Just run the cell below."),
    create_cell("code", giant_code_block),
    create_cell("markdown", "## Key Findings\n- Fill these in after running the analysis!")
]

notebook = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python",
            "version": "3.10.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

with open('notebooks/01_eda.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1)

print('Consolidated notebook created.')
