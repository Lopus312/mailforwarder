import smtplib,imaplib,email,itertools,threading,sys,getpass
from datetime import datetime
from configparser import ConfigParser
from os import path

# Welcome message
print(open('welcome.txt','r').read())

# Config.ini load
config = ConfigParser()
load = ' '
if path.isfile('./config.ini'):
    while load != 'y' and load != 'n':
        load = input('Chceš načíst uložené nastavení?(Y/n)').lower()
    if load == 'y':
        config.read('config.ini')

# Setting config variables
# IMAP
CONFIG_IMAP_EMAIL = None if load != 'y' else config.get('IMAP','IMAP_EMAIL')
CONFIG_IMAP_SERVER = None if load != 'y' else config.get('IMAP','IMAP_SERVER')
# SMTP
CONFIG_SMTP_EMAIL = None if load != 'y' else config.get('SMTP','SMTP_EMAIL')
CONFIG_SMTP_SERVER = None if load != 'y' else config.get('SMTP','SMTP_SERVER')
CONFIG_SMTP_PORT = None if load != 'y' else config.get('SMTP','SMTP_PORT')
# Other
CONFIG_TARGET_ADDRESS = None if load != 'y' else config.get('Other','TARGET_ADDRESS')
CONFIG_TARGET_BOX = None if load != 'y' else config.get('Other','TARGET_BOX')
CONFIG_TIMER = None if load != 'y' else config.get('Other','TIMER')


print(f'Základní Emailové servery:\n{"Nazev":^20}|{"IMAP":^24}|{"SMTP":^24}|{"Port":^4}\n{"-"*75}\n'
      f'{"Gmail":<20}{"imap.gmail.com":>25}{"smtp.gmail.com":>25}{"465":>5}\n'
      f'{"Outlook":<20}{"outlook.office365.com":>25}{"smtp.office365.com":>25}{"587":>5}\n')

# IMAP
IMAP_EMAIL = input('Přihlaš se přes email ze kterého budeš chtít přeposílat emaily\nLogin(email):') if CONFIG_IMAP_EMAIL == None else CONFIG_IMAP_EMAIL
IMAP_PASSWORD = getpass.getpass("Heslo:") if CONFIG_IMAP_EMAIL == None else getpass.getpass(f'{IMAP_EMAIL}\nHeslo:')
IMAP_SERVER = input('IMAP Server:') if CONFIG_IMAP_SERVER == None else CONFIG_IMAP_SERVER

# SMTP
if CONFIG_SMTP_EMAIL == None:
    x = ' '
    # Use different SMTP email if connection is blocked
    while x != 'y' and x != 'n':
        x = input('Pužít stejný email i pro odesílání emailů(Y/n)?').lower()
    SMTP_EMAIL = IMAP_EMAIL if x=='y' else input('Login:')
    SMTP_PASSWORD = IMAP_PASSWORD if x=='y' else getpass.getpass("Heslo:")
    SMTP_SERVER = IMAP_SERVER if x=='y' else input('SMTP Server:')
    SMTP_PORT = input('SMTP Port:')
else:
    SMTP_EMAIL = IMAP_EMAIL if CONFIG_SMTP_EMAIL == None else CONFIG_SMTP_EMAIL
    SMTP_PASSWORD = IMAP_PASSWORD if CONFIG_SMTP_EMAIL == None else getpass.getpass(f'{SMTP_EMAIL}\nHeslo:')
    SMTP_SERVER = IMAP_SERVER if CONFIG_SMTP_SERVER == None else CONFIG_SMTP_SERVER
    SMTP_PORT = input('SMTP Port:') if CONFIG_SMTP_PORT == None else CONFIG_SMTP_PORT

# Other
TARGET_ADDRESS = input('Na jakou adresu chceš emaily přeposlat?:') if CONFIG_TARGET_ADDRESS == None else CONFIG_TARGET_ADDRESS
x = input('Z jaké schránky chceš brát emaily?(default:inbox)') if CONFIG_TARGET_BOX == None else CONFIG_TARGET_BOX
TARGET_BOX = x if x!='' else 'inbox'
x = input('Zadej jak často bude program zjišťovat jestli nepřišel nový email v sekundách(30 default):') if CONFIG_TIMER == None else CONFIG_TIMER
TIMER  = int(x) if x!='' else 30

if load != 'y':
    # Saving settings
    print('VŠECHNA DATA KROMĚ HESEL BUDOU ULOŽENA JAKO PROSTÝ TEXT V LEHCE PŘÍSTUPNÉM SOUBORU')
    while x != 'y' and x != 'n':
        x = input('Chceš uložit nastavení?(Y/n)').lower()

    if x == 'y':
        config.add_section('IMAP')
        config.set('IMAP','IMAP_EMAIL',IMAP_EMAIL)
        config.set('IMAP','IMAP_SERVER',IMAP_SERVER)
        config.add_section('SMTP')
        config.set('SMTP','SMTP_EMAIL',SMTP_EMAIL)
        config.set('SMTP','SMTP_SERVER',SMTP_SERVER)
        config.set('SMTP','SMTP_PORT',SMTP_PORT)
        config.add_section('Other')
        config.set('Other','TARGET_ADDRESS',TARGET_ADDRESS)
        config.set('Other','TARGET_BOX',TARGET_BOX)
        config.set('Other','TIMER',str(TIMER))
        config.write(open('config.ini','w+'))

print("\n")
#IMAP_EMAIL = 'jaromir.kucera@student.spsmb.cz'
#IMAP_PASSWORD = open('IMAPPASSWORD.txt','r').read()
#IMAP_SERVER = 'outlook.office365.com'

#SMTP_EMAIL = 'lopus2056@gmail.com'
#SMTP_PASSWORD = open('SMTPPASSWORD.txt','r').read()
#SMTP_SERVER = 'smtp.gmail.com'
#SMTP_PORT = 465
#TARGET_ADDRESS = 'lopus312@gmail.com'


# Test IMAP connection
mail = imaplib.IMAP4_SSL(IMAP_SERVER)
try:
    mail.login(IMAP_EMAIL, IMAP_PASSWORD)
except imaplib.IMAP4.error:
    print('AUTHENTICATION FAILED\nInvalid IMAP login credentials')
    exit(1)

print(f'Successfully logged in IMAP as {IMAP_EMAIL}')
mail.logout()

# Test SMTP connection
server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)

server.login(SMTP_EMAIL, SMTP_PASSWORD)

# Selecting mail box
mail.select(TARGET_BOX)

# we'll search using the ALL criteria to retrieve
# every message inside the inbox
# it will return with its status and a list of ids
status, data = mail.search(None, 'ALL')

# the list returned is a list of bytes separated
# by white spaces on this format: [b'1 2 3', b'4 5 6']
# so, to separate it first we create an empty list
mail_ids = []
# then we go through the list splitting its blocks
# of bytes and appending to the mail_ids list
for block in data:
    # the split function called without parameter
    # transforms the text or bytes into a list using
    # as separator the white spaces:
    # b'1 2 3'.split() => [b'1', b'2', b'3']
    mail_ids += block.split()

LAST_MAIL = len(mail_ids)
server.quit()
      
def reload():
    global LAST_MAIL

    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(IMAP_EMAIL, IMAP_PASSWORD)
    mail.select(TARGET_BOX)

    status, data = mail.search(None, 'ALL')
    mail_ids = []
    for block in data:
        mail_ids += block.split()


    if len(mail_ids)>LAST_MAIL:

        # Iterate over mail_ids from lastId
        for id in itertools.islice(mail_ids,LAST_MAIL,None):
                # the fetch function fetch the email given its id
                # and format that you want the message to be
                status, data = mail.fetch(id, '(RFC822)')

                # the content data at the '(RFC822)' format comes on
                # a list with a tuple with header, content, and the closing
                # byte b')'
                for response_part in data:
                    # so if its a tuple...
                    if isinstance(response_part, tuple):
                        # we go for the content at its second element
                        # skipping the header at the first and the closing
                        # at the third
                        message = email.message_from_bytes(response_part[1])

                        try:
                            # we'll connect using SSL
                            server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
                            # to interact with the server, first we log in
                            # and then we send the message
                            server.login(SMTP_EMAIL, SMTP_PASSWORD)
                            server.sendmail(SMTP_EMAIL, TARGET_ADDRESS, message.as_string())
                            server.quit()
                        except:
                            print(sys.exc_info()[0])
                        finally:
                            mail.logout()

                        print(f'{datetime.now().strftime( "%H:%M:%S" )} Forwarded message from {IMAP_EMAIL} through {SMTP_EMAIL} to {TARGET_ADDRESS}. Email subject: {message["subject"]}')

    LAST_MAIL = len(mail_ids)
    timer = threading.Timer(TIMER, reload)
    timer.start()

timer = threading.Timer(TIMER, reload)
timer.start()
