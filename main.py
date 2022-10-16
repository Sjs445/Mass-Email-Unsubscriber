#!/usr/bin/env python3
import sys
from email_unsubscriber import EmailUnsubscriber
from getpass import getpass
from printer import print_error, print_success, print_warning

if __name__ == "__main__":
    email_type = input("Enter your type of email, ex. 'yahoo', 'google', etc ")
    email_unsubscriber = EmailUnsubscriber(email_type)

    logged_in = False
    while not logged_in:
        username = input("Enter your email: ")
        password = getpass("Enter your email third party app password")
        logged_in = email_unsubscriber.login(username, password)
        print_error("Login Failed") if not logged_in else print_success(
            "Login Successful"
        )

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
            "Choose from the following menu options:\n"
            "-----------------------------------------------------------------\n"
            "1 <---- Unsubscribes from all found emails.\n"
            "2 <---- Prompts for an email address to unsubscribe from from.\n"
            "3 <---- Prints the found unsubscribe info.\n"
            "4 <---- Prints unsubscribe info verbose.\n"
            "5 <---- Exits the program.\n"
            "-----------------------------------------------------------------\n"
        )
        set_choice = ""

        if choice == "1":
            set_choice = "all"
            email_unsubscriber.unsubscribe_from_emails_with_links(set_choice)
        elif choice == "2":
            set_choice = input(
                "enter the exact name shown in the SENDER section of the info"
            )
            email_unsubscriber.unsubscribe_from_emails_with_links(set_choice)
        elif choice == "3":
            email_unsubscriber.print_unsubscribe_info()
        elif choice == "4":
            email_unsubscriber.print_unsubscribe_info(verbose=True)
        if choice == "5":
            break

    print_success("\nGoodbye!")
