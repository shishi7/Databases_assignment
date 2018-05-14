import importlib
import os
import database_creator
import database_schema_creator
import database_random_filler

REQUIRED_MODULES = (('psycopg2', 'psycopg2'), ('faker', 'faker'), ('random_words', 'randomwords'))

DB_NAME = 'self_driving'


def install_if_not_exists(module_name: str, installation_name: str):
    """
    Installs module using 'pip' and 'installation_name' if there is an error while importing 'module_name'.

    :param module_name: Name for import
    :param installation_name: Name for installation
    """
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError:
        print('There is no module "{0}" installed. We will try to install it...'.format(module_name))
        if os.system('pip install {0}'.format(installation_name)):
            os.system('pip uninstall {0}'.format(installation_name))
            print('Failed to install "{0}" library! Try to install manually. Operation has been aborted.'.format(
                installation_name))
            os._exit(1)


def main():
    """
    Create database section on the PostgreSQL server under user 'postgres' with cleaning of previously set data.
    Data will be set randomly.
    """
    for mod, to_inst in REQUIRED_MODULES:
        install_if_not_exists(mod, to_inst)

    print('Input the location of folder "PostgreSQL" if other than "C:/Program files":')
    postgres_path = input()
    print("Please, specify manager's password:")
    password = input()
    print('Please, repeat this password again:')
    print()
    database_creator.initialise_db(DB_NAME, postgres_path)
    database_schema_creator.initialise_schema(DB_NAME, password)
    database_random_filler.fill_database(DB_NAME, password)


# if __name__ == '__main__':
main()
