import numpy as np


def rebin(a, new_shape, bintype):
    if bintype == "sum":
        return rebin_sum(a, new_shape)
    elif bintype == "avg":
        return rebin_avg(a, new_shape)
    elif bintype == "max":
        return rebin_max(a, new_shape)
    elif bintype == "majority":
        return rebin_majority(a, new_shape)


def rebin_sum(a, new_shape):
    """
    Resizes a 2d array by summing or repeating elements,
    new dimensions must be integral factors of original dimensions

    Parameters
    ----------
    a : array_like
        Input array.
    new_shape : tuple of int
        Shape of the output array

    Returns
    -------
    rebinned_array : ndarray
        If the new shape is smaller of the input array, the data are summed,
        if the new shape is bigger array elements are repeated
    """

    M, N = a.shape
    m, n = new_shape
    if m < M:
        return a.reshape((m, M / m, n, N / n)).sum(3).sum(1)
    else:
        return np.repeat(np.repeat(a, m / M, axis=0), n / N, axis=1)


def rebin_avg(a, new_shape):
    M, N = a.shape
    m, n = new_shape
    if m < M:
        result = a.reshape((m, M / m, n, N / n))
        result = np.nanmean(result,3)
        result = np.nanmean(result,1)
        return result
    else:
        return np.repeat(np.repeat(a, m / M, axis=0), n / N, axis=1)


def rebin_max(a, new_shape):
    M, N = a.shape
    m, n = new_shape
    if m < M:
        return a.reshape((m, M / m, n, N / n)).max(3).max(1)
    else:
        return np.repeat(np.repeat(a, m / M, axis=0), n / N, axis=1)


def rebin_majority(a, new_shape):
    M, N = a.shape
    m, n = new_shape
    if m < M:
        result = np.empty(new_shape)
        for cols in xrange(0, m):
            for rows in xrange(0, n):
                # chop into blocks of the new size and calculate majority per block
                block = a[M / m * cols:M / m * (cols + 1), M / m * rows:M / m * (rows + 1)]
                result[cols, rows] = np.argmax(np.bincount(block.ravel()))
        return result
    else:
        return np.repeat(np.repeat(a, m / M, axis=0), n / N, axis=1)
