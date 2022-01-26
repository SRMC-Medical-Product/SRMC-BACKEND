import datetime
import pytz

class TimeFormatException(Exception):
    """
        UserDefined exception to hadle time format error

    """
    def __int__(self):
        super().__init__("TimeFormatError...Time should be in HH:MM:SS format")



def generate_current_date():

    timezone=pytz.timezone("Asia/Kolkata")

    now_=datetime.datetime.now().astimezone(timezone)

    return now_

def update_availabilty(availabilty,current,days_int):
    print("adasd",availabilty)
    now_=current
    for i in range(7):
        if now_.weekday() in days_int:
            availabilty["days"][now_.weekday()]["available"]=True
        availabilty["days"][now_.weekday()]["date"]=now_.strftime("%m/%d/%Y")
        
        now_=now_+datetime.timedelta(days=1)
    
    availabilty["days_arr"]=days_int
    print(availabilty)
    return availabilty

def return_time_type(isotime):

    return datetime.time.fromisoformat(isotime)

def calculate_time_slots(start_time,end_time,duration,availabilty):
    time_slots={
        "morning":[],
        "afternoon":[],
        "evening":[]
        }
    start_=datetime.date(1,1,1)
    end_=datetime.date(1,1,1)

    start_=datetime.datetime.combine(start_,start_time)
    end_=datetime.datetime.combine(end_,end_time)

    twelve_=datetime.datetime.combine(datetime.date(1,1,1),datetime.time(12,0,0))
    five_=datetime.datetime.combine(datetime.date(1,1,1),datetime.time(17,0,0))
    while start_<end_:
        if start_<=twelve_:
            time_slots["morning"].append(start_.time().strftime("%H:%M:%S"))
        elif start_<=five_:
            time_slots["afternoon"].append(start_.time().strftime("%H:%M:%S"))
        else:
            time_slots["evening"].append(start_.time().strftime("%H:%M:%S"))
        start_=start_+datetime.timedelta(minutes=duration)
    
    return time_slots
