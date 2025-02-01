from .models import HotelSignup,Order,DeliveryAgent

def hotel_profile_processor(request):
    if request.user.is_authenticated:
        try:
            hotel_profile = HotelSignup.objects.get(user=request.user)
        except HotelSignup.DoesNotExist:
            hotel_profile = None
        return {'hotel_profile': hotel_profile}
    return {}

def pending_orders_count(request):
    # Get count of unassigned orders with status 'preparing'
    count = Order.objects.filter(status='preparing', assigned_agent__isnull=True).count()
    return {'pending_orders_count': count}

def agent_first_name(request):
    # Check if the user is authenticated and has the delivery profile
    if request.user.is_authenticated and hasattr(request.user, 'delivery_profile'):
        agent = request.user.delivery_profile
        return {'agent_first_name': agent.user.first_name}
    return {'agent_first_name': None}

def new_orders_counts(request):
    if request.user.is_authenticated and request.user.user_type == '3':  # Ensure the user is a hotel
        hotel = HotelSignup.objects.filter(user=request.user).first()
        if hotel:
            # Count the number of orders with status 'pending' for the hotel
            count = Order.objects.filter(item__hotel=hotel, status='pending').count()
            return {'new_orders_counts': count}
    return {'new_orders_counts': 0}  # Default to 0 if not a hotel user

def new_orders_count(request):
    if request.user.is_authenticated and hasattr(request.user, 'delivery_profile'):
        new_orders_count = Order.objects.filter(
            assigned_agent=request.user.delivery_profile,
            status__in=['prepared', 'preparing']
        ).count()
    else:
        new_orders_count = 0
    return {'new_orders_count': new_orders_count}