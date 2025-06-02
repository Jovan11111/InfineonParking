# Parking Reservation System for Infineon Office

## Summary
The Parking Reservation System is a web application designed to help employees at the Infineon office efficiently book parking spots. The system allows users to check parking availability, reserve spots for specific dates, and manage their reservations. It solves the problem of parking space mismanagement by ensuring that only authorized users can book and manage spots while preventing double bookings. Additionally, superusers have the ability to oversee and manage all reservations.

## User Types

### Logged User
A logged-in user can:
- Select a date and view available parking spots.
- Reserve an available parking spot for a specific date.
- Cancel their own reservations if needed.
- View their existing reservations.

### Superuser
A superuser (admin) has additional privileges, including:
- Viewing and managing all reservations.
- Canceling any user's reservation if needed.
- Overseeing parking availability and ensuring fair usage.
- Managing user accounts and permissions.

## Functional Requirements

### User Registration
Users must be able to register an account with a username and password to access the system.
- Navigate to the registration page.
- Fill in the required details and submit the form.
- Upon successful registration, the user is logged in and redirected to the main page.

### User Login & Logout
Users must authenticate themselves before accessing the system.
- Navigate to the login page.
- Enter valid credentials.
- Upon successful login, users can access the reservation system.
- Click the "Logout" button to log out of the system.

### Parking Spot Selection
Users can view and select available parking spots for a chosen date.
- Use the date picker to select a desired date.
- Available spots are displayed visually.
- Click on a free spot to make a reservation.

### Reserving a Parking Spot
Users can reserve an available parking spot for a specific date.
- Click on an available spot.
- Confirm the reservation.
- The spot is marked as reserved and cannot be booked by another user.

### Canceling a Reservation
Users can cancel their own reservations.
- Navigate to their reserved spot.
- Click to unreserve the spot.
- Confirm the action, after which the spot becomes available again.

### Waitlist
If all the parking spots are reserved for a some day, users can insert themselves into the waitlist for that day by clicking the "Zainteresovan" button.
If someone unreserves a spot, the first in the waitling list will automatically be assigned that spot, and will receive an email about it

### Admin Management
Superusers can manage reservations and oversee the system.
- View all reservations.
- Cancel reservations if needed.
- Manage user accounts and permissions.

### Admin Dashboard Access
Superusers can access the Django admin panel to manage users and reservations.
- Navigate to `/admin`.
- Log in with superuser credentials.
- Access the reservation and user management panels.

### Deployment & Accessibility
The system is deployed on Railway and accessible via a unique URL.
- Hosted on a cloud platform with a MySQL database.
- Admin panel remains accessible for superusers.

