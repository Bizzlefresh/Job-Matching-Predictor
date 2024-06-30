import streamlit as st
import subprocess
import json
import sys
import os

# Function to handle user input and predict job match
def predict_job(formData):
    try:
        # Get the Python executable from the current environment
        python_executable = sys.executable

        # Run predict.py as a subprocess using the correct Python executable
        result = subprocess.run(
            [python_executable, 'predict.py'],
            input=json.dumps(formData),
            capture_output=True,
            text=True,
            check=True
        )

        # Parse the output from predict.py
        output = json.loads(result.stdout)
        if 'error' in output:
            return None, output['error']
        return output['prediction'], None
    except subprocess.CalledProcessError as e:
        # Retrieve the log content if there's a CalledProcessError
        log_content = e.stderr or e.stdout
        return None, f'CalledProcessError: {log_content}'
    except json.JSONDecodeError as e:
        return None, f'JSONDecodeError: {str(e)}'
    except Exception as e:
        return None, f'Unexpected error: {str(e)}'

# Introduction section
st.title('Job Match Predictor')
st.markdown("""
## Welcome to the Job Match Predictor!
This application helps you determine how well a job posting matches your profile. 
Simply provide the job details and let our model predict the match quality. The predictions are categorized as:

- **Excellent Match**
- **Good Match**
- **Poor Match**

Please fill in all the fields below to get started.
""")

# Form inputs with tooltips
st.markdown("### Job Details")
formData = {}
formData['job_summary'] = st.text_area('Job Summary', help='A brief summary or description of the job.')
formData['job_title'] = st.text_input('Job Title', help='The title or designation of the job.')
formData['company'] = st.text_input('Company', help='The name of the company offering the job.')
formData['job_location'] = st.text_input('Job Location', help='The location where the job is based.')
formData['job_level'] = st.selectbox('Job Level', ['', 'Mid senior', 'Associate'], help='The level or seniority of the job position.')
formData['job_type'] = st.selectbox('Job Type', ['', 'Onsite', 'Remote'], help='The type of job, whether it is onsite or remote.')
formData['job_skills'] = st.text_area('Job Skills', help='A list of required or preferred skills for the job.')

# Track prediction state
prediction_result = None

# Validate form data
def is_valid_form(formData):
    return all(formData.values())

# Predict button
if st.button('Predict'):
    if is_valid_form(formData):
        with st.spinner('Predicting...'):
            prediction_result, error = predict_job(formData)

        if error:
            st.error(f'Prediction error: {error}')
        elif prediction_result:
            st.success('Prediction successful!')
    else:
        st.error('Please fill in all fields before predicting.')

# Display prediction result with color-coded CSS class if prediction has been made
if prediction_result:
    def get_prediction_class(prediction):
        if prediction == 'Excellent Match':
            return 'prediction-2'
        elif prediction == 'Good Match':
            return 'prediction-1'
        elif prediction == 'Poor Match':
            return 'prediction-0'
        else:
            return ''

    # Display styled prediction message
    st.markdown(
        f'<p class="{get_prediction_class(prediction_result)}">Prediction: {prediction_result}</p>',
        unsafe_allow_html=True
    )

# CSS for color-coded prediction results
st.markdown("""
    <style>
    .prediction-2 {
        color: green;
        font-weight: bold;
    }
    .prediction-1 {
        color: orange;
        font-weight: bold;
    }
    .prediction-0 {
        color: red;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)
