# tracker/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from .api import fetch_recent_vulnerabilities
from .models import Vulnerability, WatchlistItem
from .forms import CustomUserCreationForm
import json

# --- Helper Functions ---

def sync_vulnerability(vuln_data):
    """Saves or updates a vulnerability in the local database."""
    # Convert string severity to uppercase for consistency
    severity_str = vuln_data.get('severity', 'UNKNOWN').upper()

    vulnerability, created = Vulnerability.objects.update_or_create(
        cve_id=vuln_data['cve_id'],
        defaults={
            'description': vuln_data['description'],
            'severity': severity_str,
            'cvss_score': vuln_data['cvss_score'],
            'published_date': vuln_data['published_date'],
        }
    )
    return vulnerability


# --- Public Views ---

def home_page(request):
    """Home Page – Displays the latest vulnerabilities."""
    recent_vulns_data = fetch_recent_vulnerabilities(days=7)

    # Sync and get local objects for watchlist checking
    vulnerabilities = []
    for data in recent_vulns_data:
        vuln_obj = sync_vulnerability(data)
        vuln_obj.is_watched = False
        if request.user.is_authenticated:
            vuln_obj.is_watched = WatchlistItem.objects.filter(
                user=request.user,
                vulnerability=vuln_obj
            ).exists()
        vulnerabilities.append(vuln_obj)

    context = {
        'vulnerabilities': vulnerabilities,
        'page_title': 'Latest Vulnerabilities'
    }
    return render(request, 'tracker/home.html', context)


def user_register(request):
    """User Registration Page."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f'Account created for {user.username}! You can now log in.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'tracker/register.html', {'form': form, 'page_title': 'Register'})


def search_page(request):
    """Search Page – Enables users to search vulnerabilities by keyword."""
    query = request.GET.get('q')
    vulnerabilities = []

    if query:
        # Fetch from API
        api_results = fetch_recent_vulnerabilities(days=120, keyword=query)

        # TEMPORARY DIAGNOSTIC LINE
        print(f"API returned {len(api_results)} vulnerabilities for '{query}'.")

        # Sync and prepare for display
        for data in api_results:
            vuln_obj = sync_vulnerability(data)
            vuln_obj.is_watched = False
            if request.user.is_authenticated:
                vuln_obj.is_watched = WatchlistItem.objects.filter(
                    user=request.user,
                    vulnerability=vuln_obj
                ).exists()
            vulnerabilities.append(vuln_obj)

        messages.info(request, f"Found {len(vulnerabilities)} results for '{query}'.")

    context = {
        'vulnerabilities': vulnerabilities,
        'search_query': query if query else '',
        'page_title': 'Search Vulnerabilities'
    }
    return render(request, 'tracker/search.html', context)


# --- Authenticated Views ---

@login_required
def dashboard_page(request):
    """Dashboard Page – Shows personalized vulnerability feeds and statistics."""
    # Get user's watchlist count
    watchlist_count = WatchlistItem.objects.filter(user=request.user).count()

    # Get latest 5 watched vulnerabilities
    latest_watched = WatchlistItem.objects.filter(user=request.user).order_by('-added_on')[:5]

    # Simple aggregated data (e.g., severity distribution of watched items)
    severity_distribution = WatchlistItem.objects.filter(user=request.user).values(
        'vulnerability__severity'
    ).annotate(count=Count('vulnerability__severity')).order_by('-count')

    context = {
        'watchlist_count': watchlist_count,
        'latest_watched': latest_watched,
        'severity_distribution': severity_distribution,
        'page_title': 'Dashboard'
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def watchlist_page(request):
    """My Watchlist Page – Lets users bookmark vulnerabilities they want to monitor."""
    watchlist_items = WatchlistItem.objects.filter(user=request.user).order_by('-added_on')

    context = {
        'watchlist_items': watchlist_items,
        'page_title': 'My Watchlist'
    }
    return render(request, 'tracker/watchlist.html', context)


@login_required
def toggle_watchlist(request, cve_id):
    """Adds or removes a vulnerability from the user's watchlist."""
    if request.method == 'POST':
        # Ensure the vulnerability exists locally (it should from home/search page)
        vulnerability = get_object_or_404(Vulnerability, cve_id=cve_id)

        watchlist_item, created = WatchlistItem.objects.get_or_create(
            user=request.user,
            vulnerability=vulnerability
        )

        if created:
            messages.success(request, f'CVE {cve_id} added to your watchlist.')
        else:
            watchlist_item.delete()
            messages.warning(request, f'CVE {cve_id} removed from your watchlist.')

        # Redirect back to the page they came from
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    return redirect('home')


def statistics_page(request):
    """Statistics Page – Visualizes trends and severity distributions."""

    # Aggregated data for all vulnerabilities in the local DB
    severity_distribution = Vulnerability.objects.values(
        'severity'
    ).annotate(count=Count('severity')).order_by('-count')

    # Prepare Python lists for the Django template filter (Key Metrics)
    severity_labels_list = [item['severity'] for item in severity_distribution]  # NEW LIST NAME
    severity_data_list = [item['count'] for item in severity_distribution]  # NEW LIST NAME

    context = {
        # 1. JSON string version for Chart.js (needs to remain a JSON string)
        'severity_labels_json': json.dumps(severity_labels_list),  # Send JSON to Chart.js
        'severity_data_json': json.dumps(severity_data_list),  # Send JSON to Chart.js

        # 2. Python list version for the Django template (Key Metrics card)
        'severity_labels': severity_labels_list,  # Send Python list to zip_lists
        'severity_data': severity_data_list,  # Send Python list to zip_lists

        'page_title': 'Vulnerability Statistics'
    }
    return render(request, 'tracker/statistics.html', context)

# --- Vul Detail View ---
def vulnerability_detail(request, cve_id):
    """Displays the full details of a single vulnerability."""

    # Fetch the vulnerability from the local database
    vulnerability = get_object_or_404(Vulnerability, cve_id=cve_id)

    # Check if the vulnerability is on the user's watchlist
    is_watched = False
    if request.user.is_authenticated:
        is_watched = WatchlistItem.objects.filter(user=request.user, vulnerability=vulnerability).exists()

    context = {
        'vulnerability': vulnerability,
        'is_watched': is_watched,
        'page_title': vulnerability.cve_id
    }
    return render(request, 'tracker/vulnerability_detail.html', context)