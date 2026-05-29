from django.db import models
from django.conf import settings

class Bench(models.Model):
    # emp_id: links to your main employee/user profile model
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bench_allocations',
        verbose_name="Employee"
    )
    
    # skills: String (stores text lists e.g. "React, PHP, Node")
    skills = models.CharField(
        max_length=500, 
        blank=True, 
        null=True, 
        verbose_name="Skills"
    )

    # timestamps: true
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Bench Record"
        verbose_name_plural = "Bench Records"

    # COMPATIBILITY VIRTUAL FOR FRONTEND (Replicates BenchSchema.virtual('bench_id').get)
    @property
    def bench_id(self):
        """Returns the primary key as a string to replicate MongoDB hex string id mapping functionality."""
        return str(self.id)

    def __str__(self):
        return f"Bench - {self.employee.username if self.employee else 'Unknown'}"


class Travel(models.Model):
    # 1. Dropdown choices matching your Mongoose Enums
    TRAVEL_TYPE_CHOICES = [
        ('Domestic', 'Domestic'),
        ('International', 'International'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Completed', 'Completed'),
    ]

    # 2. Schema Fields
    # employeeId: ref User, required=True
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='planning_travel_requests',
        verbose_name="Employee"
    )
    
    # travelType: enum, required=True
    travel_type = models.CharField(
        max_length=20,
        choices=TRAVEL_TYPE_CHOICES,
        verbose_name="Travel Type"
    )
    
    # fromLocation & toLocation: String, required=True
    from_location = models.CharField(
        max_length=255, 
        verbose_name="From Location"
    )
    to_location = models.CharField(
        max_length=255, 
        verbose_name="To Location"
    )
    
    # purpose: String
    purpose = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Purpose"
    )
    
    # cost: Number -> Using DecimalField for secure currency tracking
    cost = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        verbose_name="Estimated Cost"
    )
    
    # status: enum, default Pending
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        verbose_name="Status"
    )
    
    # departureDate & returnDate: Date
    departure_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Departure Date"
    )
    return_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Return Date"
    )

    # 3. Timestamps (Replaces Mongoose { timestamps: true })
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Travel Request"
        verbose_name_plural = "Travel Requests"

    def __str__(self):
        return f"Travel to {self.to_location} - {self.employee.username} ({self.status})"
    

class CostMonitoring(models.Model):
    # projectId: links to a corporate Project model layout box tracker
    # (Assuming you have a 'Project' model or string reference to it)
    project_id = models.CharField(
        max_length=255, 
        verbose_name="Project ID / Name"
    )
    
    # Currency values mapping -> Using DecimalField instead of floats to prevent penny rounding errors
    budget = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Allocated Budget"
    )
    
    actual_cost = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Actual Cost Incurred"
    )
    
    resource_cost = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Human Resource Cost"
    )
    
    travel_cost = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00, 
        verbose_name="Travel & Transport Cost"
    )
    
    # variance: auto-calculated field tracking budget deviations
    variance = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00, 
        blank=True, 
        verbose_name="Budget Variance"
    )

    # Timestamps (Replaces Mongoose { timestamps: true })
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Cost Monitoring Record"
        verbose_name_plural = "Cost Monitoring Records"

    # Automated Calculation Engine (Saves hours of manual computing entry lines)
    def save(self, *args, **kwargs):
        """
        Replicates raw backend schema compute hooks.
        Automatically calculates variance before committing to database rows.
        """
        self.variance = self.budget - self.actual_cost
        super(CostMonitoring, self).save(*args, **kwargs)

    def __str__(self):
        return f"Cost Track - {self.project_id} (Variance: {self.variance})"
    



class ChangePlan(models.Model):
    # 1. Dropdown choices matching your Mongoose Enums
    IMPACT_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    # 2. Schema Fields
    # projectId: links to a corporate Project (Using CharField for flat compatibility)
    project_id = models.CharField(
        max_length=255, 
        verbose_name="Project ID / Name"
    )
    
    # changeDescription: String, required=True
    change_description = models.TextField(
        verbose_name="Change Description"
    )
    
    # impact: enum, default Low
    impact = models.CharField(
        max_length=20,
        choices=IMPACT_CHOICES,
        default='Low',
        verbose_name="Impact Level"
    )
    
    # status: enum, default Pending
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        verbose_name="Status"
    )
    
    # effectiveDate: Date
    effective_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Effective Date"
    )

    # 3. Timestamps (Replaces Mongoose { timestamps: true })
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Change Plan"
        verbose_name_plural = "Change Plans"

    def __str__(self):
        return f"Change Plan - {self.project_id} ({self.status})"

from django.db import models

class Policy(models.Model):
    # 1. Dropdown choices matching your Mongoose Enums
    CATEGORY_CHOICES = [
        ('HR', 'HR'),
        ('IT', 'IT'),
        ('Security', 'Security'),
        ('Financial', 'Financial'),
        ('General', 'General'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Archived', 'Archived'),
    ]

    # 2. Schema Fields
    # policyName: String, required=True
    policy_name = models.CharField(
        max_length=255, 
        verbose_name="Policy Name"
    )
    
    # category: enum, required=True
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        verbose_name="Category"
    )
    
    # version: String, default='1.0'
    version = models.CharField(
        max_length=50,
        default='1.0',
        verbose_name="Version"
    )
    
    # effectiveDate: Date
    effective_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Effective Date"
    )
    
    # documentPath: String -> Replicated cleanly for file links/paths
    document_path = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Document Path/Link"
    )
    
    # status: enum, default Active
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Active',
        verbose_name="Status"
    )

    # 3. Timestamps (Replaces Mongoose { timestamps: true })
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Policy Hub Record"
        verbose_name_plural = "Policy Hub Records"

    def __str__(self):
        return f"{self.policy_name} v{self.version} ({self.status})"

from django.db import models
from django.conf import settings

class Certification(models.Model):
    # Relation to User model
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="certifications"
    )

    # Unified fields
    name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255, blank=True, null=True)
    issue_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    credential_id = models.CharField(max_length=255, blank=True, null=True)
    credential_url = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=50, default="Active")

    # Legacy fields for backward compatibility
    certification_name = models.CharField(max_length=255, blank=True, null=True)  # Maps to name
    provider = models.CharField(max_length=255, blank=True, null=True)            # Maps to issuingOrganization
    completion_date = models.DateField(blank=True, null=True)                     # Maps to issueDate
    validity = models.CharField(max_length=255, blank=True, null=True)            # Maps to expiryDate (string)
    certificate_path = models.CharField(max_length=500, blank=True, null=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.employee}"
