import csv

with open("logs-insights-alt.csv") as f:
    for each_row in csv.DictReader(f):
        message = each_row.get('@message')
        timestamp = each_row.get('@timestamp')
        # if "/api/handle-payment" in message:
            # print(timestamp, message)

        # if "/api/get-cart" in message:
            # print(timestamp, message)

        if "@" in message:
            msg_list = message.split()
            [print(timestamp, x) for x in msg_list if "@" in x]
