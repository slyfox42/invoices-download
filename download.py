import email
import imaplib
import os
from datetime import datetime, date, timedelta
from email.utils import parsedate_tz, mktime_tz

OUTPUT_FOLDER = 'results'
# APPLE_ADDRESS = 'EMEA_Invoicing@email.apple.com'
APPLE_ADDRESS = 'federico@pixel.it'


class EmailManager:

    connection = None
    error = None
    attachments = {}
    default_mailbox = "Inbox"

    def get_connection(self):
        if not self.connection:
            self.connection = imaplib.IMAP4_SSL(os.getenv("SMTP_SERVER", ""))
            self.connection.login(os.getenv("EMAIL_ADDRESS", ""),
                                  os.getenv("EMAIL_PASSWORD", ""))
            self.connection.select(
                self.default_mailbox, readonly=False
            )  # so we can mark mails as read

        return self.connection

    def close_connection(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def save_attachments(self, messages):
        """
        Given a message, save its attachments to the specified
        download folder (default is .tmp)

        return: file path to attachment
        """
        print("Saving message attachments...")
        self.get_connection()

        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)

        attachments_paths = []
        for msg in messages:
            (name, address) = EmailManager.parse_email_address(msg["from"])

            for part in msg.walk():
                if part.get_content_maintype() == "multipart":
                    continue
                if part.get("Content-Disposition") is None:
                    continue

                filename = part.get_filename()

                if not filename.endswith('.pdf'):
                    continue

                att_path = os.path.join(OUTPUT_FOLDER, filename)
                attachments_paths.append(att_path)

                if not os.path.isfile(att_path):
                    fp = open(att_path, "wb")
                    fp.write(part.get_payload(decode=True))
                    fp.close()

        self.close_connection()

        print(
            f"{'Attachments' if len(attachments_paths) > 1 else 'Attachment'} saved correctly."
        )

    def get_first_unseen(
            self,
            since=(date.today() - timedelta(7)).strftime("%d-%b-%Y"),
    ):
        """
         Given a list of whitelisted addresses, fetches
         first unseen message from one of the addresses
         with an attachment in the body.

         return: msg object
         """
        print("> Fetching first unseen mail containing attachment...")
        self.get_connection()
        (result, messages) = self.connection.search(
            None, f'(FROM "{APPLE_ADDRESS}" SENTSINCE "{since}" UNSEEN)'
        )

        if result == "OK":
            id_list = messages[0].split()
            print(len(id_list))
            messages = []

            for el in id_list[::-1]:
                (result, data) = self.connection.fetch(el, "(RFC822)")
                msg = email.message_from_bytes(data[0][1])
                (name, address) = self.parse_email_address(msg["From"])

                for part in msg.walk():
                    if part.get_content_maintype() == "multipart":
                        continue
                    if part.get("Content-Disposition") is None:
                        continue

                    messages.append(msg)

            # for num in id_list:
            #     self.connection.copy(num, 'Fatture')
            #     self.connection.store(num, '+FLAGS', '\\Deleted')
            #     self.connection.expunge()

            self.close_connection()

            if not len(messages):
                print("> No messages with attachment(s) found.")
                return None

            print("> Message(s) fetched successfully.")

            return messages

        else:
            self.close_connection()

            raise Exception(
                f"Connection Error searching for emails. Result: {result}"
            )

    @staticmethod
    def parse_email_address(email_address):
        """
        Helper function to parse out the email address from the message

        return: tuple (name, address). Eg. ('John Doe', 'jdoe@example.com')
        """
        return email.utils.parseaddr(email_address)

    @staticmethod
    def parse_email_date(email_date):
        timestamp = mktime_tz(parsedate_tz(email_date))
        iso_string = datetime.utcfromtimestamp(timestamp).isoformat()

        return iso_string


def store_invoice():

    email_manager = EmailManager()

    messages = email_manager.get_first_unseen()
    if len(messages):
        email_manager.save_attachments(messages)


store_invoice()
