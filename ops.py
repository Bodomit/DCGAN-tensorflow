import math
import numpy as np 
import tensorflow as tf

from tensorflow.python.framework import ops

from utils import *

class batch_norm(object):
    def __init__(self, epsilon=1e-5, momentum = 0.1, name="batch_norm"):
        with tf.variable_scope(name) as scope:
            self.epsilon = epsilon
            self.momentum = momentum

            self.ema = tf.train.ExponentialMovingAverage(decay=1-self.momentum)

            self.gamma = None
            self.beta = None

            self.scope = scope

    def __call__(self, x, train=True):
        self.mean, self.variance = tf.nn.moments(x, [0, 1, 2])

        if train:
            self.gamma = tf.get_variable(x.get_shape(),
                                         initializer=tf.random_normal_initializer(1., 0.02))
            self.beta = tf.get_variable(x.get_shape(),
                                        initializer=tf.constant_initializer(0.))
            return tf.nn.batch_norm_with_global_normalization(x, self.mean, self.variance,
                                                              self.beta, self.gamma,
                                                              self.epsilon, True,
                                                              self.scope)
        else:
            mean = self.ema_trainer.average(self.mean)
            variance = self.ema_trainer.average(self.variance)

            return tf.nn.batch_norm_with_global_normalization(x, self.mean, self.variance,
                                                              self.beta, self.gamma,
                                                              self.epsilon, True,
                                                              self.scope)

def binary_cross_entropy_with_logits(logits, targets, name=None):
    """Computes binary cross entropy given `logits`.

    For brevity, let `x = logits`, `z = targets`.  The logistic loss is

        loss(x, z) = - sum_i (x[i] * log(z[i]) + (1 - x[i]) * log(1 - z[i]))

    Args:
        logits: A `Tensor` of type `float32` or `float64`.
        targets: A `Tensor` of the same type and shape as `logits`.
    """
    eps = 1e-12
    with ops.op_scope([logits, targets], name, "bce_loss") as name:
        logits = ops.convert_to_tensor(logits, name="logits")
        targets = ops.convert_to_tensor(targets, name="targets")
        return -tf.reduce_mean(logits * tf.log(targets + eps) +
                               (1. - logits) * tf.log(1. - targets + eps))

def conv_cond_concat(x, y):
    """Concatenate conditioning vector on feature map axis.
    """
    x_shapes = x.get_shape()
    y_shapes = y.get_shape()
    return tf.concat(3, [x, y*tf.ones([x_shapes[0], x_shapes[1], x_shapes[2], y_shapes[3]])])

def conv2d(input_, output_dim, 
           k_h=5, k_w=5, d_h=2, d_w=2, stddev=0.02,
           name="conv2d"):
    with tf.variable_scope(name):
        w = tf.get_variable('w', [k_h, k_w, output_dim, input_.get_shape()[-1]],
                            initializer=tf.truncated_normal_initializer(stddev=stddev))
        conv = tf.nn.conv2d(input_, w, strides=[1, d_h, d_w, 1], padding='SAME')
        return conv

def deconv2d(input_, output_shape,
             k_h=5, k_w=5, d_h=2, d_w=2, stddev=0.02,
             name="deconv2d"):
    with tf.variable_scope(name):
        # filter : [height, width, output_channels, in_channels]
        w = tf.get_variable('w', [k_h, k_h, output_shape[-1], input_.get_shape()[-1]],
                            initializer=tf.random_normal_initializer(stddev=stddev))
        return tf.nn.deconv2d(input_, w, output_shape=output_shape,
                              strides=[1, d_h, d_w, 1])

def lrelu(x, leak=0.2, name="lrelu"):
    with tf.variable_scope(name):
        f1 = 0.5 * (1 + leak)
        f2 = 0.5 * (1 - leak)
        return f1 * x + f2 * abs(x)

def linear(input_, output_size, stddev=0.02, scope=None):
    """Linear map: sum_i(args[i] * W[i]), where W[i] is a variable.

    Args:
        args: a 2D Tensor or a list of 2D, batch x n, Tensors.
        output_size: int, second dimension of W[i].
        scope: VariableScope for the created subgraph; defaults to "Linear".

    Returns:
        A 2D Tensor with shape [batch x output_size] equal to
        sum_i(args[i] * W[i]), where W[i]s are newly created matrices.

    Raises:
        ValueError: if some of the arguments has unspecified or wrong shape.
    """
    shape = input_.get_shape().as_list()

    # Now the computation.
    with tf.variable_scope(scope or "Linear"):
        matrix = tf.get_variable("Matrix", [shape[1], output_size],
                                 tf.random_normal_initializer(stddev=stddev))
        if len(args) == 1:
            res = tf.matmul(args[0], matrix)
        else:
            res = tf.matmul(array_ops.concat(1, args), matrix)
        return res