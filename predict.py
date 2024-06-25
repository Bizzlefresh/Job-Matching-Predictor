import sys
import json
import joblib
import pandas as pd

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
