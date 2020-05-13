import copy
from datetime import datetime, timedelta

from pymongo import MongoClient
from bson.objectid import ObjectId

import pytz
import validators
import secrets
import string
from typing import *

from utils.log import *
from config import DB, MONGO_DATABASE

import pickle
import codecs

MONGO_DB = MongoClient(DB)

def pickle_str(obj):
    return codecs.encode(pickle.dumps(obj), "base64").decode()


def pickle_decode(pickled_string):
    return pickle.loads(codecs.decode(pickled_string.encode(), "base64"))


class Database:
    """A class used to interface with the database storing teachers, students, tutoring times, and who claimed them

    To store this data, we use a sql database with 3 tables:
        1) "``teachers``": A table used to map the teachers email address to their name. Columns are as follows:
            - "``email``": The teacher's email address
            - "``first_name``": The teacher's first name
            - "``last_name``": The teacher's last name
            - "``subjects``": A pipe separated list of subjects that the teacher teachers
            - "``bio``": The teacher's biography
            - "``zoom_id``": The teacher's zoom id (as an int)
        2) "``students``": A table used to map a student's email address to their name. Columns are as follows:
            - "``email``": The student's email address
            - "``first_name``": The student's first name
            - "``last_name``": The student's last name
            - "``notes``": Notes about the student by the teacher
        3) "``times``": A table used to store the times teachers have set for tutoring, and who, if anyone, has claimed them. Columns are as follows:
            - "``teacher_email``": The teacher's email address hosting the tutoring session
            - "``start_time``": A unix timestamp representing the start of the session
            - "``duration_type``": A number representing the duration of the session (0 for 1hr, 1 for 1.5hr)
            - "``claimed``": A boolean representing if the session has been claimed
            - "``student``": The email address of the student who claimed the session
        4) "``auth`": A table used to store the email and auth, key-value pairs. Columns are as follows: 
            - "``teacher_email``": The teacher's email address hosting the tutoring session.
            - "``token``: The random 128-bit token hex string.
        4) "``carts`": A table used to store the cart of the users. Columns are as follows:
            - "``email``": The account's email address with items in the cart.
            - "``cart``: The cart (a base 64 pickled string).
            - "``intent``: Intent id of the current card ("" if there isn't one).

    Examples:
        **Handle a teacher login (call this once you know the teacher's email address)**::

            db.init_db_connection()
            if not db.check_teacher("ateacher@choate.edu"):
                # Teacher isn't in the database
                # Get the teacher to specify their name and the subjects they teach, then call the following:
                db.add_teacher("ateacher@choate.edu", "A", "Teacher", ["Math", "English"])
            db.end_db_connection()

        **Handle a student login**::

            db.init_db_connection()
            db.add_student("astudent@choate.edu", "A", "Student")
            db.end_db_connection()

        **Add a tutoring time (from teacher acct)**::

            db.init_db_connection()
            # 0 at the end means is is a 1hr session, 1 would be 1.5 hr
            db.add_time_for_tutoring("ateacher@choate.edu", datetime.datetime(2020, 4, 14, 10, 00), 0)
            db.end_db_connection()

        **Claim an available math tutoring time (from student acct)**::

            db.init_db_connection()
            possible_times = db.search_times(subject="Math", min_start_time=datetime.datetime.now(), must_be_unclaimed=True)
            db.claim_time("astudent@choate.edu", time_id=possible_times[0]['id'])
            db.end_db_connection()

        **Get student notes (from teacher acct)**::

            db.init_db_connection()
            notes = db.get_student_notes("astudent@choate.edu")
            db.end_db_connection()

        **Change student notes (from teacher acct)**::

            db.init_db_connection()
            db.set_student_notes("astudent@choate.edu", "A Student is a very good student...")
            db.end_db_connection()
    """

    def __init__(self):
        pass

    # Check for entries in database

    def check_student(self, email: str) -> bool:
        """
        Checks if a student is in the database

        Args:
            email: The email of the student

        Returns:
            True if the student was added to the database or was already there, False if something went wrong
        """
        return bool(self._find_one('students', email=email))

    def check_teacher(self, email: str) -> bool:
        """
        Checks if a teacher is in the database
        
        Args:
            email: The email of the teacher

        Returns:
            True if the teacher was added to the database or was already there, False if something went wrong
        """
        return bool(self._find_one('teachers', email=email))

    # Add entries to the database

    def add_teacher(self, email: str, first_name: str, last_name: str, subjects: List[str], bio: str, zoom_id: int) -> bool:
        """
        Adds a teacher to the database

        Args:
            email: The email of the teacher
            first_name: The teacher's first name
            last_name: The teacher's last name
            subjects: List of subjects the teacher teaches
            bio: A biography of the teacher
            zoom_id: The zoom id of the teacher's meeting room

        Returns:
            True if the teacher was added to the database or was already there, False if something went wrong
        """
        data = {"email": email, "first_name": first_name, "last_name": last_name, "subjects": "|".join(subjects),
                "bio": bio, "zoom_id": zoom_id}
        return self._upsert("teachers", data, ["email"])

    def add_student(self, email: str, first_name: str, last_name: str) -> bool:
        # def add_student(self, email: str, first_name: str, last_name: str) -> bool:
        """
        Adds a student to the database

        Args:
            email: The email of the student
            first_name: The student's first name
            last_name: The student's last name
        """
        data = {"email": email, "first_name": first_name, "last_name": last_name}
        return self._upsert("students", data, ["email"])

    # Teacher database retrieval/manipulation

    def get_teacher(self, teacher_email: str) -> dict:
        """
        Gets everything for a given teacher

        Args:
            teacher_email: The email of the teacher

        Returns:
            Everything about the teacher as a dict. Returns an empty dict if no teacher was found.
        """
        if teacher := self._find_one('teachers', email=teacher_email):
            return teacher
        return {}

    def edit_teacher(self, teacher_email: str, subjects: str, zoom_id: int, bio: str, first_name: str, last_name: str, icon: str) -> bool:
        if teacher := self._find_one('teachers', email=teacher_email):
            if subjects is not None: teacher['subjects'] = subjects
            if zoom_id is not None: teacher['zoom_id'] = zoom_id
            if bio is not None: teacher['bio'] = bio
            if first_name is not None: teacher['first_name'] = first_name
            if last_name is not None: teacher['last_name'] = last_name
            if icon is not None: teacher['icon'] = icon

            return self._upsert('teachers', teacher)

        return False

    def get_teacher_by_id(self, teacher_id: str) -> dict:
        """
        Gets everything for a given teacher

        Args:
            teacher_id: The id of the teacher

        Returns:
            Everything about the teacher as a dict. Returns an empty dict if no teacher was found.
        """
        if teacher := self._find_one('teachers', _id=teacher_id):
            return teacher
        return {}

    def make_teacher(self, email: str, subjects: List[str], bio: str, zoom_id: int) -> bool:
        """
        Makes a student into a teacher

        Args:
            email: The email of the student
            subjects: List of subjects the teacher teaches
            bio: A biography of the teacher
            zoom_id: The zoom id of the teacher's meeting room

        Returns:
            True if success, False if anything went wrong
        """

        # if student := self.get_student(email):
        if self.add_teacher(email, "", "", subjects, bio, zoom_id):
            self._delete('students', email=email)
            return True

        return False

    def all_teachers(self, subject: str = None) -> List[dict]:
        """
        Gets all teachers in the database

        Returns:
            List of teacher dicts
        """

        if subject is None:
            return self._all('teachers')

        return [i for i in self._all('teachers') if subject in i['subjects'].split('|')]

    # Student database retrieval/manipulation

    def get_student_notes(self, student_email: str) -> str:
        """
        Gets the teacher notes for a given student

        Args:
            student_email: The email of the student

        Returns:
            The notes as a string. Returns an empty string if no student was found or if the student has no notes
        """
        if student := self._find_one('students', email=student_email):
            if notes := student.get('notes'):
                return notes

        return ''

    def get_student(self, student_email: str) -> dict:
        """
        Gets everything for a given student

        Args:
            student_email: The email of the student

        Returns:
            Everything about the student as a dict. Returns an empty dict if no student was found.
        """
        if student := self._find_one('students', email=student_email):
            return student
        return {}

    def set_student_notes(self, student_email: str, notes: str) -> bool:
        """
        Sets the teacher notes for a given student

        Args:
            student_email: The email of the student
            notes: The notes to set

        Returns:
            True if the student is in the database and the notes were set, otherwise False
        """
        if student := self._find_one('students', email=student_email):
            student['notes'] = notes

            return self._upsert('students', student)

        return False

    # Time database retrieval/manipulation

    def add_time_for_tutoring(self, teacher_email: str, start_time: datetime, duration_type: int = 0) -> bool:
        """
        Adds a time for tutoring. Intended to be used by a teacher once they have logged in. It is assumed that they
        are already authorized.

        Args:
            teacher_email: Teacher's email address
            start_time: Start time of the session
            duration_type: The duration type of the session

        Returns:
            False if there was already a session in that time or the insert failed, otherwise True
        """
        print_function_call(header=teacher_email)

        start_time_unix = str(int(start_time.timestamp()))

        log_info("Timestamp: " + str(start_time_unix), header=teacher_email)

        data = {'teacher_email': teacher_email,
                'start_time': start_time_unix,
                'duration_type': duration_type,
                'claimed': False,
                'student': ''}

        log_info("Inserting " + str(data), header=teacher_email)

        return self._insert("times", data)

    def claim_time(self, student_email: str, time_id: str) -> bool:
        """
        Claim a time in the database. Intended to be used by a student once they have logged in. It is assumed that they
        are already authorized.

        Args:
            student_email: The email of the student claiming the time
            time_id: The id of the time ('id' key in the dict)

        Returns:
            False if the time was already claimed or there wasn't a time with the specified id, True if the time was successfully claimed
        """
        time_to_claim: dict = self._find_one('times', _id=time_id)

        if time_to_claim:
            if time_to_claim.get('claimed'):
                log_info("Time with id " + str(time_id) + " is already claimed", header=student_email)
                return False

            time_to_claim['claimed'] = True
            time_to_claim['student'] = student_email

            return self._upsert('times', time_to_claim)

        log_info("Unable to find time with id " + str(time_id), header=student_email)
        return False

    def edit_time(self, id: str, start_time: int = None, duration_type: int = None, claimed: bool = None,
                  student: str = None) -> bool:
        """
        Edits an already existing time.

        Args:
            id: The id of the time to edit
            start_time: The unix time the session starts
            duration_type: The duration type of the session
            claimed: Whether the session has been claimed
            student: The student that has claimed the time

        Returns:
            True if the update succeeded, otherwise False
        """
        updated_time = {"_id": id}

        if start_time is not None:
            updated_time.update({"start_time": str(start_time)})
        if duration_type is not None:
            updated_time.update({"duration_type": duration_type})
        if claimed is not None:
            updated_time.update({"claimed": claimed})
        if student is not None:
            updated_time.update({"student": student})

        return self._upsert("times", updated_time)

    def remove_time(self, id: str, email: str) -> bool:
        t = self.get_time_by_id(id)

        if t['teacher_email'] == email:
            return self._delete('times', _id=id)

        return False

    def unclaim_time(self, student_email: str, time_id: str) -> bool:
        """
        Unclaim a time in the database. Intended to be used by a student once they have logged in. It is assumed that they
        are already authorized.

        Args:
            student_email: The email of the student claiming the time
            time_id: The id of the time ('id' key in the dict)

        Returns:
            False if the time was claimed by someone else or there wasn't a time with the specified id, True if the time was successfully unclaimed
        """
        time_to_unclaim: dict = self._find_one('times', _id=time_id)

        if time_to_unclaim:
            if not time_to_unclaim.get('claimed'):
                log_info("Attempted to unclaim an unclaimed time with id " + str(time_id), header=student_email)
                return False

            c_student = time_to_unclaim.get("student")

            if c_student and c_student != student_email:
                log_info("Attempted to unclaim time id " + str(time_id) + " that belongs to " + str(c_student),
                         header=student_email)
                return False

            time_to_unclaim['claimed'] = False

            return self._upsert('times', time_to_unclaim)

        log_info("Unable to find time with id " + str(time_id), header=student_email)
        return False

    def search_times(self, teacher_email: str = None, teacher_id: str = None, student_email: str = None,
                     subject: str = None, min_start_time: datetime = None, max_start_time: datetime = None,
                     must_be_unclaimed: bool = False, insert_teacher_info=False, insert_bio: bool=True,
                     string_time_offset: timedelta = None, possible_times: List[dict] = None) -> List[dict]:
        """
        Searches the database for tutoring sessions satisfying the search parameters

        Args:
            teacher_email: The teacher's email address (None for all teachers)
            subject: The subject of the time (None for all subjects)
            min_start_time: The earliest start time for the session (None for all times)
            max_start_time: The latest start time for the session (None for all times)
            must_be_unclaimed: If the session has to be unclaimed

        Returns a list of dicts representing each time with the following keys:
            - "``teacher_email``": The teacher's email address hosting the tutoring session
            - "``start_time``": A unix timestamp representing the start of the session
            - "``duration_type``": A number representing the duration of the session (0 for 1hr, 1 for 1.5hr)
            - "``claimed``": A boolean representing if the session has been claimed
            - "``student``": The email address of the student who claimed the session

        Returns:
            The list of dicts
        """

        if possible_times is None:
            search_params = dict()

            if teacher_email is not None: search_params.update({"teacher_email": teacher_email})
            if student_email is not None: search_params.update({"student": student_email})
            if must_be_unclaimed: search_params.update({"claimed": 0})

            possible_times = self._find('times')

        if teacher_id is not None:
            teacher_email = self.get_teacher_by_id(teacher_id)['email']

        results: List[dict] = []

        for t in possible_times:
            c_start = int(t['start_time'])

            if min_start_time and datetime.fromtimestamp(c_start).astimezone(pytz.utc) < pytz.utc.localize(min_start_time):
                continue

            if max_start_time and datetime.fromtimestamp(c_start).astimezone(pytz.utc) >= pytz.utc.localize(max_start_time):
                continue

            c_teacher = None

            if teacher_id is not None:
                if teacher_email != t['teacher_email']:
                    continue

            if subject and teacher_email is not None:
                if c_teacher := self.get_teacher(teacher_email):
                    if subject not in c_teacher['subjects'].split("|"):
                        continue

            if string_time_offset is not None:
                time_obj = datetime.fromtimestamp(c_start).astimezone(pytz.utc)
                t['start_time'] = (time_obj - string_time_offset).strftime("%I:%M %p")
                t['time_num'] = c_start
                t['date_str'] = (time_obj - string_time_offset).strftime("%b %d %Y")

            if insert_teacher_info and teacher_email is not None:
                if c_teacher is None:
                    c_teacher = self.get_teacher(teacher_email)

                t_id = t['_id']
                if not insert_bio:
                    del c_teacher['bio']
                t.update(c_teacher)
                t['_id'] = t_id
                del t['email']

            results.append(t)

        return sorted(results, key=lambda x: x['time_num'])

    def get_time_schedule(self, timezone_offset: timedelta = None, time_offset: timedelta = None, num_days: int = 7, search_params: dict = None) -> List[Tuple[str, List[dict]]]:
        if timezone_offset is None:
            timezone_offset = timedelta(minutes=0)

        if search_params is None:
            search_params = {}

        midnight = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timezone_offset

        if midnight > datetime.utcnow():
            midnight -= timedelta(hours=24)

        if time_offset is not None:
            midnight += time_offset

        schedule_dict = []

        for day_num in range(num_days):
            params = dict()

            if search_params.get('teacher_email') is not None: params.update({"teacher_email": search_params.get('teacher_email')})
            if search_params.get('student_email') is not None: params.update({"student": search_params.get('student_email')})
            if search_params.get('must_be_unclaimed'): params.update({"claimed": 0})

            possible_times = self._find('times')

            today_schedule = self.search_times(min_start_time=midnight, max_start_time=midnight + timedelta(hours=24),
                                               string_time_offset=timezone_offset, insert_teacher_info=True, insert_bio=False,
                                               possible_times=possible_times, **search_params)

            # TODO
            # for t in today_schedule:
            #     if not self.get_teacher(t['teacher_email'])['hours_left'] > 0:
            #         del t

            for t in today_schedule:
                del t['teacher_email']
                del t['time_num']
                del t['duration_type']
                del t['claimed']
                del t['student']

            schedule_dict.append(((midnight - timezone_offset).strftime("%A<br>(%b %d %Y)"), today_schedule))
            midnight += timedelta(hours=24)

        return schedule_dict

    def get_time_by_id(self, time_id: str, string_time_offset: timedelta = None, insert_teacher_info=False) -> dict:
        if time := self._find_one('times', _id=time_id):
            if insert_teacher_info:
                if teacher := self.get_teacher(time['teacher_email']):
                    t_id = time['_id']
                    time.update(teacher)
                    time['_id'] = t_id
                    del time['email']

            if string_time_offset is not None:
                time['start_time'] = datetime.fromtimestamp(int(time['start_time'])).astimezone(pytz.utc) - string_time_offset
                time['date_str'] = time['start_time'].strftime("%b %d %Y")
                time['start_time'] = time['start_time'].strftime("%I:%M %p")

            return time

    # Cart database retrieval/manipulation

    def get_cart(self, email: str) -> Tuple[Set[str], str]:
        cart = self._find_one('carts', email=email)

        if cart is None:
            return set(), ""

        return pickle_decode(cart.get('cart')), cart.get('intent')

    def set_cart(self, email: str, cart: Set[str]) -> bool:
        return self._upsert('carts', {"email": email, "cart": pickle_str(cart), "intent": ""}, ['email'])

    def verify_cart(self, email: str, change=True):
        cart_set, intent = self.get_cart(email)

        new_cart_set = set()

        verified = True

        for entry in cart_set:
            if self.get_time_by_id(entry)['claimed'] and self.get_time_by_id(entry)['student'] != email:
                verified = False
            else:
                new_cart_set.add(entry)

        if change and not verified:
            self.set_cart(email, new_cart_set)

        return verified

    def set_intent(self, email: str, intent: str) -> bool:
        cart, _ = self.get_cart(email)
        return self._upsert('carts', {"email": email, "cart": pickle_str(cart), "intent": intent},
                            ['email'])

    def append_cart(self, email: str, session_id: str) -> bool:
        old_cart, _ = self.get_cart(email)
        old_cart.add(session_id)
        return self.set_cart(email, old_cart)

    # Database tools

    def init_db_connection(self, attempt=0):
        """
        Initializes the database connection.

        Args:
            attempt: The attempt number to initialize the database connection (for recursion)
        """
        pass

    def end_db_connection(self):
        """
        Closes the database connection
        """
        pass

    def _upsert(self, table: str, data: dict, key=None) -> bool:
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

        if '_id' in data:
            data['_id'] = ObjectId(data['_id'])

        if key is None:
            key = ['_id']

        f = {a: b for a, b in [(i, data[i]) for i in key]}
        MONGO_DB[MONGO_DATABASE][table].update_one(f, {'$set': data}, True)

        return True

    def _insert(self, table: str, data: dict) -> bool:
        """
        Inserts a dict into a specified database table

        Args:
            table: The database table to insert to
            data: The data to insert
            attempt: The attempt number (for recursion)

        Returns:
            True if the insert succeeded, otherwise False
        """

        MONGO_DB[MONGO_DATABASE][table].insert_one(data)
        return True

    def _find_one(self, table: str, **kwargs) -> dict:
        if '_id' in kwargs:
            kwargs['_id'] = ObjectId(kwargs['_id'])

        result = MONGO_DB[MONGO_DATABASE][table].find_one(filter=kwargs)

        if result is None:
            return result

        if '_id' in result:
            result['_id'] = str(result['_id'])

        return dict(result)

    def _find(self, table: str, **kwargs) -> List[dict]:
        if '_id' in kwargs:
            kwargs['_id'] = ObjectId(kwargs['_id'])

        result = list(MONGO_DB[MONGO_DATABASE][table].find(filter=kwargs))

        for i in range(len(result)):
            if '_id' in result[i]:
                result[i]['_id'] = str(result[i]['_id'])

        return result

    def _delete(self, table: str, **kwargs) -> bool:
        if '_id' in kwargs:
            kwargs['_id'] = ObjectId(kwargs['_id'])

        return MONGO_DB[MONGO_DATABASE][table].delete_many(kwargs)

    def _all(self, table: str) -> List[dict]:
        return self._find(table)

    # Auth functions

    def create_token(self, email: str) -> Any:
        """
        Creates or overwrites token if one exists. If creation was successful, return token. If not, return False.
        """

        token = secrets.token_hex(16)
        user = {"email": str(email), "token": token}
        if validators.email(email):
            if self._upsert("auth", user, ["email"]):
                return token
            else:
                log_info("Error creating token for " + str(email))
        else:
            log_info("Invalid email " + str(email))

        return False

    def check_auth_pair(self, token, email) -> Union[str, bool]:
        """
        Tries to fetch or make a token for a user. If not successful, return False
        """
        if token and email and self.possible_token(token):
            log_info("Checking token and email pair, " + str(token) + " " + str(email))
            if expected_token := self.find_token_by_email(str(email)):
                if secrets.compare_digest(token, expected_token):
                    log_info("Token check success: " + str(token))
                    return True
        return False

    def find_token_by_email(self, email: str) -> Any:
        """
        Finds token by email. If the token does not exist, return False.
        """
        entry = self._find_one('auth', email=str(email))
        if entry is None:
            return False
        token = entry.get('token')
        if token and self.possible_token(token):
            return token
        return False

    def possible_token(self, token: str) -> bool:
        """
        Validates if the input is a valid 128-bit token (16 byte)

        Args:
            token: The possible 128-bit token

        Returns:
            True if it could be a token, otherwise False
        """
        try:
            if isinstance(int(str(token), 16), int) and all(c in string.hexdigits for c in str(token)):
                if len(str(token)) == 32:
                    if "/" not in token:  # extra validation
                        return True
        except:
            log_info("Impossible token: " + str(token))
            return False

        log_info("Impossible token: " + str(token))
        return False
