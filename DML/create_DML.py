#!/usr/bin/env python3
import string
import random
import names
import pg8000

def database_connect():
    return pg8000.connect(database='A3_Olympics',
                        	user='postgres',
                            password='hello',
                            host='localhost')

def member_id_generator(member_type, member_number):
	"""
		members are either athlete (0), staff (1) or official (2)
	"""
	# Use a dictionary!
	mem_type = {0: 'A', 1: 'S', 2: 'O'}
	# Member id is a 10 char id
	id = str(member_number)
	id = mem_type[member_type] + id.rjust(9, '0') # Right justification on the string
	return id

# Connect to database so we can make inserts based on data already there
conn = database_connect()
cur = conn.cursor()
# Create place heirarchy
with open('populate_place_heirarchy.sql') as o:
	for line in o:
		cur.execute(line)
cur.close()
conn.close()
import pdb; pdb.set_trace()

# get country codes a for members
cur.execute("SELECT country_code FROM Country WHERE country_name IS NOT NULL;")
c_codes = cur.fetchall()
cur.execute("SELECT place_id FROM Accommodation;")
accom_id = cur.fetchall()
# import pdb; pdb.set_trace()
file = open('populate_member_heirarchy.sql', 'w')
gend = {'Mr': 'male', 'Mrs': 'female', 'Miss': 'female', 'Dr': random.choice(['male', 'female']), 'Ms': 'female'}
for mem_type in range(3):
	for i in range(30):
		# dormat is member_id char(10), title char(4) but CHECK CONSTRAINT, family and given names char(30),
		title = random.choice(['Mr', 'Mrs', 'Miss', 'Dr', 'Ms'])
		country = str(random.choice(c_codes))
		accommodation
		file.write("INSERT INTO Member VALUES (" + member_id_generator(mem_type, i) + ", " + title + ", " + names.get_first_name(gender = gend[title]) + ", " + names.get_last_name() + ", "+ country + ", " +");\n")
