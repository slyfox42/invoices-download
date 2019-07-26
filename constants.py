import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

TMP_FOLDER = os.getenv("TMP_FOLDER", "")
APPLE_ADDRESS = os.getenv("APPLE_ADDRESS", "")

INVOICES_MAIL_FOLDER = os.getenv("INVOICES_MAIL_FOLDER", "")
INVOICES_BASE_PATH = os.getenv("INVOICES_BASE_PATH", "")
