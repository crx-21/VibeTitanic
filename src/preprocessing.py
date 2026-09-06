import pandas as pd
import numpy as np
import re

class PreprocessingPipeline:
    """
    Preprocessing pipeline for the Titanic dataset to prepare data for a machine learning model.
    Handles imputation, feature engineering, and encoding.
    """
    def __init__(self):
        self.age_medians = {}
        self.embarked_mode = None
        self.columns_after_encoding = None
        self.title_mapping = {
            'Mr': 'Mr', 'Mrs': 'Mrs', 'Miss': 'Miss', 'Master': 'Master',
            'Dr': 'Rare', 'Rev': 'Rare', 'Col': 'Rare', 'Major': 'Rare',
            ' Capt': 'Rare', 'Countess': 'Rare', 'Viscount': 'Rare',
            'Viscountess': 'Rare', 'Sir': 'Rare', 'Lady': 'Rare',
            'Jonkheer': 'Rare', 'Don': 'Rare', 'Baron': 'Baron', 'Baroness': 'Baroness'
        }

    def fit(self, df):
        """
        Learn imputation values and encoding schemas from the training set.
        """
        df_copy = df.copy()

        # 1. Title Extraction for Age Imputation
        # Extract title using regex from 'Name' column
        titles = df_copy['Name'].str.extract(r', ([A-Za-z]+)\.', expand=False)
        df_copy['Title'] = titles

        # Group rare titles
        df_copy['Title'] = df_copy['Title'].map(self.title_mapping).fillna('Rare')

        # 2. Calculate median age per title
        self.age_medians = df_copy.groupby('Title')['Age'].median().to_dict()

        # 3. Calculate mode for Embarked
        if not df_copy['Embarked'].mode().empty:
            self.embarked_mode = df_copy['Embarked'].mode()[0]

        return self

    def transform(self, df):
        """
        Apply the learned transformations to the dataset.
        """
        df = df.copy()

        # 1. Title Extraction
        titles = df['Name'].str.extract(r', ([A-Za-z]+)\.', expand=False)
        df['Title'] = titles.map(self.title_mapping).fillna('Rare')

        # 2. Age Imputation
        # Fill missing Age values using the medians learned during fit()
        df['Age'] = df['Age'].fillna(df['Title'].map(self.age_medians))
        # Fallback for any titles not seen during fit
        df['Age'] = df['Age'].fillna(df['Age'].median() if not np.isnan(df['Age'].median()) else 28)

        # 3. Family Dynamics
        df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
        df['IsAlone'] = (df['FamilySize'] == 1).astype(int)

        # 4. Cabin Transformation
        df['HasCabin'] = df['Cabin'].notna().astype(int)
        df['Deck'] = df['Cabin'].str[0].fillna('U') # 'U' for Unknown

        # 5. Embarked Imputation
        df['Embarked'] = df['Embarked'].fillna(self.embarked_mode)

        # 6. Encoding
        # We use pd.get_dummies for One-Hot Encoding
        categorical_cols = ['Sex', 'Embarked', 'Title', 'Deck']
        df = pd.get_dummies(df, columns=categorical_cols)

        # Drop non-predictive or redundant columns
        cols_to_drop = ['Name', 'Ticket', 'Cabin']
        df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

        # Handle PassengerId: move it to a separate variable or keep it
        # based on whether we are training or predicting.
        # For now, we keep it but the modeling part will split it.

        # Ensure consistent columns between train and test
        if self.columns_after_encoding is not None:
            # Add missing columns with 0
            for col in self.columns_after_encoding:
                if col not in df.columns:
                    df[col] = 0
            # Remove extra columns
            df = df[self.columns_after_encoding]
        else:
            # This will be set during fit_transform for the training set
            pass

        return df

    def fit_transform(self, df):
        """
        Fit the pipeline and then transform the data.
        """
        self.fit(df)
        transformed_df = self.transform(df)

        # Store the columns after encoding to ensure consistency in transform()
        # We remove PassengerId and Survived from the feature set but keep them in the DF
        # for tracking. However, the 'columns_after_encoding' should represent the
        # features we expect.

        # Let's define what the final features should be.
        # Since we are in fit_transform (usually on train), we take whatever we got.
        self.columns_after_encoding = transformed_df.columns.tolist()

        return transformed_df
