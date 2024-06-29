import sys
import json
import joblib
import pandas as pd
import os

# Paths to the preprocessor and model files
preprocessor_path = 'preprocessor.joblib'
model_path = 'model.joblib'

# Ensure the preprocessor and model files are available
if not os.path.exists(preprocessor_path):
    print(json.dumps({'error': f"Preprocessor file not found: {preprocessor_path}"}))
    sys.exit(1)

if not os.path.exists(model_path):
    print(json.dumps({'error': f"Model file not found: {model_path}"}))
    sys.exit(1)

# Load the preprocessor and model
try:
    preprocessor = joblib.load(preprocessor_path)
except Exception as e:
    print(json.dumps({'error': f"Error loading preprocessor: {str(e)}"}))
    sys.exit(1)

try:
    model = joblib.load(model_path)
except Exception as e:
    print(json.dumps({'error': f"Error loading model: {str(e)}"}))
    sys.exit(1)

def predict(input_data):
    # Create a DataFrame from the input data
    df = pd.DataFrame([input_data])

    # Preprocess the input data
    try:
        df_transformed = preprocessor.transform(df)
    except Exception as e:
        return None, f"Error during preprocessing: {str(e)}"

    # Make predictions
    try:
        prediction = model.predict(df_transformed)[0]
    except Exception as e:
        return None, f"Error during prediction: {str(e)}"

    # Map numerical predictions to categorical labels
    if prediction == 2:
        return "Excellent Match", None
    elif prediction == 1:
        return "Good Match", None
    else:
        return "Poor Match", None

if __name__ == "__main__":
    # Read input data from stdin
    input_data = json.loads(sys.stdin.read())

    try:
        prediction, error = predict(input_data)
        if error:
            result = {'error': error}
        else:
            result = {'prediction': prediction}
    except Exception as e:
        result = {'error': str(e)}

    # Output the prediction result as JSON
    print(json.dumps(result))
