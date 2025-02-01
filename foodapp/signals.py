from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import Discount, Order
from django.utils.timezone import now

@receiver(post_save, sender=Discount)
def notify_users_about_discount(sender, instance, created, **kwargs):
    if created:  # Only trigger when a new discount is added
        discounted_item = instance.item
        users = Order.objects.filter(item=discounted_item).values_list('user__email', flat=True).distinct()
        
        subject = "🔥 Special Discount on Your Favorite Dish at Eats Xpress! 🍽️"
        message = f"""
Dear Valued Customer,

We have exciting news for you! Your favorite dish, **"{discounted_item.item}"**, is now available at a **special discount** for a limited time at **Eats Xpress**. 

🌟 **Enjoy {instance.discount_percentage}% OFF** on this delicious meal!  
📅 Offer valid until: {instance.end_date}  
🛒 Order now and treat yourself to something amazing!

Hurry! Don't miss out on this exclusive deal. Click below to place your order now:  

👉 [Order Now](https://www.eatsxpress.com)  

Thank you for choosing Eats Xpress. We look forward to serving you!  

Bon Appétit,  
**The Eats Xpress Team**  
📞 Contact us: +91-9496233231  
📧 support@eatsxpress.com  
"""
    from_email = "pvsarath2002@gmail.com"  # Replace with your email

    for email in users:
            if email:  # Ensure the user has an email
                send_mail(subject, message, from_email, [email])
