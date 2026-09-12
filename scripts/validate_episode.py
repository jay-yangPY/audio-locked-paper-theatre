#!/usr/bin/env python3
"""Validate a staged ledger for an audio-locked paper-theatre episode."""

from __future__ import annotations

import argparse
import json
import math
import re
import struct
import sys
from pathlib import Path


STAGES = ("plan", "script", "audio", "front40", "final", "deliver")
SCHEMA_VERSIONS = {
    "audio-locked-episode-1.0",
    "audio-locked-episode-1.1",
    "audio-locked-episode-1.2",
}
NATURAL_PUNCTUATION = re.compile(r"[，。！？、；：,.!?;:]")
ACTION_FIELDS = {
    "cue_id", "audio_in", "audio_out", "spoken_line", "actor_id", "target_id",
    "action_type", "action", "visible_result", "forbidden_misread", "closing_state",
}
HIGH_RISK_ACTIONS = {"scan", "inspect", "crop", "screenshot"}


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


def read_linked_json(errors: list[str], raw: str, manifest: Path, label: str) -> dict | None:
    require_file(errors, raw, manifest, label)
    if not raw:
        return None
    path = resolve_path(raw, manifest)
    if not path.is_file():
        return None
    try:
        return read_json(path)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        errors.append(f"{label} is not valid UTF-8 JSON: {exc}")
        return None


def valid_bbox(value: object) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 4
        and all(isinstance(item, (int, float)) for item in value)
        and value[2] > 0
        and value[3] > 0
    )


def bbox_inside(inner: list[float], outer: list[float], tolerance: float = 0.0) -> bool:
    ix, iy, iw, ih = inner
    ox, oy, ow, oh = outer
    return (
        ix >= ox - tolerance
        and iy >= oy - tolerance
        and ix + iw <= ox + ow + tolerance
        and iy + ih <= oy + oh + tolerance
    )


def intersect_bbox(a: list[float], b: list[float]) -> list[float] | None:
    x0, y0 = max(a[0], b[0]), max(a[1], b[1])
    x1, y1 = min(a[0] + a[2], b[0] + b[2]), min(a[1] + a[3], b[1] + b[3])
    if x1 <= x0 or y1 <= y0:
        return None
    return [x0, y0, x1 - x0, y1 - y0]


def validate_v12_evidence(errors: list[str], data: dict, manifest: Path) -> None:
    visual = data.get("visual", {})
    linked: dict[str, dict | None] = {}
    for key in (
        "semantic_action_manifest_path",
        "object_registry_path",
        "occlusion_allowlist_path",
        "silent_review_path",
        "motion_recipe_ledger_path",
    ):
        linked[key] = read_linked_json(errors, visual.get(key, ""), manifest, f"visual.{key}")

    registry = linked["object_registry_path"]
    object_by_id: dict[str, dict] = {}
    if registry is not None:
        objects = registry.get("objects")
        require(errors, isinstance(objects, list) and bool(objects), "object registry must contain objects")
        if isinstance(objects, list):
            for index, obj in enumerate(objects):
                label = f"object registry item {index + 1}"
                require(errors, isinstance(obj, dict), f"{label} must be an object")
                if not isinstance(obj, dict):
                    continue
                for field in (
                    "object_id", "parent_id", "source_id", "z_level", "visible_bounds_source",
                    "allowed_occlusions", "forbidden_occlusions", "center_in_parent",
                ):
                    require(errors, field in obj, f"{label}.{field} is required")
                object_id = obj.get("object_id")
                require(errors, isinstance(object_id, str) and bool(object_id), f"{label}.object_id is required")
                if isinstance(object_id, str) and object_id:
                    require(errors, object_id not in object_by_id, f"duplicate object_id: {object_id}")
                    object_by_id[object_id] = obj
                require(errors, valid_bbox(obj.get("visible_bounds_source")), f"{label}.visible_bounds_source must be [x,y,w,h]")
                require(errors, isinstance(obj.get("z_level"), (int, float)), f"{label}.z_level must be numeric")
                require(errors, isinstance(obj.get("allowed_occlusions"), list), f"{label}.allowed_occlusions must be an array")
                require(errors, isinstance(obj.get("forbidden_occlusions"), list), f"{label}.forbidden_occlusions must be an array")
                center = obj.get("center_in_parent")
                require(errors, isinstance(center, dict), f"{label}.center_in_parent must be an object")
                if isinstance(center, dict) and center.get("required") is True:
                    require(errors, center.get("geometry_status") == "PASS", f"{label} geometry centring must PASS")
                    require(errors, center.get("optical_status") == "PASS", f"{label} optical centring must PASS")
            for object_id, obj in object_by_id.items():
                parent_id = obj.get("parent_id")
                require(
                    errors,
                    parent_id is None or parent_id in object_by_id,
                    f"object {object_id} references unknown parent_id: {parent_id}",
                )

    action_manifest = linked["semantic_action_manifest_path"]
    if action_manifest is not None:
        actions = action_manifest.get("semantic_actions")
        require(errors, isinstance(actions, list) and bool(actions), "semantic action manifest must contain semantic_actions")
        if isinstance(actions, list):
            cue_ids: set[object] = set()
            for index, action in enumerate(actions):
                label = f"semantic action {index + 1}"
                require(errors, isinstance(action, dict), f"{label} must be an object")
                if not isinstance(action, dict):
                    continue
                for field in sorted(ACTION_FIELDS):
                    require(errors, field in action and action.get(field) not in (None, ""), f"{label}.{field} is required")
                cue_id = action.get("cue_id")
                require(errors, cue_id not in cue_ids, f"duplicate semantic action cue_id: {cue_id}")
                cue_ids.add(cue_id)
                start, end = action.get("audio_in"), action.get("audio_out")
                require(errors, isinstance(start, (int, float)) and isinstance(end, (int, float)) and end > start, f"{label} audio range is invalid")
                actor_id, target_id = action.get("actor_id"), action.get("target_id")
                require(errors, actor_id in object_by_id, f"{label} references unknown actor_id: {actor_id}")
                require(errors, target_id in object_by_id, f"{label} references unknown target_id: {target_id}")
                action_type = action.get("action_type")
                if action_type in HIGH_RISK_ACTIONS and target_id in object_by_id:
                    roles = object_by_id[target_id].get("semantic_roles", [])
                    require(errors, "primary_subject" in roles, f"{label} high-risk action must target a primary_subject")
                samples = action.get("trajectory_samples", [])
                if action_type == "scan":
                    require(errors, isinstance(samples, list) and bool(samples), f"{label} scan requires trajectory_samples")
                    for sample_index, sample in enumerate(samples if isinstance(samples, list) else []):
                        sample_label = f"{label} trajectory sample {sample_index + 1}"
                        actor_bbox = sample.get("actor_bbox") if isinstance(sample, dict) else None
                        target_bbox = sample.get("target_bbox") if isinstance(sample, dict) else None
                        mask_bbox = sample.get("mask_bbox") if isinstance(sample, dict) else None
                        require(errors, valid_bbox(actor_bbox), f"{sample_label}.actor_bbox is invalid")
                        require(errors, valid_bbox(target_bbox), f"{sample_label}.target_bbox is invalid")
                        require(errors, valid_bbox(mask_bbox), f"{sample_label}.mask_bbox is invalid")
                        if valid_bbox(actor_bbox) and valid_bbox(target_bbox) and valid_bbox(mask_bbox):
                            intersection = intersect_bbox(target_bbox, mask_bbox)
                            require(errors, intersection is not None, f"{sample_label} target and mask do not intersect")
                            if intersection is not None:
                                require(errors, bbox_inside(actor_bbox, intersection), f"{sample_label} leaves target-mask intersection")
                if action_type == "output":
                    producer_id, source_port_id = action.get("producer_id"), action.get("source_port_id")
                    require(errors, producer_id in object_by_id, f"{label} output producer_id is invalid")
                    require(errors, source_port_id in object_by_id, f"{label} output source_port_id is invalid")
                if action_type == "decompose_layers":
                    layer_ids = action.get("layer_ids")
                    require(errors, isinstance(layer_ids, list) and len(layer_ids) >= 3, f"{label} requires at least three layer_ids")
                    layers = [object_by_id.get(item) for item in layer_ids] if isinstance(layer_ids, list) else []
                    require(errors, all(layer is not None for layer in layers), f"{label} references unknown layer_ids")
                    if layers and all(layer is not None for layer in layers) and target_id in object_by_id:
                        source_ids = {layer.get("source_id") for layer in layers}
                        require(errors, len(source_ids) == 1, f"{label} layers must share one source_id")
                        require(errors, source_ids == {object_by_id[target_id].get("source_id")}, f"{label} layers must share the target source_id")
                        require(errors, action.get("decomposition_parent_id") == target_id, f"{label} decomposition_parent_id must equal target_id")

    occlusions = linked["occlusion_allowlist_path"]
    if occlusions is not None:
        require(errors, occlusions.get("status") == "PASS", "occlusion report status must PASS")
        require(errors, occlusions.get("undeclared_overlaps") == [], "undeclared overlaps must be empty")
        require(errors, occlusions.get("caption_overlaps") == [], "caption overlaps must be empty")
        allowlist = occlusions.get("allowlist")
        require(errors, isinstance(allowlist, list), "occlusion allowlist must be an array")
        for index, item in enumerate(allowlist if isinstance(allowlist, list) else []):
            label = f"occlusion allowlist item {index + 1}"
            require(errors, item.get("front_id") in object_by_id, f"{label}.front_id is invalid")
            require(errors, item.get("back_id") in object_by_id, f"{label}.back_id is invalid")
            require(errors, valid_bbox(item.get("allowed_region")), f"{label}.allowed_region is invalid")

    silent = linked["silent_review_path"]
    if silent is not None:
        reviews = silent.get("reviews")
        require(errors, isinstance(reviews, list) and bool(reviews), "silent review must contain reviews")
        for index, review in enumerate(reviews if isinstance(reviews, list) else []):
            label = f"silent review {index + 1}"
            for field in ("time_seconds", "main_subject", "action", "visible_result", "matches_spoken_line"):
                require(errors, review.get(field) not in (None, ""), f"{label}.{field} is required")
            require(errors, review.get("status") == "PASS", f"{label}.status must PASS")

    recipes = linked["motion_recipe_ledger_path"]
    if recipes is not None:
        items = recipes.get("recipes")
        require(errors, isinstance(items, list) and bool(items), "motion recipe ledger must contain recipes")
        for index, item in enumerate(items if isinstance(items, list) else []):
            label = f"motion recipe {index + 1}"
            for field in ("cue_id", "recipe", "source_kind", "implementation"):
                require(errors, item.get(field) not in (None, ""), f"{label}.{field} is required")


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
    is_v11 = schema_version in {"audio-locked-episode-1.1", "audio-locked-episode-1.2"}
    is_v12 = schema_version == "audio-locked-episode-1.2"

    project = data.get("project", {})
    require(errors, bool(project.get("title")), "project.title is required")
    require(errors, project.get("orientation") in {"horizontal", "vertical"}, "project.orientation must be horizontal or vertical")
    expected = {"horizontal": ("16:9", "1920x1080"), "vertical": ("9:16", "1080x1920")}
    if project.get("orientation") in expected:
        ratio, resolution = expected[project["orientation"]]
        require(errors, project.get("aspect_ratio") == ratio, f"aspect_ratio must be {ratio}")
        require(errors, project.get("resolution") == resolution, f"resolution must be {resolution}")
    duration = project.get("target_duration_seconds")
    if duration is not None:
        require(errors, isinstance(duration, (int, float)) and duration > 0, "target duration must be positive when provided")

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
        if is_v12:
            validate_v12_evidence(errors, data, manifest)

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
        if is_v12:
            require(errors, front.get("semantic_action_status") == "PASS", "front40 semantic-action gate must PASS")
            require(errors, front.get("physical_boundary_status") == "PASS", "front40 physical-boundary gate must PASS")
            require(errors, front.get("silent_readability_status") == "PASS", "front40 silent-readability gate must PASS")
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
        if is_v12:
            require(errors, final.get("semantic_action_status") == "PASS", "final semantic-action gate must PASS")
            require(errors, final.get("physical_boundary_status") == "PASS", "final physical-boundary gate must PASS")
            require(errors, final.get("silent_readability_status") == "PASS", "final silent-readability gate must PASS")
            require(errors, final.get("output_origin_status") == "PASS", "final output-origin gate must PASS")
            require(errors, final.get("same_source_layer_status") == "PASS", "final same-source layer gate must PASS")
        duration_for_qa = duration if isinstance(duration, (int, float)) and duration > 0 else 0
        required_frames = max(24, math.ceil(duration_for_qa / 10))
        required_crops = max(8, math.ceil(duration_for_qa / 30))
        require(
            errors,
            isinstance(final.get("original_size_frame_count"), int)
            and final["original_size_frame_count"] >= required_frames,
            f"at least {required_frames} original-size frames are required for this duration",
        )
        require(
            errors,
            isinstance(final.get("dense_crop_count"), int)
            and final["dense_crop_count"] >= required_crops,
            f"at least {required_crops} dense crops are required for this duration",
        )
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
