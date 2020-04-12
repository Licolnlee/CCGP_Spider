import csv
import redis
from data_saver import RedisClient

CONN = RedisClient('ccgp', 'filter_link')

for COUNT in range(1, 22):
    with open('csv/' + str(COUNT) + '.csv', 'rt', encoding = 'utf-8') as csvfile:
        reader = csv.DictReader(csvfile)

        for row in reader:
            name = row['name']
            id = row['id']
            # print(row)
            CONN.set(name, id)
