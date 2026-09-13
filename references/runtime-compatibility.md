# Runtime compatibility

This Skill is not limited to Codex. Its planning documents, production ledger, Python validator, and QA contracts are portable to any agent or operator that can read and write files and run local commands.

## Capability levels

| Capability | Minimum requirement | Result |
| --- | --- | --- |
| Plan and validate | File access plus Python 3.10+ | Build manifests, validate stages, review evidence, and prepare an asset-needed list |
| Compose and render | Node.js, Remotion, and FFmpeg or an equivalent deterministic renderer | Produce timed video, audio, captions, frames, and technical QA |
| Generate visual assets automatically | A callable image-generation tool available to the agent | Create original text-free paper assets inside the production run |
| Work without image generation | User-supplied assets or a licensed local asset library | Continue composition and QA after provenance and crop margins are registered |

Codex is a strong fit when its runtime exposes file tools, command execution, and built-in image generation. Claude Code, Cursor, OpenAI Agents, and other local coding agents can run the same method when they provide equivalent file and command access. Their exact tool names may differ.

Image generation is optional for the workflow and required only for automatic creation of new visual assets. A runtime without image generation must set `mode` to `user_supplied` or `local_library` in `asset-generation.json`, keep `no_imagegen_fallback` ready, and never pretend that missing assets were generated.

## Deterministic production requirements

- Real narration remains the master timeline.
- Exact text, circles, arrows, masks, captions, and motion paths are rendered deterministically.
- The renderer must support exact-frame seeking and repeatable output.
- FFmpeg or an equivalent tool must decode the entire result and report media properties.
- Final visual acceptance still requires original-size rendered-frame inspection.

## What is not bundled

The repository does not include an image model, paid generation credits, private audio, copyrighted characters, fonts, BGM, episode footage, or a hosted rendering service. Users supply or lawfully generate their own assets and music.
