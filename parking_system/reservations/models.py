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
        pass
    def __str__(self):
        return f"Spot {self.parking_spot} reserved by {self.user.username} on {self.date}"
    

