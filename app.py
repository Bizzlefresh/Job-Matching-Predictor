import streamlit as st
import subprocess
import json

# Function to handle user input and predict job match
def predict_job(formData):
    try:
        # Run predict.py as a subprocess
        result = subprocess.run(['python', 'predict.py'], input=json.dumps(formData), capture_output=True, text=True, check=True)

        # Parse the output from predict.py
        prediction_result = json.loads(result.stdout)['prediction']
        return prediction_result, None
    except subprocess.CalledProcessError as e:
        return None, f'Error: {e.stderr}'
    except Exception as e:
        return None, f'Error: {str(e)}'

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

# Predict button
if st.button('Predict'):
    st.write('Predicting...')

    prediction_result, error = predict_job(formData)

    if error:
        st.error(f'Prediction error: {error}')
    elif prediction_result:
        st.success(f'Prediction: {prediction_result}')
    else:
        st.warning('No prediction result.')

    # Display prediction result with color-coded CSS class
    def get_prediction_class(prediction):
        if prediction == 'Excellent Match':
            return 'prediction-2'
        elif prediction == 'Good Match':
            return 'prediction-1'
        elif prediction == 'Poor Match':
            return 'prediction-0'
        else:
            return ''

    # Example of displaying prediction with custom CSS class
    if prediction_result:
        st.markdown(f'<p class="{get_prediction_class(prediction_result)}">Prediction: {prediction_result}</p>', unsafe_allow_html=True)
