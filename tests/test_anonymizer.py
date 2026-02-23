"""Tests for CropAnonymizer — per-folder crop region behaviour."""

import numpy as np

from math_mind.anonymization.crop_anonymizer import CropAnonymizer


def test_fills_region_with_black(sample_image: np.ndarray) -> None:
    region = (10, 10, 50, 30)  # x, y, w, h
    result = CropAnonymizer(region).anonymize(sample_image)
    x, y, w, h = region
    assert np.all(result[y : y + h, x : x + w] == 0)


def test_does_not_modify_original(sample_image: np.ndarray) -> None:
    original_copy = sample_image.copy()
    CropAnonymizer((0, 0, 50, 50)).anonymize(sample_image)
    assert np.array_equal(sample_image, original_copy)


def test_outside_region_untouched(sample_image: np.ndarray) -> None:
    CropAnonymizer((0, 0, 20, 20)).anonymize(sample_image)
    # Original pixel below the region should still be white
    assert sample_image[100, 100, 0] == 255


def test_custom_fill_color(sample_image: np.ndarray) -> None:
    red = (0, 0, 255)  # BGR
    result = CropAnonymizer((0, 0, 20, 20), fill_color=red).anonymize(sample_image)
    assert tuple(result[5, 5]) == red


def test_zero_size_region_is_noop(sample_image: np.ndarray) -> None:
    """region (0,0,0,0) must not raise and must leave image unchanged."""
    result = CropAnonymizer((0, 0, 0, 0)).anonymize(sample_image)
    assert np.array_equal(result, sample_image)


def test_different_folders_use_independent_regions() -> None:
    """
    Verifies the per-folder design: two anonymizers with different regions
    produce independent results.
    """
    img_a = np.full((100, 100, 3), 255, dtype=np.uint8)
    img_b = np.full((100, 100, 3), 255, dtype=np.uint8)

    res_a = CropAnonymizer((0, 0, 20, 20)).anonymize(img_a)
    res_b = CropAnonymizer((80, 80, 20, 20)).anonymize(img_b)

    # The blackened corner of res_a should not appear in res_b
    assert res_b[5, 5, 0] == 255
    # The blackened corner of res_b should not appear in res_a
    assert res_a[90, 90, 0] == 255
