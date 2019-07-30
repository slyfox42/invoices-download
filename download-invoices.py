import email
import imaplib
import os
import shutil
from datetime import date, timedelta
from save_invoices import get_file_path, SSH_Manager
import constants as c


class Email_Manager:

    connection = None
    default_mailbox = c.INVOICES_MAILBOX

    def get_connection(self):
        if not self.connection:
            self.connection = imaplib.IMAP4_SSL(c.SMTP_SERVER)
            self.connection.login(c.EMAIL_ADDRESS,
                                  c.EMAIL_PASSWORD)
            self.connection.select(
                self.default_mailbox, readonly=False
            )

        return self.connection

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def save_attachments(self, messages):
        print("Saving message attachments...")
        self.get_connection()

        if not os.path.exists(c.TMP_FOLDER):
            os.makedirs(c.TMP_FOLDER)

        attachments_paths = []
        for msg in messages:

            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue

                filename = part.get_filename()

                if not filename.endswith('.pdf'):
                    continue

                att_path = os.path.join(c.TMP_FOLDER, filename)
                attachments_paths.append(att_path)

                if not os.path.isfile(att_path):
                    fp = open(att_path, "wb")
                    fp.write(part.get_payload(decode=True))
                    fp.close()

        self.close_connection()

        print(
            f"{'Attachments' if len(attachments_paths) > 1 else 'Attachment'} saved correctly."
        )

        return attachments_paths

    def fetch_emails(
            self
    ):
        print("> Fetching emails...")
        since = (date.today() - timedelta(7)).strftime("%d-%b-%Y")
        self.get_connection()
        (result, messages) = self.connection.search(
            None, f'(FROM "{c.FROM_ADDRESS}" SINCE "{since}")'
        )

        if result == "OK":
            id_list = messages[0].split()
            messages = []

            for el in id_list:
                (result, data) = self.connection.fetch(el, "(RFC822)")

                msg = email.message_from_bytes(data[0][1])

                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue

                    messages.append(msg)

            self.close_connection()

            if not len(messages):
                print("> No messages with attachment(s) found.")
                return messages

            print(f'Fetched {len(id_list)} messages.')

            return messages

        else:
            self.close_connection()

            raise Exception(
                f"Connection Error searching for emails. Result: {result}"
            )


def save_invoices():

    email_manager = Email_Manager()
    ssh_manager = SSH_Manager()
    saved = list()
    try:
        messages = email_manager.fetch_emails()

        if len(messages):
            attachments = email_manager.save_attachments(messages)
            attachments = list(set(attachments))
            file_paths = [get_file_path(attachment) for attachment in attachments]
            zipped = zip(attachments, file_paths)

            for invoice_path, new_file_path in zipped:
                invoice = ssh_manager.scp_copy(invoice_path, new_file_path)
                saved.append(invoice)

            ssh_manager.close_connection()
            saved = [x for x in saved if x]
            invoices_list = '\n'.join(saved)
            print(f'Imported invoices:\n{invoices_list}' if len(saved) else 'No invoices imported.')
            shutil.rmtree(c.TMP_FOLDER)

    except Exception as e:
        print(e)

    finally:
        ssh_manager.close_connection()

if __name__ == "__main__":
    save_invoices()

