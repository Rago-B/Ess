from django.shortcuts import render,redirect
from .models import *
from django.contrib import messages
from django.utils import timezone
import time
import datetime
def rfid(request):

    today = timezone.now().date()



    if request.method=="POST":
       

        first_name=request.POST.get('first_name')
        last_name=request.POST.get('last_name')
        department=request.POST.get('department')
        rfid_uid=request.POST.get('rfid_uid','').strip()


        if Employee.objects.filter(rfid_uid=rfid_uid).exists():
            messages.error(request,f"card{rfid_uid} is already registered")
        else :

            Employee.objects.create (
                first_name=first_name ,
                last_name=last_name,
                department=department,
                rfid_uid=rfid_uid
            )

            messages.success(request,f"Sucessfully Registered{first_name} {last_name}")
    total_active_workforce = Employee.objects.filter(is_active=True).count()
    todays_attendance = DailyAttendance.objects.filter(date=today, employee__isnull=False)

    total_present=todays_attendance.count()
    total_absent=total_active_workforce-total_present
    shift_cutoff_time = timezone.make_aware(datetime.datetime.combine(today, datetime.time(9, 0, 0)))
    total_late = todays_attendance.filter(check_in__gt=shift_cutoff_time).count()
    currently_inside = todays_attendance.filter(check_out__isnull=True).count()
    user_information=Employee.objects.all()
    context = {
        'user': Employee.objects.all(),
        'total_present': total_present,
        'total_absent': total_absent,
        'total_late': total_late,
        'currently_inside': currently_inside,
    }

    return render(request,"Rfid_system/rfid.html",context)



def gate_activity(request):

    today = timezone.now().date()
    scanned_uid = request.GET.get('scan_uid', '').strip()
    filter_date=request.GET.get('date_filter')
    filtering=None

    if filter_date :

        try:

            filtering=DailyAttendance.objects.filter(date=filter_date)
        except Exception as e :

            print(f"error {e}")


    if scanned_uid:
        try:
            employee = Employee.objects.get(rfid_uid=scanned_uid, is_active=True)
            record, created = DailyAttendance.objects.get_or_create(employee=employee, date=today)

            if created or not record.check_in:
                record.check_in = timezone.now()
                record.save()
                messages.success(request, f"Welcome {employee.first_name}! Clocked IN.")
            
            elif record.check_in and not record.check_out:
                record.check_out = timezone.now()
                time_diff = record.check_out - record.check_in
                record.total_hours = round(time_diff.total_seconds() / 3600.0, 2)
                record.save()
                messages.success(request, f"Goodbye {employee.first_name}! Clocked OUT. Hours: {record.total_hours}")
        
        except Employee.DoesNotExist:
            messages.error(request, f"🔒 Security Alert: Unregistered Card [{scanned_uid}] detected! Access Denied.")
            
        return redirect('gateactivity') 

    stream_logs = DailyAttendance.objects.filter(date=today).select_related('employee')


   
    context = {
        'stream_logs': stream_logs,
        'filtering':filtering,
       
    }




    
    return render(request, "Rfid_system/gate_activity.html", context)




