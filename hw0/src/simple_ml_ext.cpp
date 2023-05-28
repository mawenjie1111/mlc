#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
#include <iostream>

namespace py = pybind11;


void softmax_regression_epoch_cpp(const float *X, const unsigned char *y,
								  float *theta, size_t m, size_t n, size_t k,
								  float lr, size_t batch)
{
    /**
     * A C++ version of the softmax regression epoch code.  This should run a
     * single epoch over the data defined by X and y (and sizes m,n,k), and
     * modify theta in place.  Your function will probably want to allocate
     * (and then delete) some helper arrays to store the logits and gradients.
     *
     * Args:
     *     X (const float *): pointer to X data, of size m*n, stored in row
     *          major (C) format
     *     y (const unsigned char *): pointer to y data, of size m
     *     theta (float *): pointer to theta data, of size n*k, stored in row
     *          major (C) format
     *     m (size_t): number of examples
     *     n (size_t): input dimension
     *     k (size_t): number of classes
     *     lr (float): learning rate / SGD step size
     *     batch (int): SGD minibatch size
     *
     * Returns:
     *     (None)
     */

    /// BEGIN YOUR CODE

    for (size_t loop=0; loop<(m/batch);loop++){
        size_t sentry = loop*batch*n;
        float *h = new float[batch*k];
        for (size_t i = loop*batch; i<batch*(loop+1);i++){
            for (size_t j=0; j<k;j++){
                for (size_t l=0; l<n;l++){
                    h[i*k+j]+= exp(X[sentry+i*n+l]*theta[l*k+j]);
                }
            }
        }
        float *h_sum=new float[batch];
        for (size_t i = 0; i < batch; i++){
            float sum = 0;
            for(size_t j=0; j<k;j++){
                sum+=h[i*k+j];
            }
            h_sum[i]=sum;
        }
        for (size_t i = 0; i < batch; i++){
            for(size_t j=0; j<k;j++){
                h[i*k+j]/=h_sum[i];
            }
        }
        size_t *y_hat = new size_t [batch*k];
        for (size_t i = 0; i < batch; i++){
            for(size_t j=0; j<k;j++){
                y_hat[i*k+j]=(y[sentry+i]==j)?1:0;
            }
        }
        for (size_t i = 0; i < batch; i++){
            for(size_t j=0; j<k;j++){
                for(size_t l=0; l<n;l++){
                    theta[l*k+j]-=(lr*(h[i*k+j]-y_hat[i*k+j])*X[sentry+i*n+l])/batch;
                }
            }
        }
    
        

        
        
  
   
    }

    /// END YOUR CODE
}


/**
 * This is the pybind11 code that wraps the function above.  It's only role is
 * wrap the function above in a Python module, and you do not need to make any
 * edits to the code
 */
PYBIND11_MODULE(simple_ml_ext, m) {
    m.def("softmax_regression_epoch_cpp",
    	[](py::array_t<float, py::array::c_style> X,
           py::array_t<unsigned char, py::array::c_style> y,
           py::array_t<float, py::array::c_style> theta,
           float lr,
           int batch) {
        softmax_regression_epoch_cpp(
        	static_cast<const float*>(X.request().ptr),
            static_cast<const unsigned char*>(y.request().ptr),
            static_cast<float*>(theta.request().ptr),
            X.request().shape[0],
            X.request().shape[1],
            theta.request().shape[1],
            lr,
            batch
           );
    },
    py::arg("X"), py::arg("y"), py::arg("theta"),
    py::arg("lr"), py::arg("batch"));
}
