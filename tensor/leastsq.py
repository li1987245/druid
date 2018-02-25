# coding=utf-8
##最小二乘法
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
import tensorflow as tf

default_encoding = 'utf-8'


# f = lambda x: x ** 3 + np.power(1.1, x) + 10
#
#
# def generate_data():
#     X = np.arange(0, 100, 5)
#     y = f(X)
#     return X, y
#
#
# X, y = generate_data()
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4)

# tensorflow

#2行50列数据
X = np.random.randn(2, 50)
x, y = X

#构建 50行，2列的数组，第一列都是1
x_with_bias = np.array([(1., a) for a in x]).astype(np.float32)
#print(x_with_bias.shape)# (50,2) 行数和列数

losses = []
training_steps = 50
learning_rate = 0.002

with tf.Session() as sess:
    # Set up all the tensors, variables, and operations.
    input = tf.constant(x_with_bias)

    #矩阵转置 一行50列，变成50行1列
    target = tf.constant(np.transpose([y]).astype(np.float32))

    # an interface that takes a tuple as the first argument
    #2行1列
    #tf.random_normal(shape, mean=0.0, stddev=1.0, dtype=tf.float32, seed=None, name=None)
    weights = tf.Variable(tf.random_normal([2, 1], 0, 0.1))


    tf.global_variables_initializer().run()

    '''
    #tf.matmul(a, b, transpose_a=False, transpose_b=False, a_is_sparse=False, b_is_sparse=False, name=None)

    # 2-D tensor `a`
    a = tf.constant([1, 2, 3, 4, 5, 6], shape=[2, 3])
    # [[1. 2. 3.]
    # [4. 5. 6.]]

    # 2-D tensor `b`
    b = tf.constant([7, 8, 9, 10, 11, 12], shape=[3, 2])
    # [[7. 8.]
    # [9. 10.]
    # [11. 12.]]
    c = tf.matmul(a, b) 
    # [[58 64]
    #  [139 154]]
    '''
    yhat = tf.matmul(input, weights)

    #减法  tf.subtract(10, 4) # 6
    yerror = tf.subtract(yhat, target)


    '''  
    tf.nn.l2_loss(t, name=None)

    L2 Loss.

    Computes half the L2 norm of a tensor without the sqrt:

    output = sum(t ** 2) / 2
    Args:

    t: A Tensor. Must be one of the following types: float32, float64, int64, int32, uint8, int16, int8, complex64, qint8, quint8, qint32. Typically 2-D, but may have any dimensions.
    name: A name for the operation (optional).
    Returns:

    A Tensor. Has the same type as t. 0-D.
    '''

    loss = tf.nn.l2_loss(yerror)

    #梯度下降法 梯度下降法是求解最小二乘问题的一种迭代法
    update_weights = tf.train.GradientDescentOptimizer(learning_rate).minimize(loss)

    for _ in range(training_steps):
        # Repeatedly run the operations, updating the TensorFlow variable.
        update_weights.run()
        losses.append(loss.eval())

    # Training is done, get the final values for the graphs
    betas = weights.eval()
    yhat = yhat.eval()

    #print(weights.shape);
    #print(weights.eval());

# Show the fit and the loss over time.
fig, (ax1, ax2) = plt.subplots(1, 2)
plt.subplots_adjust(wspace=.3)
fig.set_size_inches(10, 4)
ax1.scatter(x, y, alpha=.7)
ax1.scatter(x, np.transpose(yhat)[0], c="g", alpha=.6)
line_x_range = (-4, 6)
ax1.plot(line_x_range, [betas[0] + a * betas[1] for a in line_x_range], "g", alpha=0.6)
ax2.plot(range(0, training_steps), losses)
ax2.set_ylabel("Loss")
ax2.set_xlabel("Training steps")
plt.show()
