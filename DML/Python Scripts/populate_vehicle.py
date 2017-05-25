import string
import random

def vehicle_code_generator():
	letters = ''.join(random.choice(string.ascii_uppercase) for _ in range(4))
	numbers = ''.join(random.choice(string.digits) for _ in range(4))
	return letters + numbers

#python script to generate insert statements for vehicle
# import pdb; pdb.set_trace()
file = open('populate_vehicle.sql', 'w')
for _ in range(50):
	# format is 'vehicle code char(8), capacity int'
	file.write("INSERT INTO Vehicle VALUES ('" + vehicle_code_generator() + "', " + str(random.randint(20,50)) + ");\n")
file.close()
