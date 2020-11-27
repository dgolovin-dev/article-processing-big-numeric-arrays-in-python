import os
import datetime
import random

os.makedirs('../data', exist_ok=True)

DAYS = 20*252
STOCKS = 2000

for i in range(STOCKS):
    with open("../data/f" + str(i)+'.csv', 'w') as f:
        f.write("date,open,low,high,close,volume,split,divs\n")
        start_date = datetime.date.today() - datetime.timedelta(days=DAYS)
        for j in range(DAYS):
            f.write(
                (start_date + datetime.timedelta(days=j)).isoformat() + ',' +
                '%.2f' % (100 + random.random() * 1000) + "," +
                '%.2f' % (90 + random.random() * 1000) + "," +
                '%.2f' % (110 + random.random() * 1000) + "," +
                '%.2f' % (100 + random.random() * 1000) + "," +
                '%.2f' % (random.random() * 1000) + "," +
                "1," +
                '%.2f' % (random.random() * 5) +
                "\n"
            )
    print(i, "/", STOCKS)