from django.db import models


class Visitor(models.Model):
    name = models.CharField(max_length=100 , blank=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    purpose = models.TextField()
    college_name=models.CharField(max_length=100 , null=True)
    passed_out_year=models.CharField(max_length=100,blank=True)
    check_in = models.DateTimeField()
    check_out = models.DateTimeField(blank=True, null=True)
    profile_photo=models.ImageField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.email})"
