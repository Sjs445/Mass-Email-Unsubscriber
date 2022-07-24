import email
import os
import quopri
import re
import requests
import lxml.html

from collections import defaultdict
from email.header import decode_header
from email.message import Message
from email.header import Header
from imaplib import IMAP4_SSL
from typing import DefaultDict, List, Tuple


class EmailUnsubscriber:
    """Email Unsubscriber Class"""

    UNSUBSCRIBE_KEYWORDS = [
        "unsubscribe",
        "[unsubscribe]",
        "exclude",
        "opt-out",
        "opt out",
        "if you no longer wish to receive this email",
    ]
    SUPPORTED_IMAP_SERVERS = {"yahoo": "imap.mail.yahoo.com"}

    def __init__(self, email_type: str) -> None:
        """Connect to the email's imap server by email_type.

        Args:
            email_type (str): The email type.

        Raises:
            Exception: If email_type is not supported.
        """
        if email_type not in self.SUPPORTED_IMAP_SERVERS:
            raise Exception(f"{email_type} is not a supported email yet.")

        self.email_type = email_type

        # Now login to the imap server
        imap_server = self.SUPPORTED_IMAP_SERVERS[email_type]
        self.imap = IMAP4_SSL(imap_server)

        self.unsubscriber_info: DefaultDict[str, List[dict]] = defaultdict(list)

    def __del__(self) -> None:
        """Disconnect from the imap server upon calling the destructor."""
        self.logout()

    def logout(self) -> None:
        """Logout of the imap server."""
        if hasattr(self, "imap") and self.imap.state != "LOGOUT":
            self.imap.logout()

    def login(self, email_username: str, email_password: str) -> bool:
        """Login to the imap server with the passed in username and password.

        Args:
            email_username (str): The email username. Must be in the form 'x@example.com'
            email_password (str): The password.

        Raises:
            Exception: If email is in incorrect format
            Exception: If username and password is incorrect.
        """
        if not re.match(
            r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email_username
        ):
            # Return early if email is in the incorrect format.
            print(f"Email: '{email_username}' not in correct format")
            return False

        # NOTE: Can raise Exception if email_username and password is incorrect.
        try:
            self.imap.login(email_username, email_password)
        except:
            return False
        return True

    def get_unsubscribe_links_from_inbox(
        self, how_many: int = None, order_by: str = "desc"
    ) -> None:
        """Iterate through the Inbox looking through the email body for
        words in `self.UNSUBSCRIBE_KEYWORDS`.
        If one of the keywords is found in the email body we look for a
        possible link that is following the position of said found keyword.

        Args:
            how_many (int, optional): Number of emails to fetch from inbox descending.
                Defaults to all emails in the Inbox.
            order_by (str, optional): Method of getting the emails, i.e. 'desc', 'asc'.
                Defaults to 'desc'.
        """
        status, messages = self.imap.select("INBOX")
        if status != "OK":
            raise Exception(f"Could not select Inbox...\tGot status: {status}")

        # If the inbox retrieval is successful but there are no emails
        # we can return early.
        if not messages or not messages[0] or not int(messages[0]):
            return

        number_of_emails = int(messages[0])

        # set how we fetch and order getting the emails.
        range_params: tuple = ()
        if order_by == "desc":
            how_many = how_many or 0
            range_params = (number_of_emails, number_of_emails - how_many, -1)
        elif order_by == "asc":
            how_many = how_many or number_of_emails
            range_params = (0, how_many)
        else:
            how_many = how_many or number_of_emails
            range_params = (how_many, 0, -1)

        # We can't fetch more emails than exist in the Inbox.
        if how_many > number_of_emails:
            raise Exception(
                "how_many can't be greater than total number of emails in Inbox:"
                f" {number_of_emails}"
            )

        print("Fetching emails...")
        for i in range(*range_params):
            response, msg = self.imap.fetch(str(i), "(RFC822)")

            if response != "OK":
                raise Exception(f"Unable to fetch email: {i}\Response: {response}")

            # Get the email as an email object
            email_msg = email.message_from_bytes(msg[0][1])

            # Get the email sender and convert from bytes if necessary
            email_from, email_subject = self.decode_from_and_subject(
                email_msg["From"], email_msg["Subject"]
            )

            # Get unsubscribe links
            unsubscribe_links = self._get_unsubscribe_links_from_email(
                email_msg, email_subject
            )

            if unsubscribe_links:
                self.unsubscriber_info[email_from].append(
                    {"subject": email_subject, "links": unsubscribe_links}
                )

        # Close the INBOX
        self.imap.close()
        print("Done fetching emails!")

    @staticmethod
    def decode_from_and_subject(
        email_from: Header = None, email_subject: Header = None
    ) -> Tuple[str, str]:
        """Decode the from and subject.

        Args:
            email_from (Header, optional): Email From Header. Defaults to None.
            email_subject (Header, optional): Email Subject. Defaults to None.

        Returns:
            Tuple[str, str]: The email_from and email_subject
        """
        email_from_bytes, from_encoding = decode_header(email_from)[0]
        email_subject_bytes, subject_encoding = decode_header(email_subject)[0]

        # Decode the email_from and email_subject from bytes. We do this by doing
        # a series of checks:
        #
        #   1. If the from/subject is of type bytes we decode it from the given
        #       encoding.
        #   2. The encoding may have not been returned from decode_header().
        #       In this case we can just perform a type conversion to string.
        #
        if isinstance(email_from_bytes, bytes) and from_encoding:
            email_from_str = email_from_bytes.decode(from_encoding)
        else:
            email_from_str = str(email_from_bytes)

        if isinstance(email_subject_bytes, bytes) and subject_encoding:
            email_subject_str = email_subject_bytes.decode(subject_encoding)
        else:
            email_subject_str = str(email_subject_bytes)

        return email_from_str, email_subject_str

    @classmethod
    def _get_unsubscribe_links_from_email(
        cls, email_msg: Message, email_subject: str
    ) -> List[str]:
        """Takes an email message object and parses the body to find links
        that will (hopefully) unsubscribe us from the email.

        Args:
            email_msg (Message): The email Message object.
            email_subject (str): The email subject. Printed to the console
             if decoding the email fails.

        Returns:
            List[str]: A list of possible unsubscribe links from the email Message.
        """
        unsubscribe_links = []

        # A multipart email message may contain both a text/plain AND text/html email.
        if email_msg.is_multipart():

            for part in email_msg.walk():

                # Get the Content-Type
                content_type = part.get_content_type()
                body = part.get_payload()

                # Parse a text/plain email
                if content_type == "text/plain":
                    try:
                        body = quopri.decodestring(body).decode(
                            "utf-8", errors="ignore"
                        )
                    except Exception as e:
                        print(
                            f"Was unable to decode body for email: {email_subject}\nError: {e}"
                        )
                        continue
                    unsubscribe_links = cls._get_unsubscribe_links_from_text_plain(
                        body=body, unsubscribe_links=unsubscribe_links
                    )

                # Parse a text/html email
                elif content_type == "text/html":
                    try:
                        body = quopri.decodestring(body).decode(
                            "utf-8", errors="ignore"
                        )
                    except Exception as e:
                        print(
                            f"Was unable to decode body for email: {email_subject}\nError: {e}"
                        )
                        continue
                    unsubscribe_links = cls._get_unsubscribe_links_from_html(
                        body=body, unsubscribe_links=unsubscribe_links
                    )

        # When the email is not multipart we can pass decode=True to get_payload() to decode the email for us.
        else:
            content_type = email_msg.get_content_type()
            body = email_msg.get_payload(decode=True).decode("utf-8", "replace")

            if content_type == "text/plain":
                unsubscribe_links = cls._get_unsubscribe_links_from_text_plain(
                    body=body, unsubscribe_links=unsubscribe_links
                )
            elif content_type == "text/html":
                unsubscribe_links = cls._get_unsubscribe_links_from_html(
                    body=body, unsubscribe_links=unsubscribe_links
                )

        return unsubscribe_links

    @classmethod
    def _get_unsubscribe_links_from_html(
        cls, body: str, unsubscribe_links: list = None
    ) -> list:
        """Look for unsubscribe links in the body of the email
        as an html email.

        Args:
            body (str): The body of the email.
            unsubscribe_links (list, optional): The current found unsubscribe links.

        Returns:
            list: The unsubscribe links found.
        """
        unsubscribe_links = unsubscribe_links.copy() or []

        # Scrub the html by removing \n and \r characters
        html = body.replace("\n", "").replace("\r", "")

        # Parse the html using lxml
        element_tree = lxml.html.fromstring(html)

        # Get html <a> elements that only contain unsubscribe keywords
        # For example <a href="https://example_link.com/unsub_from_me">unsubscribe</a>
        for unsub_keyword in cls.UNSUBSCRIBE_KEYWORDS:

            # Semi HACK way of checking for upper case characters, use .title()
            link_elements = element_tree.xpath(
                f'.//a[contains(text(), "{unsub_keyword}")]'
            ) or element_tree.xpath(
                f'.//a[contains(text(), "{unsub_keyword.title()}")]'
            )

            # If any links are found get them by accessing the 'href' attribute
            if link_elements is not None and isinstance(link_elements, list):
                for element in link_elements:
                    found_link = element.attrib.get("href")

                    if found_link and found_link not in unsubscribe_links:
                        unsubscribe_links.append(found_link)

        return unsubscribe_links

    @classmethod
    def _get_unsubscribe_links_from_text_plain(
        cls, body: str, unsubscribe_links: list = None
    ) -> list:
        """Look for unsubscribe links in the body of the email as a
        plain text email.

        Args:
            body (str): The body of the email.
            unsubscribe_links (list, optional): The unsubscribe links found.

        Returns:
            list: The unsubscribe links found.
        """
        unsubscribe_links = unsubscribe_links.copy() or []

        # Look for unsubscribe keywords, some emails have totally different keywords used for their unsubscribe hyperlinks.
        for unsub_keyword in cls.UNSUBSCRIBE_KEYWORDS:

            unsub_idx = body.lower().find(unsub_keyword)

            if unsub_idx != -1:

                # Remove \n and \r characters out of the body to sanitize the link.
                trimmed_body = body[unsub_idx:].replace("\n", "").replace("\r", "")

                # Get the link following the unsubscribe keyword
                match = re.search(
                    r"(?:(?:https?):\/\/)[\w/\-?=%~.]+\.[\w/\-&?=%~]+",
                    trimmed_body,
                )

                # If we've found the link check first to make sure we haven't found this link already.
                if match and match.group() not in unsubscribe_links:
                    unsubscribe_links.append(match.group())

        return unsubscribe_links

    def unsubscribe_from_emails_with_links(self, unsubscribe_from: str = "all") -> None:
        """Try to unsubscribe from getting emails by sending a GET request to
        the unsubscribe_links. Stores the response of each request in the
        `self.unsubscriber_info` dictionary.

        Args:
            unsubscribe_from (str, optional): A sender to unsubscribe from. Defaults to 'all'.
        """

        if unsubscribe_from == "all":
            for emailer in self.unsubscriber_info:

                # If this emailer has unsubscribe links go through and try each link. If we encounter a '200 OK'
                # status set the text response as a new key in the unsubscriber_info dictionary.
                self.unsubscribe_and_write_response(unsubscribe_from, emailer)

        else:
            emailer = self.unsubscriber_info.get(unsubscribe_from, [])

            if not emailer:
                print(f"{unsubscribe_from} does not exist.")
                return

            self.unsubscribe_and_write_response(unsubscribe_from, emailer)

    def unsubscribe_and_write_response(
        self, unsubscribe_from: str, emailer: List[dict]
    ) -> None:
        """Unsubscribes from emails and writes the html responses.

        Args:
            unsubscribe_from (str): The emailer we're attempting to unsubscribe from.
            emailer (List[dict]): A list of dictionaries containing emails and unsubscribe links.
        """
        for email in emailer:
            print(
                f"\nAttempting to unsubscribe from: {unsubscribe_from}\nLinks found in email: {email.get('subject')}"
            )

            for idx, link in enumerate(email["links"]):
                print(f"Trying link: {link}")
                res = requests.get(link)

                if res.status_code == 200:
                    # Write the response as an html file.
                    path = f"unsubscribe_response/{unsubscribe_from}"
                    if not os.path.isdir(path):
                        os.makedirs(path)
                    with open(f"{path}/{email['subject']}{idx}.html", "w") as f:
                        f.write(res.text)
                    print(f"Wrote response as an HTML file to {path}")

        del self.unsubscriber_info[unsubscribe_from]

    def set_unsubscribe_link_confidence(self):
        """Method to set the confidence level of an unsubscribe link.
        We can do this by checking for the word 'unsubscribe' in the link.
        """
        # TODO
        pass

    def print_unsubscribe_info(self) -> None:
        """Prints the unsubscribe info neatly."""
        for emailer in self.unsubscriber_info:
            print(f"\n\nSender: {emailer}")
            for emails in self.unsubscriber_info[emailer]:
                print(f"Subject: {emails.get('subject')}")
                print(f"Unsubscribe Links Found:\n{emails.get('links')}")