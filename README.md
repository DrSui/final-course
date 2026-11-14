# Labeled — Image Recognition API

**Labeled** is an image-recognition project that uses a custom neural network to classify food images into predefined categories.

The project provides:

- A custom Python neural-network implementation
- Image preprocessing and resizing
- Convolutional and fully connected layers
- An 11-class food classification model
- A Flask REST API for image classification
- API-key validation and usage tracking through Supabase
- A Svelte-based web interface
- FFT-related functionality for numerical/image processing
- Client-side example code for communicating with the API

## Features

### Image Classification

The neural network classifies images into the following 11 categories:

1. Bread
2. Dairy product
3. Dessert
4. Egg
5. Fried food
6. Meat
7. Noodles/Pasta
8. Rice
9. Seafood
10. Soup
11. Vegetable/Fruit

The classification labels are defined in the neural-network implementation.

### REST API

The backend exposes a `/process` endpoint that accepts a 3D image array and a list of classification filters.

The API:

1. Validates the supplied API key.
2. Checks the user's request quota.
3. Validates the image data.
4. Ensures that the input is a 3D array.
5. Runs the neural network.
6. Applies the requested classification filter.
7. Returns the selected classification result.

The Flask server runs on port `5000` by default.

### Web Interface

The frontend is implemented using Svelte. The main page presents the product as **Labeled**, an image-recognition service focused on speed, customisation, and ease of integration.

---

## Architecture

At a high level, the system is organized as follows:

```text
                    ┌─────────────────────┐
                    │    Svelte Frontend  │
                    │                     │
                    │  +page.svelte       │
                    │  +layout.svelte     │
                    │  +layout.ts         │
                    └──────────┬──────────┘
                               │
                               │ HTTP
                               ▼
                    ┌─────────────────────┐
                    │     Flask API       │
                    │      server.py      │
                    │                     │
                    │ POST /process       │
                    └──────────┬──────────┘
                               │
                ┌──────────────┴──────────────┐
                │                             │
                ▼                             ▼
       ┌─────────────────┐          ┌─────────────────┐
       │ Supabase        │          │ Neural Network  │
       │                 │          │                 │
       │ API keys        │          │ ConvLayer       │
       │ User quotas     │          │ HiddenLayer     │
       │ Usage tracking  │          │ OutputLayer     │
       └─────────────────┘          └────────┬────────┘
                                             │
                                             ▼
                                    ┌─────────────────┐
                                    │ Classification  │
                                    │                 │
                                    │ 11 food classes │
                                    └─────────────────┘
```

---

## Repository Structure

```text
final-course/
│
├── Documentation/
│   └── Project documentation
│
├── styles/
│   └── Frontend styles
│
├── +layout.svelte
├── +layout.ts
├── +page.svelte
│
├── client.py
├── data.py
├── fft.py
├── layers2.py
├── main.py
├── resize.py
├── server.py
├── supabase.ts
│
├── fft_comparison.png
├── image.png
│
└── README.md
```

The repository currently contains eight commits and uses `main` as its primary branch.

---

# Machine Learning Pipeline

## 1. Data Loading

The `data.py` module loads training data from a NumPy `.npz` file:

```text
dataSample.npz
```

The expected arrays are:

- `data`
- `labels`

The images are converted to floating-point values and reshaped into flattened vectors for processing. The data is also shuffled before being returned.

Example:

```python
images, labels = get_data()
```

---

## 2. Image Preprocessing

The project includes `resize.py`, which is responsible for preparing images for the neural network.

The network expects images with a resolution of:

```text
64 × 64 × 3
```

representing:

```text
height × width × RGB channels
```

During training, images are normalized before being passed through the network.

---

## 3. Neural Network

The main machine-learning implementation is contained in `main.py`.

The network consists of:

```text
Input Image
    │
    ▼
Convolution Layer
    │
    ▼
Hidden Layer
    │
    ▼
Hidden Layer
    │
    ▼
Output Layer
    │
    ▼
11 Food Classes
```

The network is initialized with parameters including:

```python
n = 200
learn_rate = 0.005
size = 64
kernel_size = 3
```

The architecture includes:

```python
ConvLayer(3, 2, 3, size, 0, learn_rate)

HiddenLayer(1024, entrance_size, learn_rate)

HiddenLayer(1024, 1024, learn_rate)

OutputLayer(11, 1024, learn_rate)
```

The final output contains 11 classification scores.

---

# Training

The `NeuralNetwork` class provides a training method:

```python
neural_net.train(epochs)
```

Training consists of:

1. Loading the dataset.
2. Warming up the network.
3. Shuffling the training data.
4. Performing forward propagation.
5. Calculating classification accuracy.
6. Calculating cross-entropy loss.
7. Performing backpropagation.
8. Recording loss and accuracy.
9. Displaying training metrics.

The implementation currently uses 25 epochs when the user selects the `train` option from `main.py`.

---

# Running the Machine Learning Model

## Requirements

The Python components use libraries including:

- Python 3
- NumPy
- SciPy
- Matplotlib
- Numba
- Flask
- Flask-RESTful
- Supabase Python client

The exact dependencies should be installed in an isolated Python environment.

### Create a virtual environment

```bash
python -m venv .venv
```

### Activate it

On Linux/macOS:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

### Install dependencies

If a `requirements.txt` file is added to the project, install dependencies with:

```bash
pip install -r requirements.txt
```

Otherwise, install the dependencies used by the Python source files:

```bash
pip install numpy scipy matplotlib numba flask flask-restful supabase requests
```

---

# Training the Model

From the repository root:

```bash
python main.py
```

The program prompts:

```text
load or train or both:
```

### Train

Enter:

```text
train
```

The current implementation trains for 25 epochs.

### Load

Enter:

```text
load
```

This attempts to load previously saved neural-network parameters.

### Train and save

Enter:

```text
both
```

The implementation trains the model and then attempts to save its parameters.

---

# Classifying an Image

After loading/training the model, the application asks for the path to an image:

```text
enter the directory to an image:
```

For example:

```text
./images/example.jpg
```

The image is resized to the expected `64 × 64 × 3` input format and passed through the neural network.

The model then displays the image and prints the classification probabilities.

---

# REST API

The REST API is implemented in `server.py` using Flask and Flask-RESTful.

Start the server with:

```bash
python server.py
```

The server listens on:

```text
http://localhost:5000
```

The main endpoint is:

```text
POST /process
```

---

## Request Format

The request body should contain:

```json
{
  "api-key": "YOUR_API_KEY",
  "image": [
    [
      [0.1, 0.2, 0.3],
      [0.4, 0.5, 0.6]
    ]
  ],
  "filter": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
}
```

The actual image must be a **3-dimensional array**.

The dimensions are expected to represent an image such as:

```text
height × width × channels
```

The API rejects input that is not three-dimensional.

---

## Filter

The `filter` array determines which classification categories may be returned.

There are 11 output classes, so the filter should contain 11 values.

For example:

```json
{
  "filter": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
}
```

allows only the first category:

```text
Bread
```

A value of `0` disables a category, while a non-zero value allows it.

At least one category must be enabled. If every filter value is zero, the API returns:

```json
{
  "error": "must select at least 1 item"
}
```

---

# API Response

A successful request returns a result similar to:

```json
{
  "result": "Bread"
}
```

The API selects the highest-scoring class that is enabled by the supplied filter.

If the API key is invalid or the request quota has been exceeded, the server returns:

```json
{
  "error": "invalid api key"
}
```

with HTTP status `401`.

---

# Python Client

The repository includes `client.py`, which demonstrates how to call the API programmatically.

The client:

1. Generates a test 3D NumPy array.
2. Creates an 11-element filter.
3. Sends the data to `/process`.
4. Reads the JSON response.
5. Converts the returned result into a NumPy array.

A simplified request looks like:

```python
import requests

response = requests.post(
    "http://localhost:5000/process",
    json={
        "image": image_array,
        "api-key": API_KEY,
        "filter": filter
    }
)
```

The existing client demonstrates this API interaction against a locally running server.

---

# Supabase Integration

Supabase is used by the backend for API-key and usage management.

The server accesses two database tables:

```text
keys
users
```

The `keys` table is used to validate API keys and track their usage.

The `users` table stores request limits, including:

```text
current_requests
allowed_requests
```

For every valid request, the server increments the usage counters before processing the image.

Conceptually:

```text
Client
  │
  ▼
API Key
  │
  ▼
Supabase
  │
  ├── Is key valid?
  │
  ├── Has quota been exceeded?
  │
  └── Update usage
  │
  ▼
Neural Network
```

---

# Frontend

The frontend uses **Svelte**.

The main application page is implemented in:

```text
+page.svelte
```

The application currently presents the product as **Labeled** and describes three main characteristics:

- Speed
- Customisability
- Ease of Use

The Svelte layout handles navigation between the home page, documentation, and login-related routes.

The frontend also integrates Supabase authentication through `+layout.ts`, which creates browser/server Supabase clients and retrieves the current session and user.

---

# FFT Processing

The repository contains an `fft.py` module implementing FFT-related functionality and an `FFTCache` used by the neural-network implementation.

The neural network creates an FFT cache during initialization:

```python
self.cache = FFTCache()
```

The cache is subsequently passed into the convolutional layer during forward and backward operations.

The repository also includes:

```text
fft_comparison.png
```

which appears to be an output/comparison artifact associated with the FFT work.

---

# Development Workflow

A typical development workflow is:

```text
1. Clone repository
       │
       ▼
2. Create Python environment
       │
       ▼
3. Install dependencies
       │
       ▼
4. Prepare training data
       │
       ▼
5. Train/test neural network
       │
       ▼
6. Start Flask API
       │
       ▼
7. Test /process endpoint
       │
       ▼
8. Run Svelte frontend
```

---

# API Example with cURL

Once the Flask server is running, an API request can be made with:

```bash
curl -X POST http://localhost:5000/process \
  -H "Content-Type: application/json" \
  -d '{
    "api-key": "YOUR_API_KEY",
    "image": [[[0.1, 0.2, 0.3]]],
    "filter": [1,1,1,1,1,1,1,1,1,1,1]
  }'
```

For a real image, the `image` value must be replaced with the complete 3D image array expected by the model.

---

# Error Handling

The API currently handles several classes of errors.

### Missing image

```json
{
  "error": "Missing \"image\" in request body"
}
```

HTTP status:

```text
400
```

### Invalid image format

```json
{
  "error": "Invalid array format: ..."
}
```

HTTP status:

```text
400
```

### Incorrect dimensions

```json
{
  "error": "Expected 3D array, got ...D"
}
```

HTTP status:

```text
400
```

### Empty filter

```json
{
  "error": "must select at least 1 item"
}
```

HTTP status:

```text
400
```

### Invalid API key

```json
{
  "error": "invalid api key"
}
```

HTTP status:

```text
401
```

### Internal server error

```json
{
  "error": "Server error: ..."
}
```

HTTP status:

```text
500
```

These behaviours are implemented in `server.py`.

---

# Security

## Important: Move Credentials to Environment Variables

The current repository contains Supabase credentials directly in source code.

For example, credentials are currently present in:

```text
+layout.ts
server.py
```

This is **not recommended for production**.

Instead, use environment variables.

For example:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-key
```

Then load them from the environment:

```python
import os

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
```

The exposed credentials in the repository should be considered compromised and rotated if they are real production credentials.

Do not commit:

```text
.env
.env.local
credentials.json
API keys
private keys
service-role keys
```

Add them to `.gitignore`.

---

# Recommended Project Improvements

The current repository is functional as a course/project prototype, but the following improvements would make it significantly easier to deploy and maintain.

## 1. Add `requirements.txt`

Create:

```text
requirements.txt
```

and pin the required dependencies.

Example:

```text
numpy
scipy
matplotlib
numba
flask
flask-restful
requests
supabase
```

Versions should ideally be pinned after testing the project environment.

---

## 2. Add Environment Configuration

Move all credentials and configurable values into environment variables.

For example:

```env
SUPABASE_URL=
SUPABASE_KEY=
API_HOST=0.0.0.0
API_PORT=5000
```

---

## 3. Add Automated Tests

Recommended tests include:

```text
test_data.py
test_layers.py
test_model.py
test_api.py
test_authentication.py
```

At minimum, the API should test:

- Valid API keys
- Invalid API keys
- Missing image data
- Invalid image dimensions
- Empty filters
- Valid classification requests
- Request quota handling

---

## 4. Improve Model Serialization

The current `save()` and `load()` implementation references several weight and bias attributes that do not appear to correspond cleanly to the current layer-based architecture.

A more robust approach would be to serialize each layer's parameters explicitly, for example:

```text
model/
├── conv_layer.npz
├── hidden_layer_1.npz
├── hidden_layer_2.npz
└── output_layer.npz
```

or use a single structured model format.

---

## 5. Add Dependency and Setup Documentation

The repository should document:

- Python version
- Node.js version
- Svelte/SvelteKit version
- Supabase setup
- Required dataset
- Dataset location
- Model training procedure
- API startup
- Frontend startup

This README provides the high-level documentation, but the exact frontend package configuration should also be committed to the repository.

---

# Troubleshooting

## `ModuleNotFoundError`

Install the Python dependencies:

```bash
pip install -r requirements.txt
```

or install the required packages manually.

---

## API returns `invalid api key`

Check that:

1. The API key exists in the Supabase database.
2. The key is being sent as `api-key`.
3. The user has not exceeded their request quota.
4. The backend is connected to the correct Supabase project.

---

## API rejects image dimensions

The API expects a 3-dimensional NumPy-compatible array.

For an RGB image:

```text
(height, width, 3)
```

For example:

```text
(64, 64, 3)
```

---

## Model cannot find training data

The data loader expects:

```text
dataSample.npz
```

with:

```text
data
labels
```

arrays inside the archive.

Make sure the file is available in the expected working directory.

---

# Project Status

The repository currently appears to be an academic/course project or prototype rather than a production-ready image-recognition service.

Current components include:

| Component | Technology | Purpose |
|---|---|---|
| Machine learning | Python / NumPy | Image classification |
| Neural network | Custom implementation | Food classification |
| Convolution | Custom `ConvLayer` | Image feature extraction |
| FFT | Python / NumPy | Numerical processing |
| Backend | Flask | REST API |
| Database | Supabase | API keys and usage |
| Frontend | Svelte | Web interface |
| Image preprocessing | Python | Resize/normalize images |

---

# Future Improvements

Potential future development includes:

- [ ] Add a complete `requirements.txt`
- [ ] Add `.env.example`
- [ ] Remove hard-coded credentials
- [ ] Rotate exposed Supabase credentials
- [ ] Add automated unit tests
- [ ] Add API documentation/OpenAPI
- [ ] Add Docker support
- [ ] Add production WSGI configuration
- [ ] Improve model serialization
- [ ] Add dataset documentation
- [ ] Add model evaluation metrics
- [ ] Add a confusion matrix
- [ ] Add validation/test datasets
- [ ] Add CI/CD
- [ ] Add frontend setup instructions
- [ ] Add authentication documentation
- [ ] Add deployment instructions

---

# License

No explicit license is currently documented in the repository README.

If this project is intended to be reused or distributed publicly, add an appropriate `LICENSE` file and specify the license here.

---

# Contributing

Contributions can be made through the normal GitHub workflow:

```text
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the changes
5. Commit the changes
6. Push the branch
7. Open a Pull Request
```

Example:

```bash
git checkout -b feature/improved-classification
git add .
git commit -m "Improve image classification"
git push origin feature/improved-classification
```

---

# Acknowledgements

This project combines several technologies and concepts, including:

- Neural-network-based image classification
- Convolutional neural networks
- FFT-based numerical processing
- REST API development
- Supabase database/authentication services
- Svelte frontend development

---

# Repository

**GitHub:** [DrSui/final-course](https://github.com/DrSui/final-course)

The repository is publicly accessible and currently contains the source code, frontend, documentation directory, image assets, and machine-learning implementation described above.
