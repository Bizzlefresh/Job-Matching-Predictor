import sys
import json
import joblib
import pandas as pd
import os
import requests

# Download function for Google Drive
def download_largefile():
    url = 'https://drive.google.com/uc?export=download&id=10hM4Wfs5E0h3hlrY-ZIxvoDoJf7MSSGM'  # Direct download link
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open('job_matching_pipeline.joblib', 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        raise Exception(f"Failed to download file: {response.status_code}")

# Ensure the large file is available
if not os.path.exists('job_matching_pipeline.joblib'):
    try:
        download_largefile()
    except Exception as e:
        print(f"Error during file download: {str(e)}")
        sys.exit(1)

# Load the model
model = joblib.load('job_matching_pipeline.joblib')

def predict(input_data):
    # Create a DataFrame from the input data
    df = pd.DataFrame([input_data])

    # Make predictions
    prediction = model.predict(df)[0]

    # Map numerical predictions to categorical labels
    if prediction == 2:
        return "Excellent Match"
    elif prediction == 1:
        return "Good Match"
    else:
        return "Poor Match"

if __name__ == "__main__":
    # Read input data from stdin
    input_data = json.loads(sys.stdin.read())

    try:
        result = {'prediction': predict(input_data)}
    except Exception as e:
        result = {'error': str(e)}

    # Output the prediction result as JSON
    print(json.dumps(result))
