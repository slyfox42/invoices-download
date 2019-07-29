import email
import imaplib
import os
import shutil
from datetime import date, timedelta
from save_invoice import get_file_path, move_invoice
import constants as c


class EmailManager:

    connection = None
    default_mailbox = "Inbox"

    def get_connection(self):
        if not self.connection:
            self.connection = imaplib.IMAP4_SSL(c.SMTP_SERVER)
            self.connection.login(c.EMAIL_ADDRESS,
                                  c.EMAIL_PASSWORD)
            self.connection.select(
                self.default_mailbox, readonly=True
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
        since = (date.today() - timedelta(7)).strftime("%d-%b-%Y")

        print("> Fetching emails...")
        self.get_connection()
        (result, messages) = self.connection.search(
            None, f'(FROM "{c.FROM_ADDRESS}" SENTSINCE "{since}" UNSEEN)'
        )

        if result == "OK":
            id_list = messages[0].split()
            print(len(id_list))
            messages = []

            for el in id_list[::-1]:
                (result, data) = self.connection.fetch(el, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])

                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue

                    messages.append(msg)

            for num in id_list:
                self.connection.copy(num, c.INVOICES_MAIL_FOLDER)
                self.connection.store(num, '+FLAGS', '\\Deleted')
                self.connection.expunge()

            self.close_connection()

            if not len(messages):
                print("> No messages with attachment(s) found.")
                return messages

            print("> Message(s) fetched successfully.")

            return messages

        else:
            self.close_connection()

            raise Exception(
                f"Connection Error searching for emails. Result: {result}"
            )


def save_invoices():

    email_manager = EmailManager()

    messages = email_manager.fetch_emails()
    if len(messages):
        attachments = email_manager.save_attachments(messages)
        file_paths = [get_file_path(attachment) for attachment in attachments]
        zipped = zip(attachments, file_paths)

        for invoice_path, new_file_path in zipped:
            move_invoice(invoice_path, new_file_path)
            print(new_file_path)

        shutil.rmtree(c.TMP_FOLDER)

if __name__ == "__main__":
    save_invoices()

