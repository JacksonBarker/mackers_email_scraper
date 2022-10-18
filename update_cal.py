from datetime import datetime
import email
from icalendar import Calendar, Event

def UpdateCalendar(imap, isFrom, tzone, summ):
    try:
        with open("last_mData.txt", "x") as mData_file:
            mData_file.close()
    except:
        pass
    try:
        mData_file = open("last_mData.txt", "rb")
        last_mData = mData_file.read()
        mData_file.close()
    except:
        last_mData = ""

    resp, items = imap.search(None, "FROM", isFrom)
    resp, data = imap.fetch(items[0].split()[-1], "(RFC822)")
    if data[0][1] != last_mData:
        with open("last_mData.txt", "wb") as mData_file:
            mData_file.write(data[0][1])
            mData_file.close()
        _UpdateCalendar(data, tzone, summ)

def _UpdateCalendar(data, tzone, summ):
    body = data[0][1]
    msg = email.message_from_bytes(body)
    content = msg.get_payload(decode=True)
    lines = str(content).split("\\r\\n")

    trigger_start = 0
    for i in range(len(lines)):
        if lines[i].__contains__("Here is your schedule for the week of "):
            trigger_start = i

    lines_date = []
    for i in range(trigger_start + 2, len(lines)):
        if not lines[i]:
            trigger_start = i
            break
        lines_date.append(lines[i])

    shifts = []
    for i in range(len(lines_date)):
        shifts.append([datetime.strptime(lines_date[i].split(" -")[0], "%A, %B %d, %Y %I:%M %p")])
        shifts[i][0] = shifts[i][0].replace(tzinfo=tzone)
        shifts[i].append(datetime.strptime(lines_date[i].split(" -")[0], "%A, %B %d, %Y %I:%M %p"))
        shifts[i][1] = shifts[i][1].replace(hour=datetime.strptime(lines_date[i].split("- ")[1].split(",")[0], "%I:%M %p").hour, minute=datetime.strptime(lines_date[i].split("- ")[1].split(",")[0], "%I:%M %p").minute, tzinfo=tzone)
        shifts[i].append(summ + " ("+ lines_date[i].split(", ")[-1] + ")")

    try:
        cal_file = open("calendar.ics", "x")
        cal_file.close()
    except:
        pass
    try:
        cal_file = open("calendar.ics", "r")
        cal = Calendar.from_ical(cal_file.read())
        cal_file.close()
    except:
        cal = Calendar()
    for shift in shifts:
        event = Event()
        event.add("summary", shift[2])
        event.add("dtstart", shift[0])
        event.add("dtend", shift[1])
        cal.add_component(event)
    cal_file = open("calendar.ics", "w")
    cal_file.write(cal.to_ical().decode("utf-8"))
    cal_file.close()