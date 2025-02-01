from django.urls import path,include
from .import views

urlpatterns = [
    path('',views.index,name="index"),
    path('loginpage',views.loginpage,name="loginpage"),
    path('signup',views.signup,name="signup"),
    path('hotel_signup',views.hotel_signup,name="hotel_signup"),
    path('user_signup/', views.user_signup, name='user_signup'),
    path('hotel_signupdb/', views.hotel_signupdb, name='hotel_signupdb'),
    path('user_profile', views.user_profile, name='user_profile'),
    path('login1',views.login1,name="login1"),
    path('view_user_profile', views.view_user_profile, name='view_user_profile'),
    path('logout/', views.logout_user, name='logout'),
    path('admin', views.admin, name='admin'),
    path('hotel', views.hotel, name='hotel'),
    path('add_food', views.add_food, name='add_food'),
    path('add_fooddb', views.add_fooddb, name='add_fooddb'),
    path('pending-items', views.pending_items, name='pending_items'),
    path('update-item-status/<int:item_id>/<str:action>/', views.update_item_status, name='update_item_status'),
    path('all_items/', views.all_items, name='all_items'),
    path('hotel_items', views.hotel_items, name='hotel_items'),
    path('approved_hotel_items', views.approved_hotel_items, name='approved_hotel_items'),
    path('edit_menu_item<int:item_id>/', views.edit_menu_item, name='edit_menu_item'),
    path('delete_menu_item/<int:item_id>/', views.delete_menu_item, name='delete_menu_item'),
    path('billing/<int:item_id>/', views.billing_view, name='billing'),
    path('order-success/', views.order_success, name='order_success'),
    path('hotel_orders', views.hotel_orders, name='hotel_orders'),
    path('hotel/orders/update/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('user_orders/', views.user_orders, name='user_orders'),
    path('add-address/', views.add_address, name='add_address'),
    path('view-addresses/', views.view_addresses, name='view_addresses'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('hotel/profile/', views.view_hotel_profile, name='view_hotel_profile'),
    path('hotel/profile/edit/<int:hotel_id>/', views.edit_hotel_profile, name='edit_hotel_profile'),
    path('add-hotel-details/', views.add_hotel_details, name='add_hotel_details'),
    path('restaurant_menu<int:hotel_id>/', views.restaurant_menu, name='restaurant_menu'),
    path('search_food', views.search_food, name='search_food'),
    path('order/<int:order_id>/submit-review/', views.submit_review, name='submit_review'),
    path('search/', views.search_restaurants, name='search_restaurants'),
    path("report_issue/<int:order_id>/", views.report_issue, name="report_issue"),
    path('admin_issue_list', views.admin_issue_list, name='admin_issue_list'),
    path('send_to_restaurant<int:issue_id>/', views.send_to_restaurant, name='send_to_restaurant'),
    path('restaurant_issue_list', views.restaurant_issue_list, name='restaurant_issue_list'),
    path('add_discount', views.add_discount, name='add_discount'),
    path('add_coupon', views.add_coupon, name='add_coupon'),
    path('validate_coupon/', views.validate_coupon, name='validate_coupon'),
    path('restaurant/resolve/<int:issue_id>/', views.restaurant_resolve_issue, name='restaurant_resolve_issue'),
    path('user_issues', views.user_issues, name='user_issues'),
    path('user/issues/resolve/<int:issue_id>/', views.handle_user_resolution, name='handle_user_resolution'),
    path('restaurant/issue/send-mail/<int:issue_id>/', views.restaurant_send_mail, name='restaurant_send_mail'),
    path('sandwiches/', views.sandwiches_menu, name='sandwiches_menu'),
    path('friedchicken/', views.friedchicken_menu, name='friedchicken_menu'),
    path('pizza/', views.pizza_menu, name='pizza_menu'),
    path('assign_and_show_coupon', views.assign_and_show_coupon, name='assign_and_show_coupon'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('update-cart-ajax/', views.update_cart_ajax, name='update_cart_ajax'),
    path('place-order/', views.place_order, name='place_order'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order-successful/<int:items_ordered>/', views.order_successful, name='order_successful'),
    path('register-delivery-agent/', views.register_delivery_agent, name='register_delivery_agent'),
    path('delivery_agent', views.delivery_agent, name='delivery_agent'),
    path('manage-orders/', views.manage_orders, name='manage_orders'),
    path('agent-orders/', views.agent_orders, name='agent_orders'),
    path('update_order_statuses/<int:order_id>/', views.update_order_statuses, name='update_order_statuses'),
    
    
    
    

    


    

    
    
   

 
    
]