#!/usr/bin/env python
import SLAPI
import pprint
from smtplib import SMTP
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import parseaddr, formataddr
DeviationData={ 'transportationMode': 'bus,metro', 'lineNumber': '816,181,17,18,19'}
#http://api.sl.se/api2/deviations.json?key=<DIN API KEY> & transportation mode = <TRANSPORT MODE> and line number = <LINE NUMBER> & SiteID = <SiteID> & from date = <FROM DATE> & todate = <todate>
recipients=["recipient@mail.com"]
sender="sender@mail.com"
def SendEmail(sender, recipient, subject, body):
    """Send an email.

    All arguments should be Unicode strings (plain ASCII works as well).

    Only the real name part of sender and recipient addresses may contain
    non-ASCII characters.

    The email will be properly MIME encoded and delivered though SMTP to
    localhost port 25.  This is easy to change if you want something different.

    The charset of the email will be the first one out of US-ASCII, ISO-8859-1
    and UTF-8 that can represent all the characters occurring in the email.
    """

    # Header class is smart enough to try US-ASCII, then the charset we
    # provide, then fall back to UTF-8.
    header_charset = 'ISO-8859-1'

    # We must choose the body charset manually
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            body.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break

    # Split real name (which is optional) and email address parts
    sender_name, sender_addr = parseaddr(sender)
    recipient_name, recipient_addr = parseaddr(recipient)

    # We must always pass Unicode strings to Header, otherwise it will
    # use RFC 2047 encoding even on plain ASCII strings.
    sender_name = str(Header(unicode(sender_name), header_charset))
    recipient_name = str(Header(unicode(recipient_name), header_charset))

    # Make sure email addresses do not contain non-ASCII characters
    sender_addr = sender_addr.encode('ascii')
    recipient_addr = recipient_addr.encode('ascii')

    # Create the message ('plain' stands for Content-Type: text/plain)
    msg = MIMEText(body.encode(body_charset), 'plain', body_charset)
    msg['From'] = formataddr((sender_name, sender_addr))
    msg['To'] = formataddr((recipient_name, recipient_addr))
    msg['Subject'] = Header(unicode(subject), header_charset)

    # Send the message via SMTP to localhost:25
    smtp = SMTP("localhost")
    smtp.sendmail(sender, recipient, msg.as_string())
    smtp.quit()
def SendAlert(alert):
    subject = u"Alert in %s\r\n" % alert['Scope']
    body = u"%s: %s\r\n\t%s\r\n\r\n" % (alert['Scope'],alert['Header'],alert['Details'])
    SendEmail(sender, recipients, subject, body)
    return True
api=SLAPI.SLAPI()
result=api.GetDeviations(DeviationData=DeviationData)
print "Result:"
pprint.pprint(result)
if result is not None and result['StatusCode'] == 0 and len(result['ResponseData']) == 0:
    print "There are no alerts."
elif result == None:
    print "There was an error and the result from getting deviations was None."
    sys.exit(1)
else:
    print "There are %s alerts:" % len(result['ResponseData'])
    for alert in result['ResponseData']:
        print " - %s: %s\n\t%s" % (alert['Scope'],alert['Header'],alert['Details'])
        SendAlert(alert)
