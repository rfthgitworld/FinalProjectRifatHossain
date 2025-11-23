
from django.contrib import admin
from .models import Vulnerability, WatchlistItem

@admin.register(Vulnerability)
class VulnerabilityAdmin(admin.ModelAdmin):
    list_display = ('cve_id', 'severity', 'cvss_score', 'published_date')
    search_fields = ('cve_id', 'description')

@admin.register(WatchlistItem)
class WatchlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'vulnerability', 'added_on')
    list_filter = ('user', 'added_on')