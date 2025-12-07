# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

gallery-dl is a command-line program to download image galleries and collections from several image hosting sites. It's a cross-platform tool written in Python with extensive configuration options and powerful filenaming capabilities.

**Key characteristics:**
- Python 3.8+ required
- Core dependencies: requests library
- Supports 500+ extractors for different image hosting sites
- Configuration via JSON files
- Extensive test suite with real-world URL examples

## Development Commands

### Running Tests
```powershell
# Run all tests
python scripts\run_tests.py

# Run specific test module
python scripts\run_tests.py extractor

# Run individual test file
python scripts\run_tests.py test_formatter
```

### Building Documentation and Assets
```powershell
# Generate all documentation and completion files
python -m pip install .
make all              # On Unix-like systems (requires make)

# Individual components (run from repository root)
python scripts\supportedsites.py    # Generate docs/supportedsites.md
python scripts\options.py            # Generate docs/options.md
python scripts\man.py                # Generate man pages
python scripts\completion_bash.py    # Generate bash completion
python scripts\completion_zsh.py     # Generate zsh completion
python scripts\completion_fish.py    # Generate fish completion
```

### Running the Application
```powershell
# Run from source (development mode)
python -m gallery_dl [OPTIONS] URLS...

# Install in development mode
python -m pip install -e .

# After install, run directly
gallery-dl [OPTIONS] URLS...
```

### Building Executables
```powershell
# Build standalone executable
python scripts\pyinstaller.py
```

## Code Architecture

### Core Components

**1. Extractors** (`gallery_dl/extractor/`)
- Base class: `Extractor` in `common.py`
- Each site has its own extractor module
- Extractors yield messages via an iterator protocol:
  - `Message.Version` - protocol version
  - `Message.Directory` - directory metadata
  - `Message.Queue` - URLs for child extractors
  - `Message.Url` - file URLs with metadata
- Pattern matching via regex to map URLs to extractors
- Category/subcategory system for organizing extractors

**2. Jobs** (`gallery_dl/job.py`)
- `DownloadJob` - Download files to disk
- `UrlJob` - List URLs without downloading
- `DataJob` - Output metadata as JSON
- Jobs orchestrate the extraction and processing pipeline

**3. Downloaders** (`gallery_dl/downloader/`)
- `HttpDownloader` - Standard HTTP downloads
- `YtdlDownloader` - Integration with yt-dlp/youtube-dl
- `TextDownloader` - Save text content
- Handle retries, progress tracking, and file validation

**4. Postprocessors** (`gallery_dl/postprocessor/`)
- Process files after download
- Examples: metadata extraction, archiving, exec commands
- Chain multiple postprocessors via configuration

**5. Configuration System** (`gallery_dl/config.py`)
- JSON-based configuration with hierarchical structure
- Extractor-specific config via path: `("extractor", category, subcategory)`
- Global and per-extractor settings
- Support for interpolation and defaults

### Key Design Patterns

**Message Protocol:**
Extractors communicate via yielding Message tuples. This allows streaming processing without loading everything into memory.

**Lazy Initialization:**
Extractors use lazy initialization pattern - `initialize()` is called on first iteration, not in `__init__`. This allows quick extractor creation without network requests.

**Category Hierarchy:**
- `basecategory` - Shared base (e.g., "booru" for all booru sites)
- `category` - Site category (e.g., "danbooru")
- `subcategory` - Content type (e.g., "post", "pool", "tag")
- Enables shared configuration across similar extractors

**Formatter System:**
Powerful string formatting system in `formatter.py` supporting:
- Python format strings with extensions
- Conditional expressions
- Nested field access
- Custom functions via `util.GLOBALS`

## Testing

### Test Structure
- `test/test_*.py` - Unit tests for core modules
- `test/results/*.py` - Integration tests with real URL examples
- Each extractor should have corresponding test cases
- Tests validate extractor patterns, categories, and data extraction

### Running Specific Tests
```powershell
# Run extractor tests only
python scripts\run_tests.py extractor

# Run formatter tests
python scripts\run_tests.py formatter

# Run all tests except results (faster)
python scripts\run_tests.py cache config cookies downloader dt formatter job oauth output postprocessor text util
```

### Test Results System
The `test/results/` directory contains integration tests with real URLs. Set `GDL_TEST_RESULTS` environment variable to point to a custom results file if needed.

## Adding a New Extractor

1. Create `gallery_dl/extractor/sitename.py`
2. Define extractor class(es) inheriting from `Extractor` or specialized base (e.g., `GelbooruPageMixin`)
3. Set `category`, `subcategory`, `pattern` (regex), and `example` (example URL)
4. Implement `items()` method to yield messages
5. Add to `gallery_dl/extractor/__init__.py` module list if needed
6. Create test file `test/results/sitename.py` with URL examples
7. Update documentation by running `python scripts\supportedsites.py`

## Important Patterns

### Extractor Configuration
```python
# Access extractor-specific config
self.config(key, default)

# Access with fallback to alternate key
self.config2(key, key2, default)

# Accumulate values from multiple config levels
self.config_accumulate(key)
```

### Making Requests
```python
# Standard request with retry logic
response = self.request(url, fatal=True, notfound=None)

# POST with JSON
response = self.request(url, method="POST", json=data)

# With custom headers
response = self.request(url, headers={"Custom": "header"})
```

### Yielding Messages
```python
def items(self):
    yield Message.Version, 1
    yield Message.Directory, metadata
    
    for item in self._get_items():
        url = item["file_url"]
        data = {
            "id": item["id"],
            "filename": item["filename"],
            "extension": item["ext"],
            # ... more metadata
        }
        yield Message.Url, url, data
```

### Request Rate Limiting
```python
# Configure in extractor class
request_interval = 1.0  # seconds between requests
request_interval_min = 0.5  # minimum interval
```

## Configuration Files

**Locations** (Windows):
- `%APPDATA%\gallery-dl\config.json`
- `%USERPROFILE%\gallery-dl\config.json`
- `%USERPROFILE%\gallery-dl.conf`

**Structure:**
```json
{
    "extractor": {
        "base-directory": "~/gallery-dl/",
        "skip": true,
        "ignore-extension": false,
        "sitename": {
            "username": "user",
            "password": "pass",
            "filename": "{id}.{extension}",
            "directory": ["{category}", "{subcategory}"]
        }
    }
}
```

### Skip Behavior Options

**`skip`**: Controls whether to skip existing files
- `true` (default): Skip files that already exist
- `false`: Download all files, overwriting existing ones
- `"enumerate"`: Append numbers to avoid conflicts (file.jpg, file.2.jpg)
- `"abort:N"`: Stop after N consecutive skips
- `"terminate:N"`: Exit extraction after N consecutive skips

**`ignore-extension`**: When `true`, skip logic ignores file extensions
- Useful when files are converted to different formats after download
- Checks for any file with the same base name, regardless of extension
- Example: If `image.png` exists, will skip downloading `image.jpg`
- Default: `false`

## Common Utilities

**Text Processing:**
- `text.py` - String utilities (parse_int, parse_float, parse_query)
- `util.py` - General utilities (compile_expression for filters)
- `dt.py` - Date/time parsing

**Path Handling:**
- `path.py` - PathFormat class for building file paths
- Handles OS-specific path restrictions
- Template-based directory and filename formatting

**Archive/History:**
- `archive.py` - Track downloaded files via SQLite
- Prevents re-downloading same content

## Development Notes

### Python Version Support
Maintains compatibility with Python 3.8+ for broad platform support.

### Windows-Specific Considerations
- Uses PowerShell for shell commands
- Path handling accounts for Windows path restrictions
- ANSI color support detection for console output

### External Integrations
- yt-dlp/youtube-dl for video downloads
- FFmpeg for video conversion (Pixiv Ugoira)
- Browser cookie extraction support

### OAuth Flow
OAuth authentication for sites like Pixiv, DeviantArt:
```powershell
gallery-dl oauth:sitename
```

This starts an interactive OAuth flow and generates tokens for configuration.

## File Organization

```
gallery_dl/
├── extractor/        # Site-specific extractors
│   ├── common.py     # Base Extractor class
│   ├── message.py    # Message protocol definitions
│   └── *.py          # Individual site extractors
├── downloader/       # Download implementations
├── postprocessor/    # Post-download processors
├── job.py            # Job orchestration
├── config.py         # Configuration system
├── formatter.py      # String formatting
├── option.py         # CLI option parsing
├── output.py         # Logging and output
└── util.py           # Common utilities

test/
├── test_*.py         # Unit tests
└── results/          # Integration test URLs
    └── *.py

scripts/              # Build and utility scripts
docs/                 # Documentation
```
