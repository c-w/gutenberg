"""Utility methods to deal with databases."""


import contextlib
import os
import sqlite3


@contextlib.contextmanager
def connect(uri, mode='r'):
    """Connects to a SQL database (for use in a with-statement).

    Arguments:
        uri (str): The URI of the database
        mode (str): Set to 'w' to commit changes on connection close

    Returns:
        contextmanager: A connection to the database

    """
    dbtype = os.path.splitext(uri)[1][1:].lower()

    if dbtype == 'sqlite3':
        dbcon = sqlite3.connect(uri)
        dbcon.row_factory = sqlite3.Row
    else:
        raise NotImplementedError('unknown database type "%s"' % dbtype)

    try:
        yield dbcon
    finally:
        if mode == 'w':
            dbcon.commit()
        dbcon.close()
