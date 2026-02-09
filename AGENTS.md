# Repository Guidelines

## Project Structure & Module Organization
- `gallery_dl/` contains the core Python package.
- `gallery_dl/extractor/` holds site-specific extractors.
- `gallery_dl/downloader/` and `gallery_dl/postprocessor/` contain download and post-processing backends.
- `test/` stores unit tests; `test/results/` contains extractor result fixtures.
- `scripts/` includes developer tooling (`run_tests.py`, man/completion generators, release helpers).
- `docs/` is the documentation source; `docs/options.md` and `docs/supportedsites.md` are generated files.

## Architecture Overview
- `gallery_dl/__main__.py` forwards to `gallery_dl.main()` in `gallery_dl/__init__.py`.
- `extractor.find(url)` in `gallery_dl/extractor/__init__.py` selects the first matching extractor class.
- Extractors emit `Directory`, `Url`, and `Queue` messages; job classes in `gallery_dl/job.py` dispatch and process them.
- `DownloadJob` orchestrates filename/path formatting, archive checks, downloader backends, and postprocessors.
- Queued child URLs are resolved recursively, enabling multi-stage extraction flows.

## Build, Test, and Development Commands
- `python3 -m pip install -e .`: install in editable mode for local development.
- `pip install -r requirements.txt && pip install flake8 yt-dlp youtube-dl`: install dependencies used in CI.
- `make test`: run the default test suite via `scripts/run_tests.py`.
- `python3 scripts/run_tests.py extractor path`: run selected test modules (prefix `test_` is optional).
- `flake8 .`: run lint checks using `setup.cfg`.
- `make`: regenerate man pages, shell completions, and docs outputs (CI validates this path).

## Coding Style & Naming Conventions
- Target Python 3.8+ with 4-space indentation and ~79-character lines (`.editorconfig`).
- Follow Flake8 rules from `setup.cfg`, including project-specific per-file exceptions.
- Use `snake_case` for modules/functions/variables and `CamelCase` for classes.
- Name new extractor modules with lowercase site identifiers (for example `gallery_dl/extractor/example.py`).

## Testing Guidelines
- Tests use `unittest` and follow `test/test_*.py` naming.
- Add or update tests with each behavioral change; extractor updates may require `test/results/*.py` fixture updates.
- Run `make test` before pushing; run targeted modules during iteration for faster feedback.

## Commit & Pull Request Guidelines
- Mirror existing history style: `[scope] imperative summary` with issue/PR refs when applicable (example: `[pixiv] fix tag parsing (#1234)`).
- Keep commits focused and single-purpose.
- PRs should target `master` and include what changed, impacted modules/sites, and local validation steps run (`flake8 .`, `make test`, `make`).
- Link related issues and note any docs/config updates required by the change.

## Security & Configuration Tips
- Never commit credentials, cookies, or personal config values.
- Keep secrets in user-local config files (for example under `~/.config/gallery-dl/`) and sanitize logs/test data.
