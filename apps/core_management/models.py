from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    # 1. Dropdown choices matching your Mongoose Enums
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('admin', 'Administrator'),
        ('hr', 'HR Manager'),
        ('lobby', 'Lobby Desk'),
        ('bgv_officer', 'BGV Officer'),

    ]

    personal_details = models.JSONField(default=dict, blank=True, null=True, verbose_name="Personal JSON Details Matrix")

    # 2. Schema Fields overriding/extending standard AbstractUser
    # email: unique=True, required=True (AbstractUser already has an email column, but we enforce uniqueness)
    email = models.EmailField(
        unique=True,
        verbose_name="Email Address"
    )
    
    # role: enum, default employee
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='employee',
        verbose_name="System Role"
    )
    
    # fullName: String (Replaces native first_name/last_name combinations for flat frontend parsing)
    full_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Full Name"
    )
    
    # authorityLevel: String
    authority_level = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Authority Level"
    )
    
    # step: Number, default 1
    step = models.IntegerField(
        default=1,
        verbose_name="Onboarding Step"
    )
    
    # otp: String
    otp = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name="OTP Code"
    )
    
    # otpExpires: Date
    otp_expires = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="OTP Expiration Timestamp"
    )
    
    # createdBy: ref User
    created_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_users',
        verbose_name="Created By"
    )
    # Inside apps/core_management/models.py -> User Model class

    # FIX: Add the missing updated_at tracker field attribute here
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Last Updated Timestamp"
    )

    profile_photo = models.ImageField(upload_to='employee_assets/photos/', blank=True, null=True, verbose_name="ID Badge Profile Photo")
    passport_doc = models.FileField(upload_to='employee_assets/documents/passports/', blank=True, null=True, verbose_name="Passport Document")
    tenth_certificate_doc = models.FileField(upload_to='employee_assets/documents/certificates/', blank=True, null=True, verbose_name="10th Marksheet Certificate")

        # 🎯 UPDATED SCHEMA: THE 4-DOCUMENT VERIFICATION MATRIX CORES
    pan_card_doc = models.FileField(upload_to='employee_assets/documents/pan/', blank=True, null=True, verbose_name="PAN Card")
    aadhar_card_doc = models.FileField(upload_to='employee_assets/documents/aadhar/', blank=True, null=True, verbose_name="Aadhar Card")
    tenth_marksheet_doc = models.FileField(upload_to='employee_assets/documents/certificates_10th/', blank=True, null=True, verbose_name="10th Marksheet")
    twelfth_marksheet_doc = models.FileField(upload_to='employee_assets/documents/certificates_12th/', blank=True, null=True, verbose_name="12th Marksheet")



    # 3. Use email as the primary login identifier instead of a standard username string
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # Required by Django internals

    class Meta:
        ordering = ['-date_joined']
        verbose_name = "User Directory Account"
        verbose_name_plural = "User Directory Accounts"

    def __str__(self):
        return f"{self.email} ({self.role})"


from django.db import models

class Client(models.Model):
    # Status choices matching your exact Mongoose Enum definitions list keys
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Suspended', 'Suspended'),
        ('Terminated', 'Terminated'),
    ]

    # client_name: String
    client_name = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Client Name"
    )
    
    # industry: String
    industry = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Industry Type"
    )
    
    # contact_person: String
    contact_person = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Contact Person"
    )
    
    # contract_value: Number -> Using DecimalField for exact financial arithmetic
    contract_value = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Contract Value"
    )
    
    # status: enum, default Active
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='Active', 
        verbose_name="Partnership Status"
    )
    
    # projects: [{ type: ObjectId, ref: 'Project' }] 
    # Mapped as a comma-separated text list array container for flat compatibility bounds 
    projects = models.TextField(
        blank=True, 
        null=True, 
        help_text="Comma-separated project IDs list tracker definitions",
        verbose_name="Linked Projects Array"
    )

    # Timestamps (Replaces Mongoose { timestamps: true })
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Client Record"
        verbose_name_plural = "Client Records"

    def __str__(self):
        return f"{self.client_name or 'Unnamed Client'} ({self.status})"


from django.db import models

class ProductClient(models.Model):
    # 1. Dropdown choices matching your exact Mongoose Enums
    LICENSE_CHOICES = [
        ('Trial', 'Trial'),
        ('Standard', 'Standard'),
        ('Premium', 'Premium'),
        ('Enterprise', 'Enterprise'),
    ]

    SUPPORT_CHOICES = [
        ('L1', 'L1 Support'),
        ('L2', 'L2 Support'),
        ('L3', 'L3 Support'),
    ]

    # 2. Schema Fields
    # productId: String
    product_id = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Product ID"
    )

    product_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Product Name"
    )
    
    # clientId: ref Client, required: true
    client = models.ForeignKey(
        'Client',
        on_delete=models.CASCADE,
        related_name='product_licences',
        verbose_name="Licensed Client"
    )
    
    # licenseType: enum, default Standard
    license_type = models.CharField(
        max_length=30,
        choices=LICENSE_CHOICES,
        default='Standard',
        verbose_name="License Type"
    )
    
    # startDate & endDate: Date
    start_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="License Start Date"
    )
    end_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="License End Date"
    )
    
    # supportLevel: enum, default L1
    support_level = models.CharField(
        max_length=10,
        choices=SUPPORT_CHOICES,
        default='L1',
        verbose_name="Technical Support Level"
    )

    # 3. Timestamps (Replaces Mongoose { timestamps: true })
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Licensed Product Client"
        verbose_name_plural = "Licensed Product Clients"

    def __str__(self):
        return f"Product {self.product_id or 'Unknown'} - {self.client.client_name}"
