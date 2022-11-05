# Mass Email Unsubscriber
Attempts to de-clutter your email and improve productivity by unsubscribing you from dreaded email lists.

# Requirements
To use this program you must have Python3 and install the required modules in the requirements.txt file:
`pip install -r requirements.txt`

You must also create a 3rd party app password for the program to login to your inbox. Instructions for Yahoo and Google can be found below. Support for more emails and OAuth to come.

NOTE: This program does not save your 3rd party app password in any way.

[Yahoo 3rd Party App Password Instructions](https://help.yahoo.com/kb/SLN15241.html)

[Google 3rd Party App Password Instructions](https://support.google.com/accounts/answer/185833?hl=en)

# Usage
```
▶ ./main.py
Enter your type of email, ex. 'yahoo', 'google', etc google
Enter your email: bobdoe@google.com
Enter your email third party app password
Login Successful
How many emails would you like to scan for?15
Fetching emails...
Progress: |████████████████████████████████████████████████████████████████████████████████████████████████████| 100.0% Complete
Done fetching emails!
Found 14 email senders to unsubscribe from!
+--------+----------------------------------------------------------------+
| number | sender                                                         |
+--------+----------------------------------------------------------------+
| 1      | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+
| 2      | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+
| 3      | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+
| 4      | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+
| 5      | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+
| 6      | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+
| 7      | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+
| 8      | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+
| 9      | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+
| 10     | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+
| 11     | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+
| 12     | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+
| 13     | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+
| 14     | An email spammer <no-reply@spam.mail.com>                      |
+--------+----------------------------------------------------------------+

Who would you like to unsubscribe from?
Choose from the following menu options:
-----------------------------------------------------------------
1 <---- Unsubscribes from all found emailers.
2 <---- Unsubscribe from one or a range of emailers.
3 <---- Prints the found unsubscribe info.
4 <---- Prints unsubscribe info verbose.
5 <---- Exits the program.
-----------------------------------------------------------------
2
Enter the emailer number or range (e.g. '1-10') of numbers whom which you would like to unsubscribe from: 10-14

Attempting to unsubscribe from: An email spammer <no-reply@spam.mail.com>
Links found in email: A spam email subject
Trying link: http://somespamlink.com/unsubscribe
Wrote response as an HTML file to unsubscribe_response/An email spammer <no-reply@spam.mail.com>

...
```

# TODOS/Ideas for future development
- Improve the searching for unsubscribe links.
- Convert all or part of this program to a command line interface?

`$ ./email_unsubscriber --type=google --email=myemailaddress@google.com --how_many=20 --all`
- Sometimes email sites require an extra step for getting unsubscribed from like clicking a confirmation after following the link. It might be possible to use a framework like Selenium to do this automatically.
- Integrate Yahoo/Google OAuth instead of a 3rd party app password.
- Add support for other email sites or personally hosted email.
- Implement a confidence attribute and show it to the user. We might not be that confident that a link is actually an unsubscribe link based on keywords in the link. Although some links might contain totally random words which would nullify that.
- Dump the unsubscribe results to a database/excel sheet instead of writing HTML responses locally.
