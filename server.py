from flask import Flask, request
from flask_restful import Api, Resource
from numba import float32
import numpy as np


from supabase import create_client, Client
from main import NeuralNetwork

supaKey: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZrbHRlc2hna2VmZnB1ZWJmZ3R4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDM3NjY3NTEsImV4cCI6MjA1OTM0Mjc1MX0.BhSwhtkS80lyUA5tQivk6J9gwaqA8qMyOCSDAPdLzpI";
supaUrl: str  = "https://fklteshgkeffpuebfgtx.supabase.co";
supabase: Client = create_client(supaUrl,supaKey)
app = Flask(__name__)
api = Api(app)

# cache = FFTCache()
# warmup = np.random.rand(4,4,4) + 1j*np.random.rand(4,4,4)
# _ = radix4_fft_3d(warmup,cache)

neural_net = NeuralNetwork(200, 0.005, 64, 3)

class ArrayProcessor(Resource):
    def post(self):
        """Process 3D array endpoint"""
        try:
            data = request.get_json()
            key = data["api-key"]
            filter = data["filter"]
            try:
                key_data = supabase.table("keys").select("*").eq("key", key).execute().data[0]
                print(key_data)
                uid = key_data["id"]
                key_requests = key_data["uses"]
                req_data = supabase.table("users").select("current_requests, allowed_requests").eq("id",uid).execute().data
                current_req = req_data[0]["current_requests"]
                max_req = req_data[0]["allowed_requests"]
                
                if current_req < max_req:
                    current_req += 1
                    key_requests += 1
                    supabase.table("users").update({"current_requests":current_req}).eq("id",uid).execute()
                    supabase.table("keys").update({"uses":key_requests}).eq("key",key).execute()
                else:
                    raise ValueError # raise some error to trigger except
            except:
                return {"error": "invalid api key"}, 401
            # Validate input exists
            if 'image' not in data:
                return {'error': 'Missing "image" in request body'}, 400
                
            # Convert to numpy array
            try:
                np_array = np.float32(np.array(data['image']))
            except ValueError as e:
                return {'error': f'Invalid array format: {str(e)}'}, 400
                
            # Validate dimensions
            if np_array.ndim != 3:
                return {'error': f'Expected 3D array, got {np_array.ndim}D'}, 400
            full_filter = [0 for _ in range(len(filter))]
            if filter == full_filter:
                return {'error': "must select at least 1 item"}, 400
            # Process array
            # result = radix4_fft_3d(np_array,cache).real
            result = np.arange(11,1)
            result = neural_net.forward(np_array)
            result_value = 0
            print(np.argmax(result))
            print(filter[np.argmax(result)])
            for i in range(len(result)):
                max_index = np.argmax(result)
                if filter[max_index] != 0: # check that current max isn't in filter
                    result_value = neural_net.output_array[max_index] # if not in filter then set result to be the label at that value
                    break
                else:
                    result[max_index] = 0 # set the maximum value to be 0 so that a new one is picked

            # Return response
            return {
                'result': result_value,
            }, 200
            
        except Exception as e:
            return {'error': f'Server error: {str(e)}'}, 500

api.add_resource(ArrayProcessor, '/process')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
