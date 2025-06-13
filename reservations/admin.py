from django.contrib import admin
from .models import Reservation, ParkingSpot, CustomUser, Company, WaitlistEntry
admin.site.register(Reservation)
admin.site.register(ParkingSpot)
admin.site.register(CustomUser)
admin.site.register(Company)
admin.site.register(WaitlistEntry)