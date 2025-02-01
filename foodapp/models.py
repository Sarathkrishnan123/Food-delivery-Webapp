from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.conf import settings
from decimal import Decimal

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('1', 'Admin'),
        ('2', 'User'),
        ('3', 'Hotel'),
        ('4', 'Delivery_agent'),
    )
    user_type = models.CharField(choices=USER_TYPE_CHOICES, default='1', max_length=10)
    status = models.IntegerField(default=0)

# User Profile model
class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="profile")
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

from django.db import models

class HotelSignup(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='hotel_profile')
    restaurant_name = models.CharField(max_length=255)
    restaurant_location = models.CharField(max_length=255)
    address = models.TextField()
    contact_number = models.CharField(max_length=15)
    operating_from = models.TimeField()
    operating_to = models.TimeField()
    registration_number = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=255)
    owner_number = models.CharField(max_length=15)
    gst_type = models.CharField(
        max_length=50,
        choices=[
            ('registered_regular', 'Registered Business - Regular'),
            ('registered_composition', 'Registered Business - Composition'),
            ('unregistered', 'Unregistered Business'),
            ('overseas', 'Overseas'),
            ('consumer', 'Consumer'),
            ('sez', 'Special Economic Zone (SEZ)'),
            ('deemed_exports', 'Deemed Exports'),
            ('tax_deductor', 'Tax Deductor'),
            ('sez_developer', 'SEZ Developer'),
        ],
    )
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    
    # Additional details
    restaurant_image = models.ImageField(upload_to='hotel_images/', null=True, blank=True)
    license_number = models.CharField(max_length=100, blank=True, null=True)
    license_copy = models.FileField(upload_to='hotel_licenses/', null=True, blank=True)

    

    



class Menu(models.Model):
    item = models.CharField(max_length=255)
    description = models.CharField(max_length=500, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Actual price
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  # To store the original price
    category = models.CharField(max_length=100)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    status = models.CharField(
        max_length=30,
        choices=[('pending', 'Pending'), ('approved', 'Approved'), ('disapproved', 'Disapproved')],
        default='pending'
    )
    added_by = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='menu_items', null=True, blank=True)
    hotel = models.ForeignKey('HotelSignup', on_delete=models.CASCADE, related_name='menu_items', null=True)

    def get_active_discount(self):
        today = date.today()
        active_discount = self.discounts.filter(start_date__lte=today, end_date__gte=today).first()
        return active_discount

    def apply_discount(self):
        active_discount = self.get_active_discount()
        if active_discount:
            # Calculate the discounted price
            discount_amount = (self.original_price * active_discount.discount_percentage) / 100
            self.price = self.original_price - discount_amount  # Apply the discount
        else:
            # Revert back to the original price when no discount is active
            self.price = self.original_price

    def save(self, *args, **kwargs):
        # Populate the original price on the first save
        if self.original_price is None:
            self.original_price = self.price

        # Save the instance first to get a primary key
        super(Menu, self).save(*args, **kwargs)

        # Apply discount logic only after the instance has a primary key
        self.apply_discount()
        super(Menu, self).save(*args, **kwargs)



    def get_final_price(self):
        # Return the current price (either discounted or original)
        return self.price

class ItemDisapproval(models.Model):
    item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    reason = models.TextField()
    issue_type = models.CharField(max_length=50, choices=[
        ('quality', 'Quality'),
        ('price', 'Price'),
        ('category', 'Category'),
        ('other', 'Other')
    ])
    created_at = models.DateTimeField(auto_now_add=True)

class DeliveryAgent(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='delivery_profile')
    vehicle_number = models.CharField(max_length=20)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    age = models.IntegerField()
    is_available = models.BooleanField(default=True)  # Track agent availability
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('preparing', 'Preparing'),
        ('prepared', 'Prepared'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    item = models.ForeignKey(Menu, on_delete=models.CASCADE,null=True)
    quantity = models.PositiveIntegerField(default=1)
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    payment_method = models.CharField(
        max_length=50, 
        choices=[('COD', 'Cash on Delivery'), ('ONLINE', 'Online')]
    )
    upi = models.CharField(max_length=255, null=True, blank=True) 
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')  # Added for order tracking
    has_review = models.BooleanField(default=False)
    has_issue = models.BooleanField(default=False)
    cancel_reason = models.TextField(null=True, blank=True) 
    assigned_agent = models.ForeignKey(DeliveryAgent, on_delete=models.SET_NULL, null=True, blank=True)
    payment_received = models.BooleanField(default=False) 

class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    hotel = models.ForeignKey(HotelSignup, on_delete=models.CASCADE)  # Cart belongs to a hotel
    item = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
     return (self.item.price * self.quantity) * Decimal('1.18')

    

class Address(models.Model):
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.CASCADE)  # Ensure this field exists
    door_floor_no = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

class Review(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="review")
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="reviews",null=True)  # Link review to Menu
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()  # Range: 1 to 5
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class OrderIssueReport(models.Model):
    ISSUE_CHOICES = [
        ('wrong_item', 'Wrong Item Delivered'),
        ('late_delivery', 'Late Delivery'),
        ('damaged_package', 'Damaged Package'),
        ('missing_item', 'Missing Item'),
        ('other', 'Other'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="issues")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    issue_type = models.CharField(max_length=50, choices=ISSUE_CHOICES)
    description = models.TextField(blank=True, null=True)
    reported_at = models.DateTimeField(auto_now_add=True)
    is_sent_to_restaurant = models.BooleanField(default=False)
    is_resolved = models.BooleanField(default=False)  # Tracks resolution status
    resolution_choice = models.CharField(max_length=50, blank=True, null=True)  # Refund or Replace
    mail_sent = models.BooleanField(default=False)  # Tracks if the mail is sent

class Discount(models.Model):
    item = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="discounts")
    start_date = models.DateField()
    end_date = models.DateField()
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=0)
    created_at = models.DateTimeField(auto_now_add=True) 

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=20, unique=True)
    discount_percentage = models.PositiveIntegerField()
    valid_from = models.DateField()
    valid_to = models.DateField()
    count_used = models.PositiveIntegerField(default=0)
    restaurant = models.ForeignKey(HotelSignup, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(Menu, on_delete=models.CASCADE, null=True)

class RecentSearch(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recent_searches',
        null=True,
        blank=True
    )
    search_query = models.CharField(max_length=255)
    menu_item = models.ForeignKey(
        'Menu',  # Assuming Menu is the related model
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='recent_searches'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']  # Show the most recent searches first

class Reward(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    assigned_date = models.DateTimeField(auto_now_add=True)





    