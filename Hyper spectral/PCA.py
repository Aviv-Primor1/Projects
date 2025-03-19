############################################################################################################
# All right reserved by BGU, 2023
# Author: Arad Gast, Ido Levokovich
# Date: 03/2023
# Description: This file contains the PCA function

#############################################################################################################

import numpy as np
from local_mean_covariance import get_m8, get_cov8
from legends import *

def get_pca(data, mean=None, cov=None):
    """This function calculates the PCA of the data cube to create un-correlated bands
    :param data: the data cube
    :param mean: the mean of the data cube, if None, the function will calculate it
    :param cov: the covariance of the data cube, if None, the function will calculate it
    :return: the PCA of the data cube, eigvec, eigval
    """

    # Get the shape of the cube
    row, col, bands = data.shape
    cube = np.zeros(shape=(row, col, bands), dtype=PRECISION)

    # If mean is not provided, calculate it
    if mean is None:
        mean = get_m8(data)

    # If covariance is not provided, calculate it
    if cov is None:
        cov = get_cov8(data, mean)

    # Perform PCA on the cropped data
    cropped_data = data - mean  # Remove broadcasting reshape
    eigval, eigvec = np.linalg.eig(cov)

    scale_eigvec = np.matmul(np.linalg.inv(np.diag(np.sqrt(eigval))), eigvec.T, dtype=PRECISION)
    upscale_eigvec = np.matmul(np.diag(np.sqrt(eigval)), eigvec.T, dtype=PRECISION)

    # Project the cropped data
    for r in range(row):
        for c in range(col):
            cube[r, c, :] = np.matmul(scale_eigvec, cropped_data[r, c, :], dtype=PRECISION)

    return cube, eigvec, eigval


if __name__ == "__main__":
    pass