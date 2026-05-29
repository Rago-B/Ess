from django.db import models
from django.utils import timezone


class Employee(models.Model):

    DEPARTMENT_CHOICES = [
        ('HR' , 'Human Resources'),
        ('IT' , 'Information Technology'),
        ('FIN' , 'Finanace'),
        ('MKT' , 'Marketting'),
        ('OPS' , 'Operations'),
    ]



    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    department=models.CharField(max_length=3 , choices=DEPARTMENT_CHOICES , default='IT')
    rfid_uid=models.CharField(max_length=50 , unique=True)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    


class AttendanceLog(models.Model):
    DIRECTION_CHOICES = [
        ('IN', 'Clock In'),
        ('OUT', 'Clock Out'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(default=timezone.now)
    direction = models.CharField(max_length=3, choices=DIRECTION_CHOICES, default='IN')

    class Meta:
        ordering = ['-timestamp']  
    def __str__(self):
        return f"{self.employee} - {self.direction} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    


class DailyAttendance(models.Model):
    employee=models.ForeignKey(Employee,on_delete=models.CASCADE,related_name='attendance_records')
    date=models.DateField(default=timezone.now)
    check_in=models.DateTimeField(null=True , blank=True)
    check_out = models.DateTimeField(null=True , blank=True)
    total_hours =models.FloatField(default=0.0)


    class Meta:
        ordering = ['-date', '-check_in']
        unique_together = ('employee', 'date') # Restricts to one core record per employee per day

    def __str__(self):
        return f"{self.employee} on {self.date}"

