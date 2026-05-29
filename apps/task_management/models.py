from django.db import models

from django.db import models
from django.conf import settings

class Task(models.Model):
    # 1. Dropdown choices matching your Mongoose Enums
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]

    # 2. Mongoose Schema Fields
    # title: { type: String, required: true }
    title = models.CharField(
        max_length=255, 
        verbose_name="Task Title"
    )
    
    # description: String
    description = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Description"
    )
    
    # assignedTo: { type: ObjectId, ref: 'User' } (Optional)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name="Assigned User"
    )
    
    # assignedToEmail: String (Store email for easy lookup)
    assigned_to_email = models.EmailField(
        blank=True, 
        null=True, 
        verbose_name="Assigned User Email"
    )
    
    # priority: { type: String, enum: ['Low', 'Medium', 'High'], default: 'Medium' }
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='Medium',
        verbose_name="Priority"
    )
    
    # dueDate: Date
    due_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Due Date"
    )
    
    # status: { type: String, enum: ['Pending', 'In Progress', 'Completed'], default: 'Pending' }
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        verbose_name="Status"
    )
    
    # completedAt: Date
    completed_at = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name="Completed At"
    )
    
    # notes: String
    notes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Notes"
    )
    
    # createdBy: { type: ObjectId, ref: 'User' }
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_tasks',
        verbose_name="Created By"
    )

    # 3. Timestamps (Replaces Mongoose { timestamps: true })
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['due_date', '-created_at']
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return f"{self.title} ({self.status})"
