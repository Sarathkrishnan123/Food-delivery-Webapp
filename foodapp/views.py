from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib.auth import get_user_model
from .models import UserProfile
from .models import HotelSignup,Menu,CustomUser,Order,Review,OrderIssueReport,Discount,Coupon,Reward
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib import auth
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator
from .models import Menu, ItemDisapproval
from django.db.models import Prefetch
from django.contrib.auth import authenticate, login as auth_login
from .models import UserProfile
from django.http import JsonResponse
from .models import Address
from datetime import datetime
from datetime import date
from django.db.models import Max
from django.core.files.storage import FileSystemStorage  # For handling file uploads
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
CustomUser = get_user_model()
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password
from itertools import groupby

def user_signup(request):
    if request.method == "POST":
        # Collecting form data
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Check if any field is empty
        if not all([username, first_name, last_name, email, phone_number, address, password, confirm_password]):
            messages.error(request, 'All fields are required. Please fill out all the fields.')
            return render(request, 'signup.html')

        # Check if username already exists
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose another.')
            return render(request, 'signup.html')

        # Check if email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please choose another.')
            return render(request, 'signup.html')

        # Validate passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'signup.html')

        # Save CustomUser
        custom_user = CustomUser.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            user_type='2',  # Default to user type
            password=make_password(password),  # Hash password
        )

        # Save UserProfile
        UserProfile.objects.create(
            user=custom_user,
            phone_number=phone_number,
            address=address,
        )

        messages.success(request, 'User account created successfully.')
        return redirect('signup')

    return render(request, 'signup.html')
# Redirect to login page
    
    


def index(request):
    return render(request,'index.html')

def loginpage(request):
    return render(request,'loginpage.html')

def signup(request):
    return render(request,'signup.html')

def hotel_signup(request):
    return render(request,'hotel_signup.html')

def admin(request):
    return render(request,'admin.html')


from django.contrib.auth.decorators import login_required

@login_required
def hotel(request):
    # Retrieve the hotel information for the logged-in user
    try:
        hotel_profile = HotelSignup.objects.get(user=request.user)
    except HotelSignup.DoesNotExist:
        hotel_profile = None

    return render(request, 'hotel.html', {'hotel': hotel_profile})

def add_food(request):
    return render(request,'add_food.html')


from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Avg
import random
from django.core.paginator import Paginator
from django.shortcuts import render

from django.db.models import F

import random
from datetime import date
from django.db.models import Avg, Max
from django.core.paginator import Paginator
from .models import UserProfile, Menu, HotelSignup, Address, Discount

import random
from django.db.models import Avg, Max
from django.core.paginator import Paginator
from datetime import date
from .models import UserProfile, Menu, HotelSignup, Address, RecentSearch, Discount
  # Import the ORS utility function

def user_profile(request):
    profile = UserProfile.objects.all()
    approved_items = Menu.objects.filter(status='approved')
    hotels = HotelSignup.objects.all()

    # Add random rating for each restaurant
    for hotel in hotels:
        hotel.random_rating = round(random.uniform(3.0, 5.0), 1)  # Random rating between 3.0 and 5.0

    # Fetch reviews and calculate average ratings for each menu item
    for item in approved_items:
        reviews = item.reviews.all()
        item.average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] if reviews.exists() else None
        item.estimated_time = random.choice([20, 25, 30, 35, 40])  # Example logic

    paginator = Paginator(approved_items, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    recent_search_items = RecentSearch.objects.filter(user=request.user, menu_item__isnull=False).select_related('menu_item')

    last_address = None
    if request.user.is_authenticated:
        last_address = Address.objects.filter(user=request.user).last()

    today = date.today()

    # Fetch only discounts that are active today
    discount_items = Discount.objects.filter(
        start_date__lte=today, 
        end_date__gte=today
    ).select_related('item')

    # Remove duplicates by using annotate to get the latest discount for each item
    discount_items = discount_items.values('item').annotate(latest_discount=Max('created_at'))

    # Fetch the latest discount for each item by using the annotated 'latest_discount'
    discount_items = Discount.objects.filter(
        created_at__in=[item['latest_discount'] for item in discount_items]
    ).select_related('item')

    # Add original and discounted prices to each item
    for discount in discount_items:
        original_price = discount.item.price
        discount_percentage = discount.discount_percentage
        discount_amount = (original_price * discount_percentage) / 100
        discounted_price = original_price - discount_amount
        discount.original_price = original_price
        discount.discounted_price = discounted_price

    # Get user's address and coordinates (latitude, longitude)
    user_lat = None
    user_lon = None
    if last_address:
        user_lat = last_address.latitude
        user_lon = last_address.longitude

    # Calculate distance and time for each restaurant if the user's address is available
    restaurant_data = []
    for hotel in hotels:
        distance = 'N/A'
        time = 'N/A'
        if user_lat and user_lon and hotel.latitude and hotel.longitude:
            # Calculate distance and time using ORS
            distance, time = calculate_distance_time(
                user_lat, user_lon, hotel.latitude, hotel.longitude, travel_mode="driving-car"
            )
        restaurant_data.append({
            'restaurant': hotel,
            'distance': f"{distance} km" if distance != 'N/A' else 'N/A',
            'time': time if time != 'N/A' else 'N/A',
        })

    return render(request, 'user_profile.html', {
        'profile': profile,
        'page_obj': page_obj,
        'last_address': last_address,
        'hotels': hotels,
        'discount_items': discount_items,
        'recent_search_items': recent_search_items,
        'restaurant_data': restaurant_data,  # Add the restaurant data to the context
    })






from django.contrib.auth.hashers import make_password
from django.contrib import messages

from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .models import CustomUser, HotelSignup

def hotel_signupdb(request):
    if request.method == 'POST':
        # Extract data from the form
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = make_password(request.POST.get('password', '').strip())

        restaurant_name = request.POST.get('restaurant_name', '').strip()
        restaurant_location = request.POST.get('restaurant_location', '').strip()
        address = request.POST.get('address', '').strip()
        contact_number = request.POST.get('contact_number', '').strip()
        operating_from = request.POST.get('operating_from', '').strip()
        operating_to = request.POST.get('operating_to', '').strip()
        registration_number = request.POST.get('registration_number', '').strip()
        owner_name = request.POST.get('owner_name', '').strip()
        owner_number = request.POST.get('owner_number', '').strip()
        gst_type = request.POST.get('gst_type', '').strip()
        gst_number = request.POST.get('gst_number', '').strip()

        # Extract latitude and longitude
        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()

        # Check for empty fields
        if not all([
            username, email, password, restaurant_name, restaurant_location, address,
            contact_number, operating_from, operating_to, registration_number, owner_name,
            owner_number, gst_type, latitude, longitude
        ]):
            messages.error(request, 'All fields are required. Please fill out all the fields.')
            return render(request, 'hotel_signup.html')

        # Check for existing username
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists. Please choose another.')
            return render(request, 'hotel_signup.html')

        # Check for existing email
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please choose another.')
            return render(request, 'hotel_signup.html')

        # Check for existing GST number (if provided)
        if gst_number and HotelSignup.objects.filter(gst_number=gst_number).exists():
            messages.error(request, 'This GST number already exists.')
            return render(request, 'hotel_signup.html')

        # Create User object
        user = CustomUser.objects.create(
            username=username,
            email=email,
            user_type='3',
            password=password
        )

        # Create HotelSignup object with latitude and longitude
        HotelSignup.objects.create(
            user=user,
            restaurant_name=restaurant_name,
            restaurant_location=restaurant_location,
            address=address,
            contact_number=contact_number,
            operating_from=operating_from,
            operating_to=operating_to,
            registration_number=registration_number,
            owner_name=owner_name,
            owner_number=owner_number,
            gst_type=gst_type,
            gst_number=gst_number,
            latitude=latitude,  # Save latitude
            longitude=longitude  # Save longitude
        )

        messages.success(request, 'Hotel Account Created Successfully.')
        return redirect('hotel_signup')  # Redirect to the signup page or another success page

    return render(request, 'hotel_signup.html')


def login1(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            if user.user_type == '1':
                auth_login(request, user)
                return redirect('admin')
            elif user.user_type == '2':
                auth_login(request, user)
                return redirect('user_profile')
            elif user.user_type == '3':
                auth_login(request, user)
                return redirect('hotel')
            elif user.user_type == '4':
                auth_login(request, user)
                return redirect('delivery_agent')
            
        # If authentication fails or user_type doesn't match
        messages.error(request, 'Invalid username or password')
    # Render the login page with the error message (if any)
    return render(request, 'loginpage.html')

def view_user_profile(request):
    profile = UserProfile.objects.all()
    last_address = None
    if request.user.is_authenticated:
        last_address = Address.objects.filter(user=request.user).last()
    return render(request, 'view_user_profile.html', {'profile': profile, 'last_address': last_address})


def logout_user(request):
    """
    Logs out the user and redirects to the login page.
    """
    logout(request)  # Logs out the current user
    return redirect('loginpage')  # Redirects to the login page

def add_fooddb(request):
    if request.method == 'POST':
        # Retrieve form data
        item = request.POST.get('item')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category = request.POST.get('category')
        image = request.FILES.get('image')

        # Check if any required field is empty
        if not all([item, description, price, category, image]):
            messages.error(request, 'All fields are required. Please fill out all the fields.')
            return redirect('add_food')  # Redirect to the same page with an error message

        # Validate the hotel of the currently logged-in user (assuming the user is a hotel owner)
        try:
            # Get the hotel profile for the logged-in user (ensure the user is a hotel)
            hotel_profile = HotelSignup.objects.get(user=request.user)
        except HotelSignup.DoesNotExist:
            messages.error(request, 'No hotel profile found for the logged-in user.')
            return redirect('add_food')  # Redirect to the same page or an error page

        # Create a new Menu item and associate it with the logged-in user's hotel
        menu_item = Menu(
            item=item,
            description=description,
            price=price,
            category=category,
            image=image,
            hotel=hotel_profile  # Assign the hotel profile here
        )
        menu_item.save()

        messages.success(request, 'Food item added successfully! Wait for Admin Approval')
        return redirect('add_food')  # Redirect to the same page or a success page

    return render(request, 'add_food.html')


@login_required
def pending_items(request):
    if request.user.user_type == '1':  # Ensure only admin can view
        pending_items = Menu.objects.filter(status='pending')  # Fetch pending items
        return render(request, 'admin_pending_items.html', {'pending_items': pending_items})
    return redirect('admin')

@login_required



def update_item_status(request, item_id, action):
    if request.user.user_type == '1':  # Ensure only admin can update
        try:
            menu_item = Menu.objects.get(id=item_id)

            if action == 'approve':
                # Set item status to 'approved'
                menu_item.status = 'approved'
                menu_item.save()

            elif action == 'disapprove':
                # Handle the disapproval
                if request.method == 'POST':
                    # Get the reason and type from the POST data
                    reason = request.POST.get('reason')
                    issue_type = request.POST.get('type')

                    # Create a new ItemDisapproval record with the reason and type
                    disapproval = ItemDisapproval(
                        item=menu_item,
                        reason=reason,
                        issue_type=issue_type
                    )
                    disapproval.save()

                    # Set item status to 'disapproved'
                    menu_item.status = 'disapproved'
                    menu_item.save()

        except Menu.DoesNotExist:
            pass

    return redirect('pending_items')  # Redirect to the pending items page


@login_required




def all_items(request):
    if request.user.user_type == '1':  # Ensure only admin can view
        # Get the search query from GET parameters
        search_query = request.GET.get('search', '')

        # Filter items based on search query (if provided)
        if search_query:
            items = Menu.objects.exclude(status='pending').filter(
                item__icontains=search_query  # Filter by item name (case-insensitive)
            )
        else:
            items = Menu.objects.exclude(status='pending')  # Exclude pending items

        # Implement pagination
        paginator = Paginator(items, 6)  # Show 6 items per page
        page_number = request.GET.get('page')  # Get the page number from the URL
        items_page = paginator.get_page(page_number)

        # Render the template with the paginated items
        return render(request, 'admin_all_items.html', {'items': items_page, 'search_query': search_query})
    
    return redirect('admin')


@login_required




def hotel_items(request):
    if request.user.user_type == '3':  # Ensure only hotel owners can view
        try:
            hotel_profile = HotelSignup.objects.get(user=request.user)
            search_query = request.GET.get('search', '')

            # Filter menu items based on the search query (if provided)
            if search_query:
                items = Menu.objects.filter(
                    hotel=hotel_profile,
                    item__icontains=search_query
                )
            else:
                items = Menu.objects.filter(hotel=hotel_profile)

            # Prefetch disapproval reasons for each menu item
            disapproval_queryset = ItemDisapproval.objects.all()
            items = items.prefetch_related(
                Prefetch('itemdisapproval_set', queryset=disapproval_queryset)
            )

            paginator = Paginator(items, 6)  # Pagination
            page_number = request.GET.get('page')
            items_page = paginator.get_page(page_number)

        except HotelSignup.DoesNotExist:
            items_page = []

        return render(request, 'hotel_items.html', {
            'items': items_page,
            'search_query': search_query
        })
    
    return redirect('hotel')



@login_required
def approved_hotel_items(request):
    # Ensure that the logged-in user is a hotel owner (assuming user_type '2' represents hotel owners)
    if request.user.user_type == '3':
        # Filter the approved menu items based on the hotel owned by the user (assuming hotel is linked via user)
        hotel_profile = HotelSignup.objects.get(user=request.user)
        menu_items = Menu.objects.filter(hotel=hotel_profile ,status='approved')

        return render(request, 'approved_hotel_items.html', {'menu_items': menu_items})
    
    return redirect('login')  # Redirect to login if the user is not a hotel owner

@login_required
def edit_menu_item(request, item_id):
    # Ensure the logged-in user is a hotel owner
    if request.user.user_type == '3':
        try:
            # Get the hotel profile linked to the logged-in user
            hotel_profile = HotelSignup.objects.get(user=request.user)

            # Ensure the menu item belongs to the logged-in user's hotel
            menu_item = get_object_or_404(Menu, id=item_id, hotel=hotel_profile)

            if request.method == 'POST':
                # Update menu item details from the form data
                menu_item.item = request.POST.get('item')
                menu_item.description = request.POST.get('description')
                menu_item.price = request.POST.get('price')
                menu_item.category = request.POST.get('category')

                if 'image' in request.FILES:
                    menu_item.image = request.FILES['image']

                menu_item.save()
                messages.success(request, 'Menu item updated successfully!')
                return redirect('approved_hotel_items')  # Redirect to the approved items page

            return render(request, 'edit_menu_item.html', {'menu_item': menu_item})

        except HotelSignup.DoesNotExist:
            messages.error(request, 'Hotel profile not found.')
            return redirect('hotel')

    return redirect('hotel')  # Redirect to login if the user is not a hotel owner



@login_required
def delete_menu_item(request, item_id):
    # Ensure the logged-in user is a hotel owner
    if request.user.user_type == '3':
        try:
            # Get the hotel profile linked to the logged-in user
            hotel_profile = HotelSignup.objects.get(user=request.user)

            # Ensure the menu item belongs to the logged-in user's hotel
            menu_item = get_object_or_404(Menu, id=item_id, hotel=hotel_profile)

            # Delete the menu item
            menu_item.delete()
            messages.success(request, "Menu item deleted successfully.")
        except HotelSignup.DoesNotExist:
            messages.error(request, "Hotel profile not found for the logged-in user.")
        except Menu.DoesNotExist:
            messages.error(request, "Menu item not found or you do not have permission to delete it.")
    else:
        messages.error(request, "You are not authorized to delete menu items.")
    
    return redirect('approved_hotel_items')

from django.shortcuts import render, get_object_or_404
from .models import Order, Menu, Address
from django.http import HttpResponse
import re
from datetime import datetime

from decimal import Decimal

from decimal import Decimal
from datetime import date
from decimal import Decimal

def billing_view(request, item_id):
    # Retrieve the menu item
    item = get_object_or_404(Menu, pk=item_id)

    # Default to item's price as final price
    final_price = item.price

    # Check for an active discount on the item
    today = date.today()
    active_discount = Discount.objects.filter(item=item, start_date__lte=today, end_date__gte=today).first()

    # If a discount is active, calculate the discounted price
    if active_discount:
        discount_amount = (item.price * active_discount.discount_percentage) / 100
        final_price -= discount_amount
    else:
        discount_amount = Decimal('0.00')  # No discount if not active

    # Convert GST rate to Decimal
    gst_rate = Decimal('0.18')

    # Initialize quantity as 1 (default)
    quantity = 1

    # Fetch applicable coupons for the item or restaurant
    coupons = Coupon.objects.filter(
        menu_item=item,
        valid_from__lte=date.today(), 
        valid_to__gte=date.today()
    )

    # Initialize selected coupon and coupon discount
    selected_coupon = None
    coupon_discount_amount = Decimal('0.00')

    # If request is POST, handle the form submission and quantity change
    if request.method == "POST":
        # Fetch and sanitize quantity
        try:
            quantity = int(request.POST.get('quantity', 1))
            quantity = max(1, quantity)  # Ensure quantity is at least 1
        except ValueError:
            quantity = 1  # Default to 1 if invalid input
            
            coupons = Coupon.objects.filter(
        menu_item=item,
        valid_from__lte=today, 
        valid_to__gte=today
    )

    # Check if there are any applicable coupons
    has_coupons = coupons.exists()

        # Fetch the coupon code entered by the user
    coupon_code = request.POST.get('coupon_code', '').strip()
    if coupon_code:
            try:
                selected_coupon = Coupon.objects.get(coupon_code=coupon_code)
                coupon_discount_percentage = Decimal(selected_coupon.discount_percentage)
                coupon_discount_amount = (final_price * coupon_discount_percentage) / 100
            except Coupon.DoesNotExist:
                selected_coupon = None
                coupon_discount_amount = Decimal('0.00')

    # Calculate the discounted price after applying the coupon
    discounted_price = final_price - coupon_discount_amount

    # Calculate GST (18%) on the discounted price
    gst = discounted_price * gst_rate

    # Calculate total price (discounted price + GST) for the given quantity
    total_price = (discounted_price + gst) * quantity

    # Fetch user's saved addresses
    user_addresses = Address.objects.filter(user=request.user)

    if request.method == "POST":
        # Fetch selected stored address or new address
        selected_address_id = request.POST.get('address')  # ID of stored address
        new_address = request.POST.get('new_address', '').strip()

        if new_address:  # If a new address is provided, prioritize it
            # Validate and split the new address
            address_parts = new_address.split(",")
            if len(address_parts) < 2:
                address = "Invalid address format"
            else:
                door_floor_no = address_parts[0].strip()
                area = ",".join(address_parts[1:]).strip()
                # Save new address to the database
                Address.objects.create(
                    user=request.user,
                    door_floor_no=door_floor_no,
                    area=area,
                    added_on=datetime.now()
                )
                address = f"{door_floor_no}, {area}"
        else:  # Use the selected stored address
            try:
                address_obj = Address.objects.get(id=selected_address_id, user=request.user)
                address = f"{address_obj.door_floor_no}, {address_obj.area}, {address_obj.landmark}"
            except Address.DoesNotExist:
                address = "Address not found"  # Fallback if the address is invalid (optional handling)

        # Fetch mobile number
        mobile_number = request.POST.get('mobile', '').strip()
        if not re.match(r'^\+?1?\d{9,15}$', mobile_number):  # Simple regex to check mobile format
            mobile_number = "Invalid mobile number"  # If invalid, set an error message

        # Fetch payment method
        payment_method = request.POST.get('payment_method').upper()
        if payment_method not in ['COD', 'CARD', 'ONLINE']:  # Assuming these are the valid methods
            payment_method = 'COD'  # Default to COD if invalid

        upi_id = request.POST.get('upi')
        if payment_method == 'ONLINE' and not upi_id:
            messages.error(request, "Please enter your UPI ID for Online Payment.")
            return redirect('billing')  # Assuming you want to reload the page if the UPI ID is missing

        # Save the order
        order = Order.objects.create(
            user=request.user,
            item=item,
            quantity=quantity,
            address=address,
            phone_number=mobile_number,
            payment_method=payment_method,
            total_price=total_price,
            upi=upi_id if payment_method == 'ONLINE' else None,  # Save the UPI ID if payment is online
        )

        # Update coupon usage count if applied
        if selected_coupon:
            selected_coupon.count_used += 1
            selected_coupon.save()

        return redirect('order_success')

    return render(request, 'billing.html', {
        'item': item,
        'final_price': final_price,
        'gst': gst,  # Pass GST to the template
        'total_price': total_price,  # Pass total price to the template
        'addresses': user_addresses,  # Send user's saved addresses to the template
        'coupons': coupons,  # Pass available coupons to the template
        'selected_coupon': selected_coupon,  # Pass selected coupon
        'discount_amount': discount_amount,  # Pass discount amount from active discount
        'coupon_discount_amount': coupon_discount_amount,  # Pass coupon discount amount
        'active_discount': active_discount,  # Pass active discount details
        
    })
def validate_coupon(request):
    coupon_code = request.GET.get('coupon_code', '').strip()
    if coupon_code:
        try:
            selected_coupon = Coupon.objects.get(coupon_code=coupon_code)
            return JsonResponse({'discount_percentage': selected_coupon.discount_percentage})
        except Coupon.DoesNotExist:
            return JsonResponse({'discount_percentage': 0})
    return JsonResponse({'discount_percentage': 0})


def order_success(request):
    # Assuming the logged-in user has placed an order, and we are showing the most recent order
    order = Order.objects.filter(user=request.user).order_by('-created_at').first()  # Get the most recent order

    if order:
        # Fetch order details like item, quantity, payment method, etc.
        item_name = order.item.item  # Get the name of the ordered item from the Menu model
        item_price = order.item.price  # Price of the ordered item
        quantity = order.quantity
        total_price = order.total_price
        payment_method = order.payment_method
        hotel_name = order.item.hotel.restaurant_name  # Assuming HotelSignup model has a 'name' field
        delivery_address = order.address
        phone_number = order.phone_number
        username = order.user.username  # Get the username of the logged-in user

        # Pass the data to the template
        context = {
            'item_name': item_name,
            'item_price': item_price,
            'quantity': quantity,
            'total_price': total_price,
            'payment_method': payment_method,
            'hotel_name': hotel_name,
            'delivery_address': delivery_address,
            'phone_number': phone_number,
            'username': username,
        }

        return render(request, 'order_success.html', context)
    else:
        # If no order is found
        return render(request, 'order_success.html', {'error': 'No recent order found.'})

@login_required
def hotel_orders(request):
    if request.user.user_type != '3':  # Ensure only hotels access this view
        return render(request, 'error.html', {"message": "Unauthorized access"})
    
    # Get the hotel linked to the logged-in user
    hotel = get_object_or_404(HotelSignup, user=request.user)

    # Fetch orders for this hotel, sorted by order ID in descending order
    orders = Order.objects.filter(item__hotel=hotel).select_related('user', 'item').order_by('-id')

    new_orders_counts = orders.filter(status='pending').count()

    return render(request, 'hotel_orders.html', {'orders': orders, 'new_orders_count': new_orders_counts})

@login_required
def update_order_status(request, order_id):
    if request.user.user_type != '3':  # Ensure only hotels access this view
        return render(request, 'error.html', {"message": "Unauthorized access"})

    # Get the order and ensure it belongs to this hotel
    order = get_object_or_404(Order, id=order_id, item__hotel__user=request.user)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):  # Validate status
            order.status = new_status
            order.save()
            # After updating, fetch all orders for the logged-in user and pass them to the template
            orders = Order.objects.filter(item__hotel__user=request.user)
            return render(request, 'hotel_orders.html', {'orders': orders, 'message': "Order status updated successfully"})

    # If it's a GET request, we just render the current order status page
    return render(request, 'hotel_orders.html', {'order': order})

def user_orders(request):
    # Get orders placed by the logged-in user
    orders = Order.objects.filter(user=request.user).select_related('item__hotel')
    last_address = None
    if request.user.is_authenticated:
        last_address = Address.objects.filter(user=request.user).last()  # Use 'item__hotel' to fetch hotel data along with the menu item
    
    return render(request, 'user_orders.html', {'orders': orders,'last_address':last_address})


def add_address(request):
    if request.method == 'POST':
        door_floor_no = request.POST.get('door_floor_no')
        area = request.POST.get('area')
        landmark = request.POST.get('landmark')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        # Validation logic (if any)
        if not door_floor_no or not area or not landmark or not latitude or not longitude:
            return JsonResponse({'error': 'All fields are required'}, status=400)

        # Save to database
        Address.objects.create(
            user=request.user, 
            door_floor_no=door_floor_no,
            area=area,
            landmark=landmark,
            latitude=latitude,
            longitude=longitude
        )
        messages.success(request, 'Address Added successfully!')

    return redirect('view_user_profile') 

def view_addresses(request):
    addresses =  addresses = Address.objects.filter(user=request.user) # Fetch logged-in user's addresses
    last_address = None
    if request.user.is_authenticated:
        last_address = Address.objects.filter(user=request.user).last()
    return render(request, 'view_addresses.html', {'addresses': addresses,'last_address':last_address})


def cancel_order(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id, user=request.user)
        if order.status in ['pending', 'preparing']:
            # Get the cancellation reason from the form
            cancel_reason = request.POST.get('cancel_reason', '')

            # Set order status to cancelled
            order.status = 'cancelled'
            order.cancel_reason = cancel_reason  # Assuming you added this field to store the reason
            order.save()

            # Show a success message
            messages.success(request, "Order has been successfully cancelled.")

        else:
            messages.error(request, "Order cannot be cancelled.")

    return redirect('user_orders')

def view_hotel_profile(request):
    hotel = get_object_or_404(HotelSignup, user=request.user)
    return render(request, 'view_hotel_profile.html', {'hotel': hotel})

from django.shortcuts import render, get_object_or_404, redirect

def edit_hotel_profile(request, hotel_id):
    hotel = get_object_or_404(HotelSignup, id=hotel_id)
    if request.method == "POST":
        # Updating basic text fields
        hotel.restaurant_name = request.POST.get("restaurant_name", hotel.restaurant_name)
        hotel.restaurant_location = request.POST.get("restaurant_location", hotel.restaurant_location)
        hotel.address = request.POST.get("address", hotel.address)
        hotel.contact_number = request.POST.get("contact_number", hotel.contact_number)
        hotel.operating_from = request.POST.get("operating_from", hotel.operating_from)
        hotel.operating_to = request.POST.get("operating_to", hotel.operating_to)

        # Updating license number
        license_number = request.POST.get("license_number")
        if license_number:
            hotel.license_number = license_number

        # Handling license copy upload
        if 'license_copy' in request.FILES:
            license_copy = request.FILES['license_copy']
            hotel.license_copy = license_copy

        # Handling restaurant image upload
        if 'restaurant_image' in request.FILES:
            restaurant_image = request.FILES['restaurant_image']
            hotel.restaurant_image = restaurant_image

        # Save the updated hotel data
        hotel.save()
        return redirect('view_hotel_profile')

    return render(request, 'edit_hotel_profile.html', {'hotel': hotel})

def add_hotel_details(request):
    if request.method == 'POST':
        # Retrieve additional details from the form
        license_number = request.POST.get('license_number', '').strip()
        
        # Handle image upload
        restaurant_image = request.FILES.get('restaurant_image')
        
        # Handle license PDF upload
        license_copy = request.FILES.get('license_copy')

        # Retrieve the hotel profile of the logged-in user
        hotel_profile = HotelSignup.objects.get(user=request.user)

        # Check for missing details
        if not all([license_number, restaurant_image, license_copy]):
            messages.error(request, 'Please provide all the details including image, license number, and license copy.')
            return redirect('edit_hotel_profile')  # Redirect to the edit profile page

        # Update the hotel profile with the new details
        hotel_profile.license_number = license_number
        hotel_profile.restaurant_image = restaurant_image
        hotel_profile.license_copy = license_copy
        hotel_profile.save()

        messages.success(request, 'Additional details added successfully.')
        return redirect('view_hotel_profile')  # Redirect to the hotel profile page

    return render(request, 'add_hotel_details.html')  # This renders the form template

def restaurant_menu(request, hotel_id):
    # Retrieve the hotel object
    hotel = get_object_or_404(HotelSignup, id=hotel_id)
    
    # Retrieve only approved menu items for the selected hotel
    menu_items = Menu.objects.filter(hotel=hotel, status='approved')
    last_address = None
    if request.user.is_authenticated:
        last_address = Address.objects.filter(user=request.user).last()

    # Add a random rating (between 1 and 5) to each menu item
    for item in menu_items:
        reviews = item.reviews.all()
        item.average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] if reviews.exists() else None

    context = {
        'hotel': hotel,
        'menu_items': menu_items,
        'hotel_id': hotel_id,  # Add this to context
        'last_address':last_address,
    }
    return render(request, 'restaurant_menu.html', context)

from django.db.models import Q  # Import for complex queries

from .models import RecentSearch

from django.db.models import Q

def search_food(request):
    query = request.GET.get('q', '')  # Get the search query from the URL parameters
    search_results = []

    if query:  # If there's a query, filter the Menu items
        search_results = Menu.objects.filter(
            Q(item__icontains=query) | Q(description__icontains=query),
            status='approved'
        )

        # Save the query and associated menu item (if found) in recent searches
        if request.user.is_authenticated:
            menu_item = search_results.first() if search_results.exists() else None
            RecentSearch.objects.create(
                user=request.user,
                search_query=query,
                menu_item=menu_item
            )

    # Fetch recent searches for the user
    recent_search_items = []
    if request.user.is_authenticated:
        # Get the recent search items related to the user
        recent_search_items = Menu.objects.filter(
            recent_searches__user=request.user,
            status='approved'
        ).distinct()

    # Fetch the last address for the user
    last_address = None
    if request.user.is_authenticated:
        last_address = Address.objects.filter(user=request.user).last()

    return render(request, 'search_results.html', {
        'query': query,
        'search_results': search_results,
        'recent_search_items': recent_search_items,
        'last_address': last_address,
    })



@login_required


def submit_review(request, order_id):
    if request.method == "POST":
        # Retrieve the order and ensure it belongs to the current user and is delivered
        order = get_object_or_404(Order, id=order_id, user=request.user, status='delivered')

        # Get the associated menu item from the order
        menu_item = order.item  # Assuming `order.item` is linked to the Menu model

        # Get rating and feedback from the form
        try:
            rating = int(request.POST.get('rating'))
            feedback = request.POST.get('review')
        except (ValueError, TypeError):
            messages.error(request, "Invalid rating or feedback provided.")
            return redirect('order_details', order_id=order_id)

        # Save or update the review
        Review.objects.update_or_create(
            order=order,
            user=request.user,
            menu_item=menu_item,  # Link review to the specific menu item
            defaults={
                'rating': rating,
                'feedback': feedback,
            }
        )

        # Mark the order as reviewed
        order.has_review = True
        order.save()

        messages.success(request, "Thank you for your review!")
        return redirect('user_orders')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('user_orders')

    



def search_restaurants(request):
    search_query = request.GET.get('location', '')
    hotels = HotelSignup.objects.filter(
        Q(restaurant_location__icontains=search_query) |
        Q(address__icontains=search_query)
    ) if search_query else HotelSignup.objects.none()

    # Add random ratings and discounts for display purposes
    for hotel in hotels:
        hotel.random_rating = round(random.uniform(3, 5), 1)
        hotel.discount = random.choice([10, 15, 20, 25])

    last_address = None
    if request.user.is_authenticated:
        last_address = Address.objects.filter(user=request.user).last()

    return render(request, 'search_restaurants.html', {
        'hotels': hotels,
        'search_query': search_query,
        'last_address':last_address
    })

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Order, OrderIssueReport

def report_issue(request, order_id):
    if request.method == "POST":
        order = get_object_or_404(Order, id=order_id)
        if order.has_issue:
            messages.error(request, "You have already reported an issue for this order.")
            return redirect("user_orders")

        issue_type = request.POST.get("issue", "other")
        description = request.POST.get("other_issue", "")

        # Save the issue report
        OrderIssueReport.objects.create(
            order=order,
            user=request.user,
            issue_type=issue_type,
            description=description if issue_type == "other" else None,
        )

        # Mark the order as having an issue
        order.has_issue = True
        order.save()

        messages.success(request, "Your issue has been reported successfully.")
        return redirect("user_orders")

    return redirect("user_orders")


def admin_issue_list(request):
    issues = OrderIssueReport.objects.select_related('order', 'order__item', 'order__item__hotel')
    context = {'issues': issues}
    return render(request, 'admin_issue_list.html', context)

from django.core.mail import send_mail
from django.conf import settings

def send_to_restaurant(request, issue_id):
    issue = get_object_or_404(OrderIssueReport, id=issue_id)
    issue.is_sent_to_restaurant = True  # Mark the issue as sent to the restaurant
    issue.save()

    # Send email notification to the user
    user_email = issue.user.email  # Assuming the user who reported the issue has an email field
    subject = "Issue Received by Restaurant"
    message = (
        f"Dear {issue.user.first_name},\n\n"
        f"We have received your reported issue for the item: {issue.order.item.item}.\n"
        f"Please log in to your profile and select your preferred resolution (Refund or Replace) from the 'Your Issues' section.\n\n"
        "Thank you for your patience.\n\n"
        "Best regards,\nRestaurant Support Team"
    )
    email_from = settings.DEFAULT_FROM_EMAIL
    recipient_list = [user_email]

    send_mail(subject, message, email_from, recipient_list, fail_silently=False)

    return redirect('admin_issue_list')  # Redirect back to the admin issue list


def restaurant_issue_list(request):
    restaurant = request.user.hotel_profile  # Assuming the logged-in user is a restaurant
    issues = OrderIssueReport.objects.filter(order__item__hotel=restaurant, is_sent_to_restaurant=True)
    context = {'issues': issues}
    return render(request, 'restaurant_issue_list.html', context)

@login_required
def add_discount(request):
    # Check if the logged-in user is of type 'Hotel'
    if request.user.user_type != '3':
        messages.error(request, "You are not authorized to add discounts.")
        return redirect('loginpage')  # Or wherever you want to redirect unauthorized users

    # Fetch the hotel profile associated with the logged-in user
    try:
        hotel = HotelSignup.objects.get(user=request.user)
    except HotelSignup.DoesNotExist:
        messages.error(request, "Hotel profile not found.")
        return redirect('loginpage')  # Handle this case accordingly

    # Get all food items that belong to this restaurant
    food_items = Menu.objects.filter(hotel=hotel,status='approved')

    # Handle form submission
    if request.method == 'POST':
        item_id = request.POST.get('item')
        discount_percentage = request.POST.get('discount_percentage')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Validate data
        if not item_id or not discount_percentage or not start_date or not end_date:
            messages.error(request, "Please fill all the fields.")
            return redirect('add_discount')

        # Add the discount
        try:
            item = Menu.objects.get(id=item_id)
            discount = Discount.objects.create(
                item=item,
                discount_percentage=discount_percentage,
                start_date=start_date,
                end_date=end_date
            )
            messages.success(request, f"Discount added successfully to {item.item}.")
        except Menu.DoesNotExist:
            messages.error(request, "Food item not found.")
            return redirect('add_discount')

    return render(request, 'add_discount.html', {'food_items': food_items})


def add_coupon(request):
    if request.method == "POST":
        item_id = request.POST.get('item')
        discount_percentage = request.POST.get('discount_percentage')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        coupon_code = request.POST.get('coupon_code')  # Assuming we add a field for this

        # Validate inputs
        if not all([item_id, discount_percentage, start_date, end_date, coupon_code]):
            messages.error(request, "All fields are required.")
            return redirect('add_coupon')

        # Ensure the food item exists
        try:
            menu_item = Menu.objects.get(id=item_id,status='approved')  # Ensure it's approved
        except Menu.DoesNotExist:
            messages.error(request, "Invalid or unapproved food item selected.")
            return redirect('add_coupon')

        # Save the coupon
        Coupon.objects.create(
            coupon_code=coupon_code,
            discount_percentage=discount_percentage,
            valid_from=start_date,
            valid_to=end_date,
            restaurant=menu_item.hotel,
            menu_item=menu_item,
        )
        messages.success(request, "Coupon added successfully!")
        return redirect('add_coupon')

    # For GET request: Fetch only approved food items of the logged-in restaurant
    try:
        restaurant = HotelSignup.objects.get(user=request.user)  # Adjust this based on your model
        food_items = Menu.objects.filter(hotel=restaurant,status='approved')
    except HotelSignup.DoesNotExist:
        messages.error(request, "Restaurant not found.")
        food_items = []

    return render(request, 'add_coupon.html', {'food_items': food_items})

def restaurant_resolve_issue(request, issue_id):
    issue = get_object_or_404(OrderIssueReport, id=issue_id)
    issue.is_resolved = True
    issue.save()
    messages.success(request, "Issue marked as resolved.")
    return redirect('restaurant_issue_list')

def user_issues(request):
    user_issues = OrderIssueReport.objects.filter(user=request.user)
    for issue in user_issues:
        issue.can_choose_resolution = issue.is_resolved and issue.issue_type in ['wrong_item', 'missing_item']

    last_address = None
    if request.user.is_authenticated:
        last_address = Address.objects.filter(user=request.user).last()
    return render(request, 'user_issues.html', {'issues': user_issues,'last_address':last_address})


def handle_user_resolution(request, issue_id):
    issue = get_object_or_404(OrderIssueReport, id=issue_id)

    if request.method == "POST" and issue.issue_type in ['wrong_item', 'missing_item']:
        resolution_choice = request.POST.get("resolution_choice")
        issue.resolution_choice = resolution_choice
        issue.save()
        messages.success(request, f"You selected {resolution_choice}. The restaurant will take action.")
        return redirect('user_issues')

    messages.error(request, "Unable to process your request.")
    return redirect('user_issues')


def restaurant_send_mail(request, issue_id):
    issue = get_object_or_404(OrderIssueReport, id=issue_id)
    if issue.resolution_choice and not issue.mail_sent:
        subject = "Update on Your Issue Resolution"
        if issue.resolution_choice == "refund":
            message = (
            f"Dear {issue.user.first_name},\n\n"
            f"Your refund for the item '{issue.order.item.item}' will be credited in 7 working days.\n\n"
            "Thank you for your patience.\n\n"
            "Best regards,\nRestaurant Support Team"
        )
        elif issue.resolution_choice == "replace":
            message = (
            f"Dear {issue.user.first_name},\n\n"
            f"A new food item will be delivered for the item '{issue.order.item.item}' soon.\n\n"
            "Thank you for your patience.\n\n"
            "Best regards,\nRestaurant Support Team"
        )
        else:
            return redirect('restaurant_issue_list')  # No valid resolution choice

        send_mail(
            subject,
            message,
            'no-reply@example.com',
            [issue.user.email],
        )

        issue.mail_sent = True
        issue.save()
        messages.success(request, "Mail sent successfully.")
    else:
        messages.error(request, "Mail already sent or no resolution choice.")
    return redirect('restaurant_issue_list')

def sandwiches_menu(request):
    # Search for items where the name contains the word 'sandwich' (case-insensitive)
    menu_items = Menu.objects.filter(item__icontains="sandwich", status="approved")
    last_address = None
    if request.user.is_authenticated:
        last_address = Address.objects.filter(user=request.user).last()
    for item in menu_items:
        reviews = item.reviews.all()
        item.average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] if reviews.exists() else None
    return render(request, 'sandwiches_menu.html', {'menu_items': menu_items,'last_address':last_address})

def friedchicken_menu(request):
    # Search for items where the name contains the word 'sandwich' (case-insensitive)
    menu_items = Menu.objects.filter(item__icontains="Fried Chicken", status="approved")
    last_address = None
    if request.user.is_authenticated:
        last_address = Address.objects.filter(user=request.user).last()
    for item in menu_items:
        reviews = item.reviews.all()
        item.average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] if reviews.exists() else None
    return render(request, 'friedchicken_menu.html', {'menu_items': menu_items,'last_address':last_address})

def pizza_menu(request):
    # Search for items where the name contains the word 'sandwich' (case-insensitive)
    menu_items = Menu.objects.filter(item__icontains="Pizza", status="approved")
    last_address = None
    if request.user.is_authenticated:
        last_address = Address.objects.filter(user=request.user).last()
    for item in menu_items:
        reviews = item.reviews.all()
        item.average_rating = reviews.aggregate(Avg('rating'))['rating__avg'] if reviews.exists() else None
    return render(request, 'pizza_menu.html', {'menu_items': menu_items,'last_address':last_address})

def assign_and_show_coupon(request):
    # Count completed orders for the logged-in user
    completed_orders = Order.objects.filter(user=request.user, status='delivered').count()

    # Calculate how many sets of 10 orders the user has completed
    completed_sets_of_10 = completed_orders // 10

    last_address = None
    if request.user.is_authenticated:
        last_address = Address.objects.filter(user=request.user).last()

    # Fetch the coupon corresponding to the completed sets of 10 orders
    if completed_sets_of_10 > 0:
        # Determine the discount percentage (10% per set of 10 orders, capped at 50%)
        discount_percentage = min(completed_sets_of_10 * 10, 50)

        # Fetch the coupon with the required discount percentage
        coupon_to_assign = Coupon.objects.filter(discount_percentage=discount_percentage).first()
    else:
        coupon_to_assign = None

    if coupon_to_assign:
        # Ensure the coupon is not already assigned
        if not Reward.objects.filter(user=request.user, coupon=coupon_to_assign).exists():
            # Assign the coupon to the user
            Reward.objects.create(user=request.user, coupon=coupon_to_assign)

        context = {'coupon': coupon_to_assign, 'last_address': last_address}
    else:
        context = {'coupon': None, 'last_address': last_address}

    return render(request, 'coupon_card.html', context)




import openrouteservice

# Initialize ORS client
ORS_API_KEY = "5b3ce3597851110001cf62480d7d9a1058aa42b792ab83f9fbb67e52"  # Replace with your ORS API key
client = openrouteservice.Client(key=ORS_API_KEY)

def calculate_distance_time(lat1, lon1, lat2, lon2, travel_mode="driving-car"):
    """
    Calculate distance and estimated time between two points using OpenRouteService.
    """
    try:
        # Make ORS API request
        response = client.directions(
            coordinates=[(lon1, lat1), (lon2, lat2)],
            profile=travel_mode,  # Options: driving-car, cycling-regular, foot-walking
            format="json"
        )

        # Extract distance (meters) and duration (seconds)
        distance_meters = response["routes"][0]["summary"]["distance"]
        duration_seconds = response["routes"][0]["summary"]["duration"]

        # Convert distance to kilometers and duration to minutes
        distance_km = round(distance_meters / 1000, 2)
        duration_minutes = round(duration_seconds / 60)+20

        return distance_km, f"{duration_minutes} min"
    except Exception as e:
        print(f"Error calculating distance and time: {e}")
        return None, None
    
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from itertools import groupby
from .models import Menu, CartItem, Order

@login_required
def add_to_cart(request, item_id):
    item = get_object_or_404(Menu, id=item_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, item=item, hotel=item.hotel)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f"{item.item} added to cart!")
    
    # Redirect to the same page (referer)
    return redirect(request.META.get('HTTP_REFERER', 'restaurant_menu2'))  # Default to 'restaurant_menu2' if referer is not found

def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    user_addresses = Address.objects.filter(user=request.user)  # Fetch stored addresses

    if not cart_items:
        return render(request, 'cart.html', {'cart_items': [], 'total_price': 0, 'user_addresses': user_addresses})

    restaurant_carts = {}
    total_price = Decimal(0)
    detailed_billing = []  # To store per-item billing details

    for item in cart_items:
        if item.hotel not in restaurant_carts:
            restaurant_carts[item.hotel] = []
        restaurant_carts[item.hotel].append(item)

    for restaurant, items in restaurant_carts.items():
        subtotal = sum(item.item.price * item.quantity for item in items)
        gst = (subtotal * Decimal(18)) / Decimal(100)
        total_price += subtotal + gst

        for item in items:
            item_subtotal = item.item.price * item.quantity
            item_gst = (item_subtotal * Decimal(18)) / Decimal(100)
            detailed_billing.append({
                'item': item.item.item,
                'quantity': item.quantity,
                'item_price': item.item.price,
                'subtotal': item_subtotal,
                'gst': item_gst,
                'total_price': item_subtotal + item_gst
            })

    return render(request, 'cart.html', {
        'restaurant_carts': restaurant_carts,
        'total_price': total_price,
        'detailed_billing': detailed_billing,
        'user_addresses': user_addresses
    })


def place_order(request):
    if request.method == "POST":
        selected_address_id = request.POST.get('address')  # ID of stored address
        new_address = request.POST.get('new_address', '').strip()
        
        

        if new_address:  # If a new address is provided, prioritize it
            address_parts = new_address.split(",")
            if len(address_parts) < 2:
                messages.error(request, "Invalid address format. Please use 'Door No, Area'")
                return redirect('view_cart')
            else:
                door_floor_no = address_parts[0].strip()
                area = ",".join(address_parts[1:]).strip()
                new_address_obj = Address.objects.create(
                    user=request.user,
                    door_floor_no=door_floor_no,
                    area=area,
                    added_on=datetime.now()
                )
                address = f"{door_floor_no}, {area}"
        else:
            try:
                address_obj = Address.objects.get(id=selected_address_id, user=request.user)
                address = f"{address_obj.door_floor_no}, {address_obj.area}"
            except Address.DoesNotExist:
                messages.error(request, "Invalid address selected.")
                return redirect('view_cart')
            
        mobile_number = request.POST.get('mobile', '').strip()
        if not re.match(r'^\+?1?\d{9,15}$', mobile_number):  # Simple regex to check mobile format
            mobile_number = "Invalid mobile number"  # If invalid, set an error message

        payment_method = request.POST.get('payment_method', 'COD').upper()
        if payment_method not in ['COD', 'CARD', 'UPI']:  # Assuming these are the valid methods
            payment_method = 'COD'  # Default to COD if invalid

        cart_items = CartItem.objects.filter(user=request.user).order_by('item__hotel')

        if not cart_items.exists():
            messages.error(request, "Your cart is empty!")
            return redirect('view_cart')

        items_ordered = len(cart_items)  # Count the number of items in the cart

        for item in cart_items:
            item_subtotal = item.item.price * item.quantity
            item_gst = (item_subtotal * Decimal(18)) / Decimal(100)
            item_total_price = item_subtotal + item_gst

            Order.objects.create(
                user=request.user,
                item=item.item,
                quantity=item.quantity,
                address=address,
                phone_number=mobile_number,
                payment_method=payment_method,
                total_price=item_total_price  # Store only the item's total price
            )

            item.delete()  # Remove from cart after ordering

        
        return redirect('order_successful', items_ordered=items_ordered)  # Pass the number of items ordered to the success page

    return redirect('view_cart')

@login_required
def update_cart_ajax(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        new_quantity = int(request.POST.get('quantity', 1))

        cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)

        if new_quantity > 0:
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart_item.delete()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})



def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    return redirect('view_cart') 

def order_successful(request, items_ordered):
    # Fetch the last 'n' orders based on the number of items ordered
    last_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:items_ordered]
    total_bill = sum(order.total_price for order in last_orders) 
    

    if not last_orders:
        messages.error(request, "No orders found.")
        return redirect('view_cart')

    # Prepare the context for the template
    context = {
        'last_orders': last_orders,
        'total_bill' : total_bill,
    }
    return render(request, 'order_successful.html', context)

from .models import CustomUser, DeliveryAgent
from django.contrib.auth.hashers import make_password
import string

def generate_random_password():
    """Generate an 8-digit random password with letters and numbers."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choices(characters, k=8))

def generate_username(first_name):
    """Generate a unique username using first_name and a random 3-digit number."""
    random_number = random.randint(100, 999)
    return f"{first_name.lower()}{random_number}"

def register_delivery_agent(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        age = request.POST.get('age')
        vehicle_number = request.POST.get('vehicle_number')
        email = request.POST.get('email')

        # Generate username and password
        username = generate_username(first_name)
        password = generate_random_password()

        # Ensure the username is unique
        while CustomUser.objects.filter(username=username).exists():
            username = generate_username(first_name)

        # Check if email already exists
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists. Please choose another.')
            return render(request, 'register_delivery_agent.html')
        
        if not all([ first_name, last_name, email, phone_number, address,age,vehicle_number]):
            messages.error(request, 'All fields are required. Please fill out all the fields.')
            return render(request, 'register_delivery_agent.html.')

        # Create a new delivery agent user
        user = CustomUser.objects.create(
            username=username,
            password=make_password(password),  # Encrypt password
            first_name=first_name,
            last_name=last_name,
            email=email,
            user_type='4'  # User type for delivery agent
        )

        # Create Delivery Agent Profile
        DeliveryAgent.objects.create(
            user=user,
            phone_number=phone_number,
            address=address,
            vehicle_number=vehicle_number,
            age=age
        )

        # Send login credentials via email
        subject = "Your Delivery Agent Account Details"
        message = f"""
        Hello {first_name},

        Your delivery agent account has been successfully created.
        
        Login Details:
        Username: {username}
        Password: {password}

        Please log in and change your password as soon as possible.

        Regards,
        Your Company Team
        """
        send_mail(subject, message, 'pvsarath2002@gmail.com', [email])

        # Show success message in the template
        messages.success(request, 'Delivery Agent registered successfully. Login credentials sent to email.')

        return redirect('register_delivery_agent')

    return render(request, 'register_delivery_agent.html')

@login_required
def delivery_agent(request):
    # Retrieve the hotel information for the logged-in user
    try:
        agent_profile = DeliveryAgent.objects.get(user=request.user)
    except DeliveryAgent.DoesNotExist:
        agent_profile = None

    return render(request, 'delivery_agent.html', {'agent': agent_profile})


def manage_orders(request):
    # Ensure delivered agents become available again
    delivered_orders = Order.objects.filter(status='delivered', assigned_agent__isnull=False)
    for order in delivered_orders:
        if order.assigned_agent:
            order.assigned_agent.is_available = True
            order.assigned_agent.save()

    # Fetch unassigned orders & available agents
    orders = Order.objects.filter(status='preparing')
    delivery_agents = DeliveryAgent.objects.filter(is_available=True)

    pending_orders_count = orders.filter(assigned_agent__isnull=True).count()

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        agent_id = request.POST.get('agent_id')

        try:
            order = get_object_or_404(Order, id=order_id)
            agent = get_object_or_404(DeliveryAgent, id=agent_id)

            # Assign the agent to the order
            order.assigned_agent = agent
            order.save()

            # Mark agent as unavailable when assigned
            agent.is_available = False
            agent.save()

            messages.success(request, "Delivery agent assigned successfully!")
        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect('manage_orders')

    # Pass each order's assigned agent to the template
    for order in orders:
        order.assigned_agent_name = order.assigned_agent.user.first_name if order.assigned_agent else None

    return render(request, 'manage_orders.html', {
        'orders': orders,
        'delivery_agents': delivery_agents,
        'pending_orders_count': pending_orders_count
    })
def agent_orders(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'delivery_profile'):
        return redirect('login')

    orders = Order.objects.filter(assigned_agent=request.user.delivery_profile)

    new_orders_count = orders.filter(status__in=['prepared', 'preparing']).count()
    
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        new_status = request.POST.get("status")
        order = Order.objects.get(id=order_id)
        
        if new_status == "picked":
            order.status = "picked"
            messages.success(request, "Order picked successfully!")
        elif new_status == "delivered":
            if order.payment_method == "COD":
                order.status = "delivered"
                order.payment_received = True  # Assume you have this field in your model
                messages.success(request, "Order delivered and payment collected!")
            else:
                order.status = "delivered"
                messages.success(request, "Order delivered successfully!")
        
        order.save()
        return redirect("agent_orders")
    
    return render(request, "agent_orders.html", {
        "orders": orders,
        "new_orders_count": new_orders_count  # Pass the new orders count to the template
    })

def update_order_statuses(request, order_id):
    order = get_object_or_404(Order, id=order_id, assigned_agent=request.user.delivery_profile)

    if request.method == "POST":
        new_status = request.POST.get("status")

        # Handle status transitions
        if new_status == "picked" and order.status == "prepared":
            order.status = "picked"
            messages.success(request, f"Order {order.id} has been picked up.")
        
        elif new_status == "delivered" and order.status == "picked":
            if order.payment_method == "cod":
                if request.POST.get("payment_received") == "on":
                    order.payment_received = True
                    order.status = "delivered"
                    messages.success(request, f"Order {order.id} has been delivered and payment received.")
                else:
                    messages.error(request, "Please confirm that payment has been collected before delivering the order.")
                    return redirect('agent_orders')
            else:
                order.status = "delivered"
                messages.success(request, f"Order {order.id} has been delivered successfully.")

        order.save()
        return redirect('agent_orders')

    return redirect('agent_orders')




    