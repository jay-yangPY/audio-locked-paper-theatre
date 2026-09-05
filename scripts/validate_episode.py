#!/usr/bin/env python3
"""Validate a staged ledger for an audio-locked paper-theatre episode."""

from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from pathlib import Path


STAGES = ("plan", "script", "audio", "front40", "final", "deliver")
SCHEMA_VERSIONS = {"audio-locked-episode-1.0", "audio-locked-episode-1.1"}
NATURAL_PUNCTUATION = re.compile(r"[，。！？、；：,.!?;:]")


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("root must be a JSON object")
    return data


def resolve_path(raw: str, manifest: Path) -> Path:
    candidate = Path(raw)
    return candidate if candidate.is_absolute() else manifest.parent / candidate


def require(errors: list[str], condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


def require_file(errors: list[str], raw: str, manifest: Path, label: str) -> None:
    require(errors, bool(raw), f"{label} is empty")
    if raw:
        require(errors, resolve_path(raw, manifest).is_file(), f"{label} does not exist: {raw}")


def parse_timestamp(value: str) -> float:
    hours, minutes, rest = value.replace(".", ",").split(":")
    seconds, millis = rest.split(",")
    return int(hours) * 3600 + int(minutes) * 60 + int(seconds) + int(millis) / 1000


def validate_srt(errors: list[str], path: Path, *, require_punctuation: bool = False) -> dict:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot read SRT as UTF-8: {exc}")
        return {"cue_count": 0, "punctuation_count": 0, "text": ""}
    blocks = [block for block in re.split(r"\r?\n\s*\r?\n", text.strip()) if block.strip()]
    numbers: list[int] = []
    payload_lines: list[str] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 3:
            continue
        try:
            numbers.append(int(lines[0]))
        except ValueError:
            errors.append(f"SRT cue number is invalid: {lines[0]}")
        payload_lines.extend(lines[2:])
    if numbers:
        require(errors, numbers == list(range(1, len(numbers) + 1)), "SRT cue numbers must be contiguous from 1")
    pattern = re.compile(r"(?m)^(\d{2}:\d{2}:\d{2}[,.]\d{3})\s+-->\s+(\d{2}:\d{2}:\d{2}[,.]\d{3})$")
    cues = [(parse_timestamp(start), parse_timestamp(end)) for start, end in pattern.findall(text)]
    require(errors, bool(cues), "SRT contains no valid timecode cues")
    if not cues:
        return {"cue_count": 0, "punctuation_count": 0, "text": ""}
    previous_end = -1.0
    positive_gaps = 0
    for index, (start, end) in enumerate(cues, start=1):
        require(errors, start >= previous_end, f"SRT cue {index} overlaps the previous cue")
        require(errors, end > start, f"SRT cue {index} has non-positive duration")
        if previous_end >= 0 and start - previous_end >= 0.05:
            positive_gaps += 1
        previous_end = end
    require(errors, positive_gaps > 0, "SRT has no preserved pause of at least 0.05s")
    payload = "".join(payload_lines)
    punctuation_count = len(NATURAL_PUNCTUATION.findall(payload))
    if require_punctuation:
        require(errors, punctuation_count > 0, "TTS SRT must preserve natural punctuation")
    return {"cue_count": len(cues), "punctuation_count": punctuation_count, "text": payload}


def image_size(path: Path) -> tuple[int, int] | None:
    with path.open("rb") as handle:
        header = handle.read(24)
        if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) >= 24:
            return struct.unpack(">II", header[16:24])
        if header[:2] != b"\xff\xd8":
            return None
        handle.seek(2)
        while True:
            marker_start = handle.read(1)
            if not marker_start:
                return None
            if marker_start != b"\xff":
                continue
            marker = handle.read(1)
            while marker == b"\xff":
                marker = handle.read(1)
            if marker in {bytes([code]) for code in range(0xC0, 0xC4)} | {bytes([code]) for code in range(0xC5, 0xC8)} | {bytes([code]) for code in range(0xC9, 0xCC)} | {bytes([code]) for code in range(0xCD, 0xD0)}:
                length = int.from_bytes(handle.read(2), "big")
                segment = handle.read(length - 2)
                if len(segment) >= 5:
                    return int.from_bytes(segment[3:5], "big"), int.from_bytes(segment[1:3], "big")
                return None
            length_raw = handle.read(2)
            if len(length_raw) != 2:
                return None
            length = int.from_bytes(length_raw, "big")
            handle.seek(max(0, length - 2), 1)


def validate_cover_ratio(errors: list[str], path: Path, expected: float, label: str) -> None:
    try:
        size = image_size(path)
    except OSError as exc:
        errors.append(f"cannot inspect {label}: {exc}")
        return
    require(errors, size is not None, f"{label} must be PNG or JPEG with readable dimensions")
    if size:
        width, height = size
        require(errors, height > 0 and abs(width / height - expected) <= 0.005, f"{label} has wrong ratio: {width}x{height}")


def validate(data: dict, manifest: Path, stage: str) -> list[str]:
    errors: list[str] = []
    schema_version = data.get("schema_version")
    require(errors, schema_version in SCHEMA_VERSIONS, "unsupported schema_version")
    is_v11 = schema_version == "audio-locked-episode-1.1"

    project = data.get("project", {})
    require(errors, bool(project.get("title")), "project.title is required")
    require(errors, project.get("orientation") in {"horizontal", "vertical"}, "project.orientation must be horizontal or vertical")
    expected = {"horizontal": ("16:9", "1920x1080"), "vertical": ("9:16", "1080x1920")}
    if project.get("orientation") in expected:
        ratio, resolution = expected[project["orientation"]]
        require(errors, project.get("aspect_ratio") == ratio, f"aspect_ratio must be {ratio}")
        require(errors, project.get("resolution") == resolution, f"resolution must be {resolution}")

    visual = data.get("visual", {})
    require(errors, visual.get("production_profile") == "audio-locked-paper-theatre-longform", "wrong production_profile")
    require(errors, visual.get("background_motion") == "locked", "background_motion must be locked")
    require(errors, visual.get("max_simultaneous_subject_groups", 99) <= 2, "max simultaneous subject groups must be <= 2")
    require(errors, visual.get("captions_and_marks_are_deterministic_post") is True, "captions and marks must be deterministic post elements")
    if is_v11:
        require(errors, visual.get("role_based_character_entry") is True, "characters must use role-based entry")
        require(
            errors,
            visual.get("full_frame_padding_policy") == "forbid-mirror-reflect-tile-loop-stretch",
            "full-frame mirror/reflect/tile/loop/stretch padding must be forbidden",
        )
        require(errors, visual.get("viewport_inside_valid_source_pixels") is True, "viewport must stay inside valid source pixels")
        require(
            errors,
            visual.get("all_visible_container_children_register_center_in_parent") is True,
            "all visible container children must register center_in_parent",
        )
        require(errors, visual.get("geometry_and_optical_center_required") is True, "geometry and optical centre checks are required")

    if stage in STAGES[1:]:
        script = data.get("script", {})
        require(errors, script.get("fact_check") == "passed", "script.fact_check must be passed")
        require(errors, script.get("beginner_restate_check") == "passed", "script.beginner_restate_check must be passed")
        require(errors, script.get("human_approval") == "approved", "script.human_approval must be approved")
        require(errors, bool(script.get("version")), "script.version is required")
        require(
            errors,
            script.get("voice_speed_decision_owner") == "owner-in-jianying",
            "script must leave voice speed selection to the owner in Jianying",
        )
        require_file(errors, script.get("locked_script_path", ""), manifest, "script.locked_script_path")
        jianying = data.get("jianying", {})
        require(errors, jianying.get("format") == "srt", "jianying.format must be srt")
        require(errors, jianying.get("timed") is True, "Jianying import must contain timecodes")
        require(errors, jianying.get("preserve_pauses") is True, "Jianying import must preserve pauses")
        require(errors, jianying.get("untimed_txt_is_formal_asset") is False, "untimed TXT cannot be a formal asset")
        if is_v11:
            require(errors, jianying.get("tts_preserves_natural_punctuation") is True, "TTS SRT must preserve natural punctuation")
            require(errors, jianying.get("tts_text_integrity_status") == "PASS", "TTS text integrity must PASS")
            require(errors, jianying.get("screen_captions_follow_real_audio") is True, "screen captions must follow the returned real audio")
            require(errors, jianying.get("assets_are_separate_files") is True, "TTS and screen-caption SRTs must be separate assets")
            require_file(errors, jianying.get("tts_import_srt", ""), manifest, "jianying.tts_import_srt")
            if jianying.get("tts_import_srt"):
                subtitle_path = resolve_path(jianying["tts_import_srt"], manifest)
                if subtitle_path.is_file():
                    validate_srt(errors, subtitle_path, require_punctuation=True)
        else:
            require_file(errors, jianying.get("import_file", ""), manifest, "jianying.import_file")
            if jianying.get("import_file"):
                subtitle_path = resolve_path(jianying["import_file"], manifest)
                if subtitle_path.is_file():
                    validate_srt(errors, subtitle_path)

    if stage in STAGES[2:]:
        audio = data.get("audio", {})
        require(errors, audio.get("voiceover_is_master") is True, "voiceover must be the master timeline")
        require(
            errors,
            audio.get("voice_speed_owner_controlled") is True,
            "voice speed must be selected by the owner in Jianying",
        )
        require(errors, isinstance(audio.get("duration_seconds"), (int, float)) and audio["duration_seconds"] > 0, "audio.duration_seconds must be positive")
        require(errors, audio.get("bgm_role") == "secondary", "BGM must be secondary")
        require_file(errors, audio.get("voiceover_path", ""), manifest, "audio.voiceover_path")
        require_file(errors, audio.get("bgm_path", ""), manifest, "audio.bgm_path")
        require_file(errors, visual.get("sentence_visual_map_path", ""), manifest, "visual.sentence_visual_map_path")
        require_file(errors, visual.get("asset_manifest_path", ""), manifest, "visual.asset_manifest_path")
        if is_v11:
            jianying = data.get("jianying", {})
            require_file(errors, jianying.get("screen_caption_srt", ""), manifest, "jianying.screen_caption_srt")
            require(
                errors,
                jianying.get("tts_import_srt") != jianying.get("screen_caption_srt"),
                "TTS and screen-caption SRTs must be different files",
            )
            if jianying.get("screen_caption_srt"):
                screen_path = resolve_path(jianying["screen_caption_srt"], manifest)
                if screen_path.is_file():
                    validate_srt(errors, screen_path)

    if stage in STAGES[3:]:
        front = data.get("gates", {}).get("front40", {})
        require(errors, front.get("status") == "approved", "front40.status must be approved")
        require_file(errors, front.get("sample_path", ""), manifest, "front40.sample_path")
        coverage = front.get("coverage", {})
        required_coverage = {
            "three_theatre_expressions", "one_line_caption", "two_line_caption",
            "semantic_mark", "multi_layer_occlusion", "theatre_transition",
            "progressive_performance", "final_voiceover", "actual_bgm"
        }
        for key in sorted(required_coverage):
            require(errors, coverage.get(key) is True, f"front40.coverage.{key} must be true")
        require(errors, front.get("dao_geometry_status") == "PASS", "front40 DAO geometry gate must PASS")
        if is_v11:
            require(errors, front.get("canvas_edge_status") == "PASS", "front40 canvas-edge gate must PASS")
            require(errors, front.get("container_center_status") == "PASS", "front40 container-centre gate must PASS")
            require(errors, front.get("route_regression_status") == "PASS", "front40 route regression must PASS")
        require(errors, front.get("steward_status") == "OWNER_PREVIEW_ALLOWED", "front40 steward must allow preview")

    if stage in STAGES[4:]:
        final = data.get("gates", {}).get("final", {})
        require(errors, final.get("dao_geometry_status") == "PASS", "final DAO geometry gate must PASS")
        interval = final.get("scan_interval_seconds")
        require(errors, isinstance(interval, (int, float)) and interval <= 0.1, "final scan interval must be <= 0.1s")
        require(errors, final.get("violations") == 0, "final violations must be 0")
        require(errors, final.get("old_failure_regression_status") == "PASS", "old failure regression must PASS")
        if is_v11:
            require(errors, final.get("all_object_collision_status") == "PASS", "all-object collision gate must PASS")
            require(errors, final.get("semantic_mark_status") == "PASS", "all semantic marks must PASS")
            require(errors, final.get("canvas_edge_status") == "PASS", "final canvas-edge gate must PASS")
            require(errors, final.get("container_geometry_center_status") == "PASS", "container geometry-centre gate must PASS")
            require(errors, final.get("container_optical_center_status") == "PASS", "container optical-centre gate must PASS")
        require(errors, isinstance(final.get("original_size_frame_count"), int) and final["original_size_frame_count"] >= 24, "at least 24 original-size frames are required")
        require(errors, isinstance(final.get("dense_crop_count"), int) and final["dense_crop_count"] >= 8, "at least 8 dense crops are required")
        require(errors, final.get("full_decode_status") == "PASS", "full decode must PASS")
        require(errors, final.get("steward_status") == "OWNER_PREVIEW_ALLOWED", "fresh final steward approval is required")
        delivery = data.get("delivery", {})
        require_file(errors, delivery.get("final_video_path", ""), manifest, "delivery.final_video_path")
        brand = data.get("brand_tail", {})
        if brand.get("source_path"):
            require_file(errors, brand.get("source_path", ""), manifest, "brand_tail.source_path")
            require(errors, brand.get("status") == "accepted", "supplied brand tail must be accepted")
            duration = brand.get("duration_seconds")
            limits = brand.get("target_duration_range_seconds", [3.5, 4.5])
            require(errors, isinstance(duration, (int, float)) and limits[0] <= duration <= limits[1], "brand tail duration is outside the approved range")

    if stage == "deliver":
        delivery = data.get("delivery", {})
        require(errors, delivery.get("status") == "release_package_ready", "delivery.status must be release_package_ready")
        require(errors, delivery.get("covers_are_native_compositions") is True, "covers must be native compositions")
        if is_v11:
            require(errors, delivery.get("cover_text_fidelity_status") == "PASS", "cover text fidelity must PASS")
            require(errors, delivery.get("cover_optical_center_status") == "PASS", "cover optical centring must PASS")
            require(errors, delivery.get("cover_platform_ui_overlap_status") == "PASS", "cover platform-UI overlap gate must PASS")
            require(errors, delivery.get("cover_steward_status") == "OWNER_PREVIEW_ALLOWED", "cover steward approval is required")
        for key in ("timed_subtitle_path", "cover_3x4_path", "cover_4x3_path", "release_copy_path", "qa_report_path", "sha256_ledger_path"):
            require_file(errors, delivery.get(key, ""), manifest, f"delivery.{key}")
        if delivery.get("cover_3x4_path"):
            cover_3x4 = resolve_path(delivery["cover_3x4_path"], manifest)
            if cover_3x4.is_file():
                validate_cover_ratio(errors, cover_3x4, 3 / 4, "3:4 cover")
        if delivery.get("cover_4x3_path"):
            cover_4x3 = resolve_path(delivery["cover_4x3_path"], manifest)
            if cover_4x3.is_file():
                validate_cover_ratio(errors, cover_4x3, 4 / 3, "4:3 cover")
        require(errors, delivery.get("cover_3x4_path") != delivery.get("cover_4x3_path"), "3:4 and 4:3 covers must be separate files")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--stage", choices=STAGES, required=True)
    args = parser.parse_args()
    try:
        data = read_json(args.manifest)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "errors": [str(exc)]}, ensure_ascii=False, indent=2))
        return 1
    errors = validate(data, args.manifest.resolve(), args.stage)
    result = {"status": "PASS" if not errors else "BLOCKED", "stage": args.stage, "errors": errors}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
