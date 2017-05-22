#!/usr/bin/env python3
import string
import random
def id_generator(size=8, chars=string.ascii_uppercase + string.digits):
	letters = ''.join(random.choice(string.ascii_uppercase) for _ in range(4))
	numbers = ''.join(random.choice(string.digits) for _ in range(3))
	return letters + '-' + numbers


#python script to generate insert statements for vehicle
for _ in range(500):
	print ("INSERT INTO Vehicle VALUES ('" + id_generator() + "', " + str(random.randint(1,30)) + ");")


"INSERT INTO Vehicle VALUES ('ABC123', 15);"
