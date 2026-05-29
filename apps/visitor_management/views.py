from django.shortcuts import render ,redirect
from .models import Visitor
from django.utils import timezone
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
def visitor_management (request):

    return render (request,'visitor_management/dashboard.html')


def view_visitors(request):
      visitors=Visitor.objects.all().order_by('check_in')
      context = {
        'visitors':visitors
       }
      for v in visitors :
            print(f"Name: {v.name} | College: {v.college_name} | Year: {v.passed_out_year} | Phone: {v.phone}")


      print(context)
      return render(request,'visitor_management/view_visitors.html',context)



from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Visitor

def add_visitor_form(request):
    # 1. When the user clicks the submit button:
    if request.method == 'POST':
        # Grab the text values from the HTML input fields
        v_name = request.POST.get('name')
        v_phone = request.POST.get('phone')
        v_email = request.POST.get('email')
        v_college = request.POST.get('college_name')
        v_year = request.POST.get('passed_out_year')
        v_purpose = request.POST.get('purpose')
        v_profile_photo=request.FILES.get('profile_photo')

        # 2. Save the new visitor into your database model
        Visitor.objects.create(
            name=v_name,
            phone=v_phone,
            email=v_email,
            profile_photo=v_profile_photo,
            college_name=v_college if v_college else "",
            passed_out_year=int(v_year) if v_year else None,
            purpose=v_purpose,
            check_in=timezone.now()  # Automatically sets the arrival time right now
        )

        return redirect('viewvisitors')

    return render(request, 'visitor_management/add_visitors.html')


def edit_visitors(request):
     
    if request.method=='POST':
     #targets the model  so we can can acess like visitor.name
     visitor_id=request.POST.get('visitor_id')   


     visitor=get_object_or_404(Visitor,id=visitor_id)

     visitor.name=request.POST.get('name','').strip()
     visitor.email=request.POST.get('email','').strip()
     visitor.phone=request.POST.get('phone','').strip()
     visitor.college_name=request.POST.get('college_name','').strip()

     visitor.passed_out_year=request.POST.get('passed_out_year',' ').strip()
     visitor.purpose=request.POST.get('purpose', '')

     if 'profile_photo' in request.FILES :
         visitor.profile_photo = request.FILES['profile_photo']

     visitor.save()

     return redirect('viewvisitors')





     


    visitors=Visitor.objects.all().order_by('check_in')

    context={
          'visitors':visitors
     }


     
     
    return render(request,'visitor_management/edit_visitors.html',context)



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Visitor

import subprocess
import sys
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from apps.visitor_management.models import Visitor  # Ensure app name is correct

def api_delete_visitor(request, visitor_id):
    if request.method == "POST":
        # 1. Grab target visitor entry details from your database before erasing it
        visitor = get_object_or_404(Visitor, id=visitor_id)
        target_email = visitor.email
        visitor_name = visitor.name
        
        # 2. Wipe the row layout from your local Django database grid instantly
        visitor.delete()

        # 3. EXACT METHOD FROM TERMINAL: Launch your clean script out-of-process
        # This completely mimics typing 'python delete_sheets.py Raj@gmail.com' into your command prompt
        try:
            # sys.executable targets your exact active python / virtual environment path
            subprocess.Popen(
                [sys.executable, "delete_sheets.py", target_email],
                stdout=sys.stdout, 
                stderr=sys.stderr
            )
            google_status = "Isolated terminal execution process spawned successfully."
        except Exception as e:
            google_status = f"System failed to call standalone shell thread: {str(e)}"

        return JsonResponse({
            "success": True, 
            "message": f"Wiped record grid for {visitor_name}. Sheets Status: {google_status}"
        })
        
    return JsonResponse({"success": False, "message": "Invalid method request type."}, status=400)



from apps.visitor_management.utils import sync_google_sheets_data
from django.contrib import messages
from django.core.management import call_command

def refresh_google_sheets(request):
    try:
        call_command('sync_visitors') 
        messages.success(request,"visitor data synced Successfull")
    except Exception as e :
        messages.error(request,f"Sync failed :{str(e)}")

    return redirect ('viewvisitors')