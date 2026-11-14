# Labeled — Image Recognition API

**Labeled** is an image-recognition project that uses a custom neural network to classify food images into predefined categories.

The project combines a custom neural-network implementation, image preprocessing, JIT-compiled numerical algorithms, a Flask REST API, Supabase integration, and a Svelte frontend.

## Features

- Custom neural network implemented in Python
- Image preprocessing and resizing
- Convolutional and fully connected layers
- 11-class food image classification
- Custom Fast Fourier Transform (FFT) implementation
- JIT compilation using Numba for high-performance numerical computation
- FFT implementation benchmarked against NumPy
- Flask REST API for image classification
- Supabase-based API-key validation and request tracking
- Svelte-based web interface

---

# Food Classification

The neural network classifies images into 11 food categories:

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

---

# Architecture

The system consists of a Svelte frontend, Flask API, Supabase backend, and custom neural-network implementation.

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

# Repository Structure

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

The repository contains the machine-learning implementation, FFT implementation, API server, frontend, image-processing utilities, and supporting documentation.

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

The images are converted into floating-point values and prepared for processing.

---

## 2. Image Preprocessing

The project includes `resize.py`, which prepares images for the neural network.

The network operates on images with a resolution of:

```text
64 × 64 × 3
```

where the three channels represent RGB colour information.

---

## 3. Neural Network

The main machine-learning implementation is contained in `main.py`.

The network consists of convolutional and fully connected layers:

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

The implementation includes:

```python
ConvLayer(3, 2, 3, size, 0, learn_rate)

HiddenLayer(1024, entrance_size, learn_rate)

HiddenLayer(1024, 1024, learn_rate)

OutputLayer(11, 1024, learn_rate)
```

The final output contains 11 classification scores.

---

# Fast Fourier Transform

A significant part of the project is the implementation of a custom **Fast Fourier Transform (FFT)**.

The FFT implementation is contained in:

```text
fft.py
```

Rather than relying entirely on NumPy's FFT implementation, the project implements the required FFT functionality directly and uses **Numba JIT compilation** to accelerate the numerical operations.

The implementation makes use of Numba's:

```python
@njit
```

and related JIT functionality to compile numerical Python code into optimized machine code at runtime.

The FFT implementation also uses precomputed values such as:

- Bit-reversal indices
- Twiddle factors
- Cached FFT parameters

The repository contains an `FFTCache` implemented as a Numba `jitclass`, which stores these values for reuse.

This reduces repeated computation when the FFT is executed multiple times.

---

# FFT Performance

The custom FFT was developed with performance as a key objective.

By using **JIT compilation**, the implementation is able to execute the FFT algorithm as compiled numerical code rather than interpreting the Python implementation directly.

The project includes:

```text
fft_comparison.png
```

which contains the performance comparison between the custom JIT-compiled FFT implementation and NumPy's FFT implementation.

The benchmark demonstrates that the custom implementation **outperforms NumPy's FFT for the tested workloads**, showing the performance benefits of combining a custom FFT implementation with Numba JIT compilation.

The implementation therefore serves two purposes:

1. Providing a custom FFT implementation for use within the project.
2. Demonstrating how JIT compilation can significantly improve the performance of numerical Python code.

---

# FFT Implementation

The FFT implementation contains several performance-oriented components.

### Bit Reversal

FFT algorithms commonly require bit-reversed ordering of the input.

The project calculates and caches these indices so that they can be reused for repeated transforms.

### Twiddle Factors

The complex exponential coefficients used during the FFT are precomputed and cached.

This avoids repeatedly calculating the same complex values during subsequent FFT operations.

### JIT Compilation

Numba is used to compile performance-critical functions.

The repository imports:

```python
from numba import njit, int64, complex128, prange, types, typed, vectorize
```

and uses Numba's experimental `jitclass` functionality for the FFT cache.

### FFT Cache

The `FFTCache` stores:

```text
Bit-reversal indices
        +
Twiddle factors
```

indexed by transform size.

This allows the FFT implementation to reuse precomputed data rather than generating it for every transform.

---

# Training

The `NeuralNetwork` class provides a training method:

```python
neural_net.train(epochs)
```

Training consists of:

1. Loading the dataset.
2. Preparing the network.
3. Shuffling the training data.
4. Performing forward propagation.
5. Calculating classification accuracy.
6. Calculating loss.
7. Performing backpropagation.
8. Recording training metrics.

The training process can be selected through `main.py`.

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
- Supabase
- Requests

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Linux/macOS:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

Install the required dependencies:

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

This trains the neural network.

### Load

Enter:

```text
load
```

This loads previously saved model parameters.

### Train and save

Enter:

```text
both
```

This trains the model and saves the resulting parameters.

---

# Classifying an Image

After loading or training the model, the application requests an image path:

```text
enter the directory to an image:
```

For example:

```text
./images/example.jpg
```

The image is resized to the expected `64 × 64 × 3` format and passed through the neural network.

The resulting classification probabilities are then displayed.

---

# REST API

The REST API is implemented in `server.py` using Flask and Flask-RESTful.

Start the server with:

```bash
python server.py
```

The server runs on:

```text
http://localhost:5000
```

The main endpoint is:

```text
POST /process
```

---

# API Request

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

The image must be supplied as a 3-dimensional array.

The expected format is effectively:

```text
height × width × channels
```

for example:

```text
64 × 64 × 3
```

---

# Classification Filter

The `filter` array determines which classification categories can be selected.

There are 11 output classes, so the filter contains 11 values.

For example:

```json
{
  "filter": [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
}
```

enables only the first classification category:

```text
Bread
```

A value of `0` disables a category, while a non-zero value enables it.

At least one category must be enabled.

---

# API Response

A successful request returns a classification result similar to:

```json
{
  "result": "Bread"
}
```

The API selects the highest-scoring class that is enabled by the supplied filter.

---

# API Authentication

The API uses Supabase to validate API keys and track usage.

The server accesses database tables containing API-key and user information.

The request flow is:

```text
Client
  │
  ▼
API Key
  │
  ▼
Supabase
  │
  ├── Validate key
  │
  ├── Check request quota
  │
  └── Update request count
  │
  ▼
Neural Network
  │
  ▼
Classification
```

---

# Python Client

The repository includes `client.py`, which demonstrates how to communicate with the API programmatically.

A request can be made using Python:

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

The response is returned as JSON.

---

# Supabase Integration

Supabase provides API-key management and request tracking.

The backend uses Supabase to:

- Validate API keys
- Identify users
- Track API requests
- Enforce request limits

The user information includes request counters such as:

```text
current_requests
allowed_requests
```

This allows the API to limit usage associated with individual API keys.

---

# Frontend

The frontend is implemented using **Svelte**.

The primary application page is:

```text
+page.svelte
```

The application presents **Labeled** as an image-recognition service focused on:

- Speed
- Customisation
- Ease of use

The Svelte layout also handles application-level configuration and authentication.

---

# Error Handling

The API handles several types of invalid requests.

### Missing image

```json
{
  "error": "Missing \"image\" in request body"
}
```

### Invalid image format

```json
{
  "error": "Invalid array format: ..."
}
```

### Incorrect dimensions

```json
{
  "error": "Expected 3D array, got ...D"
}
```

### Empty filter

```json
{
  "error": "must select at least 1 item"
}
```

### Invalid API key

```json
{
  "error": "invalid api key"
}
```

### Server error

```json
{
  "error": "Server error: ..."
}
```

---

# Security

API credentials should not be stored directly in source code.

Sensitive values such as Supabase credentials should be provided through environment variables.

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

If credentials have previously been committed to a public repository, they should be rotated.

---

# Project Components

| Component | Technology | Purpose |
|---|---|---|
| Neural network | Python / NumPy | Food image classification |
| Convolution | Custom implementation | Image feature extraction |
| FFT | Python / Numba | High-performance numerical processing |
| JIT compilation | Numba | Accelerated FFT computation |
| Image preprocessing | Python | Image resizing and preparation |
| Backend | Flask | REST API |
| Database | Supabase | API keys and usage tracking |
| Frontend | Svelte | Web interface |

---

# Performance

The project places particular emphasis on numerical performance through its custom FFT implementation.

The FFT implementation uses:

- Numba JIT compilation
- Precomputed bit-reversal indices
- Precomputed twiddle factors
- Cached FFT data
- Parallel/performance-oriented numerical routines

The resulting implementation is benchmarked against NumPy's FFT implementation.

The benchmark shown in `fft_comparison.png` demonstrates that the JIT-compiled implementation **outperforms NumPy for the workloads tested in the project**.

This is an important component of the project because it demonstrates how algorithms normally implemented in high-level Python can be optimized using JIT compilation and careful caching of repeated computations.

---

# Project Status

The project is an academic/course project demonstrating the integration of machine learning, numerical computing, web APIs, database services, and frontend development.

The main functionality consists of:

```text
Image
  │
  ▼
Preprocessing
  │
  ▼
Custom Neural Network
  │
  ├── Convolution
  │
  ├── FFT-based processing
  │
  └── Fully Connected Layers
  │
  ▼
Food Classification
  │
  ▼
Flask REST API
  │
  ▼
Client / Svelte Frontend
```

---

# License

No explicit license is currently documented in the repository.

---

# Repository

**GitHub:** [DrSui/final-course](https://github.com/DrSui/final-course)

The repository contains the complete implementation of the neural network, custom FFT, API, frontend, image-processing utilities, and associated project files.
