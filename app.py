import streamlit as st
import subprocess
import json
import sys
import os
import hashlib

# File to store user credentials
CREDENTIALS_FILE = 'users.json'


# Utility function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Function to load credentials from the file
def load_credentials():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            return json.load(file)
    return {}


# Function to save credentials to the file
def save_credentials(credentials):
    with open(CREDENTIALS_FILE, 'w') as file:
        json.dump(credentials, file)


# Function to handle user authentication
def authenticate(username, password):
    credentials = load_credentials()
    hashed_password = hash_password(password)
    return username in credentials and credentials[username] == hashed_password


# Function to handle user registration
def register_user(username, password):
    credentials = load_credentials()
    if username in credentials:
        return False, "Username already exists."
    credentials[username] = hash_password(password)
    save_credentials(credentials)
    return True, "User registered successfully."


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


# --- Start of Streamlit Application ---
st.title('Job Match Predictor')

# Authentication check
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["username"] = ""

# Sign-Up and Login Flow
if not st.session_state["logged_in"]:
    auth_mode = st.sidebar.selectbox("Choose Authentication Mode", ["Login", "Sign Up"])

    if auth_mode == "Sign Up":
        st.subheader("Create a New Account")
        new_username = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Sign Up"):
            if new_password != confirm_password:
                st.error("Passwords do not match.")
            else:
                success, message = register_user(new_username, new_password)
                if success:
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = new_username
                    st.success(message)
                    st.experimental_rerun()  # Redirect to the main page
                else:
                    st.error(message)

    elif auth_mode == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if authenticate(username, password):
                st.session_state["logged_in"] = True
                st.session_state["username"] = username
                st.success("Login successful! Redirecting...")
                st.experimental_rerun()  # Redirect to the main page
            else:
                st.error("Invalid username or password.")
else:
    st.markdown(f"## Welcome, {st.session_state['username']}!")
    st.markdown("""
    This application helps you determine how well a job posting matches your profile. 
    Simply provide the job details and let our model predict the match quality. The predictions are categorized as:

    - **Excellent Match**
    - **Good Match**
    - **Fair Match**
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
    formData['job_level'] = st.selectbox('Job Level', ['', 'Mid senior', 'Associate'],
                                         help='The level or seniority of the job position.')
    formData['job_type'] = st.selectbox('Job Type', ['', 'Onsite', 'Remote'],
                                        help='The type of job, whether it is onsite or remote.')
    formData['job_skills'] = st.text_area('Job Skills', help='A list of required or preferred skills for the job.')
    formData['resume'] = st.file_uploader("Upload Resume", type=["pdf", "docx"],
                                          help="Upload your resume in PDF or DOCX format.")

    # Track prediction state
    prediction_result = None


    # Validate form data
    def is_valid_form(formData):
        return all(formData.values()) and formData['resume'] is not None


    # Predict button
    if st.button('Predict'):
        if is_valid_form(formData):
            with st.spinner('Predicting...'):
                resume_content = formData['resume'].read()
                formData['resume_content'] = resume_content.decode('utf-8', errors='ignore')
                del formData['resume']
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
                return 'prediction-3'
            elif prediction == 'Good Match':
                return 'prediction-2'
            elif prediction == 'Fair Match':
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
        .prediction-3 {
            color: green;
            font-weight: bold;
        }
        .prediction-2 {
            color: blue;
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
