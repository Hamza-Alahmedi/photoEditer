import cv2
import numpy as np


def median_filter(image, k=5):
    if k % 2 == 0:
        k = k + 1
    return cv2.medianBlur(image, k)


# def bilateral_filter(image, d):
#     return cv2.bilateralFilter(image, d=d / 2 + 1, sigmaColor=75, sigmaSpace=75)


def dark_colors_filter(image):
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Convert the grayscale image back to BGR color space
    dark_image = cv2.cvtColor(gray_image, cv2.COLOR_GRAY2BGR)

    return dark_image


def gaussian_filter(image, filter_size):
    return cv2.GaussianBlur(image, (filter_size, filter_size), 0)


def increase_contrast(image, contrast_factor):
    """Increase the contrast of the image using contrast stretching."""
    # Calculate the minimum and maximum values of the image
    minimum = np.min(image)
    maximum = np.max(image)

    # Calculate the lower and upper percentiles based on the contrast factor
    lower = minimum + (maximum - minimum) * (contrast_factor / 200)
    upper = maximum - (maximum - minimum) * (contrast_factor / 200)

    # Apply contrast stretching
    stretched_image = (image - lower) * 255.0 / (upper - lower)
    stretched_image = np.clip(stretched_image, 0, 255)
    stretched_image = stretched_image.astype(np.uint8)

    return stretched_image


def laplacian_filter(image, strength=10):
    """Apply Laplacian filter on the image with reduced strength."""
    # The Laplacian filter is used to detect edges in an image.
    # No parameters are needed for this filter.
    laplacian_image = cv2.Laplacian(image, cv2.CV_64F)
    # Reduce the strength of the filter by multiplying with a factor less than 1
    laplacian_image = laplacian_image * strength
    # We need to convert the image back to an 8-bit image after applying the filter.
    laplacian_image = cv2.convertScaleAbs(laplacian_image)
    return laplacian_image


def sobel_filter(image):
    """Apply Sobel filter on the image."""
    # The Sobel filter is used for edge detection.
    # We apply it separately on the x and y axis, then combine the results.
    sobel_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=5)
    sobel_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=5)
    sobel_image = cv2.sqrt(
        cv2.addWeighted(cv2.pow(sobel_x, 2.0), 1.0, cv2.pow(sobel_y, 2.0), 1.0, 0)
    )
    sobel_image = cv2.normalize(
        sobel_image, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U
    )
    return sobel_image


def warm_filter(image, intensity):
    # Ensure intensity is in a valid range
    intensity = np.clip(intensity, -255, 255)

    # Split the image into its B, G, R components
    B, G, R = cv2.split(image)

    # Add to the red channel
    R = np.clip(R + intensity * 0.2, 0, 255).astype(np.uint8)

    # Add to the green channel
    G = np.clip(G + intensity * 0.1, 0, 255).astype(np.uint8)

    # Subtract from the blue channel
    B = np.clip(B - intensity * 0.1, 0, 255).astype(np.uint8)

    # Merge the channels
    return cv2.merge((B, G, R))


def cold_filter(image, intensity):
    # Ensure intensity is in a valid range
    intensity = np.clip(intensity, -255, 255)

    # Split the image into its B, G, R components
    B, G, R = cv2.split(image)

    # Subtract from the red channel
    R = np.clip(R - intensity * 0.2, 0, 255).astype(np.uint8)

    # Subtract from the green channel
    G = np.clip(G - intensity * 0.1, 0, 255).astype(np.uint8)

    # Add to the blue channel
    B = np.clip(B + intensity * 0.2, 0, 255).astype(np.uint8)

    # Merge the channels
    return cv2.merge((B, G, R))
