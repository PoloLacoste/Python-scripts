import argparse, os
from lxml import etree
from datetime import datetime

delay = 30
limit = 90

parser = argparse.ArgumentParser(description='Make stats sms xml file (from SMS Backup & Restore)')
parser.add_argument('--file', action='store', type=str, nargs='*', help="The file to analyze", required=True)
parser.add_argument('--phone', action='store', type=str, help="The phone number", required=True)
parser.add_argument('--delay', action='store', type=int, default=delay, help="Delay between messages")
parser.add_argument('--limit', action='store', type=int, default=limit, help="Count days if the number of message is higher")

def convertNumber(number):
	return number.replace("+33", "0") if number is not None else None

def toJson(file):

	jason = {}
	if os.path.exists(file):
		print("Converting xml file %s..." % file)

		for event, sms in etree.iterparse(file, events=('start', 'end', 'start-ns', 'end-ns')):
			if(event == "start"):
				number = convertNumber(sms.get("address"))
				if number is not None:
					ts = sms.get("date")
					if ts is not None:
						if number in jason:
							jason[number][ts] = sms.attrib
						else:
							jason[number] = {
								ts: sms.attrib
							}
	else:
		print("This file doesn't exists !")
	
	return jason

if __name__ == "__main__":
	args = parser.parse_args()

	delay = args.delay
	limit = args.limit

	file = args.file[0]
	phone = args.phone

	print("Analyzing file %s..." % file)
	conversations = toJson(file)

	if phone in conversations:

		my_sms = 0
		contact_sms = 0

		last_date = None
		current_sms_day = 0
		max_sms_day = 0
		max_sms_date = None

		last_ts = None
		current_conv_sms = 0
		max_conv_sms = 0
		max_conv_date = None

		last_day_date = None
		day_sms_limit = 0

		count_days = 0

		for ts, sms in conversations[phone].items():

			ts = int(ts) / 1000

			try:
				if "type" in sms and sms["type"] == "1":
					contact_sms += 1
				else:
					my_sms += 1
			except:
				pass
#
			date = datetime.fromtimestamp(ts)
			start = datetime(date.year, date.month, date.day)
				
			if last_date != start:
				if max_sms_day < current_sms_day:
					max_sms_date = start
					max_sms_day = current_sms_day
				current_sms_day = 0
				last_date = start
				count_days += 1
			else:
				current_sms_day += 1

			if last_day_date != start and current_sms_day > limit:
				last_day_date = start
				day_sms_limit += 1

			if last_ts == None or last_ts + delay > ts:
				last_ts = ts
				current_conv_sms += 1
			else:
				if max_conv_sms < current_conv_sms:
					max_conv_date = start
					max_conv_sms = current_conv_sms
				current_conv_sms = 0
				last_ts = ts

		print("There is %d messages" % (my_sms + contact_sms))
		print("You sent %d messages" % my_sms)
		print("Your contact sent %d messages" % contact_sms)
		print("Total days : %d " % count_days)
		print("Max messages in one day : %d on %s" % (max_sms_day, max_sms_date))
		print("Max message in a row : %d on %s" % (max_conv_sms, max_conv_date))
		print("Days messages higher than limit : %d " % day_sms_limit)

	else:
		print("This phone number doesn't exists !")