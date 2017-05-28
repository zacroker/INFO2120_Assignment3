import pg8000
import string
import numpy
import random
import names
import re
import pdb

def dbconnect():
    connection = pg8000.connect(
        database = 'A3_Olympics',
        user = 'postgres',
        password = 'hello',
        host = 'localhost')
    return connection

def exec_sql_file(cursor, sql_file):
    print ("\n[INFO] Executing SQL script file: '%s'" % (sql_file))
    statement = ""

    for line in open(sql_file):
        if re.match(r'--', line):  # ignore sql comment lines
            continue
        if not re.search(r'[^-;]+;', line):  # keep appending lines that don't end in ';'
            statement = statement + line
        else:  # when you get a line ending in ';' then exec statement and reset for next statement
            statement = statement + line
            # print ("\n\n[DEBUG] Executing SQL statement:\n%s" % (statement))
            try:
                cursor.execute(statement)
                conn.commit()
            except (OperationalError, ProgrammingError) as e:
                print ("\n[WARN] PostgreSQL error during execute statement \n\tArgs: '%s'" % (str(e.args)))

            statement = ""

def createdb():
    exec_sql_file(cur, 'olympics_ddl.sql')

def populate_location_heirarchy():
    """
        Populates location, place, sport venue and accommodation
    """
    exec_sql_file(cur, 'populate_location.sql')
    exec_sql_file(cur, 'populate_place.sql')
    find_accomm = ("SELECT place_id FROM Place JOIN Location ON located_in = location_id WHERE loc_type = 'suburb' ORDER BY place_id ASC LIMIT 10")
    find_venue = ("SELECT place_id FROM Place JOIN Location ON located_in = location_id WHERE loc_type = 'eventvenue'")
    insert_accomm = ("INSERT INTO Accommodation VALUES (%s)")
    insert_venue  = ("INSERT INTO SportVenue VALUES (%s)")

    # Populate accommodation and sportvenue
    cur.execute(find_venue)
    venue_ids = cur.fetchall()
    for ids in venue_ids:
        cur.execute(insert_venue, ids)
        conn.commit()
    cur.execute(find_accomm)
    accomm_ids = cur.fetchall()
    for ids in accomm_ids:
        cur.execute(insert_accomm, ids)
        conn.commit()

def member_id_generator(member_type, number):
	"""
		members are either athlete (0), staff (1) or official (2)
	"""
    # Member id is a 10 char id
	id = str(number)
	return mem_type[member_type][0] + id.rjust(9, '0')

def populate_member_heirarchy():
    """
        Populates member, athlete, official and staff
    """
    exec_sql_file(cur, 'populate_country.sql')
    # get country codes and accom_id for members
    c_code = ("SELECT country_code FROM Country WHERE country_name IS NOT NULL ORDER BY RANDOM() LIMIT 1")
    accom_id = ("SELECT place_id FROM Accommodation ORDER BY RANDOM() LIMIT 1")
    memberinsert = ("INSERT INTO Member VALUES (%s, %s, %s, %s, %s, %s, %s)")
    memtypeinsert = {0: "INSERT INTO Athlete VALUES (%s)",
                    1: "INSERT INTO Official VALUES (%s)",
                    2: "INSERT INTO Staff VALUES (%s)"}

    # 3 types of member (athlete official or staff)
    for m_type in range(3):
    	for i in range(50):
            title = random.choice(['Mr', 'Mrs', 'Miss', 'Dr', 'Ms'])
            firstname = names.get_first_name(gender = gend[title])
            lastname = names.get_last_name()

            cur.execute(accom_id)
            accom = int(cur.fetchone()[0])

            member_id = member_id_generator(m_type, i)

            cur.execute(c_code)
            country = cur.fetchone()[0]

            cur.execute(memberinsert, (member_id, title, lastname, firstname, country, accom, 'password'))
            cur.execute(memtypeinsert[m_type], (member_id,))
            conn.commit()

def populate_sports():
    """
        Populates sport table, event, team event and individual event
    """
    exec_sql_file(cur, 'populate_sport.sql')
    exec_sql_file(cur, 'populate_event.sql')
    exec_sql_file(cur, 'populate_individualevent.sql')
    #select event id not in individual and put in team
    cur.execute("SELECT event_id FROM Event EXCEPT SELECT event_id FROM IndividualEvent")
    teameventids = cur.fetchall()
    for teid in teameventids:
        cur.execute("INSERT INTO TeamEvent VALUES (%s)", teid)
        conn.commit()

def populate_events_relationships():
    """
        Populates runsevent, team, team member and participates
    """
    roles = {0: 'time keep', 1: 'judge', 2: 'boss', 3: 'food man', 4: 'cleaner',
            5: 'ticketer', 6: 'crowd ctrl'}

    cur.execute("SELECT event_id FROM Event")
    events = cur.fetchall()
    cur.execute("SELECT event_id FROM IndividualEvent")
    indivents = cur.fetchall()
    cur.execute("SELECT event_id FROM TeamEvent")
    teamevents = cur.fetchall()
    cur.execute("SELECT member_id FROM Official")
    officials = cur.fetchall()
    cur.execute("SELECT member_id FROM Athlete")
    athletes = cur.fetchall()
    aths = []
    for ath in athletes:
        aths.append(ath[0])

    cur.execute("SELECT country_code FROM Country WHERE country_name IS NOT NULL")
    c_codes = cur.fetchall()
    codes = []
    for code in c_codes:
        codes.append(code[0])

    for event in events:
        cur.execute("INSERT INTO runsevent VALUES(%s, %s, %s)", (event[0], random.choice(officials)[0], random.choice(roles)))
        conn.commit()
    for event in indivents:
        athletes = numpy.random.choice(aths, 3, replace = False)
        for ath in athletes:
            cur.execute("INSERT INTO participates VALUES (%s, %s)", (event[0], str(ath)))
        conn.commit()
    for event in teamevents:
        c_codes = numpy.random.choice(codes, 3, replace = False)
        for i in range(3):
            cur.execute("INSERT INTO Team VALUES (%s, %s, %s)", (event[0], str(c_codes[i]), str(c_codes[i])))
            cur.execute("INSERT INTO TeamMember VALUES (%s, %s, %s)", (event[0], str(c_codes[i]), str(numpy.random.choice(aths))))

def vehicle_code_generator():
	letters = ''.join(random.choice(string.ascii_uppercase) for _ in range(4))
	numbers = ''.join(random.choice(string.digits) for _ in range(4))
	return letters + numbers

def populate_vehicle_relationships():
    """
        Populates vehicle, journey and booking with some testing values
    """
    for i in range(20):
        cur.execute("INSERT INTO Vehicle VALUES ('" + vehicle_code_generator() + "', " + str(random.randint(20,50)) + ")")
        conn.commit()

    vehicle = ("SELECT vehicle_code FROM Vehicle ORDER BY RANDOM() LIMIT 1")
    places = ("SELECT place_id FROM Place ORDER BY RANDOM() LIMIT 2")

    for i in range(20):
        cur.execute(vehicle)
        code = cur.fetchone()[0]
        cur.execute(places)
        place1 = cur.fetchone()[0]
        place2 = cur.fetchone()[0]
        cur.execute("SELECT TIMESTAMP '2017-03-01 00:00:00' + RANDOM() * (TIMESTAMP '2017-07-01 00:00:00' - TIMESTAMP '2017-03-01 00:00:00')")
        time = cur.fetchone()[0]
        cur.execute("INSERT INTO Journey VALUES (%s, %s, %s, %s, %s, %s)", (i, time, place1, place2, code, 0))
        conn.commit()

    for i in range(20):
        cur.execute("SELECT member_id FROM Member ORDER BY random() LIMIT 1")
        member = cur.fetchone()[0]
        cur.execute("SELECT member_id FROM Staff ORDER BY random() LIMIT 1")
        staff = cur.fetchone()[0]
        cur.execute("SELECT TIMESTAMP '2017-03-01 00:00:00' + RANDOM() * (TIMESTAMP '2017-07-01 00:00:00' - TIMESTAMP '2017-03-01 00:00:00')")
        time = cur.fetchone()[0]
        cur.execute("SELECT journey_id FROM journey ORDER BY random() LIMIT 1")
        journey = cur.fetchone()[0]
        cur.execute("INSERT INTO Booking VALUES (%s, %s, %s, %s)", (member, staff, time, journey))
        conn.commit()

# Member type dictionary
mem_type = {0: 'Athlete',
            1: 'Official',
            2: 'Staff'}
# Gender dictionary for name generation
gend = {'Mr': 'male',
        'Mrs': 'female',
        'Miss': 'female',
        'Dr': random.choice(['male', 'female']),
        'Ms': 'female'}

# Create global connection object
conn = dbconnect()
if conn == None:
    print("Error connecting to database")
    exit()
cur = conn.cursor()

"""
    Start with general outline... To use this function, change the dbconnect function parameters
    to the parameters of your own PostgreSQL database. Note there is not really any error checking when
    connecting to this database (DIY...)
"""
createdb() # Creates the database from the DML file
populate_location_heirarchy() # Populates location, place, sport venue and accommodation
populate_member_heirarchy() # Populates member, athlete, official and Staff
populate_sports() # Populates sport table, event, team event and individual event
populate_events_relationships() # Populates runsevent, team, team member and participates
populate_vehicle_relationships() # Populates vehicle, journey and booking with some testing values
exec_sql_file(cur, 'populate_medals.sql')
