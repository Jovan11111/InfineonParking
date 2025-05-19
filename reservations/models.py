    
from django.contrib.auth.models import User
from django.db import models

class ParkingSpot(models.Model):
    number = models.IntegerField(unique=True)

    def __str__(self):
        return f"Spot {self.number}"
    
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    spot = models.ForeignKey(ParkingSpot, on_delete=models.CASCADE)
    date = models.DateField()

    class Meta:
        unique_together = ('spot', 'date')

    def __str__(self):
        return f"Spot {self.spot} reserved by {self.user.username} on {self.date}"

class WaitlistEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'date')
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user.username} is waiting for {self.date}"

