import csv
import os.path
import sqlite3
import sys

from util import *

threema_db_file = sys.argv[1]
output_dir = sys.argv[2] if len(sys.argv) == 3 else './output'

# create output directory, if not already created
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

# connection to the sqlite (iOS) database
threema_db_conn = sqlite3.connect(threema_db_file)

#
# CSV Mapping
# csv row name -> sql select query mappings
#

contact_csv_columns = ['identity', 'publickey', 'verification', 'acid', 'tacid', 'firstname', 'lastname', 'nick_name',
                       'color', 'hidden', 'archived']
contact_query = """
    SELECT
        ZIDENTITY AS identity,
        lower(hex(ZPUBLICKEY)) AS publickey,
        CASE ZVERIFICATIONLEVEL
            WHEN 0
                THEN 'UNVERIFIED'
            WHEN 1
                THEN 'SERVER_VERIFIED'
            WHEN 2
                THEN 'FULLY_VERIFIED'
            ELSE ''
        END,
        '' AS acid,
        '' AS tacid,
        ZFIRSTNAME AS firstname,
        ZLASTNAME AS lastname,
        ZPUBLICNICKNAME AS nick_name,
        '' AS color,
        ZHIDDEN AS hidden,
        '0' AS archived
    FROM ZCONTACT
"""

group_csv_columns = ['id', 'creator', 'groupname', 'created_at', 'members', 'deleted', 'archived']
group_query = """
    SELECT
        lower(hex(conv.ZGROUPID)) AS id,
        contact.ZIDENTITY AS creator,
        conv.ZGROUPNAME AS groupname,
        '0' AS created_at,
        conv.ZGROUPMYIDENTITY || ';' || group_concat(group_member_contact.ZIDENTITY, ';') AS members,
        '0' AS deleted,
        '0' AS archived
    FROM ZCONVERSATION AS conv
    LEFT JOIN ZCONTACT AS contact ON (conv.ZCONTACT = contact.Z_PK)
    LEFT JOIN Z_5GROUPCONVERSATIONS group_member ON (group_member.Z_6GROUPCONVERSATIONS = conv.Z_PK)
    LEFT JOIN ZCONTACT group_member_contact ON (group_member_contact.Z_PK = group_member.Z_5MEMBERS)
    WHERE conv.ZGROUPID IS NOT NULL
    GROUP BY id
"""

#
# Export Contact List
#
cursor = threema_db_conn.execute(contact_query)
f = open(output_dir + '/contacts.csv', 'w+', encoding='utf-8')
writer = csv.writer(f, 'unix')
write_csv(writer, cursor.fetchall(), contact_csv_columns)
f.close()


#
# Export Group List
#
cursor = threema_db_conn.execute(group_query)
f = open(output_dir + '/groups.csv', 'w+', encoding='utf-8')
writer = csv.writer(f, 'unix')
write_csv(writer, cursor.fetchall(), group_csv_columns)
f.close()


#
# Export Private Chats
#
for contact in get_all_contact_ids(threema_db_conn):
    columns = ['apiid', 'uid', 'isoutbox', 'isread', 'issaved', 'messagestae', 'posted_at', 'created_at', 'modified_at',
               'type', 'body', 'isstatusmessage', 'isqueued', 'caption', 'quoted_message_apiid']

    print('Exporting private chat for: ', contact)

    file_name = 'message_' + contact + '.csv'
    f = open(output_dir + '/' + file_name, 'w+', encoding='utf-8')
    writer = csv.writer(f, 'unix')
    writer.writerow(columns)

    select = """
        SELECT
            lower(hex(msg.ZID)) AS apiid,
            '' AS uid,
            msg.ZISOWN AS isoutbox,
            msg.ZREAD AS isread,
            1 AS issaved,
            '' AS messagestae,
            cast((msg.ZDATE + 978307200) * 1000 as int) AS posted_at,
            cast((msg.ZDELIVERYDATE + 978307200) * 1000 as int) AS created_at,
            cast((msg.ZREADDATE + 978307200) * 1000 as int) AS modified_at,
            'TEXT' AS type,
            msg.ZTEXT AS body,
            0 AS isstatusmessage,
            0 AS isqueued,
            NULL AS caption,
            lower(hex(msg.ZQUOTEDMESSAGEID)) AS quoted_message_apiid
        FROM ZCONVERSATION conv
        LEFT JOIN ZCONTACT contact ON (contact.Z_PK = conv.ZCONTACT)
        LEFT JOIN ZMESSAGE msg ON (msg.ZCONVERSATION = conv.Z_PK)
        WHERE contact.ZIDENTITY='{contact_id}'
            AND conv.ZGROUPID IS NULL
            AND msg.ZDATE IS NOT NULL
    """.format(contact_id=contact)

    cursor = threema_db_conn.execute(select)

    for row in cursor:
        # allow changes
        row = list(row)

        if (row[columns.index('body')]) is None:
            # TODO handle different message types than text
            continue

        writer.writerow(row)


#
# Export Group Chat
#
for group in get_all_group_ids(threema_db_conn):
    columns = ['apiid', 'uid', 'isoutbox', 'isread', 'issaved', 'messagestae', 'posted_at', 'created_at', 'modified_at',
               'type', 'body', 'isstatusmessage', 'isqueued', 'caption', 'quoted_message_apiid']

    print('Exporting group chat for: ', group)

    group_creator = get_group_creator(threema_db_conn, group)
    file_name = 'group_message_' + group + '_' + group_creator + '.csv'

    f = open(output_dir + '/' + file_name, 'w+', encoding='utf-8')
    writer = csv.writer(f, 'unix')
    writer.writerow(columns)

    select = """
        SELECT
            lower(hex(msg.ZID)) AS apiid,
            '' AS uid,
            msgContact.ZIDENTITY AS identity,
            msg.ZISOWN AS isoutbox,
            msg.ZREAD AS isread,
            1 AS issaved,
            '' AS messagestae,
            cast((msg.ZDATE + 978307200) * 1000 as int) AS posted_at,
            cast((msg.ZDELIVERYDATE + 978307200) * 1000 as int) AS created_at,
            cast((msg.ZREADDATE + 978307200) * 1000 as int) AS modified_at,
            'TEXT' AS type,
            msg.ZTEXT AS body,
            0 AS isstatusmessage,
            0 AS isqueued,
            '' AS caption,
            lower(hex(msg.ZQUOTEDMESSAGEID)) AS quoted_message_apiid
        FROM ZCONVERSATION conv
        LEFT JOIN ZCONTACT cont ON (cont.Z_PK = conv.ZCONTACT)
        LEFT JOIN ZMESSAGE msg ON (msg.ZCONVERSATION = conv.Z_PK)
        LEFT JOIN ZCONTACT as msgContact ON (msgContact.Z_PK = msg.ZSENDER)
        WHERE lower(hex(conv.ZGROUPID))='{group_id}'
    """.format(group_id=group)

    cursor = threema_db_conn.execute(select)

    for row in cursor:
        row = list(row)

        if (row[columns.index('body')]) is None:
            # TODO handle different message types than text
            continue

        writer.writerow(row)

print('Done exporting private and group chats.')
