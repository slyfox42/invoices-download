import re
import subprocess
from datetime import datetime, timedelta
from calendar import monthrange

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
    process = subprocess.Popen(['/usr/local/bin/pdftotext', '-raw', invoice_path, '-'], cwd='/', stdout=subprocess.PIPE)
    output = process.stdout.read()
    document_type = output.split('\n')[1]

    return re.search(DOC_DATE_REGEXP[document_type], output, re.IGNORECASE).group(1)

invoice_date = '22.07.2019'

date_obj = datetime.strptime(invoice_date, '%d.%m.%Y')

start_of_week = date_obj - timedelta(days=date_obj.weekday())  # Monday
end_of_week = start_of_week + timedelta(days=6)  # Sunday
print(start_of_week)
print(end_of_week)

_, last_day = monthrange(date_obj.year, date_obj.month)
last_day_of_month_date = datetime.strptime(f'{last_day}.{date_obj.month}.{date_obj.year}', '%d.%m.%Y')

start = start_of_week.strftime('%y.%m.%d')
end = end_of_week.strftime('%d') if end_of_week <= last_day_of_month_date else end_of_week.strftime("%m-%d")

folder_name = f'{date_obj.year}/{MONTHS[start_of_week.month]}/{start}-{end}'


print(folder_name)

