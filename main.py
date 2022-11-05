#!/usr/bin/env python3
import re
import sys
from email_unsubscriber import EmailUnsubscriber
from getpass import getpass
from printer import print_error, print_purple, print_success


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
    print_purple(
        f"Found {len(email_unsubscriber.unsubscriber_info)} email senders to unsubscribe from!"
    )
    email_unsubscriber.print_unsubscribe_info()

    # Get input from user and unsubscribe
    choice = ""
    while choice != "-1" and email_unsubscriber.unsubscriber_info:
        choice = input(
            "\nWho would you like to unsubscribe from?\n"
            "Choose from the following menu options:\n"
            "-----------------------------------------------------------------\n"
            "1 <---- Unsubscribes from all found emailers.\n"
            "2 <---- Unsubscribe from one or a range of emailers.\n"
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
                "Enter the emailer number or range (e.g. '1-10') of numbers whom which you would like to unsubscribe from: "
            )
            range = None
            if re.search(r"^\d+\-\d+$", set_choice):
                first_num = 0
                last_num = 0

                try:
                    first_num = re.search(r"^\d+", set_choice).group()
                    last_num = re.search(r"\d+$", set_choice).group()
                    first_num = int(first_num) - 1
                    last_num = int(last_num)
                    range = (first_num, last_num)
                except Exception as e:
                    print_error(
                        f"There was a problem processing your input: {set_choice}\nError: {e}"
                    )
            else:
                try:
                    set_choice = int(set_choice) - 1
                except Exception as e:
                    print_error(
                        f"There was a problem processing your input: {set_choice}\nError: {e}"
                    )

            email_unsubscriber.unsubscribe_from_emails_with_links(set_choice, range)
        elif choice == "3":
            email_unsubscriber.print_unsubscribe_info()
        elif choice == "4":
            email_unsubscriber.print_unsubscribe_info(verbose=True)
        elif choice == "5":
            break

    print_success("\nGoodbye!")
