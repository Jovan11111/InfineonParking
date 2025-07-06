from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomUserCreationForm
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from .models import Reservation, ParkingSpot, WaitlistEntry, UserProfile
from django.http import JsonResponse
import json
from django.middleware.csrf import rotate_token
from .async_email import send_mail_async

def login_user(request):
    if request.user.is_authenticated:
        return redirect('/main')
    
    rotate_token(request)
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)    
            if request.POST.get('remember_me'):
                request.session.set_expiry(315360000) 
            else:
                request.session.set_expiry(0)        
            return redirect('/main') 
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
            return redirect('/main')
    context = {'form': form}
    return render(request, 'register.html', context)

@login_required
def main_page(request):
    today = datetime.today().date()
    max_day = today + timedelta(days=7)
    
    date = request.GET.get('date', datetime.today().strftime('%Y-%m-%d'))
    selected_date = datetime.strptime(date, '%Y-%m-%d').date()
    
    if not (today <= selected_date <= max_day):
        return redirect(f'/main?date={today.strftime("%Y-%m-%d")}&invalid_date=true')
    
    spots = ParkingSpot.objects.all()
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
        'spots': spots,
        'all_spots_taken': all_spots_taken,
        'date_selected': date,
        'num_interested': num_interested
    }

    return render(request, 'main.html', context)

@login_required
def get_spots_for_date(request):
    date_str = request.GET.get('date')
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Nevažeći datum'}, status=400)

    today = datetime.today().date()
    max_day = today + timedelta(days=7)

    if not (today <= date <= max_day):
        return JsonResponse({'error': 'Datum van opsega'}, status=400)

    spots_data = []
    spots = ParkingSpot.objects.all()
    for spot in spots:
        reservation = Reservation.objects.filter(date=date, spot=spot).first()
        spots_data.append({
            'id': spot.id,
            'number': spot.number,
            'reserved': bool(reservation),
            'reserved_by': reservation.user.username if reservation else None
        })

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
    return JsonResponse({
        'spots': spots_data,
        'num_interested' : num_interested,
        'all_spots_taken': all_spots_taken
    })

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
        return JsonResponse({"success": True, "reserved_by": request.user.username})

    return JsonResponse({"success": False, "error": "Invalid request method"})

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
            return JsonResponse({"success": True, "waitlist_entry": None})

        Reservation.objects.create(
            user=entry.user,
            spot=spot,
            date=date
        )

        send_mail_async("Parking spot reserved for you!", 
                        f"You have been automatically assigned a spot ({spot}) for {date}.", 
                        "infineonparking@gmail.com",
                        [entry.user.email]
                        )

        entry.delete()

        return JsonResponse({
            "success": True, 
            "waitlist_entry": entry.user.username
        })
    return JsonResponse({"success": False, "error": "Invalid request method"})

@login_required
def interest_queue(request):
    if request.method == "POST":
        date_str = request.POST.get("date")
        print(date_str)
        user = request.user
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return JsonResponse({"success": False, "error": "Invalid request method"})
        
        user_profile = UserProfile.objects.get(user=user)
        company = user_profile.company

        WaitlistEntry.objects.create(user=user, date=date_obj, company=company)

    return JsonResponse({"success": True})