# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Einbürgerator is a Python console utility that monitors Berlin VHS (Volkshochschule) for available Einbürgerungstest (citizenship test) appointments. The application continuously polls the Berlin service website, and when appointments become available, it automatically opens the registration page in the browser.

## Architecture

This is a single-file Python application (`einbürgerator.py`) with a simple polling-based architecture:

- **Main Loop**: Continuously polls the Berlin service endpoint every 60-90 seconds (randomized intervals)
- **HTTP Session Management**: Uses `requests.Session` with retry logic for resilient HTTP communication
- **Response Processing**: Parses HTML responses to detect appointment availability
- **Browser Integration**: Uses `subprocess.run(["open", URL])` to launch the default browser on macOS

Key constants:
- `MAIN_PAGE`: Berlin service appointment booking page
- `REFRESH_PAGE`: Alternative endpoint (currently unused)
- `NO_APPOINTMENTS`: German text pattern indicating no available appointments

## Development Commands

### Setup Environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # or activate.fish for Fish shell
pip install -r requirements.txt
```

### Run Application
```bash
# Use virtual environment python
.venv/bin/python einbürgerator.py

# Show available services and options
.venv/bin/python einbürgerator.py --help

# Monitor specific service
.venv/bin/python einbürgerator.py --service trade-driving-license-3rd-countries
```

### Dependencies
The project uses minimal dependencies specified in `requirements.txt`:
- `requests` for HTTP operations (includes urllib3 with retry utilities)

## Important Implementation Details

- **Service Selection**: CLI supports multiple Berlin services via `--service` argument:
  - `leben-in-deutschland` (351180): Einbürgerungstest (citizenship test) - default
  - `trade-driving-license-3rd-countries` (327537): Trade driving license from 3rd countries
- The application includes retry logic for HTTP requests with exponential backoff
- User-Agent spoofing is explicitly avoided as Berlin.de detects it and returns 403 errors
- Random sleep intervals (60-90 seconds) prevent aggressive polling
- Successful appointment detection triggers browser opening and application exit
- Graceful handling of keyboard interrupts with statistics reporting
- Temporary HTML files are created for debugging purposes when appointments are found