import os
import logging
import mysql.connector
import postgresql
import postgresql.driver.dbapi20 as pgdb
import time
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_random_exponential

logging.basicConfig(level=logging.DEBUG)

@retry(retry=retry_if_exception_type(mysql.connector.errors.InterfaceError), stop=stop_after_attempt(10), wait=wait_random_exponential(multiplier=1, max=10))
def get_mysql_connection(host: str, user: str, password: str, database: str):
    logging.debug(f'Getting MySQL connection on host={host} database={database} user={user} password={password}...')
    db = mysql.connector.connect(
        host=host,
        user=user,
        passwd=password,
        db=database)
    logging.debug(f'Got MySQL connection: {db}')
    return db

def get_postgres_connection(host: str, user: str, password: str, database: str):
    logging.debug(f'Getting PostgreSQL connection on host={host} database={database} user={user} password={password}...')
    db = pgdb.connect(
        host=host, 
        user=user, 
        password=password, 
        database=database)
    logging.debug(f'Got PostgreSQL connection: {db}')
    return db

def get_all_approved_emails(email_database):
    logging.debug('Getting all accepted emails...')

    sql_select_query = "SELECT mail FROM mails"
    cursor = email_database.cursor()
    cursor.execute(sql_select_query)
    records = cursor.fetchall()
    logging.debug(f'Got {cursor.rowcount} rows')

    accepted_emails = []
    for row in records:
        #logging.debug(f'Found accepted mail: {row[0]}')
        accepted_emails.append(row[0])

    count = len(accepted_emails)
    logging.debug(f'Got {count} accepted emails')
    return accepted_emails

def get_all_pending_users(greenlight_database):
    logging.debug('Getting all pending users...')

    pending_role_id = get_role_id("pending", greenlight_database)

    cursor = greenlight_database.cursor()
    cursor.execute(f"SELECT id, email FROM users WHERE users.role_id = {pending_role_id}")
    records = cursor.fetchall() 
    logging.debug(f'Got {cursor.rowcount} rows') # TODO: always -1

    pending_users = []
    for row in records:
        pending_user = {"user_id": row[0], "mail": row[1]}
        logging.debug(f'Found pending user: {pending_user}')
        pending_users.append(pending_user)

    count = len(pending_users)
    logging.debug(f'Got {count} pending users')
    return pending_users

def get_role_id(role_name: str, greenlight_database):
    """
    role_name: e.g. "pending", "user"
    """
    logging.debug(f'Getting id of "{role_name}" role...')

    cursor = greenlight_database.cursor()
    cursor.execute(f"SELECT id FROM roles WHERE name = '{role_name}'")
    records_one = cursor.fetchone()
    role_id = records_one[0]

    logging.debug(f'Getting id of "{role_name}" role: {role_id}')
    return role_id

def approve_pending_user(greenlight_database, user_id, pending_role_id, user_role_id):
    logging.debug(f'Changing "pending" role to "user" of user id {user_id}...')

    cursor = greenlight_database.cursor()
    cursor.execute(f"UPDATE users_roles SET role_id = {user_role_id} WHERE user_id = {user_id} AND role_id = {pending_role_id}")
    rows_changed = cursor.rowcount
    logging.debug(f'Changed {rows_changed} rows...')
    greenlight_database.commit()

    logging.debug(f'Changed "pending" role to "user" of user id {user_id}')

def approve_pending_users(user_ids, greenlight_database):
    logging.debug(f'Approving {len(user_ids)} pending users...')

    pending_role_id = get_role_id("pending", greenlight_database)
    user_role_id = get_role_id("user", greenlight_database)
    for user_id in user_ids:
        approve_pending_user(greenlight_database, user_id, pending_role_id, user_role_id)

    logging.debug(f'Approved pending users...')

def get_all_accepted_user_ids(pending_users, accepted_emails):
    logging.debug(f'Getting user ids of pending users with accepted mails...')

    accepted_user_ids = []
    for pending_user in pending_users:
        if pending_user["mail"] in accepted_emails:
            logging.debug(f'User {pending_user["user_id"]} with email={pending_user["mail"]} is accepted')
            accepted_user_ids.append(pending_user["user_id"])
        else:
            logging.debug(f'User {pending_user["user_id"]} with email={pending_user["mail"]} is NOT accepted')

    logging.debug(f'Got {len(accepted_user_ids)} user ids of pending users with accepted mails')
    return accepted_user_ids

def loop():
    logging.info('Executing main loop...')

    email_database = get_mysql_connection(os.environ['MYSQL_HOST'], os.environ['MYSQL_USER'], os.environ['MYSQL_PASSWORD'], os.environ['MYSQL_DATABASE'])
    accepted_emails = get_all_approved_emails(email_database)

    greenlight_database = get_postgres_connection(os.environ['POSTGRESQL_HOST'], os.environ['POSTGRESQL_USER'], os.environ['POSTGRESQL_PASSWORD'], os.environ['POSTGRESQL_DATABASE'])
    pending_users = get_all_pending_users(greenlight_database)
    accepted_user_ids = get_all_accepted_user_ids(pending_users, accepted_emails)
    approve_pending_users(accepted_user_ids, greenlight_database)

    email_database.close()
    greenlight_database.close()

def main():
    logging.info('Starting BigBlueButton auto approver...')
    while True:
        loop()
        
        sleeptime = int(os.environ['SLEEP_INTERVAL'])
        logging.info(f'Sleeping for {sleeptime}s until next loop...')
        time.sleep(sleeptime)

if __name__ == "__main__":
    main()