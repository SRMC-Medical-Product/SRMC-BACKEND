from mainapp.models import *

def create_doctor_notification(doctorid,msg):
    get_doctor = Doctor.objects.filter(id=doctorid).first()
    if get_doctor is None:
        return {
            "res": False,
            "err": "Doctor not found"
        }

    try:    
        DoctorNotification.objects.create(doctorid=get_doctor,msg=msg)
        return {
            "res": True,
            "err" : None,
        }
    except Exception as e:
        return {
            "res": False,
            "err": str(e)
        }

def create_patient_notification(patientid,msg):
    patient = Patient.objects.filter(id=patientid).first()
    get_doctor = User.objects.filter(id=patient.id).first()
    if get_doctor is None:
        return {
            "res": False,
            "err": "User not found"
        }

    try:    
        PatientNotification.objects.create(patientid=get_doctor,msg=msg)
        return {
            "res": True,
            "err" : None,
        }
    except Exception as e:
        return {
            "res": False,
            "err": str(e)
        }
