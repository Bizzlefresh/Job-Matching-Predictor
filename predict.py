import sys
import json
import joblib
import pandas as pd
import os

# Paths to the preprocessor and model files
preprocessor_path = 'preprocessor.joblib'
model_path = 'support_vector_machine_model.joblib'

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

# Check if docx module is available
try:
    from docx import Document
except ModuleNotFoundError:
    log_error("python-docx module is not installed.")
    Document = None

# Check if PyPDF2 module is available
try:
    import PyPDF2
except ModuleNotFoundError:
    log_error("PyPDF2 module is not installed.")
    PyPDF2 = None

def extract_text_from_pdf(file_content):
    if PyPDF2 is None:
        return ""
    try:
        reader = PyPDF2.PdfFileReader(file_content)
        text = ''
        for page_num in range(reader.getNumPages()):
            text += reader.getPage(page_num).extract_text()
        return text
    except Exception as e:
        log_error(f"Error extracting text from PDF: {str(e)}")
        return ""

def extract_text_from_docx(file_content):
    if Document is None:
        return ""
    try:
        doc = Document(file_content)
        text = ''
        for para in doc.paragraphs:
            text += para.text
        return text
    except Exception as e:
        log_error(f"Error extracting text from DOCX: {str(e)}")
        return ""

def predict(input_data):
    # Create a DataFrame from the input data
    df = pd.DataFrame([input_data])

    # Parse resume content
    resume_text = ""
    if 'resume_content' in input_data:
        file_content = input_data['resume_content'].encode('utf-8', errors='ignore')
        if file_content.startswith(b'%PDF'):
            resume_text = extract_text_from_pdf(file_content)
        else:
            resume_text = extract_text_from_docx(file_content)

    df['resume'] = resume_text

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
    if prediction == 3:
        return "Excellent Match", None
    elif prediction == 2:
        return "Good Match", None
    elif prediction == 1:
        return "Fair Match", None
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
