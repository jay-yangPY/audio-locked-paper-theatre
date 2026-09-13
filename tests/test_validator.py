from __future__ import annotations

import importlib.util
import hashlib
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
            "runtime-compatibility.md",
        ):
            write_file(folder / name)
        write_srt(folder / "tts.srt", punctuated=True)
        write_srt(folder / "screen.srt", punctuated=False)
        write_png_header(folder / "cover-3x4.png", 900, 1200)
        write_png_header(folder / "cover-4x3.png", 1200, 900)

        template_map = {
            "semantic-actions.json": "semantic-action-template.json",
            "objects.json": "object-registry-template.json",
            "occlusions.json": "occlusion-allowlist-template.json",
            "silent-review.json": "silent-review-template.json",
            "motion-recipes.json": "motion-recipe-ledger-template.json",
            "semantic-focus.json": "semantic-focus-template.json",
            "asset-generation.json": "asset-generation-template.json",
            "background-music.json": "background-music-ledger-template.json",
        }
        for output_name, template_name in template_map.items():
            (folder / output_name).write_text(
                (ROOT / "assets" / template_name).read_text(encoding="utf-8"),
                encoding="utf-8",
            )

        manifest = json.loads((ROOT / "assets" / "episode-template.json").read_text(encoding="utf-8"))
        bgm_ledger = self.load_linked(folder, "background-music.json")
        bgm_ledger.update(
            {
                "source_path": "bgm.wav",
                "sha256": hashlib.sha256((folder / "bgm.wav").read_bytes()).hexdigest(),
                "provenance_status": "PASS",
                "audible_review_status": "PASS",
                "speech_masking_status": "PASS",
            }
        )
        self.save_linked(folder, "background-music.json", bgm_ledger)
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
                "background_music_ledger_path": "background-music.json",
            }
        )
        manifest["visual"].update(
            {
                "sentence_visual_map_path": "sentence-map.json",
                "asset_manifest_path": "assets.json",
                "semantic_action_manifest_path": "semantic-actions.json",
                "object_registry_path": "objects.json",
                "occlusion_allowlist_path": "occlusions.json",
                "silent_review_path": "silent-review.json",
                "motion_recipe_ledger_path": "motion-recipes.json",
                "semantic_focus_manifest_path": "semantic-focus.json",
                "asset_generation_manifest_path": "asset-generation.json",
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
                "semantic_action_status": "PASS",
                "physical_boundary_status": "PASS",
                "silent_readability_status": "PASS",
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
                "semantic_action_status": "PASS",
                "physical_boundary_status": "PASS",
                "silent_readability_status": "PASS",
                "output_origin_status": "PASS",
                "same_source_layer_status": "PASS",
                "semantic_focus_status": "PASS",
                "background_music_status": "PASS",
                "runtime_compatibility_status": "PASS",
                "repository_identity_status": "PASS",
                "original_size_frame_count": 24,
                "dense_crop_count": 8,
                "full_decode_status": "PASS",
                "steward_status": "OWNER_PREVIEW_ALLOWED",
            }
        )
        manifest["release"].update(
            {
                "runtime_compatibility_path": "runtime-compatibility.md",
                "show_repository_identity": True,
                "repository_identity": {
                    "skill_name": "audio-locked-paper-theatre",
                    "repository_url": "https://github.com/example/audio-locked-paper-theatre",
                    "text_fidelity_status": "PASS",
                    "foreground_protection_status": "PASS",
                },
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

    def test_complete_v13_manifest_passes_delivery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, manifest = self.make_project(Path(tmp))
            self.assertEqual(MODULE.validate(manifest, path, "deliver"), [])

    def test_v12_manifest_remains_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, manifest = self.make_project(Path(tmp))
            manifest["schema_version"] = "audio-locked-episode-1.2"
            manifest["audio"].pop("background_music_ledger_path", None)
            manifest["visual"].pop("semantic_focus_manifest_path", None)
            manifest["visual"].pop("asset_generation_manifest_path", None)
            manifest.pop("release", None)
            for key in ("semantic_focus_status", "background_music_status", "runtime_compatibility_status", "repository_identity_status"):
                manifest["gates"]["final"].pop(key, None)
            self.assertEqual(MODULE.validate(manifest, path, "deliver"), [])

    def test_v11_manifest_remains_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, manifest = self.make_project(Path(tmp))
            manifest["schema_version"] = "audio-locked-episode-1.1"
            for key in (
                "semantic_action_manifest_path", "object_registry_path", "occlusion_allowlist_path",
                "silent_review_path", "motion_recipe_ledger_path",
            ):
                manifest["visual"].pop(key, None)
            for key in ("semantic_action_status", "physical_boundary_status", "silent_readability_status"):
                manifest["gates"]["front40"].pop(key, None)
            for key in (
                "semantic_action_status", "physical_boundary_status", "silent_readability_status",
                "output_origin_status", "same_source_layer_status",
            ):
                manifest["gates"]["final"].pop(key, None)
            self.assertEqual(MODULE.validate(manifest, path, "deliver"), [])

    def load_linked(self, folder: Path, name: str) -> dict:
        return json.loads((folder / name).read_text(encoding="utf-8"))

    def save_linked(self, folder: Path, name: str, data: dict) -> None:
        (folder / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def test_scan_target_must_be_primary_subject(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            objects = self.load_linked(folder, "objects.json")
            objects["objects"].append(
                {
                    "object_id": "magnifier",
                    "parent_id": "book_stage",
                    "source_id": "magnifier-source",
                    "semantic_roles": ["prop"],
                    "z_level": 50,
                    "visible_bounds_source": [100, 100, 200, 200],
                    "allowed_occlusions": [],
                    "forbidden_occlusions": [],
                    "center_in_parent": {"required": False},
                }
            )
            self.save_linked(folder, "objects.json", objects)
            actions = self.load_linked(folder, "semantic-actions.json")
            actions["semantic_actions"][0]["target_id"] = "magnifier"
            self.save_linked(folder, "semantic-actions.json", actions)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("primary_subject" in error for error in errors))

    def test_scan_trajectory_cannot_leave_target_mask_intersection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            actions = self.load_linked(folder, "semantic-actions.json")
            actions["semantic_actions"][0]["trajectory_samples"][0]["actor_bbox"] = [895, 250, 20, 280]
            self.save_linked(folder, "semantic-actions.json", actions)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("leaves target-mask intersection" in error for error in errors))

    def test_machine_output_requires_registered_port(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            actions = self.load_linked(folder, "semantic-actions.json")
            actions["semantic_actions"][1]["source_port_id"] = "missing-port"
            self.save_linked(folder, "semantic-actions.json", actions)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("source_port_id is invalid" in error for error in errors))

    def test_three_layers_must_share_target_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            objects = self.load_linked(folder, "objects.json")
            next(item for item in objects["objects"] if item["object_id"] == "platform_layer")["source_id"] = "unrelated-source"
            self.save_linked(folder, "objects.json", objects)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("layers must share one source_id" in error for error in errors))

    def test_silent_review_requires_all_four_answers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            review = self.load_linked(folder, "silent-review.json")
            review["reviews"][0]["visible_result"] = ""
            self.save_linked(folder, "silent-review.json", review)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("visible_result is required" in error for error in errors))

    def test_caption_overlap_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            occlusions = self.load_linked(folder, "occlusions.json")
            occlusions["caption_overlaps"] = [{"caption_id": "caption_strip", "object_id": "hero_image"}]
            self.save_linked(folder, "occlusions.json", occlusions)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("caption overlaps must be empty" in error for error in errors))

    def test_required_center_needs_optical_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            objects = self.load_linked(folder, "objects.json")
            next(item for item in objects["objects"] if item["object_id"] == "caption_strip")["center_in_parent"].pop("optical_status")
            self.save_linked(folder, "objects.json", objects)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("optical centring must PASS" in error for error in errors))

    def test_undeclared_overlap_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            occlusions = self.load_linked(folder, "occlusions.json")
            occlusions["undeclared_overlaps"] = [{"front_id": "scanner_shell", "back_id": "caption_strip"}]
            self.save_linked(folder, "occlusions.json", occlusions)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("undeclared overlaps must be empty" in error for error in errors))

    def test_front40_new_gate_cannot_be_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, manifest = self.make_project(Path(tmp))
            manifest["gates"]["front40"]["physical_boundary_status"] = "pending"
            errors = MODULE.validate(manifest, path, "front40")
            self.assertTrue(any("physical-boundary" in error for error in errors))

    def test_final_output_origin_gate_cannot_be_pending(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, manifest = self.make_project(Path(tmp))
            manifest["gates"]["final"]["output_origin_status"] = "pending"
            errors = MODULE.validate(manifest, path, "final")
            self.assertTrue(any("output-origin" in error for error in errors))

    def test_tts_without_punctuation_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            write_srt(folder / "tts.srt", punctuated=False)
            errors = MODULE.validate(manifest, path, "script")
            self.assertTrue(any("natural punctuation" in error for error in errors))

    def test_screen_caption_terminal_punctuation_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            write_srt(folder / "screen.srt", punctuated=True)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("omit terminal punctuation" in error for error in errors))

    def test_visible_text_foreground_occlusion_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            occlusions = self.load_linked(folder, "occlusions.json")
            occlusions["visible_text_occlusions"] = [{"text_id": "caption_strip", "occluder_id": "clapper"}]
            self.save_linked(folder, "occlusions.json", occlusions)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("visible text occlusions" in error for error in errors))

    def test_isolated_asset_crop_edge_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            objects = self.load_linked(folder, "objects.json")
            hero = next(item for item in objects["objects"] if item["object_id"] == "hero_image")
            hero["isolated_asset"] = True
            hero["alpha_edge_margin_px"] = {"left": 0, "top": 8, "right": 8, "bottom": 8}
            hero["source_edge_status"] = "PASS"
            self.save_linked(folder, "objects.json", objects)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("source crop edge" in error for error in errors))

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

    def test_semantic_focus_wrong_target_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            focus = self.load_linked(folder, "semantic-focus.json")
            focus["focus_events"][0]["mark_center"] = [700, 390]
            self.save_linked(folder, "semantic-focus.json", focus)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("wrong target" in error for error in errors))

    def test_background_music_hash_mismatch_is_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            bgm = self.load_linked(folder, "background-music.json")
            bgm["sha256"] = "0" * 64
            self.save_linked(folder, "background-music.json", bgm)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("hash does not match" in error for error in errors))

    def test_builtin_imagegen_requires_available_tool(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            assets = self.load_linked(folder, "asset-generation.json")
            assets["runtime_capabilities"]["image_generation_available"] = False
            self.save_linked(folder, "asset-generation.json", assets)
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("requires an available image-generation tool" in error for error in errors))

    def test_no_imagegen_runtime_can_use_user_supplied_assets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            path, manifest = self.make_project(folder)
            assets = self.load_linked(folder, "asset-generation.json")
            assets["mode"] = "user_supplied"
            assets["runtime_capabilities"]["image_generation_available"] = False
            assets["assets"][0]["source_mode"] = "user_supplied"
            self.save_linked(folder, "asset-generation.json", assets)
            self.assertEqual(MODULE.validate(manifest, path, "audio"), [])

    def test_repository_identity_is_required_when_shown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path, manifest = self.make_project(Path(tmp))
            manifest["release"]["repository_identity"]["repository_url"] = "github.com/example/repo"
            errors = MODULE.validate(manifest, path, "audio")
            self.assertTrue(any("full GitHub repository URL" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
