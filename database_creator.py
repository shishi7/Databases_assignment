def initialise_db(db_name: str, postgres_path: str):
    """
    Initialise database on DBMS server using 'CREATE DATABASE ...' command.
    NOTE: You need to enter PostgreSQL DB manager's password (user: postgres).

    :param db_name: Name of DB
    :param postgres_path: Path to the folder containing PostgreSQL
    """
    import os

    path = (postgres_path if postgres_path else 'C:/Program files') + '/PostgreSQL/10/bin/psql.exe'

    query = ''
    query += 'DROP DATABASE IF EXISTS {0};'.format(db_name)
    query += 'CREATE DATABASE {0};'.format(db_name)
    query += r'\l\\'  # Show databases

    if os.system('echo {0} | "{1}" -U postgres'.format(query, path)):
        print('Unable to execute PostgreSQL Shell by path: "{0}"'.format(path))
        print('Try to create DB {0} by your own...'.format(db_name))
        os._exit(1)
    else:
        print('Database was created on the PostgreSQL server!\n')
