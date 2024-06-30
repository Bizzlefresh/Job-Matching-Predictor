import streamlit as st
import subprocess
import json
import sys

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
        with open("error_log.txt", "r") as log_file:
            log_content = log_file.read()
        return None, f'CalledProcessError: {log_content}'
    except json.JSONDecodeError as e:
        return None, f'JSONDecodeError: {str(e)}'
    except Exception as e:
        return None, f'Unexpected error: {str(e)}'

# Streamlit UI components
st.title('Job Match Predictor')

# Form inputs
formData = {}
formData['job_summary'] = st.text_area('Job Summary')
formData['job_title'] = st.text_input('Job Title')
formData['company'] = st.text_input('Company')
formData['job_location'] = st.text_input('Job Location')
formData['job_level'] = st.selectbox('Job Level', ['', 'Mid senior', 'Associate'])
formData['job_type'] = st.selectbox('Job Type', ['', 'Onsite', 'Remote'])
formData['job_skills'] = st.text_area('Job Skills')

# Track prediction state
prediction_result = None

# Validate form data
def is_valid_form(formData):
    return all(formData.values())

# Predict button
if st.button('Predict'):
    if is_valid_form(formData):
        st.write('Predicting...')
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
