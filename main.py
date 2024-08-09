import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from joblib import dump
import time
from tqdm import tqdm
from scipy.sparse import hstack

def load_dataset(file_path):
    try:
        start_time = time.time()
        df = pd.read_csv(file_path)
        end_time = time.time()
        print(f"Loaded {file_path} in {end_time - start_time:.2f} seconds")
        print(f"Dataset size: {df.shape}")
        return df
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return pd.DataFrame()

def merge_datasets(datasets, on='job_link'):
    try:
        merged_data = datasets[0]
        for dataset in tqdm(datasets[1:], desc="Merging datasets"):
            merged_data = merged_data.merge(dataset, on=on, how='left')
        return merged_data
    except Exception as e:
        print(f"Error merging datasets: {e}")
        return pd.DataFrame()

def create_target(df):
    try:
        conditions = [
            (df['job_level'] == 'Mid senior') & (df['job_type'] == 'Onsite'),
            (df['job_level'] == 'Associate') & (df['job_type'] == 'Onsite'),
            (df['job_level'] == 'Mid senior') & (df['job_type'] == 'Remote'),
            (df['job_level'] == 'Associate') & (df['job_type'] == 'Remote')
        ]
        choices = [3, 2, 1, 1]  # 3 = Excellent Match, 2 = Good Match, 1 = Fair Match, 0 = Poor Match
        df['target'] = np.select(conditions, choices, default=0)
        return df
    except Exception as e:
        print(f"Error creating target column: {e}")
        return df

def check_columns(df, required_columns):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        print(f"Missing columns in dataset: {missing_columns}")
        return False
    return True

def main():
    # Load datasets
    datasets = ['job_skills.csv', 'job_summary.csv', 'linkedin_job_postings.csv']
    loaded_datasets = []
    for file in tqdm(datasets, desc="Loading datasets"):
        df = load_dataset(file)
        if check_columns(df, ['job_link']):
            loaded_datasets.append(df)
        else:
            print(f"Skipping dataset {file} due to missing job_link column")

    # Ensure we have all necessary columns before merging
    if not loaded_datasets:
        print("No datasets to merge. Exiting.")
        return

    # Merge datasets
    merged_data = merge_datasets(loaded_datasets)
    if merged_data.empty:
        print("Merged dataset is empty. Exiting.")
        return

    # Ensure merged_data contains necessary columns
    required_columns = ['job_summary', 'job_title', 'company', 'job_location', 'job_level', 'job_type', 'job_skills']
    if not check_columns(merged_data, required_columns):
        print("Merged dataset is missing required columns. Exiting.")
        return

    # Create target column
    merged_data = create_target(merged_data)

    # Feature selection
    features = required_columns
    X = merged_data[features]
    y = merged_data['target']

    # Fill missing values in text features
    X['job_summary'] = X['job_summary'].fillna('')
    X['job_skills'] = X['job_skills'].fillna('')

    # Sample data to reduce size
    X_sampled = X.sample(frac=0.1, random_state=42)
    y_sampled = y.loc[X_sampled.index]

    # Splitting data
    X_train, X_test, y_train, y_test = train_test_split(X_sampled, y_sampled, test_size=0.2, random_state=42)
    print(f"Training set size: {X_train.shape}, Test set size: {X_test.shape}")

    # Preprocessing
    text_features = ['job_summary', 'job_skills']
    categorical_features = ['job_title', 'company', 'job_location', 'job_level', 'job_type']

    preprocessor = ColumnTransformer(
        transformers=[
            ('text_summary', TfidfVectorizer(), 'job_summary'),
            ('text_skills', TfidfVectorizer(), 'job_skills'),
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=True), categorical_features)
        ],
        sparse_threshold=0.3
    )

    # Fit the preprocessor
    print("Fitting the preprocessor...")
    X_train_transformed = preprocessor.fit_transform(X_train)
    X_test_transformed = preprocessor.transform(X_test)

    # Combine text and categorical features if they are sparse
    if hasattr(X_train_transformed, 'toarray'):
        X_train_transformed = hstack([X_train_transformed])
    if hasattr(X_test_transformed, 'toarray'):
        X_test_transformed = hstack([X_test_transformed])

    # Train the model with reduced complexity
    model = RandomForestClassifier(n_estimators=5, max_depth=10, random_state=42)
    print("Training the model...")
    start_time = time.time()
    for _ in tqdm(range(1), desc="Training progress"):
        model.fit(X_train_transformed, y_train)
    train_time = time.time() - start_time

    # Predict
    print("Predicting...")
    start_time = time.time()
    y_pred = model.predict(X_test_transformed)
    predict_time = time.time() - start_time

    # Evaluate
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted')
    recall = recall_score(y_test, y_pred, average='weighted')
    f1 = f1_score(y_test, y_pred, average='weighted')

    print(f'Training time: {train_time:.2f} seconds')
    print(f'Prediction time: {predict_time:.2f} seconds')
    print(f'Accuracy: {accuracy}')
    print(f'Precision: {precision}')
    print(f'Recall: {recall}')
    print(f'F1 Score: {f1}')

    # Save the preprocessor and model separately with compression
    preprocessor_path = 'preprocessor.joblib'
    model_path = 'model.joblib'
    dump(preprocessor, preprocessor_path, compress=3)
    dump(model, model_path, compress=3)
    print(f'Preprocessor saved to {preprocessor_path}')
    print(f'Model saved to {model_path}')

if __name__ == "__main__":
    main()

