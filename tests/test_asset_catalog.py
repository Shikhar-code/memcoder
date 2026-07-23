"""Approved visual assets must stay separate from learned memory and be searchable."""

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


sys.path.append(str(Path(__file__).resolve().parents[1]))

from memory.assets import build_asset_catalog, search_assets, write_asset_catalog


with TemporaryDirectory() as temporary_directory:
    root = Path(temporary_directory) / "Knowledge-Base-main"
    economics = root / "Economics assets" / "economics-diagrams"
    physics = root / "Assets_Physics" / "Motion"
    economics.mkdir(parents=True)
    physics.mkdir(parents=True)
    (economics / "demand-curve.svg").write_text(
        '<svg viewBox="0 0 640 360"><title>Price Demand Curve</title><text>Quantity</text><path /></svg>', encoding="utf-8"
    )
    (economics / "demand-curve-copy.svg").write_text(
        '<svg viewBox="0 0 640 360"><title>Price Demand Curve</title><text>Quantity</text><path /></svg>', encoding="utf-8"
    )
    (physics / "newton-second-law.png").write_bytes(b"example-image")
    (root / "Economics assets" / "manifest.json").write_text(
        json.dumps([{
            "outFile": "demand-curve.svg",
            "component": "DemandCurveAnimation",
            "file": "scenes/Demand2Scene.tsx",
            "duplicateOf": [],
        }]),
        encoding="utf-8",
    )
    metadata_path = root / "asset-metadata.json"
    metadata_path.write_text(json.dumps({
        "assets": {
            "Economics assets/economics-diagrams/demand-curve.svg": {
                "concepts": ["market equilibrium"],
                "visual_types": ["chart"],
                "grade_levels": ["Class 11"],
                "review_status": "approved",
            }
        }
    }), encoding="utf-8")

    catalog = build_asset_catalog(root, metadata_path=metadata_path)
    assert catalog["asset_count"] == 3
    assert catalog["subjects"] == ["economics", "physics"]
    economics_only = build_asset_catalog(root, subject="economics")
    assert economics_only["asset_count"] == 2
    assert economics_only["subjects"] == ["economics"]
    demand = next(asset for asset in catalog["assets"] if asset["path"].endswith("demand-curve.svg"))
    assert demand["view_box"] == [0.0, 0.0, 640.0, 360.0]
    assert demand["source_components"][0]["component"] == "DemandCurveAnimation"
    assert {"price", "quantity", "market", "equilibrium"}.issubset(demand["tags"] + demand["concepts"])
    assert demand["visual_types"] == ["chart"]
    assert demand["concept_phrases"] == ["market_equilibrium"]
    assert demand["grade_levels"] == ["class_11"]
    assert demand["review_status"] == "approved"
    duplicate = next(asset for asset in catalog["assets"] if asset["path"].endswith("copy.svg"))
    assert duplicate["duplicate_of"] == demand["id"]

    catalog_path = Path(temporary_directory) / "catalog" / "assets.json"
    written = write_asset_catalog(root, catalog_path, metadata_path=metadata_path)
    assert written["asset_count"] == 3
    assert written["subject"] is None
    assert written["metadata"] == str(metadata_path.resolve())
    economics_catalog_path = Path(temporary_directory) / "catalog" / "economics-assets.json"
    economics_written = write_asset_catalog(root, economics_catalog_path, subject="economics")
    assert economics_written["asset_count"] == 2
    assert economics_written["subject"] == "economics"
    matches = search_assets(catalog_path, "explain a demand curve", subject="economics")
    assert [match["path"] for match in matches["matches"]] == [
        "Economics assets/economics-diagrams/demand-curve.svg",
        "Economics assets/economics-diagrams/demand-curve-copy.svg",
    ]
    assert "demand" in demand["tags"]
    assert "curve" in demand["tags"]
    assert search_assets(catalog_path, "newton law", subject="physics")["matches"][0]["kind"] == "png"
    assert search_assets(catalog_path, "market equilibrium", subject="economics")["matches"][0]["path"].endswith("demand-curve.svg")

print("PASS: separate approved visual-asset catalog")
