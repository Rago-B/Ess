from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import SeatAllocation
from django.contrib.auth import get_user_model

User = get_user_model()

def seat_allocation(request):
    # 1. Matches: router.get('/seats') with .populate('employeeId')
    seats = SeatAllocation.objects.all().select_related('employee')
    employees = User.objects.filter(is_active=True)

    vacant_count = seats.filter(status='Vacant').count()
    allocated_count = seats.filter(status='Allocated').count()

    # 2. Matches: router.put('/seats/:id/allocate')
    if request.method == "POST" and "allocate_seat_id" in request.POST:
        seat_id = request.POST.get("allocate_seat_id")
        emp_id = request.POST.get("employee_id")
        alloc_date = request.POST.get("allocation_date") or timezone.now().date()
        
        try:
            seat = SeatAllocation.objects.get(id=seat_id)
            employee = User.objects.get(id=emp_id)
            
            # Update fields exactly like the Mongoose update body payload
            seat.employee = employee
            seat.allocation_date = alloc_date
            seat.status = 'Allocated'
            seat.save()
            messages.success(request, f"Seat {seat.seat_id} allocated successfully!")
        except Exception as e:
            messages.error(request, f"Failed to allocate seat: {e}")
        return redirect('seatallocation')

    # 3. Matches: router.put('/seats/:id/deallocate')
    vacate_id = request.GET.get('vacate')
    if vacate_id:
        try:
            seat = SeatAllocation.objects.get(id=vacate_id)
            
            # Clear fields exactly like setting them to null in Mongoose
            seat.employee = None
            seat.allocation_date = None
            seat.status = 'Vacant'
            seat.save()
            messages.success(request, f"Seat {seat.seat_id} vacated successfully!")
        except Exception as e:
            messages.error(request, f"Failed to vacate seat: {e}")
        return redirect('seatallocation')

    context = {
        'seats': seats,
        'employees': employees,
        'vacant_count': vacant_count,
        'allocated_count': allocated_count,
        'current_date': timezone.now().date().strftime('%Y-%m-%d')
    }
    return render(request, "office_logistics/seatallocat.html", context)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import Asset
from django.contrib.auth import get_user_model

User = get_user_model()

def asset_allocation_view(request):
    """
    Matches Mongoose: router.get('/') and router.post('/') / router.put('/:id')
    """
    # 1. Capture query filter from URL parameters matching req.query.assignedTo
    assigned_to_filter = request.GET.get('assignedTo')
    
    # 2. Base Query matching: Asset.find(query).populate('emp_id').sort({ createdAt: -1 })
    query_set = Asset.objects.all().select_related('employee').order_by('-created_at')
    
    if assigned_to_filter:
        query_set = query_set.filter(employee_id=assigned_to_filter)
    
    # Fetch all employees for the modal dropdown mapping selection
    employees = User.objects.filter(is_active=True)

    # Calculate reactive totals for the 3 light-theme metrics cards
    total_assets = query_set.count()
    available_count = query_set.filter(status='Available').count()
    assigned_count = query_set.filter(status='Assigned').count()

    # 3. Handle data mutation form logic submission
    if request.method == "POST":
        asset_pk = request.POST.get("selected_id")
        asset_type = request.POST.get("asset_type")
        serial_no = request.POST.get("serial_no")
        emp_id = request.POST.get("emp_id")
        form_status = request.POST.get("status", "Available")

        # Replicate automated payload state assignment
        final_status = 'Assigned' if emp_id else form_status

        employee_obj = None
        if emp_id:
            try:
                employee_obj = User.objects.get(id=emp_id)
            except User.DoesNotExist:
                pass

        if asset_pk:  
            # MATCHES router.put('/:id') -> Asset.findByIdAndUpdate
            asset = get_object_or_404(Asset, id=asset_pk)
            asset.asset_type = asset_type
            asset.serial_no = serial_no
            asset.employee = employee_obj
            asset.status = final_status
            asset.save()
            messages.success(request, 'Asset record updated successfully!')
        else:  
            # MATCHES router.post('/') -> new Asset(req.body).save()
            Asset.objects.create(
                asset_type=asset_type,
                serial_no=serial_no,
                employee=employee_obj,
                status=final_status
            )
            messages.success(request, 'Asset record created successfully!')

        return redirect('assetallocation')

    context = {
        'assets': query_set,
        'employees': employees,
        'total_assets': total_assets,
        'available_count': available_count,
        'assigned_count': assigned_count,
        'active_section': 'asset_allocation'
    }
    return render(request, "office_logistics/assetallocation.html", context)


def delete_asset_view(request, asset_id):
    
    asset = get_object_or_404(Asset, id=asset_id)
    asset.delete()
    messages.success(request, 'Asset deleted successfully!')
    return redirect('asset_allocation')

# Open apps/office_logistics/views.py and paste this exact complete code:

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .models import VehiclePass
from django.contrib.auth import get_user_model

User = get_user_model()

# Inside apps/office_logistics/views.py

def vehicle_passes_view(request):
    passes = VehiclePass.objects.all().select_related('employee').order_by('-created_at')
    employees = User.objects.filter(is_active=True)

    if request.method == "POST":
        selected_id = request.POST.get("selected_id")
        emp_id = request.POST.get("employee_id")
        vehicle_number = request.POST.get("vehicle_number")
        vehicle_type = request.POST.get("vehicle_type", "4-Wheeler")
        
        # 1. FIX: Grab the form input data value
        parking_slot = request.POST.get("pass_type", "Regular") 
        valid_until = request.POST.get("valid_until")

        try:
            employee_obj = User.objects.get(id=emp_id)
            clean_date = valid_until if valid_until else None

            if selected_id:  
                # Edit Mode
                pass_obj = get_object_or_404(VehiclePass, id=selected_id)
                pass_obj.employee = employee_obj
                pass_obj.vehicle_number = vehicle_number
                pass_obj.vehicle_type = vehicle_type
                
                # 2. FIX: Map it to your true database column field name
                pass_obj.parking_slot = parking_slot 
                pass_obj.valid_until = clean_date
                pass_obj.save()
                messages.success(request, 'Vehicle pass updated successfully!')
            else:  
                # Create Mode
                # 3. FIX: Create the record using the correct keyword parameter field key
                VehiclePass.objects.create(
                    employee=employee_obj,
                    vehicle_number=vehicle_number,
                    vehicle_type=vehicle_type,
                    parking_slot=parking_slot, 
                    valid_until=clean_date
                )
                messages.success(request, 'Vehicle pass issued successfully!')
                
        except User.DoesNotExist:
            messages.error(request, 'Selected employee profile could not be found.')
        except Exception as e:
            messages.error(request, f'An error occurred while saving the pass: {e}')

        return redirect('vehiclepasses')

    context = {
        'passes': passes,
        'employees': employees,
        'active_section': 'vehicle_passes',
        'current_date': timezone.now().date().strftime('%Y-%m-%d')
    }
    return render(request, "office_logistics/vehiclepasses.html", context)



def revoke_pass_view(request, pass_id):
    """
    MATCHES Mongoose: router.delete('/vehicle-passes/:id') -> findByIdAndDelete
    """
    pass_obj = get_object_or_404(VehiclePass, id=pass_id)
    pass_obj.delete()
    messages.success(request, 'Vehicle pass revoked successfully!')
    return redirect('vehiclepasses')




from .models import CafeteriaComplaint
# =========================================================================
# 4. CAFETERIA CONTROLLERS
# =========================================================================
def cafeteria_management_view(request):
    active_filter = request.GET.get('filter', 'All')
    complaints = CafeteriaComplaint.objects.all().select_related('employee').order_by('-date')
    
    stats = {
        'total': complaints.count(),
        'pending': complaints.filter(status='Pending').count(),
        'addressed': complaints.filter(status='Addressed').count(),
        'resolved': complaints.filter(status='Resolved').count()
    }

    if active_filter != 'All':
        complaints = complaints.filter(status=active_filter)

    context = {
        'complaints': complaints, 'current_filter': active_filter,
        'stats': stats, 'active_section': 'cafeteria_mgt'
    }
    return render(request, "office_logistics/cafeteriamanagement.html", context)

def update_complaint_status_view(request, complaint_id, new_status):
    complaint = get_object_or_404(CafeteriaComplaint, id=complaint_id)
    if new_status in ['Pending', 'Addressed', 'Resolved']:
        complaint.status = new_status
        complaint.save()
        messages.success(request, f"Complaint marked as {new_status}")
    return redirect(f"/cafeteria/?filter={request.GET.get('filter', 'All')}")
