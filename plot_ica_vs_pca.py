#!/usr/bin/env python3
"""
@author:Harold
@file: plot_ica_vs_pca.py
@time: 12/09/2019
"""
"""
==========================
FastICA on 2D point clouds
==========================
This example illustrates visually in the feature space a comparison by
results using two different component analysis techniques.
:ref:`ICA` vs :ref:`PCA`.
Representing ICA in the feature space gives the view of 'geometric ICA':
ICA is an algorithm that finds directions in the feature space
corresponding to projections with high non-Gaussianity. These directions
need not be orthogonal in the original feature space, but they are
orthogonal in the whitened feature space, in which all directions
correspond to the same variance.
PCA, on the other hand, finds orthogonal directions in the raw feature
space that correspond to directions accounting for maximum variance.
Here we simulate independent sources using a highly non-Gaussian
process, 2 student T with a low number of degrees of freedom (top left
figure). We mix them to create observations (top right figure).
In this raw observation space, directions identified by PCA are
represented by orange vectors. We represent the signal in the PCA space,
after whitening by the variance corresponding to the PCA vectors (lower
left). Running ICA corresponds to finding a rotation in this space to
identify the directions of largest non-Gaussianity (lower right).
"""
print(__doc__)

# Authors: Alexandre Gramfort, Gael Varoquaux
# License: BSD 3 clause

import numpy as np
import matplotlib.pyplot as plt

from sklearn.decomposition import PCA, FastICA

# #############################################################################
# Generate sample data
rng = np.random.RandomState(42)
S = rng.standard_t(1.5, size=(2000, 2))
S[:, 0] *= 2.

# Mix data
A = np.array([[1, 1], [0, 2]])  # Mixing matrix

X = np.dot(S, A.T)  # Generate observations
print(X.shape)

u, d, _ = np.linalg.svd(X, full_matrices=False)
print(u.shape, d.shape)
print(d)
K = (u / d).T[:2]
print(K.shape)

np.savetxt("ica_data.txt", X, delimiter=" ", fmt="%1.6f")

pca = PCA()
S_pca_ = pca.fit(X).transform(X)

ica = FastICA(n_components=2, random_state=rng, algorithm='deflation')
S_ica_ = ica.fit(X).transform(X)  # Estimate the sources

S_ica_ /= S_ica_.std(axis=0)

np.savetxt("ica_pyres.txt", S_ica_, delimiter=" ", fmt="%1.6f")
print("K: ", ica.whitening_)
print("W (unmixing): ", ica.components_)
print("mixing: ", ica.mixing_)


# #############################################################################
# Plot results

def plot_samples(S, axis_list=None):
    plt.scatter(S[:, 0], S[:, 1], s=2, marker='o', zorder=10,
                color='steelblue', alpha=0.5)
    if axis_list is not None:
        colors = ['orange', 'red']
        for color, axis in zip(colors, axis_list):
            axis /= axis.std()
            x_axis, y_axis = axis
            # Trick to get legend to work
            plt.plot(0.1 * x_axis, 0.1 * y_axis, linewidth=2, color=color)
            plt.quiver(0, 0, x_axis, y_axis, zorder=11, width=0.01, scale=6,
                       color=color)

    plt.hlines(0, -3, 3)
    plt.vlines(0, -3, 3)
    plt.xlim(-3, 3)
    plt.ylim(-3, 3)
    plt.xlabel('x')
    plt.ylabel('y')


plt.figure()
plt.subplot(3, 2, 1)
plot_samples(S / S.std())
plt.title('True Independent Sources')

axis_list = [pca.components_.T, ica.mixing_]
plt.subplot(3, 2, 2)
plot_samples(X / np.std(X), axis_list=axis_list)
legend = plt.legend(['PCA', 'ICA'], loc='upper right')
legend.set_zorder(100)

plt.title('Observations')

plt.subplot(3, 2, 3)
plot_samples(S_pca_ / np.std(S_pca_, axis=0))
plt.title('PCA recovered signals')

plt.subplot(3, 2, 4)
plot_samples(S_ica_ / np.std(S_ica_))
plt.title('ICA recovered signals')

plt.subplot(3, 2, 5)
plot_samples(ica._fit(X, True))
plt.title('ICA sources')

plt.subplot(3, 2, 6)
Sss = np.genfromtxt('ica_res.txt', delimiter=' ')
plot_samples(Sss)
plt.title('My ICA sources')

plt.subplots_adjust(0.09, 0.04, 0.94, 0.94, 0.26, 0.36)
plt.show()
