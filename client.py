import requests
import numpy as np

# Generate test data
np.random.seed(1)
image_array_3d = np.random.rand(64, 64, 3).tolist()
filter = [1 for _ in range(11)]
filter[10] = 0
response = requests.post(
    'http://localhost:5000/process',
    json={'image': image_array_3d, "api-key":"843368a7-cc2e-427e-93fe-dbd036a518e8", "filter":filter}
)

if response.status_code == 200:
    result = response.json()
    processed_array = np.array(result['result'])
    print(processed_array)
else:
    print(f"Error {response.status_code}: {response.json()['error']}")
