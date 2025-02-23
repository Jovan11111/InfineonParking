from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Reservation, ParkingSpot
from django.http import JsonResponse
import json

def login_user(request):
    if request.user.is_authenticated:
        return redirect('/main')

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('/main') 
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('/')

def register_user(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/main')
        else:
            print(form.non_field_errors)
    context = {'form': form}
    return render(request, 'register.html', context)

@login_required
def main_page(request):
    date = request.GET.get('date', datetime.today().strftime('%Y-%m-%d'))
    spots = ParkingSpot.objects.all()

    for spot in spots:
        reservation = Reservation.objects.filter(date=date, spot=spot).first()
        if reservation:
            spot.reserved = True
            spot.reserved_by = reservation.user.username
        else:
            spot.reserved = False
            spot.reserved_by = None

    return render(request, 'main.html', {'spots': spots})

@csrf_exempt
@login_required
def reserve_spot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        spot_id = data.get('spot_id')
        date = data.get('date', datetime.today().strftime('%Y-%m-%d'))

        if Reservation.objects.filter(user=request.user, date=date).exists():
            return JsonResponse({"success": False, "error": "Vec ste rezervisali mesto za izabrani datum!"})

        spot = ParkingSpot.objects.get(id=spot_id)

        if Reservation.objects.filter(date=date, spot=spot).exists():
            return JsonResponse({"success": False, "error": "Mesto je vec rezervisano!"})

        Reservation.objects.create(user=request.user, spot=spot, date=date)
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request method"})

@csrf_exempt
@login_required
def unreserve_spot(request):
    if request.method == "POST":
        data = json.loads(request.body)
        spot_id = data.get('spot_id')
        date = data.get('date', datetime.today().strftime('%Y-%m-%d'))

        spot = ParkingSpot.objects.get(id=spot_id)
        reservation = Reservation.objects.filter(date=date, spot=spot).first()

        if not reservation:
            return JsonResponse({"success": False, "error": "No reservation found!"})

        if request.user != reservation.user and not request.user.is_superuser:
            return JsonResponse({"success": False, "error": "You can only cancel your own reservation!"})

        reservation.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"success": False, "error": "Invalid request method"})