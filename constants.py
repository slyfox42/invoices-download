import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

TMP_FOLDER = os.getenv("TMP_FOLDER", "")
FROM_ADDRESS = os.getenv("FROM_ADDRESS", "")

INVOICES_MAIL_FOLDER = os.getenv("INVOICES_MAIL_FOLDER", "")

SSH_HOSTNAME = os.getenv("SSH_HOSTNAME", "")
SSH_USERNAME = os.getenv("SSH_USERNAME", "")
SSH_PASSWORD = os.getenv("SSH_PASSWORD", "")
SSH_KEY_PATH = os.getenv("SSH_KEY_PATH", "")

SCP_BASE_PATH = os.getenv("SCP_BASE_PATH", "")


