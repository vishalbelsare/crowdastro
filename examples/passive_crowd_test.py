import logging
import os.path
import sys

import matplotlib.pyplot as plt
import numpy
import sklearn.datasets

sys.path.insert(1, os.path.join('..', 'crowdastro', 'active_learning'))
import passive_crowd

lr_init = False
skip_zeros = False

n_annotators, n_dim, n_samples = 20, 2, 50
x, z = sklearn.datasets.make_classification(
        n_samples=n_samples,
        n_features=n_dim,
        n_informative=n_dim,
        n_redundant=0,
        random_state=100)
z = z.reshape((-1, 1))
y = z.repeat(n_annotators, axis=1).T
if True:
    # Annotator 1 is good, but only if y[0] > 0.
    y[0, y[:, 0] <= 0] = numpy.round(
            numpy.random.uniform(size=((y[:, 0] <= 0).sum(),)))
    # Annotator 2 is wrong 10% of the time.
    indices = numpy.arange(n_samples)
    numpy.random.shuffle(indices)
    indices = indices[:n_samples // 10]
    indices.sort()
    y[1, indices] = 1 - y[1, indices]
    # Annotator 3 is good, but only if x[0] > 0.
    y[2, x[:, 0] <= 0] = numpy.round(
            numpy.random.uniform(size=((x[:, 0] <= 0).sum(),)))
    # ALl other annotators are wrong 50% of the time.
    for annotator in range(3, n_annotators):
        indices = numpy.arange(n_samples)
        numpy.random.shuffle(indices)
        indices = indices[:n_samples * 3 // 10]
        indices.sort()
        y[annotator, indices] = 1 - y[annotator, indices]
assert y.shape == (n_annotators, n_samples)

logging.root.setLevel(logging.DEBUG)
logging.captureWarnings(True)
a, b, w, g = passive_crowd.train(x, y, lr_init=lr_init, skip_zeros=False)
print('w:', w)
print('g:', g)
predictions = passive_crowd.predict(a, b, x)
plt.subplot(2, 3, 1)
plt.title('Groundtruth')
plt.scatter(x[z.ravel() == 0, 0], x[z.ravel() == 0, 1], c='blue', marker='x')
plt.scatter(x[z.ravel() == 1, 0], x[z.ravel() == 1, 1], c='red', marker='x')
for t in range(4):
    if t >= 2:
        plt.subplot(2, 3, 2 + t + 1)
    else:
        plt.subplot(2, 3, 2 + t)
    plt.title('Annotator {}'.format(t + 1))
    plt.scatter(x[y[t] == 0, 0], x[y[t] == 0, 1], c='blue', marker='x')
    plt.scatter(x[y[t] == 1, 0], x[y[t] == 1, 1], c='red', marker='x')
plt.subplot(2, 3, 4)
plt.title('Predictions')
plt.scatter(x[predictions.ravel() == 0, 0], x[predictions.ravel() == 0, 1], c='blue', marker='x')
plt.scatter(x[predictions.ravel() == 1, 0], x[predictions.ravel() == 1, 1], c='red', marker='x')
plt.show()
