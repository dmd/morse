#!/usr/bin/env python3

import os
import sys
from datetime import datetime
import email.utils as utils
from email.mime.text import MIMEText
import smtplib

file_name = "post_log.txt"


def mail_message(message):
    to = "you@yourdomain.com"
    me = "morsecode@yourdomain.com"
    msg = MIMEText("")
    msg["message-id"] = utils.make_msgid()
    msg["Subject"] = f"MORSE: {message}"
    msg["From"] = me
    msg["To"] = to
    msg.set_payload(message)

    s = smtplib.SMTP("your.smtp.server", 587)
    s.login("username", "password")

    s.sendmail(me, [to], msg.as_string())


print("Content-Type: text/plain\n")

if os.environ["REQUEST_METHOD"] == "POST":
    content_length = int(os.environ.get("CONTENT_LENGTH", 0))
    post_data = sys.stdin.read(content_length)

    data_to_write = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {post_data}\n\n"

    try:
        with open(file_name, "a") as f:
            f.write(data_to_write)
        print(f"Data successfully appended to {file_name}")
        if len(post_data.replace(" ", "")) > 3:
            mail_message(post_data)
        else:
            print(f"Ignoring data: '{post_data}' because too short")
    except Exception as e:
        print(f"Error writing to file: {str(e)}")
else:
    print("This script only accepts POST requests.")
