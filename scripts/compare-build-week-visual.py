"""Create reproducible THEKEY Build Week visual-comparison evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageStat


REGIONS = {
    "title_bar": (0, 0, 1448, 48),
    "navigation": (0, 48, 270, 1086),
    "hero": (270, 48, 1448, 420),
    "primary_action": (317, 302, 1007, 414),
    "operation_cards": (312, 432, 1390, 684),
    "upcoming_modes": (312, 723, 1390, 834),
    "activity": (288, 849, 1420, 1060),
}


def normalized_mae(image: Image.Image) -> float:
    values = ImageStat.Stat(image).mean[:3]
    return sum(values) / (255.0 * len(values))


def region_report(reference: Image.Image, actual: Image.Image) -> dict[str, dict[str, float]]:
    report: dict[str, dict[str, float]] = {}
    for name, bounds in REGIONS.items():
        diff = ImageChops.difference(reference.crop(bounds), actual.crop(bounds))
        mae = normalized_mae(diff)
        report[name] = {"mae": round(mae, 6), "similarity_percent": round((1 - mae) * 100, 3)}
    return report


def foreground_mae(reference: Image.Image, actual: Image.Image) -> tuple[float, int]:
    """Measure non-black content without letting the dark canvas dominate."""
    total = 0
    count = 0
    reference_pixels = reference.get_flattened_data() if hasattr(reference, "get_flattened_data") else reference.getdata()
    actual_pixels = actual.get_flattened_data() if hasattr(actual, "get_flattened_data") else actual.getdata()
    for expected, observed in zip(reference_pixels, actual_pixels):
        if max(expected) <= 35 and max(observed) <= 35:
            continue
        total += sum(abs(expected[channel] - observed[channel]) for channel in range(3))
        count += 1
    return (total / (count * 255.0 * 3.0) if count else 0.0), count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--actual", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    reference = Image.open(args.reference).convert("RGB")
    actual = Image.open(args.actual).convert("RGB")
    if reference.size != actual.size:
        raise SystemExit(f"dimension mismatch: reference={reference.size}, actual={actual.size}")
    if reference.size != (1448, 1086):
        raise SystemExit(f"unexpected canonical dimensions: {reference.size}")

    diff = ImageChops.difference(reference, actual)
    pixels = diff.get_flattened_data() if hasattr(diff, "get_flattened_data") else diff.getdata()
    changed = sum(1 for pixel in pixels if max(pixel) > 12)
    mae = normalized_mae(diff)
    foreground_error, foreground_pixels = foreground_mae(reference, actual)
    reference_edges = reference.convert("L").filter(ImageFilter.FIND_EDGES)
    actual_edges = actual.convert("L").filter(ImageFilter.FIND_EDGES)
    edge_error = normalized_mae(ImageChops.difference(reference_edges, actual_edges))
    regions = region_report(reference, actual)
    region_average = sum(item["similarity_percent"] for item in regions.values()) / len(regions)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    diff_path = args.output_dir / "diff.png"
    ImageEnhance.Contrast(diff).enhance(3.0).save(diff_path)
    report = {
        "schema_version": "v2",
        "reference": str(args.reference.resolve()),
        "actual": str(args.actual.resolve()),
        "diff": str(diff_path.resolve()),
        "dimensions": {"width": reference.width, "height": reference.height},
        "metric": {
            "method": "RGB normalized mean absolute error; changed pixels use channel delta > 12",
            "mae": round(mae, 6),
            "similarity_percent": round((1 - mae) * 100, 3),
            "changed_pixel_ratio_percent": round(changed / (reference.width * reference.height) * 100, 3),
            "foreground_similarity_percent": round((1 - foreground_error) * 100, 3),
            "foreground_pixel_ratio_percent": round(foreground_pixels / (reference.width * reference.height) * 100, 3),
            "edge_similarity_percent": round((1 - edge_error) * 100, 3),
            "equal_weight_region_similarity_percent": round(region_average, 3),
        },
        "regions": regions,
        "review_scope": [
            "geometry", "text", "cropping", "alignment", "background", "iconography"
        ],
    }
    report_path = args.output_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
