import express from 'express';
import bodyParser from 'body-parser';
import { spawn } from 'child_process';
import path from 'path';
import { fileURLToPath } from 'url';

const app = express();
const port = process.env.PORT || 3005;

// Middleware
app.use(bodyParser.json());

// Get the directory of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Serve static files from the React app
app.use(express.static(path.join(__dirname, 'frontend/build')));

// Test route to serve a simple HTML file
app.get('/test', (req, res) => {
    res.sendFile(path.join(__dirname, 'frontend/build/index.html'));
});

// Prediction endpoint
app.post('/predict', (req, res) => {
    const inputData = req.body;

    // Ensure all required fields are present
    const requiredFields = ['job_summary', 'job_title', 'company', 'job_location', 'job_level', 'job_type', 'job_skills'];
    for (const field of requiredFields) {
        if (!inputData[field]) {
            return res.status(400).json({ error: `Missing required field: ${field}` });
        }
    }

    // Update Python executable path (e.g., python3 for Unix-like systems)
    const pythonExecutable = 'python';  // Ensure this points to your Python executable
    const pythonProcess = spawn(pythonExecutable, [path.join(__dirname, 'predict.py')]);

    let data = '';
    pythonProcess.stdout.on('data', (chunk) => {
        data += chunk.toString();
    });

    pythonProcess.stderr.on('data', (chunk) => {
        console.error(`stderr: ${chunk}`);
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            console.error(`Prediction script exited with code ${code}`);
            return res.status(500).json({ error: 'Failed to predict.' });
        }
        try {
            const prediction = JSON.parse(data);
            res.json(prediction);
        } catch (error) {
            console.error('Error parsing JSON:', error);
            res.status(500).json({ error: 'Failed to parse prediction.' });
        }
    });

    // Send input data to Python script
    pythonProcess.stdin.write(JSON.stringify(inputData));
    pythonProcess.stdin.end();
});

// Catchall handler for any requests that don't match the API routes
app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, 'frontend/build/index.html'));
});

// Global error handling middleware
app.use((err, req, res, next) => {
    console.error('Error:', err.stack);
    res.status(500).json({ error: 'Internal Server Error' });
});

// Start the server
app.listen(port, () => {
    console.log(`Server is running on http://localhost:${port}`);
});
