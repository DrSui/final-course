from numba import njit, int64, float64, complex128, prange, types, typed, float32
from numba.experimental import jitclass
import numpy as np
from scipy.signal import correlate2d, fftconvolve, convolve
from fft import FFTCache, fftconvolve_3d

IO_TYPE =  float64[:,:,:]
LINEAR_TYPES =  float64[:,:]
META_PARAMS_TYPE = float64
INT_TYPE = int64
HIDDEN_TYPES = [
    ('input', LINEAR_TYPES),
    ('input_pre', LINEAR_TYPES),
    ('output', LINEAR_TYPES),
    ('output_pre', LINEAR_TYPES),
    ('bias', LINEAR_TYPES),
    ('weights', LINEAR_TYPES),
    ('learn_rate', META_PARAMS_TYPE),
    ]

@jitclass(HIDDEN_TYPES)
class HiddenLayer:
    def __init__(self, height, width, learn_rate=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8, l2_lambda=0.0005) -> None:
        # Initialize weights and bias
        self.learn_rate = learn_rate
        self.weights = np.random.randn(height, width) * np.sqrt(8.0 / width)  # He initialization
        self.bias = np.random.randn(height, 1) * 0.01

    @staticmethod
    def activation(x, alpha=0.01):
        return np.where(x > 0, x, alpha * x)  # Leaky ReLU

    def derivative_activation(self, x, alpha=0.01):
        return np.where(x > 0, 1, alpha)  # Derivative of Leaky ReLU

    def forward(self, in_matrix,cache):
        self.input = in_matrix.reshape((self.weights.T.shape[0], 1))
        self.output_pre = np.ascontiguousarray(self.weights @ self.input) + self.bias
        #self.output_pre = self.normalize(self.output_pre)
        self.output = self.activation(self.output_pre)
        return self.output
    
    def backward(self, dA,cache):
        # Increment time step for Adam
        self.t += 1
        
        # Find relevant derivatives
        dZ = dA * self.derivative_activation(self.output_pre)
        dW = np.ascontiguousarray(np.dot(dZ, self.input.T))
        dB = dZ
        
        # Update parameters with Adam
        self.weights -= self.learn_rate * dW
        self.bias -= self.learn_rate * dB        
        
        # Calculate gradient for next layer
        dN = np.ascontiguousarray(np.dot(self.weights.T, dZ))
        
        return dN

OUTPUT_TYPES = [
    ('input', LINEAR_TYPES),
    ('input_pre', LINEAR_TYPES),
    ('output', LINEAR_TYPES),
    ('output_pre', LINEAR_TYPES),
    ('bias', LINEAR_TYPES),
    ('m_bias', LINEAR_TYPES),
    ('v_bias', LINEAR_TYPES),
    ('weights', LINEAR_TYPES),
    ('m_weights', LINEAR_TYPES),
    ('v_weights', LINEAR_TYPES),
    ('learn_rate', META_PARAMS_TYPE),
    ('beta1', META_PARAMS_TYPE),
    ('beta2', META_PARAMS_TYPE),
    ('epsilon', META_PARAMS_TYPE),
    ('l2_lambda', META_PARAMS_TYPE),
    ('clip_threshold', META_PARAMS_TYPE),
    ('t', INT_TYPE),
    ]
@jitclass(OUTPUT_TYPES)
class OutputLayer(): 
    def __init__(self, height, width, learn_rate=0.001, beta1=0.9, beta2=0.999, epsilon=1e-8, l2_lambda=0.01) -> None:
                # Initialize weights and bias
        self.learn_rate = learn_rate
        self.weights = np.random.randn(height, width) * np.sqrt(8.0 / width)  # He initialization
        self.bias = np.random.randn(height, 1) * 0.01
        
        # Adam optimizer parameters
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.m_weights = np.zeros_like(self.weights)
        self.v_weights = np.zeros_like(self.weights)
        self.m_bias = np.zeros_like(self.bias)
        self.v_bias = np.zeros_like(self.bias)
        self.t = 0  # Time step for Adam
        
        # L2 regularization parameter
        self.l2_lambda = l2_lambda
        
        # Gradient clipping threshold
        self.clip_threshold = 5.0
    @staticmethod 
    def activation(x, alpha=0.01):
        x = x - np.max(x)  
        exp_x = np.exp(x)
        return exp_x / np.sum(exp_x)
        
    def derivative_activation(self, x, alpha=0.01):
        # Not directly used in this implementation since we calculate
        # the gradient of softmax with cross-entropy directly

        return self.output - x
    
    def forward(self, in_matrix,cache):
        self.input = in_matrix
        self.output_pre = np.ascontiguousarray(self.weights @ in_matrix) + self.bias
        #self.output_pre = self.normalize(self.output_pre)
        self.output = self.activation(self.output_pre)
        return self.output
    
    def backward(self, dA, cache):
        
        # Direct computation of gradient for softmax with cross-entropy
        dZ = self.output - self.derivative_activation(dA)
        dW = np.ascontiguousarray(np.dot(dZ, self.input.T))
        
        # Update parameters with Adam
        self.weights -= self.learn_rate * dW
        self.bias -= self.learn_rate * dZ        
        # Calculate gradient for next layer
        dN = np.ascontiguousarray(np.dot(self.weights.T, dZ))
        
        return dN

IMG_TYPE = float32[:,:,:]
CONV_TYPES = [
    ('input', IMG_TYPE),
    ('input_pre', IO_TYPE),
    ('output', IO_TYPE),
    ('output_pre', IO_TYPE),
    ('bias', IO_TYPE),
    ('weights', IO_TYPE),
    ('input_channels', INT_TYPE),
    ('entrance_size', INT_TYPE),
    ('output_channels', INT_TYPE),
    ('kernel_size', INT_TYPE),
    ('size', INT_TYPE),
    ('padding', INT_TYPE),
    ('learn_rate', META_PARAMS_TYPE),
    ]
@jitclass(CONV_TYPES)
class ConvLayer:
    def __init__(self,
                input_channels,
                output_channels,
                kernel_size,
                size,
                padding=0, 
                learn_rate=0.001,
                ):
        self.input_channels = input_channels
        self.output_channels = output_channels
        self.kernel_size = kernel_size
        self.padding = padding
        self.learn_rate = learn_rate
        self.entrance_size = size - kernel_size + 1
        
        # Xavier initialization of weights
        self.weights = np.random.randn(input_channels, kernel_size, kernel_size) * np.sqrt(1. / (input_channels * kernel_size * kernel_size))
        self.bias = np.zeros((self.entrance_size, self.entrance_size, 1))
    
    def pad_input(self, x):
        if self.padding > 0:
            return np.pad(x, ((self.padding, self.padding), (self.padding, self.padding), (0, 0)), mode='constant')
        return x
    
    def forward(self, x,cache):
        self.input = x  # Store input for backpropagation
        #height, width, _ = x.shape
        #padded_x = self.pad_input(x)
        #output_height = (height + 2 * self.padding - self.kernel_size) // self.stride + 1
        #output_width = (width + 2 * self.padding - self.kernel_size) // self.stride + 1
        
        #output = np.zeros((output_height, output_width, self.output_channels))
        # print(padded_x.shape) 
        output = fftconvolve_3d(x, self.weights, cache, mode='valid') + self.bias
        # Apply normalization
        #output = self.normalize(output)
        
        return output
    
    def backward(self, dZ,cache):
        # Increment time step for Adam
        self.t += 1
        
        padded_input = self.input
        dZ = dZ.reshape(self.entrance_size, self.entrance_size, self.output_channels-1)
        
        # grad_weights = np.zeros_like(self.weights)
        # grad_biases = np.zeros_like(self.bias)
        
        
        grad_weights = fftconvolve_3d(padded_input, dZ, cache, mode='valid', correlate=True)
        d_padded_input = fftconvolve_3d(dZ, self.weights, cache, mode='full')
        # Add L2 regularization gradient
        
        # Update parameters with Adam
        self.weights -= self.learn_rate * grad_weights 
        self.bias -= self.learn_rate * dZ 
        
        # Clip weights to prevent extreme values
        # self.weights = self.clip_gradients(self.weights)
        self.bias = np.clip(self.bias, -1, 1)
        
        # Remove padding from d_padded_input to get d_input
        if self.padding > 0:
            d_input = d_padded_input[self.padding:-self.padding, self.padding:-self.padding, :]
        else:
            d_input = d_padded_input
        
        return d_input
