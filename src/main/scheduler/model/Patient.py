import pymssql
from typing import Optional
import sys
sys.path.append("../util/*")
sys.path.append("../db/*")
from util.Util import Util # noqa
from db.ConnectionManager import ConnectionManager  # noqa


"""
Implementation for patient representation
"""


class Patient:

    def __init__(self, username: str, password: str = None, salt: str = None, uhash: str = None) -> None:
        """
        Patient Initializer, stores username, password, salt and hash in obj.
        """
        self._uname: str = username
        self._pw: str = password
        self._salt: str = salt
        self._hash: str = uhash

    def get(self) -> Optional[object]:
        """
        Accesses DB, ensures that provided salt and hash are valid (Correct PW)
        """
        cm = ConnectionManager()
        conn = cm.create_connection()
        cursor = conn.cursor(as_dict=True)
        get_patient_details = "SELECT Salt, Hash FROM Patients WHERE Username = %s"
        try:
            cursor.execute(get_patient_details, self._uname)
            for row in cursor:
                curr_salt = row['Salt']
                curr_hash = row['Hash']
                calculated_hash = Util.generate_hash(self._pw, curr_salt)
                if not calculated_hash == curr_hash:
                    # Incorrect PW entered by user
                    cm.close_connection()
                    return None
                else:
                    self._salt = curr_salt
                    self._hash = calculated_hash
                    cm.close_connection()
                    return self
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()
        return None

    """
    Following functions are helpers for returning private fields.
    """
    def get_username(self) -> str:
        return self._uname

    def get_salt(self) -> str:
        return self._salt

    def get_hash(self) -> str:
        return self._hash

    def save_to_db(self) -> None:
        """
        Upload changed information (USERNAME, SALT, HASH) into database
        """
        cm = ConnectionManager()
        conn = cm.create_connection()
        curr = conn.cursor()
        add_patient = "INSERT INTO Patients VALUES (%s, %s, %s)"
        try:
            curr.execute(add_patient, (self._uname, self._salt, self._hash))
            conn.commit()
        except pymssql.Error as e:
            raise e
        finally:
            cm.close_connection()

    def add_availability(self):
        pass

    
    