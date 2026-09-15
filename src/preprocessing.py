import pandas as pd
import numpy as np

class PreprocessingPipeline:
    """
    Preprocessing pipeline for the Titanic dataset.
    Handles imputation, feature engineering, and encoding while maintaining
    strict separation between metadata (PassengerId, Survived) and ML features.
    """
    def __init__(self):
        self.age_medians = {}
        self.overall_age_median = 28
        self.fare_median = None
        self.embarked_mode = None
        self.ticket_counts = {}
        self.feature_columns = None
        self.title_mapping = {
            'Mr': 'Mr', 'Mrs': 'Mrs', 'Miss': 'Miss', 'Master': 'Master',
            'Mlle': 'Miss', 'Ms': 'Miss', 'Mme': 'Mrs',
            'Dr': 'Rare', 'Rev': 'Rare', 'Col': 'Rare', 'Major': 'Rare',
            'Capt': 'Rare', 'Countess': 'Rare', 'Viscount': 'Rare',
            'Viscountess': 'Rare', 'Sir': 'Rare', 'Lady': 'Rare',
            'Jonkheer': 'Rare', 'Don': 'Rare', 'Dona': 'Rare'
        }

    def fit(self, df):
        """Learn imputation statistics and ticket counts from training data."""
        df_copy = df.copy()

        # 1. Title Extraction & Age Medians
        titles = df_copy['Name'].str.extract(r', ([A-Za-z]+)\.', expand=False)
        df_copy['Title'] = titles.map(self.title_mapping).fillna('Rare')

        self.age_medians = df_copy.groupby('Title')['Age'].median().to_dict()
        self.overall_age_median = df_copy['Age'].median() if not np.isnan(df_copy['Age'].median()) else 28
        self.fare_median = df_copy['Fare'].median()

        if not df_copy['Embarked'].mode().empty:
            self.embarked_mode = df_copy['Embarked'].mode()[0]

        # 2. Ticket Frequency
        self.ticket_counts = df_copy['Ticket'].value_counts().to_dict()

        # Record feature columns by performing a transform.
        self.feature_columns = None
        transformed_df = self.transform(df)
        meta_cols = {'PassengerId', 'Survived'}
        self.feature_columns = [col for col in transformed_df.columns if col not in meta_cols]

        return self

    def transform(self, df):
        """Apply learned transformations to train or test data."""
        df = df.copy()

        # Keep track of metadata columns if present
        target = df['Survived'] if 'Survived' in df.columns else None
        passenger_ids = df['PassengerId'] if 'PassengerId' in df.columns else None

        # 1. Title Extraction & Imputation
        titles = df['Name'].str.extract(r', ([A-Za-z]+)\.', expand=False)
        df['Title'] = titles.map(self.title_mapping).fillna('Rare')

        df['Age'] = df['Age'].fillna(df['Title'].map(self.age_medians))
        df['Age'] = df['Age'].fillna(self.overall_age_median)
        df['Fare'] = df['Fare'].fillna(self.fare_median)
        df['Embarked'] = df['Embarked'].fillna(self.embarked_mode)

        # 2. Feature Engineering
        df['FamilySize'] = df['SibSp'] + df['Parch'] + 1
        df['IsAlone'] = (df['FamilySize'] == 1).astype(int)
        df['HasCabin'] = df['Cabin'].notna().astype(int)
        df['Deck'] = df['Cabin'].str[0].fillna('U')

        # Use learned ticket counts with fallback to local count
        learned_counts = df['Ticket'].map(self.ticket_counts)
        local_counts = df.groupby('Ticket')['Ticket'].transform('count')
        df['TicketGroupSize'] = learned_counts.fillna(local_counts).astype(int)

        df['Pclass_Sex'] = df['Pclass'].astype(str) + '_' + df['Sex'].astype(str)

        # 3. Categorical Encoding
        categorical_cols = ['Sex', 'Embarked', 'Title', 'Deck', 'Pclass_Sex']
        df_encoded = pd.get_dummies(df, columns=categorical_cols, dtype=int)

        # Drop non-predictive/redundant raw columns for the feature set
        cols_to_drop = ['PassengerId', 'Survived', 'Name', 'Ticket', 'Cabin']
        features_df = df_encoded.drop(columns=[col for col in cols_to_drop if col in df_encoded.columns])

        # 4. Feature Column Alignment
        if self.feature_columns is not None:
            for col in self.feature_columns:
                if col not in features_df.columns:
                    features_df[col] = 0
            features_df = features_df[self.feature_columns]

        # Re-attach PassengerId and Survived
        result_df = features_df.copy()
        if passenger_ids is not None:
            result_df.insert(0, 'PassengerId', passenger_ids)
        if target is not None:
            result_df['Survived'] = target

        return result_df

    def fit_transform(self, df):
        """Fit parameters on training set and return transformed data."""
        self.fit(df)
        return self.transform(df)
