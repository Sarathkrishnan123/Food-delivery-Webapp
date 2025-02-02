Full-Stack Food Delivery Platform

Overview

This project is a full-stack food delivery platform inspired by popular services like Swiggy and Zomato. It includes a responsive and attractive frontend built with HTML, CSS, JavaScript, and Bootstrap, along with a robust backend powered by Python-Django. The platform supports multi-role authentication, real-time order tracking, and advanced features like discounts, coupons, and location-based restaurant searches.

Features
User Features:

Sign Up/Sign In: Secure authentication with live validations for email, mobile, and required fields.

User Dashboard: Profile management, address addition, and order history.

Food Ordering: Browse restaurants, view menus, and place orders with multiple food items.

Order Tracking: Real-time updates on order status (preparing, out for delivery, delivered).

Ratings and Reviews: Rate and review restaurants and food items.

Discounts and Coupons: Use discount codes and view discounted items.

Recent Searches: Display recently searched food items on the landing page.

Location-Based Search: Search for restaurants based on location and view approximate delivery time/distance.

Order Issues: Raise issues related to orders, which are forwarded to the admin and hotel.

Order Cancellation: Cancel orders (if status is "preparing") with a reason.

Hotel Features:

Hotel Registration: Separate registration page with validations.

Hotel Dashboard: Add, edit, delete, and view food items. Manage orders and update order status.

Discount Management: Offer discounts on food items.

Coupon Codes: Generate and share coupon codes with users.

Order Issues: View and resolve issues raised by users.

Admin Features:

Admin Dashboard: Approve or reject food items added by hotels. Provide rejection reasons.

User and Hotel Management: Manage user and hotel profiles.

Order Issues: Handle order-related issues and assign them to hotels.

Delivery Boy Management: Register delivery boys and assign orders to them.

Coupon Distribution: Provide coupons to users based on their order history.

Delivery Boy Features:

Order Delivery: Receive orders assigned by the admin, deliver them, and update order status.

Payment Handling: Collect payments (if applicable) and mark orders as delivered.

Technologies Used:

Frontend: HTML, CSS, JavaScript, Bootstrap (Responsive and Attractive UI)

Backend: Python-Django (REST API and Database Management)

Database: SQLite (for development) / PostgreSQL (for production)

Authentication: Django’s built-in authentication system

Email Notifications: Django’s Email Backend

Search and Pagination: Django’s ORM and custom implementations

Version Control: Git and GitHub
