# 🎯 Job Matching Predictor

Welcome to the **Job Matching Predictor**! This repository contains all the necessary scripts and data for predicting how well a job posting matches your profile. Below you'll find a detailed description of the project structure, its components, and how to use them.

## 📂 Project Structure

The project is organized as follows:

```
Job Matching Predictor
│
├── CSV Files
│   ├── job_skills.csv
│   ├── job_summary.csv
│   ├── linkedin_job_postings.csv
│
├── app.py
├── main.py
├── predict.py
├── model.joblib
├── preprocessor.joblib
├── requirements.txt
├── server.mjs
├── package.json
└── package-lock.json
```

### CSV Files

- **job_skills.csv**: Contains job skills data.
- **job_summary.csv**: Contains job summary data.
- **linkedin_job_postings.csv**: Contains LinkedIn job postings data.

### Scripts

- **app.py**: The main Streamlit application for user interaction.
- **main.py**: Script for data preprocessing, model training, and saving the trained model.
- **predict.py**: Script for loading the preprocessor and model to make predictions.
- **server.mjs**: Node.js server file to handle backend requests.

### Model Files

- **model.joblib**: The saved file for the trained model.
- **preprocessor.joblib**: The saved file for the data preprocessor.

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.x
- Node.js
- Pip

### Installation

Clone the repository and navigate to the project directory:

```bash
git clone https://github.com/yourusername/job-matching-predictor.git
cd job-matching-predictor
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Install the required Node.js packages:

```bash
npm install
```

## 🛠️ Usage

### Using Streamlit

1. **Start the Streamlit app**:
    ```bash
    streamlit run app.py
    ```

2. **Open your browser** and go to `http://localhost:8501` to interact with the Job Matching Predictor UI.

### Using Node.js Server

1. **Start the Node.js server**:
    ```bash
    node server.mjs
    ```

2. **Open your browser** and go to `http://localhost:3005` to access the application.

### Training the Model

1. **Load and merge datasets**:
    ```bash
    python main.py
    ```

2. **The script will preprocess the data, train the model, and save the preprocessor and model files**.

## 🔧 Components

### app.py

Handles user input and interacts with the prediction script to provide job match predictions via a Streamlit interface.

### main.py

Manages data loading, preprocessing, feature engineering, model training, and saving the preprocessor and model.

### predict.py

Loads the preprocessor and model to make predictions based on user input.

### server.mjs

Node.js server to handle API requests for predictions.

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## 📚 Acknowledgments

- The **Scikit-learn** library for machine learning algorithms.
- The **Streamlit** library for building the web application.
- The **Joblib** library for model persistence.
- The **Express.js** library for the Node.js server.

## 📞 Contact

If you have any questions or need further assistance, feel free to contact me at [adebiyiolanrewaju12@gmail.com](mailto:adebiyiolanrewaju12@gmail.com).

---

Let's make job hunting a breeze! 🚀

---
