from sqlite3 import Connection


def write_csv(writer, rows, header_row=None):
    if header_row is not None:
        writer.writerow(header_row)
    writer.writerows(rows)


def get_all_contact_ids(connection: Connection):
    return map(
        lambda x: x[0], connection.execute("SELECT DISTINCT ZIDENTITY FROM ZCONTACT").fetchall()
    )


def get_all_group_ids(connection: Connection):
    return map(
        lambda x: x[0],
        connection.execute('''
            SELECT DISTINCT lower(hex(conv.ZGROUPID))
            FROM ZCONVERSATION conv
            WHERE conv.ZGROUPID IS NOT NULL 
        ''')
    )


def get_group_creator(connection: Connection, group_id, default_id):
    return connection.execute('''
        SELECT IFNULL(contact.ZIDENTITY, '{default_id}')
        FROM ZCONVERSATION conv
        LEFT JOIN ZCONTACT contact ON (contact.Z_PK = conv.ZCONTACT)
        WHERE lower(hex(ZGROUPID)) = '{group_id}'
    '''.format(group_id=group_id, default_id=default_id)).fetchone()[0]
