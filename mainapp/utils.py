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
