import copy
import dataset
from datetime import datetime, timedelta
from typing import *

from utils.log import *
from config import DB


class Database:
    """A class used to interface with the database storing teachers, students, tutoring times, and who claimed them

    To store this data, we use a sql database with 3 tables:
        1) "``teachers``": A table used to map the teachers email address to their name. Columns are as follows:
            - "``email``": The teacher's email address
            - "``first_name``": The teacher's first name
            - "``last_name``": The teacher's last name
        2) "``students``": A table used to map a student's email address to their name. Columns are as follows:
            - "``email``": The student's email address
            - "``first_name``": The student's first name
            - "``last_name``": The student's last name
        3) "``times``": A table used to store the times teachers have set for tutoring, and who, if anyone, has claimed them. Columns are as follows:
            - "``teacher_email``": The teacher's email address hosting the tutoring session
            - "``start_time``": A unix timestamp representing the start of the session
            - "``duration``": The duration of the tutoring session (in seconds)
            - "``claimed``": A boolean representing if the session has been claimed
            - "``student``": The email address of the student who claimed the session

    Attributes:
        _db (dataset.Database): The sql database

    """

    def __init__(self):
        self._db = None
        self.init_db_connection()
        self.end_db_connection()

    def add_teacher(self, email: str, first_name: str, last_name: str) -> bool:
        """
        Adds a teacher to the database
        
        Args:
            email: The email of the teacher
            first_name: The teacher's first name
            last_name: The teacher's last name

        Returns:
            True if the teacher was added to the database or was already there, False if something went wrong
        """
        data = {"email": email, "first_name": first_name, "last_name": last_name}
        return self._transactional_upsert("teachers", data, ["email"])

    def add_student(self, email: str, first_name: str, last_name: str) -> bool:
        """
        Adds a student to the database

        Args:
            email: The email of the student
            first_name: The student's first name
            last_name: The student's last name
        """
        data = {"email": email, "first_name": first_name, "last_name": last_name}
        return self._transactional_upsert("students", data, ["email"])

    def add_time_for_tutoring(self, teacher_email: str, start_time: datetime, duration: timedelta):
        """
        Adds a time for tutoring. Intended to be used by a teacher once they have logged in. It is assumed that they
        are already authorized.

        Args:
            teacher_email:
            start_time:
            duration:

        Returns:
            False if there was already a session in that time or the insert failed, otherwise True
        """
        start_time_unix = start_time.timestamp()
        duration_seconds = int(duration.total_seconds())

        for time in self._db['times'].find(teacher_email=teacher_email):
            try:
                c_start = int(time['start_time'])
                c_end = c_start + int(time['duration'])
            except KeyError:
                continue

            if (c_start < start_time_unix < c_end) or (start_time_unix < c_start < start_time_unix + duration_seconds):
                log_info("Attempted to add overlapping session", header=teacher_email)
                return False

        data = {'teacher_email': teacher_email,
                'start_time': start_time_unix,
                'duration': duration_seconds,
                'claimed': False,
                'student': ''}

        return self._transactional_insert("times", data)

    def claim_time(self, student_email: str, time_id: int):
        """
        Claim a time in the database. Intended to be used by a student once they have logged in. It is assumed that they
        are already authorized.

        Args:
            student_email: The email of the student claiming the time
            time_id: The id of the time ('id' key in the dict)

        Returns:
            False if the time was already claimed or there wasn't a time with the specified id, True if the time was successfully claimed
        """
        time_to_claim: dict = self._db['times'].find_one(id=time_id)

        if time_to_claim:
            if time_to_claim.get('claimed'):
                return False

            time_to_claim['claimed'] = True
            time_to_claim['student'] = student_email

            return self._transactional_upsert('times', time_to_claim, ["id"])

        return False

    def unclaim_time(self, student_email: str, time_id: int):
        """
        Unclaim a time in the database. Intended to be used by a student once they have logged in. It is assumed that they
        are already authorized.

        Args:
            student_email: The email of the student claiming the time
            time_id: The id of the time ('id' key in the dict)

        Returns:
            False if the time was claimed by someone else or there wasn't a time with the specified id, True if the time was successfully unclaimed
        """
        time_to_unclaim: dict = self._db['times'].find_one(id=time_id)

        if time_to_unclaim:
            if not time_to_unclaim.get('claimed'):
                return False

            c_student = time_to_unclaim.get("student")

            if c_student and c_student != student_email:
                return False

            time_to_unclaim['claimed'] = False

            return self._transactional_upsert('times', time_to_unclaim, ["id"])

        return False

    def search_times(self, teacher_email: str = None, min_start_time: datetime = None, max_start_time: datetime = None, must_be_unclaimed: bool = False) -> List[dict]:
        """
        Searches the database for tutoring sessions satisfying the search parameters

        Args:
            teacher_email: The teacher's email address (None for all teachers)
            min_start_time: The earliest start time for the session (None for all times)
            max_start_time: The latest start time for the session (None for all times)
            must_be_unclaimed: If the session has to be unclaimed

        Returns a list of dicts representing each time with the following keys:
                - "``teacher_email``": ``str`` - The email of the teacher hosting the session
                - "``start_time``": ``datetime`` - The start time of the session
                - "``end_time``": ``datetime`` - The end time of the session
                - "``duration``": ``timedelta`` - The start time of the session
                - "``claimed``": ``bool`` - If the session has been claimed
                - "``student``": ``str`` - The student who claimed the session (if any)

        Returns:
            The list of dicts
        """
        if teacher_email:
            possible_times = self._db['times'].find(teacher_email=teacher_email)
        else:
            possible_times = self._db['times'].all()

        results: List[dict] = []

        for t in possible_times:
            try:
                c_start = t['start_time']
                c_duration = t['duration']
                c_claimed = t['claimed']
            except KeyError:
                continue

            if must_be_unclaimed and c_claimed:
                continue

            if min_start_time and c_start < min_start_time.timestamp():
                continue

            if max_start_time and c_start > max_start_time.timestamp():
                continue

            t['start_time'] = datetime.fromtimestamp(c_start)
            t['end_time'] = datetime.fromtimestamp(c_start + c_duration)
            t['duration'] = t['end_time'] - t['start_time']
            results.append(t)

        return results

    def init_db_connection(self, attempt=0):
        """
        Initializes the database connection.

        Args:
            attempt: The attempt number to initialize the database connection (for recursion)
        """
        try:
            self._db = dataset.connect(DB, engine_kwargs={'pool_recycle': 3600, 'pool_pre_ping': True})
            # log_info("New Database Connection")
        except ConnectionResetError as e:
            log_info("ConnectionResetError " + str(e) + ", attempt: " + str(attempt))
            if attempt <= 3:
                self._db.close()
                self.init_db_connection(attempt=attempt + 1)
        except AttributeError as e:
            log_info("AttributeError " + str(e) + ", attempt: " + str(attempt))
            if attempt <= 3:
                self._db.close()
                self.init_db_connection(attempt=attempt + 1)

    def end_db_connection(self):
        """
        Closes the database connection
        """
        self._db.close()
        # log_info("Disconnected From Database")

    def _transactional_upsert(self, table: str, data: dict, key: list, attempt=0) -> bool:
        """
        Upserts a dict into a specified database table

        Args:
            table: The database table to upsert to
            data: The data to upsert
            key: The key to upsert with
            attempt: The attempt number (for recursion)

        Returns:
            True if the upsert succeeded, otherwise False
        """
        if attempt <= 3:
            self._db.begin()
            try:
                self._db[str(table)].upsert(dict(copy.deepcopy(data)), list(key))
                self._db.commit()
                return True
            except:
                self._db.rollback()
                log_info("Exception caught with DB, rolling back and trying again " + str((table, data, key, attempt)))
                return self._transactional_upsert(table, data, key, attempt=attempt + 1)
        else:
            log_info("Automatic re-trying failed with these args: " + str((table, data, key, attempt)))

        return False

    def _transactional_insert(self, table: str, data: dict, attempt=0) -> bool:
        """
        Inserts a dict into a specified database table

        Args:
            table: The database table to insert to
            data: The data to insert
            attempt: The attempt number (for recursion)

        Returns:
            True if the insert succeeded, otherwise False
        """
        if attempt <= 3:
            self._db.begin()
            try:
                self._db[str(table)].insert(dict(copy.deepcopy(data)))
                self._db.commit()
                return True
            except:
                self._db.rollback()
                log_info("Exception caught with DB, rolling back and trying again " + str((table, data, attempt)))
                return self._transactional_insert(table, data, attempt=attempt + 1)
        else:
            log_info("Automatic re-trying failed with these args: " + str((table, data, attempt)))

        return False
