    
from django.contrib.auth.models import AbstractUser
from django.db import models
from parking_system import settings

class Company(models.Model):
    name = models.CharField(max_length=100)

class CustomUser(AbstractUser):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null="True")
    is_moderator = models.BooleanField(default=False)

class ParkingSpot(models.Model):
    number = models.IntegerField(unique=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)

    def __str__(self):
        return f"Spot {self.number}"
    
class Reservation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        unique_together = ('spot', 'date')

    def __str__(self):
        return f"Spot {self.spot} reserved by {self.user.username} on {self.date}"

class WaitlistEntry(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date = models.DateField()
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user.username} is waiting for {self.date}"

