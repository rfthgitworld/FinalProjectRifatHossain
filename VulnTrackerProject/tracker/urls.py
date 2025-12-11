from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.home_page, name='home'),
    path('register/', views.user_register, name='register'),
    path('search/', views.search_page, name='search'),
    path('statistics/', views.statistics_page, name='statistics'),

    # Authenticated Pages
    path('dashboard/', views.dashboard_page, name='dashboard'),
    path('watchlist/', views.watchlist_page, name='watchlist'),

    # Actions
    path('watchlist/toggle/<str:cve_id>/', views.toggle_watchlist, name='toggle_watchlist'),

    # NEW: Detail Page for a single vulnerability
    path('vulnerability/<str:cve_id>/', views.vulnerability_detail, name='vulnerability_detail'),
]