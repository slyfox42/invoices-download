import re
import os
import subprocess
from fabric import Connection
from datetime import datetime, timedelta
from calendar import monthrange
import constants as c

DOC_DATE_REGEXP = {
    'Invoice': r"invoice date: (\d{2}\.\d{2}\.\d{4})",
    'Debit memo': r"debit memo date: (\d{2}\.\d{2}\.\d{4})",
    'Credit memo': r"credit memo date: (\d{2}\.\d{2}\.\d{4})",
}

MONTHS = {
    1: '01_Gennaio',
    2: '02_Febbraio',
    3: '03_Marzo',
    4: '04_Aprile',
    5: '05_Maggio',
    6: '06_Giugno',
    7: '07_Luglio',
    8: '08_Agosto',
    9: '09_Settembre',
    10: '10_Ottobre',
    11: '11_Novembre',
    12: '12_Dicembre'
}


def parse_document_date(invoice_path):
    process = subprocess.Popen(
        ['/usr/local/bin/pdftotext', '-raw', invoice_path, '-'], stdout=subprocess.PIPE)
    output = process.stdout.read().decode("utf-8")
    document_type = output.split('\n')[1]

    return re.search(DOC_DATE_REGEXP[document_type], output, re.IGNORECASE).group(1)


def get_file_path(invoice_path):
    invoice_date = parse_document_date(invoice_path)
    date_obj = datetime.strptime(invoice_date, '%d.%m.%Y')

    start_of_week = date_obj - timedelta(days=date_obj.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)  # Sunday

    _, last_day = monthrange(start_of_week.year, start_of_week.month)
    last_day_of_month_date = datetime.strptime(
        f'{start_of_week.year}.{start_of_week.month}.{last_day}', '%Y.%m.%d')

    start_day = start_of_week.strftime('%y.%m.%d')
    end_day = end_of_week.strftime(
        '%d') if end_of_week <= last_day_of_month_date else end_of_week.strftime("%m.%d")
    year_folder = date_obj.year
    month_folder = MONTHS[start_of_week.month]

    if date_obj.month == 1:
        start_of_month = datetime.strptime(
            f'{date_obj.year}.{date_obj.month}.01', '%Y.%m.%d')
        month_folder = month_folder if start_of_week.month <= date_obj.month else MONTHS[
            date_obj.month]
        start_day = start_day if start_of_week > start_of_month else start_of_month.strftime(
            '%y.%m.%d')

    if date_obj.month == 12:
        end_day = end_of_week.strftime(
            '%d') if end_of_week <= last_day_of_month_date else last_day_of_month_date.strftime('%d')

    return f'{year_folder}/{month_folder}/{start_day}-{end_day}/{os.path.basename(invoice_path)}'


def scp_copy(invoice_path, new_file_path):
    """ Securely copy the file to the server. """
    conn = Connection(
        host=c.SSH_HOSTNAME,
        user=c.SSH_USERNAME,
        connect_kwargs={
            "key_filename": c.SSH_KEY_PATH
        },
    )
    conn.config.sudo.password = c.SSH_PASSWORD
    directories = f'{c.SCP_BASE_PATH}/{os.path.dirname(new_file_path)}'
    # temporarily move te file to the user's $HOME directory
    filename = os.path.basename(invoice_path)
    tmp_file_path = f'/Users/{c.SSH_USERNAME}/{filename}'
    conn.put(invoice_path, tmp_file_path)
    # create correct directory with sudo under shared folder, move file
    conn.sudo(f'mkdir -p {directories}')
    conn.sudo(f'mv {tmp_file_path} {c.SCP_BASE_PATH}/{new_file_path}')

    conn.close()
