from django.db import models

from django.db import models
from django.conf import settings  # Use this to link cleanly to your user model
from django.utils import timezone

class CafeteriaComplaint(models.Model):
    # 1. Dropdown choices matching your Mongoose Enums
    COMPLAINT_TYPE_CHOICES = [
        ('Food Quality', 'Food Quality'),
        ('Hygiene', 'Hygiene'),
        ('Staff Behavior', 'Staff Behavior'),
        ('Service Delay', 'Service Delay'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Addressed', 'Addressed'),
        ('Resolved', 'Resolved'),
    ]

    # 2. Schema Fields
    # ForeignKey links to your User model (replaces mongoose.Schema.Types.ObjectId)
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='cafeteria_complaints',
        verbose_name="Employee"
    )
    
    complaint_type = models.CharField(
        max_length=50, 
        choices=COMPLAINT_TYPE_CHOICES, 
        verbose_name="Complaint Type"
    )
    
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Description"
    )
    
    date = models.DateTimeField(
        default=timezone.now, 
        verbose_name="Date Logged"
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Pending', 
        verbose_name="Status"
    )

    # 3. Timestamps (Replaces Mongoose { timestamps: true })
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date'] # Shows newest complaints first by default

    def __str__(self):
        return f"{self.complaint_type} - {self.status} ({self.employee.username})"

from django.db import models
from django.conf import settings

class SeatAllocation(models.Model):
    # 1. Dropdown choices matching your Mongoose Enum
    STATUS_CHOICES = [
        ('Allocated', 'Allocated'),
        ('Vacant', 'Vacant'),
        ('Maintenance', 'Maintenance'),
    ]

    # 2. Schema Fields
    # seatId: String, required, unique -> unique=True makes it index-optimized
    seat_id = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Seat ID"
    )
    
    # floor & location: String -> mapped to nullable/blank-friendly CharFields
    floor = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Floor"
    )
    
    location = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Location"
    )
    
    # employeeId: ref User -> null=True makes it completely optional if a seat is "Vacant"
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='seat_allocations',
        verbose_name="Assigned Employee"
    )
    
    # allocationDate: Date -> Standard clean date input field tracking mapping
    allocation_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Allocation Date"
    )
    
    # status: enum, default Vacant -> Enforces matching structural choices rules
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Vacant', 
        verbose_name="Status"
    )

    # 3. Timestamps (Replaces Mongoose { timestamps: true })
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['seat_id']

    def __str__(self):
        assigned_to = self.employee.username if self.employee else "None"
        return f"Seat {self.seat_id} - {self.status} (Assigned to: {assigned_to})"


from django.db import models
from django.conf import settings
from django.utils import timezone

class Asset(models.Model):
    # 1. Dropdown choices matching your Mongoose Enums
    ASSET_TYPE_CHOICES = [
        ('Laptop', 'Laptop'),
        ('Monitor', 'Monitor'),
        ('Phone', 'Phone'),
        ('Other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Assigned', 'Assigned'),
        ('In Repair', 'In Repair'),
        ('Scrapped', 'Scrapped'),
    ]

    # 2. Schema Fields
    # asset_id: String, unique -> blank=True lets Django save the form before generating the ID
    asset_id = models.CharField(
        max_length=50, 
        unique=True, 
        blank=True, 
        verbose_name="Asset ID"
    )
    
    asset_type = models.CharField(
        max_length=20, 
        choices=ASSET_TYPE_CHOICES, 
        verbose_name="Asset Type"
    )
    
    serial_no = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Serial Number"
    )
    
    # emp_id: ref User, nullable if unassigned -> on_delete=models.SET_NULL preserves hardware asset history
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='allocated_assets',
        verbose_name="Assigned Employee"
    )
    
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Available', 
        verbose_name="Status"
    )

    # 3. Timestamps (Replaces Mongoose { timestamps: true })
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    # 4. Auto-ID Generation Logic (Replaces Mongoose AssetSchema.pre('save'))
    def save(self, *args, **kwargs):
        if not self.asset_id:
            # Replicates 'AST-' + last 6 digits of current timestamp
            timestamp_str = str(int(timezone.now().timestamp() * 1000))
            self.asset_id = f"AST-{timestamp_str[-6:]}"
        super(Asset, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.asset_id} - {self.asset_type} ({self.status})"


from django.db import models
from django.conf import settings

class VehiclePass(models.Model):
    # 1. Dropdown choices matching your Mongoose Enums
    VEHICLE_TYPE_CHOICES = [
        ('2-Wheeler', '2-Wheeler'),
        ('4-Wheeler', '4-Wheeler'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        ('Revoked', 'Revoked'),
    ]

    # 2. Schema Fields
    # employeeId: ref User, required=True -> cascade delete clears pass if employee is removed
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vehicle_passes',
        verbose_name="Employee"
    )
    
    # vehicleNumber: String, required=True
    vehicle_number = models.CharField(
        max_length=50, 
        verbose_name="Vehicle Number"
    )
    
    # vehicleType: enum, default '2-Wheeler'
    vehicle_type = models.CharField(
        max_length=20, 
        choices=VEHICLE_TYPE_CHOICES, 
        default='2-Wheeler',
        verbose_name="Vehicle Type"
    )
    
    # parkingSlot: String -> nullable/blank allowed
    parking_slot = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="Parking Slot/Bay"
    )
    
    # validUntil: Date -> Standard clean date input field tracker mapping
    valid_until = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Valid Until"
    )
    
    # status: enum, default 'Active'
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Active', 
        verbose_name="Pass Status"
    )

    # 3. Timestamps (Replaces Mongoose { timestamps: true })
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Vehicle Pass"
        verbose_name_plural = "Vehicle Passes"

    def __str__(self):
        return f"{self.vehicle_number} - {self.employee.username} ({self.status})"
