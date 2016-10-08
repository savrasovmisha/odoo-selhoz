import datetime

def week_magic(day):
	if type(day)==str:
		day = datetime.datetime.strptime(day, "%Y-%m-%d").date()
	day_of_week = day.weekday()

	to_beginning_of_week = datetime.timedelta(days=day_of_week)
	beginning_of_week = day - to_beginning_of_week

	to_end_of_week = datetime.timedelta(days=6 - day_of_week)
	end_of_week = day + to_end_of_week
	number_of_week = day.isocalendar()[1]

	return (beginning_of_week, end_of_week, number_of_week)

def last_day_of_month(date):
	if type(date)==str:
		date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
	if date.month == 12:
		return date.replace(day=31)
	return date.replace(month=date.month+1, day=1) - datetime.timedelta(days=1)


