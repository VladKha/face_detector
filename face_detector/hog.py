import numpy as np


def _normalize_block(block):
    """
    Block normalization using L2-norm
    """
    eps = 1e-5
    return block / np.sqrt(np.sum(block ** 2) + eps ** 2)


def _cell_hog(magnitude, orientation,
              orientation_start, orientation_end,
              cell_columns, cell_rows,
              column_index, row_index,
              size_columns, size_rows,
              range_rows_start, range_rows_stop,
              range_columns_start, range_columns_stop):
    """Calculation of the cell's HOG value
    Parameters
    ----------
    magnitude : ndarray
        The gradient magnitudes of the pixels.
    orientation : ndarray
        Lookup table for orientations.
    orientation_start : float
        Orientation range start.
    orientation_end : float
        Orientation range end.
    cell_columns : int
        Pixels per cell (rows).
    cell_rows : int
        Pixels per cell (columns).
    column_index : int
        Block column index.
    row_index : int
        Block row index.
    size_columns : int
        Number of columns.
    size_rows : int
        Number of rows.
    range_rows_start : int
        Start row of cell.
    range_rows_stop : int
        Stop row of cell.
    range_columns_start : int
        Start column of cell.
    range_columns_stop : int
        Stop column of cell
    Returns
    -------
    total : float
        The total HOG value.
    """
    total = 0.

    for cell_row in range(range_rows_start, range_rows_stop):
        cell_row_index = row_index + cell_row
        if cell_row_index < 0 or cell_row_index >= size_rows:
            continue

        for cell_column in range(range_columns_start, range_columns_stop):
            cell_column_index = column_index + cell_column
            if (cell_column_index < 0 or cell_column_index >= size_columns
                or orientation[cell_row_index, cell_column_index]
                    >= orientation_start
                or orientation[cell_row_index, cell_column_index]
                    < orientation_end):
                continue

            total += magnitude[cell_row_index, cell_column_index]

    return total / (cell_rows * cell_columns)


def _hog_histograms(gradient_columns,
                    gradient_rows,
                    cell_columns, cell_rows,
                    size_columns, size_rows,
                    number_of_cells_columns, number_of_cells_rows,
                    number_of_orientations,
                    orientation_histogram):
    """Extract Histogram of Oriented Gradients (HOG) for a given image.
    Parameters
    ----------
    gradient_columns : ndarray
        First order image gradients (rows).
    gradient_rows : ndarray
        First order image gradients (columns).
    cell_columns : int
        Pixels per cell (rows).
    cell_rows : int
        Pixels per cell (columns).
    size_columns : int
        Number of columns.
    size_rows : int
        Number of rows.
    number_of_cells_columns : int
        Number of cells (rows).
    number_of_cells_rows : int
        Number of cells (columns).
    number_of_orientations : int
        Number of orientation bins.
    orientation_histogram : ndarray
        The histogram array which is modified in place.
    """

    magnitude = np.sqrt(gradient_columns ** 2 + gradient_rows ** 2)
    orientation = np.rad2deg(np.arctan2(gradient_rows, gradient_columns)) % 180

    y0 = cell_rows // 2
    x0 = cell_columns // 2
    cc = cell_rows * number_of_cells_rows
    cr = cell_columns * number_of_cells_columns
    range_rows_stop = cell_rows // 2
    range_rows_start = -range_rows_stop
    range_columns_stop = cell_columns // 2
    range_columns_start = -range_columns_stop
    number_of_orientations_per_180 = 180 / number_of_orientations

    # compute orientations integral images
    for i in range(number_of_orientations):
        # isolate orientations in this range
        orientation_start = number_of_orientations_per_180 * (i + 1)
        orientation_end = number_of_orientations_per_180 * i
        y = y0
        yi = 0

        while y < cc:
            xi = 0
            x = x0

            while x < cr:
                orientation_histogram[yi, xi, i] = \
                    _cell_hog(magnitude, orientation,
                              orientation_start, orientation_end,
                              cell_columns, cell_rows, x, y,
                              size_columns, size_rows,
                              range_rows_start, range_rows_stop,
                              range_columns_start, range_columns_stop)
                xi += 1
                x += cell_columns

            yi += 1
            y += cell_rows
    return orientation_histogram


def hog(image, orientations=9, pixels_per_cell=(8, 8), cells_per_block=(3, 3),
        visualize=False, transform_sqrt=False, feature_vector=True):
    """Extract Histogram of Oriented Gradients (HOG) for a given image.
    Compute a Histogram of Oriented Gradients (HOG) by
        1. (optional) global image normalization
        2. computing the gradient image in x and y
        3. computing gradient histograms
        4. normalizing across blocks
        5. flattening into a feature vector
    Parameters
    ----------
    image : (M, N) ndarray
        Input image (greyscale).
    orientations : int, optional
        Number of orientation bins.
    pixels_per_cell : 2-tuple (int, int), optional
        Size (in pixels) of a cell.
    cells_per_block : 2-tuple (int, int), optional
        Number of cells in each block.
    visualize : bool, optional
        Also return an image of the HOG.
    transform_sqrt : bool, optional
        Apply power law compression to normalize the image before
        processing. DO NOT use this if the image contains negative
        values. Also see `notes` section below.
    feature_vector : bool, optional
        Return the data as a feature vector by calling .ravel() on the result
        just before returning.
    Returns
    -------
    newarr : ndarray
        HOG for the image as a 1D (flattened) array.
    hog_image : ndarray (if visualize=True)
        A visualisation of the HOG image.

    Notes
    -----
    The presented code implements the HOG extraction method with
    the following changes: blocks of (3, 3) cells are used ((2, 2) in the paper
    """

    if type(image) != np.ndarray:
        image = np.array(image)
    if image.ndim != 2:
        raise ValueError('image must be grayscale -> ndim == 2')

    """
    The first stage applies an optional global image normalization
    equalisation that is designed to reduce the influence of illumination
    effects. In practice we use gamma (power law) compression, either
    computing the square root or the log of each color channel.
    Image texture strength is typically proportional to the local surface
    illumination so this compression helps to reduce the effects of local
    shadowing and illumination variations.
    """

    if transform_sqrt:
        image = np.sqrt(image)

    """
    The second stage computes first order image gradients. These capture
    contour, silhouette and some texture information, while providing
    further resistance to illumination variations. The locally dominant
    color channel is used, which provides color invariance to a large
    extent. Variant methods may also include second order image derivatives,
    which act as primitive bar detectors - a useful feature for capturing,
    e.g. bar like structures in bicycles and limbs in humans.
    """

    if image.dtype.kind == 'u':
        # convert uint image to float
        # to avoid problems with subtracting unsigned numbers
        image = image.astype('float')

    gx = np.zeros(image.shape)
    gy = np.zeros(image.shape)
    gx[:, :-1] = np.diff(image, n=1, axis=1)  # compute gradient on x-direction
    gy[:-1, :] = np.diff(image, n=1, axis=0)  # compute gradient on y-direction

    """
    The third stage aims to produce an encoding that is sensitive to
    local image content while remaining resistant to small changes in
    pose or appearance. The adopted method pools gradient orientation
    information locally in the same way as the SIFT [Lowe 2004]
    feature. The image window is divided into small spatial regions,
    called "cells". For each cell we accumulate a local 1-D histogram
    of gradient or edge orientations over all the pixels in the
    cell. This combined cell-level 1-D histogram forms the basic
    "orientation histogram" representation. Each orientation histogram
    divides the gradient angle range into a fixed number of
    predetermined bins. The gradient magnitudes of the pixels in the
    cell are used to vote into the orientation histogram.
    """

    sy, sx = image.shape
    cx, cy = pixels_per_cell
    bx, by = cells_per_block

    n_cells_x = int(sx / cx)  # number of cells in x
    n_cells_y = int(sy / cy)  # number of cells in y

    # compute orientations integral images
    orientation_histogram = np.zeros((n_cells_y, n_cells_x, orientations))
    orientation_histogram = _hog_histograms(gx, gy, cx, cy, sx, sy, n_cells_x, n_cells_y,
                                                        orientations, orientation_histogram)

    # now compute the histogram for each cell
    hog_image = None

    if visualize:
        from skimage import draw

        radius = min(cx, cy) // 2 - 1
        orientations_arr = np.arange(orientations)
        dx_arr = radius * np.cos(orientations_arr / orientations * np.pi)
        dy_arr = radius * np.sin(orientations_arr / orientations * np.pi)
        hog_image = np.zeros((sy, sx), dtype=float)
        for x in range(n_cells_x):
            for y in range(n_cells_y):
                for o, dx, dy in zip(orientations_arr, dx_arr, dy_arr):
                    centre = (y * cy + cy // 2, x * cx + cx // 2)
                    rr, cc = draw.line(int(centre[0] - dx),
                                       int(centre[1] + dy),
                                       int(centre[0] + dx),
                                       int(centre[1] - dy))
                    hog_image[rr, cc] += orientation_histogram[y, x, o]

    """
    The fourth stage computes normalization, which takes local groups of
    cells and contrast normalizes their overall responses before passing
    to next stage. Normalization introduces better invariance to illumination,
    shadowing, and edge contrast. It is performed by accumulating a measure
    of local histogram "energy" over local groups of cells that we call
    "blocks". The result is used to normalize each cell in the block.
    Typically each individual cell is shared between several blocks, but
    its normalizations are block dependent and thus different. The cell
    thus appears several times in the final output vector with different
    normalizations. This may seem redundant but it improves the performance.
    We refer to the normalized block descriptors as Histogram of Oriented
    Gradient (HOG) descriptors.
    """

    n_blocks_x = (n_cells_x - bx) + 1
    n_blocks_y = (n_cells_y - by) + 1
    normalized_blocks = np.zeros((n_blocks_y, n_blocks_x,
                                  by, bx, orientations))

    for x in range(n_blocks_x):
        for y in range(n_blocks_y):
            block = orientation_histogram[y:y + by, x:x + bx, :]
            normalized_blocks[y, x, :] = _normalize_block(block)

    """
    The final step collects the HOG descriptors from all blocks of a dense
    overlapping grid of blocks covering the detection window into a combined
    feature vector for use in the window classifier.
    """

    if feature_vector:
        normalized_blocks = normalized_blocks.ravel()

    if visualize:
        return normalized_blocks, hog_image
    else:
        return normalized_blocks
