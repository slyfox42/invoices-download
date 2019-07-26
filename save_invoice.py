import re
import os
import shutil
import subprocess
from datetime import datetime, timedelta
from calendar import monthrange
import constants as c

DOC_DATE_REGEXP = {
    'Invoice': r"invoice date: (\d{2}\.\d{2}\.\d{4})",
    'Debit memo': r"debit memo date: (\d{2}\.\d{2}\.\d{4})",
    'Credit memo': r"credit memo date: (\d{2}\.\d{2}\.\d{4})",
}

MONTHS = {
    1: '01 Gennaio',
    2: '02 Febbraio',
    3: '03 Marzo',
    4: '04 Aprile',
    5: '05 Maggio',
    6: '06 Giugno',
    7: '07 Luglio',
    8: '08 Agosto',
    9: '09 Settembre',
    10: '10 Ottobre',
    11: '11 Novembre',
    12: '12 Dicembre'
}


def parse_document_date(invoice_path):
    process = subprocess.Popen(
        ['pdftotext', '-raw', invoice_path, '-'], stdout=subprocess.PIPE)
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

    return f'{c.INVOICES_BASE_PATH}/{year_folder}/{month_folder}/{start_day}-{end_day}/{os.path.basename(invoice_path)}'


def move_invoice(invoice_path, new_file_path):
    if os.path.exists(new_file_path):
        return

    directory = os.path.dirname(new_file_path)

    if not os.path.exists(directory):
        os.makedirs(directory)

    shutil.copyfile(invoice_path, new_file_path)

