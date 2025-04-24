# Eingürgerator

## Description

This is a console utility to find a right moment for Einbürgerungstest in Berlin VHS.
It searches for the available dates once every couple minutes and if it finds one, it opens the browser with the registration page.
You only need to enter your data really quick.

## How to use

Prerequisites: `python3`.

1. Clone the repository
2. Create a virtualenv and activate it: `python3 -m venv .venv && source .venv/bin/activate` (or `activate.fish` for the Fish shell)
3. Install the requirements: `pip install -r requirements.txt`
4. Run the script: `python einbürgerator.py`
