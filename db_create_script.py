import json

from data import teachers, goals

try:
    with open('data_base.json', 'w') as jf:
        json.dump(teachers, jf)
        print()

    with open('booking.json', 'w') as jf:
        json.dump([], jf)

    with open('request.json', 'w') as jf:
        json.dump([], jf)

except IOError:
    print("An IOError has occurred!")