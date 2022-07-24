#!/usr/bin/env python3
import sys
from email_unsubscriber import EmailUnsubscriber
from getpass import getpass

if __name__ == "__main__":
    email_type = input("Enter your type of email, ex. 'yahoo', 'google', etc ")
    email_unsubscriber = EmailUnsubscriber(email_type)

    logged_in = False
    while not logged_in:
        username = input("Enter your email: ")
        password = getpass("Enter your email third party app password")
        logged_in = email_unsubscriber.login(username, password)
        print("Login Failed") if not logged_in else print("Login Successful")

    how_many = input("How many emails would you like to scan for?")
    try:
        how_many = int(how_many)
    except Exception as e:
        sys.exit(f"Enter an integer. Error: {e}")

    # Begin scanning for unsubscribe emails
    email_unsubscriber.get_unsubscribe_links_from_inbox(how_many)
    print(
        f"Found {len(email_unsubscriber.unsubscriber_info)} email senders to unsubscribe from.\n\n"
    )
    email_unsubscriber.print_unsubscribe_info()

    # Get input from user and unsubscribe
    choice = ""
    while choice != "-1" and email_unsubscriber.unsubscriber_info:
        choice = input(
            "\n\nWho would you like to unsubscribe from?\n"
            "Type 'all' to unsubscribe from all emails found or type the sender's name.\n"
            "-1 to quit.\n"
        )
        if choice == "-1":
            break
        email_unsubscriber.unsubscribe_from_emails_with_links(choice)
        email_unsubscriber.print_unsubscribe_info()

    print("\nGoodbye!")
