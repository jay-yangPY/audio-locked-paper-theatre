from __future__ import annotations

import importlib.util
import json
import struct
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_episode", ROOT / "scripts" / "validate_episode.py"
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_file(path: Path, data: bytes = b"fixture") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_png_header(path: Path, width: int, height: int) -> None:
    write_file(path, b"\x89PNG\r\n\x1a\n" + b"\x00" * 8 + struct.pack(">II", width, height))


def write_srt(path: Path, punctuated: bool) -> None:
    first = "记住，我不吃香菜。" if punctuated else "记住我不吃香菜"
    path.write_text(
        "1\n00:00:00,000 --> 00:00:01,000\n"
        + first
        + "\n\n2\n00:00:01,200 --> 00:00:02,000\n换个聊天还记得吗\n",
        encoding="utf-8",
    )


class ValidatorTests(unittest.TestCase):
    def make_project(self, folder: Path) -> tuple[Path, dict]:
        for name in (
            "script.md",
            "voice.wav",
            "bgm.wav",
            "sentence-map.json",
            "assets.json",
            "front40.mp4",
            "final.mp4",
            "release.md",
            "qa.json",
            "sha256.txt",
        ):
            write_file(folder / name)
        write_srt(folder / "tts.srt", punctuated=True)
        write_srt(folder / "screen.srt", punctuated=False)
        write_png_header(folder / "cover-3x4.png", 900, 1200)
        write_png_header(folder / "cover-4x3.png", 1200, 900)

        manifest = json.loads((ROOT / "assets" / "episode-template.json").read_text(encoding="utf-8"))
        manifest["project"].update({"title": "Example", "target_duration_seconds": 120})
        manifest["script"].update(
            {
                "fact_check": "passed",
                "beginner_restate_check": "passed",
                "human_approval": "approved",
                "version": "v1",
                "locked_script_path": "script.md",
            }
        )
        manifest["jianying"].update(
            {
                "tts_import_srt": "tts.srt",
                "screen_caption_srt": "screen.srt",
                "tts_text_integrity_status": "PASS",
            }
        )
        manifest["audio"].update(
            {
                "voiceover_path": "voice.wav",
                "duration_seconds": 120,
                "sample_rate_hz": 48000,
                "channels": 2,
                "bgm_path": "bgm.wav",
            }
        )
        manifest["visual"].update(
            {
                "sentence_visual_map_path": "sentence-map.json",
                "asset_manifest_path": "assets.json",
            }
        )
        manifest["gates"]["front40"].update(
            {
                "status": "approved",
                "sample_path": "front40.mp4",
                "dao_geometry_status": "PASS",
                "canvas_edge_status": "PASS",
                "container_center_status": "PASS",
                "route_regression_status": "PASS",
                "steward_status": "OWNER_PREVIEW_ALLOWED",
            }
        )
        for key in manifest["gates"]["front40"]["coverage"]:
            manifest["gates"]["front40"]["coverage"][key] = True
        manifest["gates"]["final"].update(
            {
                "dao_geometry_status": "PASS",
                "violations": 0,
                "old_failure_regression_status": "PASS",
                "all_object_collision_status": "PASS",
                "semantic_mark_status": "PASS",
                "canvas_edge_status": "PASS",
                "container_geometry_center_status": "PASS",
                "container_optical_center_status": "PASS",
                "original_size_frame_count": 24,
                "dense_crop_count": 8,
                "full_decode_status": "PASS",
                "steward_status": "OWNER_PREVIEW_ALLOWED",
            }
        )
        manifest["delivery"].update(
            {
                "status": "release_package_ready",
                "final_video_path": "final.mp4",
                "timed_subtitle_path": "screen.srt",
                "cover_3x4_path": "cover-3x4.png",
                "cover_4x3_path": "cover-4x3.png",
                "cover_text_fidelity_status": "PASS",
                "cover_optical_center_status": "PASS",
                "cover_platform_ui_overlap_status": "PASS",
                "cover_steward_status": "OWNER_PREVIEW_ALLOWED",
                "release_copy_path": "release.md",
                "qa_report_path": "qa.json",
                "sha256_ledger_path": "sha256.txt",
            }
        )
        path = folder / "episode.json"
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return path, manifest

    def test_complete_v11_manifest_passes_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, manifest = self.make_project(Path(tmp))
            self.assertEqual(MODULE.validate(manifest, path, "deliver"), [])

    def test_tts_without_punctuation_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            write_srt(folder / "tts.srt", punctuated=False)
            errors = MODULE.validate(manifest, path, "script")
            self.assertTrue(any("natural punctuation" in error for error in errors))

    def test_mirror_padding_policy_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, manifest = self.make_project(Path(tmp))
            manifest["visual"]["full_frame_padding_policy"] = "mirror"
            errors = MODULE.validate(manifest, path, "plan")
            self.assertTrue(any("padding must be forbidden" in error for error in errors))

    def test_tts_and_screen_caption_cannot_be_same_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, manifest = self.make_project(Path(tmp))
            manifest["jianying"]["screen_caption_srt"] = "tts.srt"
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("must be different files" in error for error in errors))

    def test_missing_optical_center_gate_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, manifest = self.make_project(Path(tmp))
            manifest["gates"]["final"]["container_optical_center_status"] = "pending"
            errors = MODULE.validate(manifest, path, "final")
            self.assertTrue(any("optical-centre" in error for error in errors))

    def test_wrong_cover_ratio_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            write_png_header(folder / "cover-3x4.png", 1000, 1000)
            errors = MODULE.validate(manifest, path, "deliver")
            self.assertTrue(any("wrong ratio" in error for error in errors))

    def test_long_episode_scales_visual_qa_counts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, manifest = self.make_project(Path(tmp))
            manifest["project"]["target_duration_seconds"] = 600
            errors = MODULE.validate(manifest, path, "final")
            self.assertTrue(any("at least 60 original-size frames" in error for error in errors))
            self.assertTrue(any("at least 20 dense crops" in error for error in errors))
            manifest["gates"]["final"]["original_size_frame_count"] = 60
            manifest["gates"]["final"]["dense_crop_count"] = 20
            self.assertEqual(MODULE.validate(manifest, path, "final"), [])


if __name__ == "__main__":
    unittest.main()
