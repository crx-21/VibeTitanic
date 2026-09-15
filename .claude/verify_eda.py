import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from src.data_loader import load_train, load_test

# Setup
Path('outputs/figures').mkdir(parents=True, exist_ok=True)
sns.set_theme(style='whitegrid')

def run_eda():
    print("Loading data...")
    train_df = load_train()
    test_df = load_test()

    print("Target Analysis...")
    plt.figure(figsize=(6, 4))
    sns.countplot(data=train_df, x='Survived', palette='viridis')
    plt.title('Distribution of Survival')
    plt.savefig('outputs/figures/survival_distribution.png')
    plt.close()

    print("Univariate Analysis...")
    plt.figure(figsize=(8, 5))
    sns.histplot(train_df['Age'].dropna(), kde=True, color='blue')
    plt.title('Age Distribution')
    plt.savefig('outputs/figures/age_distribution.png')
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.histplot(train_df['Fare'], kde=True, color='green')
    plt.title('Fare Distribution')
    plt.savefig('outputs/figures/fare_distribution.png')
    plt.close()

    print("Bivariate Analysis...")
    plt.figure(figsize=(6, 4))
    sns.barplot(data=train_df, x='Sex', y='Survived', palette='viridis')
    plt.title('Survival Rate by Sex')
    plt.savefig('outputs/figures/survival_by_sex.png')
    plt.close()

    plt.figure(figsize=(6, 4))
    sns.barplot(data=train_df, x='Pclass', y='Survived', palette='viridis')
    plt.title('Survival Rate by Pclass')
    plt.savefig('outputs/figures/survival_by_pclass.png')
    plt.close()

    plt.figure(figsize=(8, 5))
    sns.kdeplot(data=train_df[train_df['Survived'] == 0], x='Age', label='Not Survived', fill=True)
    sns.kdeplot(data=train_df[train_df['Survived'] == 1], x='Age', label='Survived', fill=True)
    plt.title('Age Distribution by Survival')
    plt.legend()
    plt.savefig('outputs/figures/age_survival_distribution.png')
    plt.close()

    print("Multivariate Analysis...")
    plt.figure(figsize=(8, 5))
    sns.barplot(data=train_df, x='Pclass', y='Survived', hue='Sex', palette='viridis')
    plt.title('Survival Rate by Pclass and Sex')
    plt.savefig('outputs/figures/survival_by_pclass_sex.png')
    plt.close()

    plt.figure(figsize=(10, 8))
    numeric_df = train_df.select_dtypes(include=[np.number])
    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Correlation Heatmap')
    plt.savefig('outputs/figures/correlation_heatmap.png')
    plt.close()

    print("EDA Verification complete. Figures saved to outputs/figures/")

if __name__ == "__main__":
    run_eda()
