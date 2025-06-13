from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Reservation, ParkingSpot, WaitlistEntry, Company
from django.http import JsonResponse
from django.core.mail import send_mail
import json

def login_user(request):
    if request.user.is_authenticated:
        if not request.user.company:
                return redirect('/logout')
        return redirect('company', id=request.user.company.id)

    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('company', id=user.company.id) 
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    return redirect('/')

def register_user(request):
    form = CustomUserCreationForm()
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/company', id=user.company.id)
    context = {'form': form}
    return render(request, 'register.html', context)

@login_required
def main_page(request):
    return render(request, 'main.html', {})


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
        
        entry = WaitlistEntry.objects.filter(date=date).order_by('timestamp').first()
        
        if not entry:
            return JsonResponse({"success": True})

        Reservation.objects.create(
            user=entry.user,
            spot=spot,
            date=date
        )

        send_mail(
            subject="Parking spot reserved for you!",
            message=f"You have been automatically assigned a spot ({spot}) for {date}.",
            from_email="infineonparking@gmail.com",
            recipient_list=[entry.user.email],
            fail_silently=False,
        )

        entry.delete()

        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Invalid request method"})

@login_required
def interest_queue(request):
    if request.method == "POST":
        date_str = request.POST.get("date")
        user = request.user
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return redirect('/company', id=user.company.id)

        WaitlistEntry.objects.create(user=user, date=date_obj)

    return redirect('/company', id=user.company.id)

def company(request, id):
    date = request.GET.get('date', datetime.today().strftime('%Y-%m-%d'))
    company = Company.objects.get(id=id)
    spots = ParkingSpot.objects.filter(company=company)
    user = request.user
    user_has_reservation = False

    for spot in spots:
        reservation = Reservation.objects.filter(date=date, spot=spot).first()
        if reservation:
            spot.reserved = True
            spot.reserved_by = reservation.user.username
            if reservation.user == user:
                user_has_reservation = True
        else:
            spot.reserved = False
            spot.reserved_by = None

    already_in_queue = WaitlistEntry.objects.filter(user=user, date=date).exists()

    all_spots_taken = (
        all(s.reserved for s in spots) and 
        not user_has_reservation and 
        not already_in_queue
    )

    num_interested = WaitlistEntry.objects.filter(date=date).count()

    context = {
        'moderator_status' : user.is_moderator,
        'company_id' : user.company.id,
        'spots': spots,
        'all_spots_taken': all_spots_taken,
        'date_selected': date,
        'num_interested': num_interested
    }

    return render(request, 'company.html', context)

@login_required
def moderator(request, id):
    spots = ParkingSpot.objects.filter(company=id)
    context = {
        'spots' : spots,
        'company_id' : id
    }
    return render(request, 'moderator.html', context)

@login_required
def add_parking_spot(request, id):
    spot_number = request.POST.get("spot_num")
    company = Company.objects.get(id=id)
    ParkingSpot.objects.create(number=spot_number, company=company)

    return redirect('moderator', id=id)