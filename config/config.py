"""Configuration settings for the Underwriting Dashboard application."""

import os
from pathlib import Path

# Base directories
PROJECT_ROOT = Path("C:/Users/MattBorgeson/OneDrive - B&R Capital/Programming Projects/Underwriting Dashboard")
DATABASE_DIR = PROJECT_ROOT / "database"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
os.makedirs(DATABASE_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Database settings
DATABASE_PATH = DATABASE_DIR / "underwriting_models.db"
DATABASE_TABLE = "underwriting_model_data"

# Deal directories
DEALS_ROOT = Path("C:/Users/MattBorgeson/B&R Capital/B&R Capital - Real Estate/Deals")
DEAL_STAGE_DIRS = [
    DEALS_ROOT / "0) Dead Deals",
    DEALS_ROOT / "1) Initial UW and Review",
    DEALS_ROOT / "2) Active UW and Review",
    DEALS_ROOT / "3) Deals Under Contract",
    DEALS_ROOT / "4) Closed Deals",
    DEALS_ROOT / "5) Realized Deals"
]

# Reference file
REFERENCE_FILE = PROJECT_ROOT / "Prompt" / "Underwriting Dashboard Project - Cell Value References.xlsx"
REFERENCE_SHEET = "UW Model - Cell Reference Table"

# File criteria
FILE_TYPES = [".xlsb", ".xlsm"]
FILE_INCLUDES = ["UW Model vCurrent"]
FILE_EXCLUDES = ["Speedboat"]
MIN_MODIFIED_DATE = "2024-07-15"  # YYYY-MM-DD format

# Monitoring settings
MONITORING_INTERVAL = 60  # seconds