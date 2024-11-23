from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    # Add custom fields here, if needed

    def __str__(self):
        return self.username
    

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=100)
    available_count = models.PositiveIntegerField()

class Rental(models.Model):
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'member'})
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    rental_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    fine = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

class Request(models.Model):
    member = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'member'})
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('denied', 'Denied')], default='pending')
