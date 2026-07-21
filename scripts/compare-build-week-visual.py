"""Strict regional visual gates for the canonical THEKEY desktop surface."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageStat


CANONICAL_SIZE = (1448, 1086)
REGIONS = {
    "sidebar": (0, 48, 270, 1086),
    "hero": (270, 48, 1448, 302),
    "cta": (317, 302, 1007, 414),
    "cards": (312, 432, 1390, 684),
    "modes": (312, 702, 1390, 834),
    "activity": (288, 849, 1420, 1060),
}
THRESHOLDS = {
    "edge_distance_p95_px_max": 4.0,
    "edge_distance_max_px_max": 8.0,
    "ssim_min": 0.95,
    "rgb_changed_percent_max": 5.0,
    "rgb_delta_threshold": 12,
}


def normalized_mae(image: Image.Image) -> float:
    values = ImageStat.Stat(image).mean[:3]
    return sum(values) / (255.0 * len(values))


def global_ssim(reference: np.ndarray, actual: np.ndarray) -> float:
    """Compute deterministic luminance SSIM over one named region."""
    expected = reference.astype(np.float64)
    observed = actual.astype(np.float64)
    mean_expected = expected.mean()
    mean_observed = observed.mean()
    centered_expected = expected - mean_expected
    centered_observed = observed - mean_observed
    variance_expected = np.mean(centered_expected * centered_expected)
    variance_observed = np.mean(centered_observed * centered_observed)
    covariance = np.mean(centered_expected * centered_observed)
    c1 = (0.01 * 255.0) ** 2
    c2 = (0.03 * 255.0) ** 2
    numerator = (2 * mean_expected * mean_observed + c1) * (2 * covariance + c2)
    denominator = (
        (mean_expected**2 + mean_observed**2 + c1)
        * (variance_expected + variance_observed + c2)
    )
    if denominator == 0:
        return 1.0 if np.array_equal(reference, actual) else 0.0
    return float(max(-1.0, min(1.0, numerator / denominator)))


def rolling_support(mask: np.ndarray, radius: int, axis: int) -> np.ndarray:
    if axis == 1:
        padded = np.pad(mask.astype(np.uint8), ((0, 0), (radius, radius)))
        prefix = np.pad(padded, ((0, 0), (1, 0))).cumsum(axis=1, dtype=np.int32)
        return prefix[:, radius * 2 + 1 :] - prefix[:, : -(radius * 2 + 1)]
    padded = np.pad(mask.astype(np.uint8), ((radius, radius), (0, 0)))
    prefix = np.pad(padded, ((1, 0), (0, 0))).cumsum(axis=0, dtype=np.int32)
    return prefix[radius * 2 + 1 :, :] - prefix[: -(radius * 2 + 1), :]


def edge_mask(image: Image.Image, threshold: int) -> np.ndarray:
    edge_image = image.convert("L").filter(ImageFilter.FIND_EDGES)
    mask = (np.asarray(edge_image, dtype=np.uint8) >= threshold).copy()
    # Geometry is evaluated from sustained horizontal/vertical boundaries,
    # not from letter strokes, icon detail, or photographic texture. Crop
    # boundaries remain in the symmetric comparison because they are the
    # canonical outer bounds of each independently gated region.
    horizontal = rolling_support(mask, radius=20, axis=1)
    vertical = rolling_support(mask, radius=20, axis=0)
    return mask & ((horizontal >= 35) | (vertical >= 35))


def directed_edge_distances(source: np.ndarray, target: np.ndarray, maximum: int) -> np.ndarray:
    coordinates = np.argwhere(source)
    if coordinates.size == 0:
        return np.zeros(0, dtype=np.float32) if not target.any() else np.array([maximum + 1.0])
    if not target.any():
        return np.full(coordinates.shape[0], maximum + 1.0, dtype=np.float32)

    height, width = target.shape
    distances = np.full(coordinates.shape[0], maximum + 1.0, dtype=np.float32)
    unresolved = np.ones(coordinates.shape[0], dtype=bool)
    offsets = sorted(
        (
            (dx * dx + dy * dy, dx, dy)
            for dy in range(-maximum, maximum + 1)
            for dx in range(-maximum, maximum + 1)
            if dx * dx + dy * dy <= maximum * maximum
        ),
        key=lambda item: item[0],
    )
    for distance_squared, dx, dy in offsets:
        if not unresolved.any():
            break
        indexes = np.flatnonzero(unresolved)
        y = coordinates[indexes, 0] + dy
        x = coordinates[indexes, 1] + dx
        valid = (x >= 0) & (x < width) & (y >= 0) & (y < height)
        matched = np.zeros(indexes.shape[0], dtype=bool)
        matched[valid] = target[y[valid], x[valid]]
        if matched.any():
            resolved_indexes = indexes[matched]
            distances[resolved_indexes] = math.sqrt(distance_squared)
            unresolved[resolved_indexes] = False
    return distances


def symmetric_edge_distances(reference: Image.Image, actual: Image.Image) -> tuple[float, float, int, int]:
    expected_edges = edge_mask(reference, threshold=32)
    actual_edges = edge_mask(actual, threshold=32)
    expected_to_actual = directed_edge_distances(expected_edges, actual_edges, maximum=8)
    actual_to_expected = directed_edge_distances(actual_edges, expected_edges, maximum=8)
    distances = np.concatenate((expected_to_actual, actual_to_expected))
    if distances.size == 0:
        return 0.0, 0.0, 0, 0
    return (
        float(np.percentile(distances, 95)),
        float(distances.max()),
        int(expected_edges.sum()),
        int(actual_edges.sum()),
    )


def analyze_region(reference: Image.Image, actual: Image.Image, bounds: tuple[int, int, int, int]) -> dict:
    expected = reference.crop(bounds)
    observed = actual.crop(bounds)
    expected_rgb = np.asarray(expected, dtype=np.int16)
    observed_rgb = np.asarray(observed, dtype=np.int16)
    channel_delta = np.abs(expected_rgb - observed_rgb)
    changed = np.max(channel_delta, axis=2) > THRESHOLDS["rgb_delta_threshold"]
    expected_gray = np.asarray(expected.convert("L"), dtype=np.uint8)
    observed_gray = np.asarray(observed.convert("L"), dtype=np.uint8)
    p95, maximum, expected_edge_count, actual_edge_count = symmetric_edge_distances(expected, observed)
    ssim = global_ssim(expected_gray, observed_gray)
    changed_percent = float(changed.mean() * 100.0)
    failures = []
    if p95 > THRESHOLDS["edge_distance_p95_px_max"]:
        failures.append("edge_distance_p95")
    if maximum > THRESHOLDS["edge_distance_max_px_max"]:
        failures.append("edge_distance_max")
    if ssim < THRESHOLDS["ssim_min"]:
        failures.append("ssim")
    if changed_percent > THRESHOLDS["rgb_changed_percent_max"]:
        failures.append("rgb_changed_percent")
    diff = ImageChops.difference(expected, observed)
    mae = normalized_mae(diff)
    return {
        "bounds": {"x": bounds[0], "y": bounds[1], "width": bounds[2] - bounds[0], "height": bounds[3] - bounds[1]},
        "edge_distance_p95_px": round(p95, 3),
        "edge_distance_max_px": round(maximum, 3),
        "reference_edge_pixels": expected_edge_count,
        "actual_edge_pixels": actual_edge_count,
        "ssim": round(ssim, 6),
        "rgb_changed_percent": round(changed_percent, 3),
        "mae": round(mae, 6),
        "similarity_percent": round((1.0 - mae) * 100.0, 3),
        "passed": not failures,
        "failures": failures,
    }


def save_region_artifacts(
    output_dir: Path,
    name: str,
    reference: Image.Image,
    actual: Image.Image,
    bounds: tuple[int, int, int, int],
    result: dict,
) -> dict[str, str]:
    """Persist the independently reviewable evidence requested for one region."""
    region_dir = output_dir / "regions" / name
    region_dir.mkdir(parents=True, exist_ok=True)
    expected = reference.crop(bounds)
    observed = actual.crop(bounds)
    reference_path = region_dir / "reference.png"
    actual_path = region_dir / "actual.png"
    overlay_path = region_dir / "overlay-50.png"
    diff_path = region_dir / "diff.png"
    report_path = region_dir / "report.json"
    expected.save(reference_path)
    observed.save(actual_path)
    Image.blend(expected, observed, 0.5).save(overlay_path)
    ImageEnhance.Contrast(ImageChops.difference(expected, observed)).enhance(3.0).save(diff_path)
    region_report = {
        "schema_version": "v3",
        "region": name,
        "thresholds": THRESHOLDS,
        "result": result,
        "gate_rule": "This region passes only when every threshold passes.",
    }
    report_path.write_text(json.dumps(region_report, indent=2), encoding="utf-8")
    return {
        "reference": str(reference_path.resolve()),
        "actual": str(actual_path.resolve()),
        "overlay_50": str(overlay_path.resolve()),
        "diff": str(diff_path.resolve()),
        "report": str(report_path.resolve()),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--allow-failures", action="store_true")
    args = parser.parse_args()

    reference = Image.open(args.reference).convert("RGB")
    actual = Image.open(args.actual).convert("RGB")
    if reference.size != actual.size:
        raise SystemExit(f"dimension mismatch: reference={reference.size}, actual={actual.size}")
    if reference.size != CANONICAL_SIZE:
        raise SystemExit(f"unexpected canonical dimensions: {reference.size}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    diff = ImageChops.difference(reference, actual)
    diff_path = args.output_dir / "diff.png"
    overlay_path = args.output_dir / "overlay-50.png"
    ImageEnhance.Contrast(diff).enhance(3.0).save(diff_path)
    Image.blend(reference, actual, 0.5).save(overlay_path)

    regions = {}
    for name, bounds in REGIONS.items():
        region = analyze_region(reference, actual, bounds)
        region["artifacts"] = save_region_artifacts(args.output_dir, name, reference, actual, bounds, region)
        regions[name] = region
    all_regions_passed = all(region["passed"] for region in regions.values())
    full_diff = np.asarray(diff, dtype=np.uint8)
    full_changed = np.max(full_diff, axis=2) > THRESHOLDS["rgb_delta_threshold"]
    full_mae = normalized_mae(diff)
    report = {
        "schema_version": "v3",
        "status": "PASS" if all_regions_passed else "FAIL",
        "all_regions_passed": all_regions_passed,
        "reference": str(args.reference.resolve()),
        "actual": str(args.actual.resolve()),
        "overlay_50": str(overlay_path.resolve()),
        "diff": str(diff_path.resolve()),
        "dimensions": {"width": reference.width, "height": reference.height, "dpi": 96},
        "thresholds": THRESHOLDS,
        "metric": {
            "method": "Regional global-luminance SSIM, symmetric bounded Euclidean distance over sustained structural edges, and RGB channel delta",
            "mae": round(full_mae, 6),
            "similarity_percent": round((1.0 - full_mae) * 100.0, 3),
            "rgb_changed_percent": round(float(full_changed.mean() * 100.0), 3),
        },
        "regions": regions,
        "failed_regions": [name for name, result in regions.items() if not result["passed"]],
        "gate_rule": "The complete interface passes only when every named region passes every threshold.",
    }
    report_path = args.output_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    if not all_regions_passed and not args.allow_failures:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
