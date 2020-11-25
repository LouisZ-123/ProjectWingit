"""
Automatically builds and deploys the lambda API. Does the following in order:

1. Does prechecks to make sure some basic things were not messed up
2. If --db_rebuild (-D/-d) tag is passed:
    - Delete the current table under USERS_TABLE_NAME
    - Rebuild the table with SQL found in BuildConstants
    - Insert into the table two values:
        * A test user that will remain unverified
        * A test user that is immediately verified
3. Runs offline tests on the lambda_code to make sure there are no initial errors in the python code (could be more
    later on the server)
    - If there are failed tests or errors, they are shown and program execution is exited
4. If there were no errors, generate a zip file of all the code that needs to be copied to the lambda server, and
    places it onto the desktop under the file name "lambda_code.zip"
"""
print("Loading packages...")
from BuildConstants import *
from tests.LambdaTestUtils import random_str
import argparse
import os, shutil
import sys

_LAMBDA_CODE_DIR = 'lambda_code'
_LAMBDA_IGNORE = [r'.*dist-info.*']

_REBUILD_DB = True  # So I don't have to keep changing build args


def build_prechecks():
    """
    Initial checks to make sure I didn't mess up anything with variables that I could see myself overlooking...
    """
    if RETURN_GOOD_MESSAGE_STR == 'message':
        raise ValueError("Cannot set the RETURN_GOOD_MESSAGE_STR to 'message'")


def rebuild_database(conn):
    """
    WARNING: deletes and rebuilds the database, saving no information
    :param conn: the database connection
    """
    # Delete the table
    cursor = conn.cursor()
    cursor.execute(DELETE_USERS_TABLE_SQL)
    conn.commit()

    # Recreate the table
    cursor.execute(CREATE_USERS_TABLE_SQL)
    conn.commit()

    # Insert two elements into the table
    cursor.execute(*make_insert_sql(USERS_TABLE_NAME, **TEST_ACCOUNT_VERIFIED_KWARGS))
    conn.commit()

    cursor.execute(*make_insert_sql(USERS_TABLE_NAME, **TEST_ACCOUNT_UNVERIFIED_KWARGS))
    conn.commit()

    conn.close()


def build_zip_file():
    """
    Builds a zip file of the directory lambda_code/ and saves it in the base directory as lambda_code.zip. Some things
    need to be done automatically before the zip file is built, however:
        - Everything needed is copied into a temp directory
            - ignores every path that matches a regex in the LAMBDA_IGNORE list
        - As files are being copied, all files in lambda_code/*.py will be skimmed and any imports that start with
            "from lambda_code." or "import lambda_code." will be replaced with "from " and "import " respectively, to
            fix the package references for when it is actually on the server
    """
    # Make a temporary directory to work in
    temp_dir = random_str(30, all_ascii=True)

    # Strings for replacing
    _start_repl_str_1 = 'from %s.' % _LAMBDA_CODE_DIR
    _new_repl_str_1 = 'from '
    _start_repl_str_2 = 'import %s.' % _LAMBDA_CODE_DIR
    _new_repl_str_2 = 'import '

    # Surround in a try-catch so if something goes wrong, we can at least try to delete the temp_dir
    try:
        # Go through all files
        for root, _, files in os.walk('.\\%s\\' % _LAMBDA_CODE_DIR):

            # Ignore __pychache__
            if root == '.\\%s\\__pycache__' % _LAMBDA_CODE_DIR:
                continue

            # Make the directory
            new_dir = root.replace('.\\%s\\' % _LAMBDA_CODE_DIR, '.\\%s\\' % temp_dir)
            os.mkdir(new_dir)

            # Go through each file in this directory
            for f in files:
                filename = os.path.join(root, f)
                new_filename = os.path.join(new_dir, f)

                # For the base files in _LAMBDA_CODE_DIR, do the whole replacy thingy
                if root == '.\\%s\\' % _LAMBDA_CODE_DIR and filename.endswith('.py'):

                    # Read the new file, change any line that needs changing, then write it back
                    with open(filename, 'r') as infile:
                        with open(new_filename, 'w') as outfile:
                            for line in infile.readlines():
                                line = line.replace('from %s.' % _LAMBDA_CODE_DIR, 'from ')
                                line = line.replace('import %s.' % _LAMBDA_CODE_DIR, 'import ')
                                outfile.write(line)

                # Otherwise copy it over directly
                else:
                    shutil.copy(filename, new_filename)

        # Make the actual zip file
        shutil.make_archive(_LAMBDA_CODE_DIR, 'zip', '.\\%s\\' % temp_dir)

    # Try and delete temp_dir if there was a problem, then show the error
    except Exception:
        exc_inf = str(sys.exc_info()[0])

        try:
            shutil.rmtree(temp_dir)
        except:
            pass

        print("Unexpected error:", exc_inf)
        raise

    # Delete the old temp directory
    shutil.rmtree(temp_dir)


def make_java_constants():
    """
    Writes all of the needed constants to a java file for the app
    """
    if os.path.isfile(JAVA_CONSTANTS_FILE_PATH):
        os.remove(JAVA_CONSTANTS_FILE_PATH)

    with open(JAVA_CONSTANTS_FILE_PATH, 'w') as f:
        f.write(JAVA_CONSTANTS_FILE_DATA)


# Main call
if __name__ == "__main__":
    # Do the build prechecks first
    print("Doing prechecks...")
    build_prechecks()
    print("Prechecks passed!")

    # Parse them args
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "-D", "--db_rebuild",
                        help="WARNING: deletes and rebuilds the USERS database, all data will be deleted.",
                        action="store_true")
    args = parser.parse_args()

    # Delete and rebuild the database if the arg has been passed
    if args.db_rebuild or _REBUILD_DB:
        print("Rebuilding database...")
        from lambda_code.utils import get_new_db_conn

        rebuild_database(get_new_db_conn())
        print("Database rebuilt!")

    # Now, do the unit tests offline to make sure everything works
    from tests.LambdaTestUtils import set_request_type_online

    set_request_type_online(False)

    print("\nTesting lambda code offline...")
    from tests.TestLambda import TestLambda

    TestLambda().test_all()

    # Tests should have passed if we made it this far, make a zip file of everything needed
    print('Building zip file...')
    build_zip_file()
    print("Zipfile made!")

    # Make the file of constants for java app
    print('Writing java constants file...')
    make_java_constants()
    print('Constants written!\n\n')

    # Wait for input to test online stuff...
    print("Would you like to test online? (y/n)")
    if input().lower() == 'y':
        print("\nTesting online...")
        set_request_type_online(True)
        TestLambda().test_all()
    else:
        print("Not testing online")
