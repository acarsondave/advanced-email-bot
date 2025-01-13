import logging

import smtplib

import ssl

import re

import random

import string

import time

import yaml

from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart

from tqdm import tqdm

from art import text2art

from googletrans import Translator



class EmailBot:

    def __init__(self, config_file):

        self.config = self.load_config(config_file)

        self.translator = Translator()

        self.domain_language_map = {

            "com": "en",  # Default language for generic domains

            "org": "en",  # Default language for generic domains

            "net": "en",  # Default language for generic domains

            "edu": "en",  # Default language for generic domains

            "gov": "en",  # Default language for generic domains

            "uk": "en",   # English - United Kingdom

            "us": "en",   # English - United States

            "ca": "en",   # English - Canada

            "au": "en",   # English - Australia

            "nz": "en",   # English - New Zealand

            "ie": "en",   # English - Ireland

            "sg": "zh-CN",  # Mandarin Chinese - Singapore

            "hk": "zh-CN",  # Mandarin Chinese - Hong Kong

            "tw": "zh-CN",  # Mandarin Chinese - Taiwan

            "cn": "zh-CN",  # Mandarin Chinese - China

            "jp": "ja",      # Japanese - Japan

            "kr": "ko",      # Korean - South Korea

            "de": "de",      # German - Germany

            "fr": "fr",      # French - France

            "es": "es",      # Spanish - Spain

            "it": "it",      # Italian - Italy

            "nl": "nl",      # Dutch - Netherlands

            "se": "sv",      # Swedish - Sweden

            "no": "no",      # Norwegian - Norway

            "dk": "da",      # Danish - Denmark

            "fi": "fi",      # Finnish - Finland

            "pt": "pt",      # Portuguese - Portugal

            "br": "pt",      # Portuguese - Brazil

            # Add more mappings as needed

        }



        # Configure logging

        self.logger = logging.getLogger(__name__)

        self.logger.setLevel(logging.DEBUG)



        # Create file handler which logs debug messages

        fh = logging.FileHandler('email_bot.log')

        fh.setLevel(logging.DEBUG)



        # Create console handler with a higher log level

        ch = logging.StreamHandler()

        ch.setLevel(logging.INFO)



        # Create formatter and add it to the handlers

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        fh.setFormatter(formatter)

        ch.setFormatter(formatter)



        # Add the handlers to the logger

        self.logger.addHandler(fh)

        self.logger.addHandler(ch)



    def load_config(self, config_file):

        with open(config_file, 'r') as file:

            return yaml.safe_load(file)



    def send_email(self, receiver_email, sent_emails, send_html=False):

        sender_name = self.config['email']['sender_name']

        sender_email = self.config['email']['sender_email']

        sender_password = self.config['email']['sender_password']

        smtp_server = self.config['email']['smtp_server']

        smtp_port = self.config['email']['smtp_port']

        subject = self.config['email']['subject']

        reply_to = self.config['email'].get('reply_to', sender_email)

        sent_emails_file_path = self.config['email']['sent_emails_file_path']



        if send_html:

            message = self.config['email']['html_message'].format(receiver_email, "{}")

        else:

            message = self.config['email']['message'].format(receiver_email, "{}")



        # Log sending email

        self.logger.debug(f"\033[1;34mSending email to {receiver_email}\033[0m")



        # Check recipient's domain for language detection

        recipient_domain = receiver_email.split('@')[-1]

        recipient_domain_extension = recipient_domain.split('.')[-1].lower()

        recipient_language = self.domain_language_map.get(recipient_domain_extension, None)



        if recipient_language:

            # Translate subject

            translated_subject = self.translate_message(subject, recipient_language)

            if translated_subject:

                subject = translated_subject



            # Translate message

            translated_message = self.translate_message(message, recipient_language)

            if translated_message:

                message = translated_message

            else:

                self.logger.warning(f"\033[1;33mTranslation not available for {recipient_language}. Sending original message.\033[0m")



            # Add second reply-to if available

            if 'second_reply_to' in self.config['email']:

                message = message.format(self.config['email']['second_reply_to'])



        try:

            if send_html:

                msg = MIMEMultipart("alternative")

                msg.attach(MIMEText(message, 'plain'))

                msg.attach(MIMEText(message, 'html'))

            else:

                msg = MIMEMultipart()

                msg.attach(MIMEText(message, 'plain'))



            msg['From'] = f"{sender_name} <{sender_email}>"

            msg['To'] = receiver_email

            msg['Subject'] = subject

            msg['Reply-To'] = reply_to



            context = ssl.create_default_context()

            with smtplib.SMTP(smtp_server, smtp_port) as server:

                server.starttls(context=context)

                server.login(sender_email, sender_password)

                server.sendmail(sender_email, receiver_email, msg.as_string())



            # Log email sent

            self.logger.info(f"\033[1;32mEmail sent to {receiver_email}\033[0m")

            sent_emails.append(receiver_email)

            self.save_sent_emails(sent_emails, sent_emails_file_path)  # Save sent emails immediately

            return True

        except smtplib.SMTPException as e:

            self.logger.error(f"\033[1;31mFailed to send email to {receiver_email}. SMTP Exception: {e}\033[0m")

            return False

        except Exception as e:

            self.logger.error(f"\033[1;31mAn error occurred while sending email to {receiver_email}: {e}\033[0m")

            return False



    def translate_message(self, message, target_lang):

        try:

            translation = self.translator.translate(message, dest=target_lang)

            return translation.text

        except Exception as e:

            self.logger.error(f"\033[1;31mError occurred during translation: {e}. Unable to translate message.\033[0m")

            return None



    def send_emails(self):

        email_file_path = self.config['email']['email_file_path']

        sent_emails_file_path = self.config['email']['sent_emails_file_path']



        all_emails = self.load_emails_from_file(email_file_path)

        valid_emails = [email for email in all_emails if self.is_valid_email(email)]



        sent_emails = self.load_sent_emails(sent_emails_file_path)



        total_emails = len(valid_emails)

        successful_emails = 0



        self.logger.info("\033[1;34mStarting email sending process...\033[0m")



        with tqdm(total=total_emails, desc="\033[1;36mSending Emails\033[0m") as pbar:

            for email in valid_emails:

                if email in sent_emails:

                    successful_emails += 1

                    pbar.update(1)

                    continue



                if self.send_email(email, sent_emails):

                    successful_emails += 1

                pbar.update(1)

                time.sleep(random.uniform(1, 3))



        self.logger.info("\033[1;34mEmail sending process completed.\033[0m")

        self.logger.info(f"\033[1;32mTotal emails sent: {successful_emails}/{total_emails}\033[0m")







    @staticmethod

    def is_valid_email(email):

        regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        return re.match(regex, email)



    @staticmethod

    def load_emails_from_file(file_path):

        with open(file_path, 'r') as file:

            return [line.strip() for line in file]



    @staticmethod

    def load_sent_emails(file_path):

        try:

            with open(file_path, 'r') as file:

                return [line.strip() for line in file]

        except FileNotFoundError:

            return []



    @staticmethod

    def save_sent_emails(sent_emails, file_path):

        with open(file_path, 'w') as file:  # Write mode to overwrite existing file

            for email in sent_emails:

                file.write(email + '\n')



def print_header():

    print("\033[1;33m")

    print(text2art("ACARMAIL BOT"))

    print("\033[0m")



def main():

    print_header()

    config_file = "config.yaml"

    email_bot = EmailBot(config_file)

    email_bot.send_emails()



if __name__ == "__main__":

    main()

