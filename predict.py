import sys
import json
import joblib
import pandas as pd
import os

# Paths to the preprocessor and model files
preprocessor_path = 'preprocessor.joblib'
model_path = 'model.joblib'

# Log to file
def log_error(message):
    with open("error_log.txt", "a") as log_file:
        log_file.write(message + "\n")

# Ensure the preprocessor and model files are available
if not os.path.exists(preprocessor_path):
    error_message = f"Preprocessor file not found: {preprocessor_path}"
    log_error(error_message)
    print(json.dumps({'error': error_message}))
    sys.exit(1)

if not os.path.exists(model_path):
    error_message = f"Model file not found: {model_path}"
    log_error(error_message)
    print(json.dumps({'error': error_message}))
    sys.exit(1)

# Load the preprocessor and model
try:
    preprocessor = joblib.load(preprocessor_path)
except Exception as e:
    error_message = f"Error loading preprocessor: {str(e)}"
    log_error(error_message)
    print(json.dumps({'error': error_message}))
    sys.exit(1)

try:
    model = joblib.load(model_path)
except Exception as e:
    error_message = f"Error loading model: {str(e)}"
    log_error(error_message)
    print(json.dumps({'error': error_message}))
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
    try:
        # Read input data from stdin
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError as e:
        error_message = f"JSONDecodeError: {str(e)}"
        log_error(error_message)
        print(json.dumps({'error': error_message}))
        sys.exit(1)

    try:
        prediction, error = predict(input_data)
        if error:
            result = {'error': error}
            log_error(error)
        else:
            result = {'prediction': prediction}
    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        log_error(error_message)
        result = {'error': error_message}

    # Output the prediction result as JSON
    print(json.dumps(result))
