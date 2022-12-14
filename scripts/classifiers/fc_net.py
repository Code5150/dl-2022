from builtins import range
from builtins import object
import numpy as np

from ..layers import *
from ..layer_utils import *


class TwoLayerNet(object):
    """
    A two-layer fully-connected neural network with ReLU nonlinearity and
    softmax loss that uses a modular layer design. We assume an input dimension
    of D, a hidden dimension of H, and perform classification over C classes.

    The architecure should be affine - relu - affine - softmax.

    Note that this class does not implement gradient descent; instead, it
    will interact with a separate Solver object that is responsible for running
    optimization.

    The learnable parameters of the model are stored in the dictionary
    self.params that maps parameter names to numpy arrays.
    """

    def __init__(
        self,
        input_dim=28 * 28,
        hidden_dim=100,
        num_classes=10,
        weight_scale=1e-3,
        reg=0.0,
    ):
        """
        Initialize a new network.

        Inputs:
        - input_dim: An integer giving the size of the input
        - hidden_dim: An integer giving the size of the hidden layer
        - num_classes: An integer giving the number of classes to classify
        - weight_scale: Scalar giving the standard deviation for random
          initialization of the weights.
        - reg: Scalar giving L2 regularization strength.
        """
        self.params = {}
        self.reg = reg

        ############################################################################
        # TODO: Initialize the weights and biases of the two-layer net. Weights    #
        # should be initialized from a Gaussian centered at 0.0 with               #
        # standard deviation equal to weight_scale, and biases should be           #
        # initialized to zero. All weights and biases should be stored in the      #
        # dictionary self.params, with first layer weights                         #
        # and biases using the keys 'W1' and 'b1' and second layer                 #
        # weights and biases using the keys 'W2' and 'b2'.                         #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        mu = 0
        sigma = weight_scale
        self.params['W1'] = mu + sigma * np.random.randn(input_dim,hidden_dim)

        self.params['b1'] = np.zeros(hidden_dim)

        self.params['W2'] = mu + sigma * np.random.randn(hidden_dim,num_classes)
        self.params['b2'] = np.zeros(num_classes)

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

    def loss(self, X, y=None):
        """
        Compute loss and gradient for a minibatch of data.

        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
          scores[i, c] is the classification score for X[i] and class c.

        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
          names to gradients of the loss with respect to those parameters.
        """
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the two-layer net, computing the    #
        # class scores for X and storing them in the scores variable.              #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        N = X.shape[0]
        D = np.prod(X.shape[1:])
        x_in = X
        x_in = x_in.reshape(N, D)
        fc1 = x_in.dot(self.params['W1']) + self.params['b1']
        relu = np.maximum(0, fc1)
        fc2 = relu.dot(self.params['W2']) + self.params['b2']
        scores = fc2

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If y is None then we are in test mode so just return scores
        if y is None:
            return scores

        loss, grads = 0, {}
        ############################################################################
        # TODO: Implement the backward pass for the two-layer net. Store the loss  #
        # in the loss variable and gradients in the grads dictionary. Compute data #
        # loss using softmax, and make sure that grads[k] holds the gradients for  #
        # self.params[k]. Don't forget to add L2 regularization!                   #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        W1, b1 = self.params['W1'], self.params['b1']
        W2, b2 = self.params['W2'], self.params['b2']

        loss, dout2 = softmax_loss(scores, y)
        loss += 0.5 * self.reg * (np.sum(W1*W1)+np.sum(W2*W2))

        cache2 = relu, W2, b2
        dx2,dw2,db2 = affine_backward(dout2, cache2)
        grads['W2'] = dw2 + self.reg * self.params['W2'] #Be careful not to forget the contribution of W1, W2 and regularization parameters in loss
        grads['b2'] = db2

        cache1 = fc1
        dout1 = dx2
        dout =  relu_backward(dout1, cache1)

        cache = X, W1, b1
        dx1,dw1,db1 = affine_backward(dout, cache)
        grads['W1'] = dw1 + self.reg * self.params['W1']
        grads['b1'] = db1

        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads


class FullyConnectedNet(object):
    """Class for a multi-layer fully connected neural network.
    Network contains an arbitrary number of hidden layers, ReLU nonlinearities,
    and a softmax loss function. This will also implement dropout and batch/layer
    normalization as options. For a network with L layers, the architecture will be
    {affine - [batch/layer norm] - relu - [dropout]} x (L - 1) - affine - softmax
    where batch/layer normalization and dropout are optional and the {...} block is
    repeated L - 1 times.
    Learnable parameters are stored in the self.params dictionary and will be learned
    using the Solver class.
    """

    def __init__(
        self,
        hidden_dims,
        input_dim=28*28,
        num_classes=10,
        dropout_keep_ratio=1,
        normalization=None,
        reg=0.0,
        weight_scale=1e-2,
        dtype=np.float32,
        seed=None,
    ):
        """Initialize a new FullyConnectedNet.
        Inputs:
        - hidden_dims: A list of integers giving the size of each hidden layer.
        - input_dim: An integer giving the size of the input.
        - num_classes: An integer giving the number of classes to classify.
        - dropout_keep_ratio: Scalar between 0 and 1 giving dropout strength.
            If dropout_keep_ratio=1 then the network should not use dropout at all.
        - normalization: What type of normalization the network should use. Valid values
            are "batchnorm", "layernorm", or None for no normalization (the default).
        - reg: Scalar giving L2 regularization strength.
        - weight_scale: Scalar giving the standard deviation for random
            initialization of the weights.
        - dtype: A numpy datatype object; all computations will be performed using
            this datatype. float32 is faster but less accurate, so you should use
            float64 for numeric gradient checking.
        - seed: If not None, then pass this random seed to the dropout layers.
            This will make the dropout layers deteriminstic so we can gradient check the model.
        """
        self.normalization = normalization
        self.use_dropout = dropout_keep_ratio != 1
        self.reg = reg
        self.num_layers = 1 + len(hidden_dims)
        self.dtype = dtype
        self.params = {}

        ############################################################################
        # TODO: Initialize the parameters of the network, storing all values in    #
        # the self.params dictionary. Store weights and biases for the first layer #
        # in W1 and b1; for the second layer use W2 and b2, etc. Weights should be #
        # initialized from a normal distribution centered at 0 with standard       #
        # deviation equal to weight_scale. Biases should be initialized to zero.   #
        #                                                                          #
        # When using batch normalization, store scale and shift parameters for the #
        # first layer in gamma1 and beta1; for the second layer use gamma2 and     #
        # beta2, etc. Scale parameters should be initialized to ones and shift     #
        # parameters should be initialized to zeros.                               #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****




        _size_list = []
        _size_list.append(input_dim)
        for i in range(len(hidden_dims)) : 
            _size_list.append(hidden_dims[i])
        _size_list.append(num_classes)
        _size_list[-1] = num_classes
        
        
        for i in range(self.num_layers) : 
            self.params['W' + str(i+1)] = np.random.normal(0.0, weight_scale, size=(_size_list[i], _size_list[i+1]))
            self.params['b' + str(i+1)] = np.zeros(_size_list[i+1])

            if self.normalization == "batchnorm":
                if i is not self.num_layers-1 : 
                    self.params['gamma' + str(i+1)] = np.ones(_size_list[i+1])
                    self.params['beta' + str(i+1)] = np.zeros(_size_list[i+1])
            
            if self.normalization == "layernorm":
                if i is not self.num_layers-1 : 
                    self.params['gamma' + str(i+1)] = np.ones(_size_list[i+1])
                    self.params['beta' + str(i+1)] = np.zeros(_size_list[i+1])


        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # When using dropout we need to pass a dropout_param dictionary to each
        # dropout layer so that the layer knows the dropout probability and the mode
        # (train / test). You can pass the same dropout_param to each dropout layer.
        self.dropout_param = {}
        if self.use_dropout:
            self.dropout_param = {"mode": "train", "p": dropout_keep_ratio}
            if seed is not None:
                self.dropout_param["seed"] = seed

        # With batch normalization we need to keep track of running means and
        # variances, so we need to pass a special bn_param object to each batch
        # normalization layer. You should pass self.bn_params[0] to the forward pass
        # of the first batch normalization layer, self.bn_params[1] to the forward
        # pass of the second batch normalization layer, etc.
        self.bn_params = []
        if self.normalization == "batchnorm":
            self.bn_params = [{"mode": "train"} for i in range(self.num_layers - 1)]
        if self.normalization == "layernorm":
            self.bn_params = [{} for i in range(self.num_layers - 1)]

        # Cast all parameters to the correct datatype.
        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)

    def loss(self, X, y=None):
        """Compute loss and gradient for the fully connected net.
        
        Inputs:
        - X: Array of input data of shape (N, d_1, ..., d_k)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].
        Returns:
        If y is None, then run a test-time forward pass of the model and return:
        - scores: Array of shape (N, C) giving classification scores, where
            scores[i, c] is the classification score for X[i] and class c.
        If y is not None, then run a training-time forward and backward pass and
        return a tuple of:
        - loss: Scalar value giving the loss
        - grads: Dictionary with the same keys as self.params, mapping parameter
            names to gradients of the loss with respect to those parameters.
        """
        X = X.astype(self.dtype)
        mode = "test" if y is None else "train"

        # Set train/test mode for batchnorm params and dropout param since they
        # behave differently during training and testing.
        if self.use_dropout:
            self.dropout_param["mode"] = mode
        if self.normalization == "batchnorm":
            for bn_param in self.bn_params:
                bn_param["mode"] = mode
        scores = None
        ############################################################################
        # TODO: Implement the forward pass for the fully connected net, computing  #
        # the class scores for X and storing them in the scores variable.          #
        #                                                                          #
        # When using dropout, you'll need to pass self.dropout_param to each       #
        # dropout forward pass.                                                    #
        #                                                                          #
        # When using batch normalization, you'll need to pass self.bn_params[0] to #
        # the forward pass for the first batch normalization layer, pass           #
        # self.bn_params[1] to the forward pass for the second batch normalization #
        # layer, etc.                                                              #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        in_i = X
        aff_out = []
        aff_cache = []
        if self.normalization == "batchnorm":
            bn_out = []
            bn_cache = []
        if self.normalization == "layernorm":
            ln_out = []
            ln_cache = []
        relu_out = []
        relu_cache = []
        if self.use_dropout:
            do_out = []
            do_cache = []
        
        for i in range(self.num_layers):  
          
          if i is self.num_layers-1 : 
            out_i, cache_i = affine_forward( in_i, self.params['W'+str(i+1)], self.params['b'+str(i+1)] )
            aff_out.append(out_i) 
            aff_cache.append(cache_i)

          
          else:
            out_i, cache_i = affine_forward( in_i, self.params['W'+str(i+1)], self.params['b'+str(i+1)] )
            aff_out.append(out_i) 
            aff_cache.append(cache_i)

            if self.normalization == "batchnorm":
                out_i, cache_i = batchnorm_forward(out_i, self.params['gamma'+str(i+1)], self.params['beta'+str(i+1)], self.bn_params[i])
                bn_out.append(out_i)
                bn_cache.append(cache_i)
            
            if self.normalization == "layernorm":
                out_i, cache_i = layernorm_forward(out_i, self.params['gamma'+str(i+1)], self.params['beta'+str(i+1)], self.bn_params[i])
                ln_out.append(out_i)
                ln_cache.append(cache_i)

            out_i, cache_i = relu_forward(out_i)
            relu_out.append(out_i)
            relu_cache.append(cache_i)
            
            if self.use_dropout:
                out_i, cache_i = dropout_forward(out_i, self.dropout_param)
                do_out.append(out_i)
                do_cache.append(cache_i)
                    
          
          in_i = out_i

        scores = aff_out[-1] 

                # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        # If test mode return early.
        if mode == "test":
            return scores

        loss, grads = 0.0, {}
        ############################################################################
        # TODO: Implement the backward pass for the fully connected net. Store the #
        # loss in the loss variable and gradients in the grads dictionary. Compute #
        # data loss using softmax, and make sure that grads[k] holds the gradients #
        # for self.params[k]. Don't forget to add L2 regularization!               #
        #                                                                          #
        # When using batch/layer normalization, you don't need to regularize the   #
        # scale and shift parameters.                                              #
        #                                                                          #
        # NOTE: To ensure that your implementation matches ours and you pass the   #
        # automated tests, make sure that your L2 regularization includes a factor #
        # of 0.5 to simplify the expression for the gradient.                      #
        ############################################################################
        # *****START OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****

        loss, dscores = softmax_loss(scores, y)
        for i in range(self.num_layers):
            loss += 0.5 * self.reg * np.sum(self.params['W'+str(i+1)]**2)

        dout, grads['W'+str(self.num_layers)], grads['b'+str(self.num_layers)] = affine_backward(dscores, aff_cache[-1])
        
        for i in reversed(range(self.num_layers-1)) : 
          
          if self.use_dropout:
                dout = dropout_backward(dout, do_cache[i])

          
          dout = relu_backward(dout, relu_cache[i])
          
          if self.normalization == "batchnorm":
                dout, grads['gamma'+str(i+1)], grads['beta'+str(i+1)] = batchnorm_backward_alt(dout, bn_cache[i])
          
          if self.normalization == "layernorm":
                dout, grads['gamma'+str(i+1)], grads['beta'+str(i+1)] = layernorm_backward(dout, ln_cache[i])

          
          dout, grads['W'+str(i+1)], grads['b'+str(i+1)] = affine_backward(dout, aff_cache[i])


        for i in range(self.num_layers) :
            grads['W'+str(i+1)] += self.reg * self.params['W'+str(i+1)]
        
        # *****END OF YOUR CODE (DO NOT DELETE/MODIFY THIS LINE)*****
        ############################################################################
        #                             END OF YOUR CODE                             #
        ############################################################################

        return loss, grads    