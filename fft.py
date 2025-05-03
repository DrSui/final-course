import numpy as np
import numba as nb
from numba import njit, int64, complex128, prange, types, typed, vectorize
import time
import matplotlib.pyplot as plt
from scipy.signal import fftconvolve as scipy_fftconvolve

#initialise the strict types for numba
BR_TYPE = types.DictType(int64, types.int64[:])
TWIDDLE_TYPE = types.DictType(int64, types.ListType(complex128[:]))

@nb.experimental.jitclass([
    ('br_indices', BR_TYPE),
    ('twiddle_factors', TWIDDLE_TYPE)
    ])#pyright: ignore
class FFTCache:
    def __init__(self):
        self.br_indices = typed.Dict.empty(int64, types.int64[:])
        self.twiddle_factors = typed.Dict.empty(int64, types.ListType(complex128[:]))

    def get_br(self, N):
        key = hash(N)  # use builtin hash for caching
        if key not in self.br_indices:
            self.br_indices[key] = compute_bit_reversal(N)
        return self.br_indices[key]

    def get_twiddles(self, N):
        key = hash(N)  # use builtin hash for caching
        if key not in self.twiddle_factors:
            self.twiddle_factors[key] = precompute_twiddles(N)
        return self.twiddle_factors[key]

# @njit(nogil=True, fastmath=True, inline='always')
@vectorize()
def next_pow2(n):
    return 1 << int(np.ceil(np.log2(n)))

@njit(nogil=True, fastmath=True)
def compute_bit_reversal(N):
    logN = int(np.log2(N))
    br = np.empty(N, dtype=int64)
    for i in range(N):
        rev = 0
        temp = i
        for _ in range(logN):
            rev = (rev << 1) | (temp & 1)
            temp >>= 1
        br[i] = rev
    return br

@njit(nogil=True, fastmath=True, inline="always")
def precompute_twiddles(N):
    twiddles = typed.List.empty_list(complex128[:])
    current_N = 2
    while current_N <= N:
        angle = -2j * np.pi / current_N
        W = np.exp(angle * np.arange(current_N//2))
        twiddles.append(W)
        current_N *= 2
    return twiddles

@njit(nogil=True, fastmath=True)
def fft_1d(x, br, twiddles):
    X = x[br].copy()
    N = X.shape[0]
    for twiddle in twiddles:
        half = len(twiddle)
        step = 2 * half
        for k in range(0, N, step):
            for j in range(half):
                idx = k + j
                even = X[idx]
                odd = twiddle[j] * X[idx + half]
                X[idx] = even + odd
                X[idx + half] = even - odd
    return X

@njit(nogil=True, fastmath=True, parallel=True)
def fft_3d_inplace(buf, cache):
    N = buf.shape[0]
    M = buf.shape[1]
    P = buf.shape[2]
    
    # X-axis FFT (axis 0)
    br_N = cache.get_br(N)
    twiddles_N = cache.get_twiddles(N)
    for i in prange(M):
        for j in range(P):
            buf[:, i, j] = fft_1d(buf[:, i, j], br_N, twiddles_N)
    
    # Y-axis FFT (axis 1)
    br_M = cache.get_br(M)
    twiddles_M = cache.get_twiddles(M)
    buf_T = np.ascontiguousarray(buf.transpose(1, 0, 2))
    for i in prange(N):
        for j in range(P):
            buf_T[:, i, j] = fft_1d(buf_T[:, i, j], br_M, twiddles_M)
    buf = np.ascontiguousarray(buf_T.transpose(1, 0, 2))
    
    # Z-axis FFT (axis 2)
    br_P = cache.get_br(P)
    twiddles_P = cache.get_twiddles(P)
    for i in prange(N):
        for j in range(M):
            buf[i, j, :] = fft_1d(buf[i, j, :], br_P, twiddles_P)
    
    return buf
@njit(nogil=True, fastmath=True, parallel=True, inline="always")
def fftconvolve_3d(a, b, cache, mode="valid", correlate=False):
    # Output shape
    out_shape = (
        a.shape[0] + b.shape[0] - 1,
        a.shape[1] + b.shape[1] - 1,
        a.shape[2] + b.shape[2] - 1
    )
    
    # Pad to next power-of-two dimensions
    pad_shape = (
        next_pow2(out_shape[0]),
        next_pow2(out_shape[1]),
        next_pow2(out_shape[2])
    )
    
    # Allocate and populate padded arrays
    a_pad = np.zeros(pad_shape, dtype=np.complex128)
    b_pad = np.zeros(pad_shape, dtype=np.complex128)
    a_pad[:a.shape[0], :a.shape[1], :a.shape[2]] = a
    b_pad[:b.shape[0], :b.shape[1], :b.shape[2]] = b
    
    # FFT transforms
    fft_a = fft_3d_inplace(a_pad, cache)
    fft_b = fft_3d_inplace(b_pad, cache)
    # Multiply in Fourier space & perform inverse FFT
    if correlate==True:
        fft_b = fft_b.conj()
    fft_prod = fft_a * fft_b
    inv_fft = fft_3d_inplace(fft_prod.conj(), cache).conj()
    inv_fft /= np.prod(np.array(pad_shape, dtype=np.float64))
    if mode == "valid":
        valid_shape = (
            a.shape[0] - b.shape[0] + 1,
            a.shape[1] - b.shape[1] + 1,
            a.shape[2] - b.shape[2] + 1
        )
        # Check if any dimension is non-positive
        '''
            was a bug where <= instead of < caused a logical error in main.py for second conv layer
        '''
        if valid_shape[0] < 0 or valid_shape[1] < 0 or valid_shape[2] < 0:
            return np.zeros((0, 0, 0), dtype=np.float64)
        
        # Compute start indices
        start_0 = b.shape[0] - 1
        start_1 = b.shape[1] - 1
        start_2 = b.shape[2] - 1
        
        # Extract valid region
        output = inv_fft[
            start_0 : start_0 + valid_shape[0],
            start_1 : start_1 + valid_shape[1],
            start_2 : start_2 + valid_shape[2]
        ].real
    elif mode == "full": 
        output = inv_fft[:out_shape[0], :out_shape[1], :out_shape[2]].real 
    else:
        output = np.zeros((0,0,0))

    return output

def benchmark(sizes, repeats=3):
    custom_times = []
    scipy_times = []
    cache = FFTCache()  # Shared cache instance
    p = np.random.randn(64*64*64).reshape(64,64,64)
    a = np.random.rand(62, 62, 1)
    b = np.random.rand(2,2,2)
    fftconvolve_3d(p,a,cache)
    out_shape = (
        a.shape[0] + b.shape[0] - 1,
        a.shape[1] + b.shape[1] - 1,
        a.shape[2] + b.shape[2] - 1
    )
    
    # Pad to next power-of-two dimensions
    pad_shape = (
        next_pow2(out_shape[0]),
        next_pow2(out_shape[1]),
        next_pow2(out_shape[2])
    )
    #print(pad_shape)
    for i in range(10):
        t = fftconvolve_3d(a,b,cache, correlate=False, mode="valid")
    for N in sizes:
        print(f"Testing size {N}x{N}x{N}")
        a = np.random.rand(N, N, N)
        b = np.random.rand(N//2, N//2, N//2)
        
        # Custom FFTConvolve timing
        t_total = 0.0
        for _ in range(repeats):
            start = time.time()
            t1 = fftconvolve_3d(a, b, cache)
            t_total += time.time() - start
        custom_times.append(t_total / repeats)
        
        # SciPy FFTConvolve timing
        t_total = 0.0
        for _ in range(repeats):
            start = time.time()
            t2 = scipy_fftconvolve(a, b, mode='valid')
            t_total += time.time() - start
        scipy_times.append(t_total / repeats)
        assert np.allclose(t1,t2,atol=1e-6)
        print(np.max(np.subtract(t1,t2)))
    return custom_times, scipy_times

def plot_results(sizes, custom_times, scipy_times):
    print(custom_times)
    print(scipy_times)
    plt.figure(figsize=(10, 6))
    plt.plot(sizes, custom_times, marker='o', label='Custom FFTConvolve')
    plt.plot(sizes, scipy_times, marker='s', label='SciPy FFTConvolve')
    plt.xlabel('Input Size (N x N x N)')
    plt.ylabel('Time (seconds)')
    plt.title('3D Convolution Benchmark')
    plt.legend()
    plt.grid(True)
    plt.show()

# Example usage
if __name__ == "__main__":
    sizes = [16, 32, 48]  # Smaller sizes for quick testing
    custom_times, scipy_times = benchmark(sizes, repeats=5)
    plot_results(sizes, custom_times, scipy_times)



