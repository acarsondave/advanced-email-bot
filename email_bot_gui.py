import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
from colorama import Fore, Style
from art import text2art

class EmailBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ACARMAIL BOT")
        self.root.geometry("800x600")

        self.load_config("config.yaml")

        self.create_menu()
        self.create_header()
        self.create_email_editor()
        self.create_send_button()
        self.create_status_bar()

    def load_config(self, config_file):
        with open(config_file, 'r') as file:
            self.config = yaml.safe_load(file)

    def create_menu(self):
        self.menu_bar = tk.Menu(self.root)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open...", command=self.open_file)
        self.file_menu.add_command(label="Save As...", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)

        self.help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.help_menu.add_command(label="About", command=self.show_about_dialog)

        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)

        self.root.config(menu=self.menu_bar)

    def create_header(self):
        self.header_frame = ttk.Frame(self.root)
        self.header_frame.pack(pady=20)

        self.header_label = ttk.Label(self.header_frame, text=text2art("ACARMAIL BOT"), font=('Helvetica', 20))
        self.header_label.pack()

    def create_email_editor(self):
        self.editor_frame = ttk.Frame(self.root)
        self.editor_frame.pack(pady=20)

        self.subject_label = ttk.Label(self.editor_frame, text="Subject:")
        self.subject_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.subject_entry = ttk.Entry(self.editor_frame, width=50)
        self.subject_entry.grid(row=0, column=1, padx=10, pady=5)

        self.message_label = ttk.Label(self.editor_frame, text="Message:")
        self.message_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.message_text = tk.Text(self.editor_frame, width=60, height=10)
        self.message_text.grid(row=1, column=1, padx=10, pady=5)

    def create_send_button(self):
        self.send_button = ttk.Button(self.root, text="Send Emails", command=self.send_emails)
        self.send_button.pack(pady=10)

    def create_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="", anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def open_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as file:
                email_content = file.read()
                self.message_text.delete(1.0, tk.END)
                self.message_text.insert(tk.END, email_content)

    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.message_text.get(1.0, tk.END))

    def show_about_dialog(self):
        about_text = "ACARMAIL BOT\n\nA sophisticated email bot GUI application.\n\nAuthor: Your Name"
        messagebox.showinfo("About", about_text)

    def send_email(self, receiver_email):
        sender_email = self.config['email']['sender_email']
        sender_password = self.config['email']['sender_password']
        smtp_server = self.config['email']['smtp_server']
        smtp_port = self.config['email']['smtp_port']
        subject = self.subject_entry.get()
        message = self.message_text.get(1.0, tk.END)
        sent_emails_file_path = self.config['email']['sent_emails_file_path']

        try:
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls(context=context)
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, receiver_email, msg.as_string())
            
            self.status_bar.config(text=f"Email sent to {receiver_email}", foreground="green")
            return True
        except smtplib.SMTPException as e:
            self.status_bar.config(text=f"Failed to send email to {receiver_email}. SMTP Exception: {e}", foreground="red")
            return False
        except Exception as e:
            self.status_bar.config(text=f"An error occurred while sending email to {receiver_email}: {e}", foreground="red")
            return False

    def send_emails(self):
        email_file_path = self.config['email']['email_file_path']
        sent_emails_file_path = self.config['email']['sent_emails_file_path']

        all_emails = self.load_emails_from_file(email_file_path)
        valid_emails = [email for email in all_emails if self.is_valid_email(email)]

        sent_emails = self.load_sent_emails(sent_emails_file_path)
        valid_emails = [email for email in valid_emails if email not in sent_emails]

        total_emails = len(valid_emails)
        successful_emails = 0

        self.status_bar.config(text="Starting email sending process...", foreground="blue")

        with tqdm(total=total_emails, desc="Sending Emails") as pbar:
            for email in valid_emails:
                if self.send_email(email):
                    successful_emails += 1
                    sent_emails.append(email)
                pbar.update(1)
                time.sleep(random.uniform(1, 3))

        self.save_sent_emails(sent_emails, sent_emails_file_path)

        self.status_bar.config(text=f"Email sending process completed. Total emails sent: {successful_emails}/{total_emails}", foreground="green")

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
        with open(file_path, 'a') as file:
            for email in sent_emails:
                file.write(email + '\n')

def main():
    root = tk.Tk()
    app = EmailBotGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
