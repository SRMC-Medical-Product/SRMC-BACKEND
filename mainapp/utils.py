import datetime
import time
import pytz
 

'''Time Formatting'''
IST_TIMEZONE = pytz.timezone('Asia/Kolkata')
dmY = "%d-%m-%Y"
Ymd = '%Y-%m-%d'
IMp = "%I:%M %p"
HMS = "%H:%M:%S"
YmdHMS = "%Y-%m-%d %H:%M:%S"
dmYHMS = "%d-%m-%Y %H:%M:%S"
YmdTHMSf = "%Y-%m-%dT%H:%M:%S.%f"
YmdHMSf = "%Y-%m-%d %H:%M:%S.%f"
YmdTHMSZ = "%Y-%m-%dT%H:%M:%S.%Z"

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
    
    now_=current
    dates_arr=[]
    for i in range(7):
        if now_.weekday() in days_int:
            availabilty["days"][now_.weekday()]["available"]=True
            dates_arr.append(now_.strftime("%m/%d/%Y"))
        availabilty["days"][now_.weekday()]["date"]=now_.strftime("%m/%d/%Y")
        
        now_=now_+datetime.timedelta(days=1)
    
    availabilty["days_arr"]=days_int
    availabilty["dates_arr"]=dates_arr
    
    return availabilty

def return_time_type(isotime):

    return datetime.time.fromisoformat(isotime)

    
def calculate_time_slots(start_time,end_time,duration,availabilty,time_slots=None):
    if time_slots:
        
        time_slots_arr=list(time_slots.keys())
        dates_arr=availabilty["dates_arr"]

        final_=[]
        new_=[]
        old_=[]

        for i in dates_arr:
            if i in time_slots_arr:
                final_.append(i)
                old_.append(i)
                time_slots_arr.remove(i)
            else:
                final_.append(i)
                new_.append(i)
        
        
        slots_={}
        
        morning_={}
        afternoon_={}
        evening_={}
        slot_availabilty_={
            "available":True,
            "count":0
        }
        start_=datetime.date(1,1,1)
        end_=datetime.date(1,1,1)

        start_=datetime.datetime.combine(start_,start_time)
        end_=datetime.datetime.combine(end_,end_time)

        twelve_=datetime.datetime.combine(datetime.date(1,1,1),datetime.time(12,0,0))
        five_=datetime.datetime.combine(datetime.date(1,1,1),datetime.time(17,0,0))
        while start_<end_:
            if start_<=twelve_:
                morning_[start_.time().strftime("%H:%M:%S")]=slot_availabilty_
            elif start_<=five_:
                afternoon_[start_.time().strftime("%H:%M:%S")]=slot_availabilty_
            else:
                evening_[start_.time().strftime("%H:%M:%S")]=slot_availabilty_
            start_=start_+datetime.timedelta(minutes=duration)
        
        for i in final_:
            if i in old_:
                
                slots_[i]=time_slots[i]
                
            else:
                slots_[i]={
                    "morning":{},
                    "afternoon":{},
                    "evening":{},
                }
                slots_[i]["morning"]=morning_
                slots_[i]["afternoon"]=afternoon_
                slots_[i]["evening"]=evening_

        return slots_
  
    else:
        slots_={}
        for i in availabilty["days"]:
            if i["available"]==True:
                slots_[i["date"]]={
                    "morning":{},
                    "afternoon":{},
                    "evening":{}
                        }
        slot_availabilty_={
            "available":True,
            "count":0
        }
        morning_={}
        afternoon_={}
        evening_={}

        start_=datetime.date(1,1,1)
        end_=datetime.date(1,1,1)

        start_=datetime.datetime.combine(start_,start_time)
        end_=datetime.datetime.combine(end_,end_time)

        twelve_=datetime.datetime.combine(datetime.date(1,1,1),datetime.time(12,0,0))
        five_=datetime.datetime.combine(datetime.date(1,1,1),datetime.time(17,0,0))
        while start_<end_:
            if start_<=twelve_:
                morning_[start_.time().strftime("%H:%M:%S")]=slot_availabilty_
            elif start_<=five_:
                afternoon_[start_.time().strftime("%H:%M:%S")]=slot_availabilty_
            else:
                evening_[start_.time().strftime("%H:%M:%S")]=slot_availabilty_
            start_=start_+datetime.timedelta(minutes=duration)
        for j in slots_.keys():
            slots_[j]["morning"]=morning_
            slots_[j]["afternoon"]=afternoon_
            slots_[j]["evening"]=evening_
        
        return slots_



