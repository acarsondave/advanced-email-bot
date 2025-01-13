import imaplib
import email
import time
import datetime
from blessed import Terminal
from art import *

# Initialize blessed terminal
term = Terminal()

def delete_undelivered_emails():
    # Email account credentials
    username = "css@globalrevenuesavingsmarket.us"
    password = "Chimdindu7$"

    # IMAP settings
    imap_server = "imap.hostinger.com"
    port = 993

    # ASCII art for the header
    header_text = "ACARMAIL TOOL"
    header_art = text2art(header_text)

    # Add color to the header art
    colored_header_art = term.bold_red + header_art + term.normal

    # Initialize variables for total time elapsed, countdown, and deleted email counter
    total_start_time = time.time()
    countdown = 30
    deleted_emails_count = 0

    while True:
        try:
            # Connect to the IMAP server
            mail = imaplib.IMAP4_SSL(imap_server, port)

            # Login to your account
            mail.login(username, password)

            # Get the email provider from the IMAP server address
            if "hostinger" in imap_server:
                # Hostinger-specific folder structure
                inbox_folder = "INBOX"
                junk_folder = "INBOX.Junk"
                trash_folder = "INBOX.Trash"
            else:
                # Default folder structure
                inbox_folder = "INBOX"
                junk_folder = "Junk"
                trash_folder = "Trash"

                # Detect popular webmail providers and adjust folder names
                if "gmail" in imap_server:
                    junk_folder = "[Gmail]/Spam"
                    trash_folder = "[Gmail]/Bin"
                elif "yahoo" in imap_server:
                    junk_folder = "Spam"
                    trash_folder = "Deleted Items"
                elif "outlook" in imap_server:
                    junk_folder = "Junk"
                    trash_folder = "Deleted Items"

            # Print header
            print(term.clear + term.move_y(0) + term.move_x(0) + colored_header_art)

            # Start time for calculating total time elapsed
            start_time = time.time()

            # Check and delete undelivered emails in the Inbox folder
            status, _ = mail.select(inbox_folder)
            if status == 'OK':
                print(term.bold_green("Checking Inbox folder..."))
                deleted_emails_count += delete_undelivered_from_folder(mail)
            else:
                print(term.bold_red(f"Inbox folder '{inbox_folder}' does not exist."))

            # Check and delete undelivered emails in the Junk folder
            status, _ = mail.select(junk_folder)
            if status == 'OK':
                print(term.bold_yellow("Checking Junk folder..."))
                deleted_emails_count += delete_undelivered_from_folder(mail)
            else:
                print(term.bold_red(f"Junk folder '{junk_folder}' does not exist."))

            # Check and delete undelivered emails in the Trash folder
            status, _ = mail.select(trash_folder)
            if status == 'OK':
                print(term.bold_red("Checking Trash folder..."))
                deleted_emails_count += delete_undelivered_from_folder(mail)
            else:
                print(term.bold_red(f"Trash folder '{trash_folder}' does not exist."))

            # Logout from the server
            mail.logout()

            # Calculate total time elapsed
            total_end_time = time.time()
            total_time_elapsed = total_end_time - total_start_time

            # Print total time elapsed and deleted emails count
            print(term.bold(f"Total time elapsed: {datetime.timedelta(seconds=int(total_time_elapsed))}"))
            print(term.bold(f"Deleted undelivered emails count: {deleted_emails_count}"))

            # Countdown animation for waiting before the next check
            print(term.bold_blue("Waiting for next check..."), end=" ")
            for i in range(countdown, 0, -1):
                spinner = "|/-\\"
                print(term.move_x(0) + term.clear_eol + term.bold(f"Next check in {i:2d} seconds {spinner[i % len(spinner)]}"), end="\r")
                time.sleep(1)  # Adjust the sleep time as needed

        except KeyboardInterrupt:
            # If interrupted by keyboard (e.g., Ctrl+C), gracefully exit
            print(term.bold_red("\nBot stopped."))
            break
        except Exception as e:
            # Handle other exceptions gracefully
            print(term.bold_red("An error occurred:"), e)
            print(term.bold_red("Attempting to continue..."))

def delete_undelivered_from_folder(mail):
    # Search for emails with a specific subject
    status, messages = mail.search(None, '(HEADER Subject "Undelivered Mail Returned to Sender")')
    if status == 'OK':
        # Check if any messages are found
        if messages[0]:
            print(term.bold_yellow("Undelivered emails found. Deleting..."))

            # Iterate through each email found
            for num in messages[0].split():
                # Delete the email
                mail.store(num, '+FLAGS', '\\Deleted')

            # Expunge (permanently delete) the deleted emails
            mail.expunge()
            print(term.bold_green("Deleted undelivered emails successfully."))
            return len(messages[0].split())  # Return the number of deleted emails
        else:
            print(term.bold_blue("No undelivered emails found."))
            return 0
    else:
        print(term.bold_red("Failed to search for undelivered emails."))
        return 0

if __name__ == "__main__":
    delete_undelivered_emails()
