# Mailsort

Python script to sort your email on a POP server

## Why?

If you only read your email on a web interface or you only read it on
one device, this is not really meant for you.  I won't discourage you
from trying it, but you're likely not to see the full benefit.

If you, like me, access your email from more than one computer, using
a thick client, this *is* for you.

The problem I had was that I was using Thunderbird on a desktop,
Thunderbird on a laptop, and K-9 Mail on my phone to access my email,
and had no single, coherent way to have my mail sorted according to
rules.  I tried, for a while, making sure that the rules always got
set on one computer, and that Thunderbird would be left open on that
one, and that worked when I didn't forget and close it, but when I
did, my phone email got so cluttered that it was not manageable.

Enter this script.

What this script does is it logs in to every email account in its
database, and applies a set of simple rules, each consisting of a
field to examine, a string to find there, and a place to move the
message to when the rule triggers.  It's that simple.  I run it as a
cron job on a Raspberry Pi every fifteen mintes, and it helps me keep
my sanity.

## Setup

To set it up, you will need to install sqlite3 on the machine where
you will be running it.  If you are running a Debian derivative
(including Ubuntu, Netrunner, Debian, LinuxMint, Raspian, etc.), you
can do this:

    sudo apt-get install sqlite3

Next, you will want to create your initial database schema.

    sqlite3 mailsort.db < create_schema.sql

Enter your account info into the database.  If your mail provider uses
ssl (shame on them if they do not), do this:

    sqlite3 mailsort.db "insert into account (host, type, username,
        password) values ('mail.example.com', 'ssl', 'your_username',
        'your_password')"

If they do not use ssl, do this:

    sqlite3 mailsort.db "insert into account (host, type, username,
        password) values ('mail.example.com', 'plain',
        'your_username', 'your_password')"

In either case, replace mail.example.com with the actual name of the
mail server, and your_username and your_password with your actual
username and password.

Next, using your email client, create a folder where you would like to
move some mail to.

Once that's done, create a rule, something like this:

    sqlite3 mailsort.db "insert into rule (account_id, field,
        searchstring, destination) values (1, 'FROM',
        'Motherinlaw@example.com', 'Junk')"

That rule will move emai lfrom motherinlaw@example.com to the Junk
folder.  The 1 tells the script which account to apply this rule to.
To see the list of accounts, do this:

    sqlite3 mailsort.db "select * from account"

## Advanced

If you want a rule to go off before others, you can use the priority
colume in the rule table.  It defaults to 10.  Setting a lower number
will make it go off sooner; a higher number will make it go off later.

The database also contains a log of all actions.  Simply select from
the log table to see it.

## Bugs

Folder names may not contain spaces.
