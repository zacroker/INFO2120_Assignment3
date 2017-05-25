# Script to generate a DML file which can populate the Olympics Database

# Open a file to write to for each TABLE

##########
## Location Heirarchy
##########
# INSERT INTO Location VALUES (id, name, loc_type, part_of (can be NULL))
# INSERT INTO Place VALUES (place_id, name, gps_long, lat, address, located_in ref ^)
# INSERT INTO SportVenue (place_id)
# INSERT INTO Accommodation (place_id)

##########
## Member Heirarchy
##########
