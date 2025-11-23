from django.db import models
from django.contrib.auth.models import User


class Vulnerability(models.Model):
    """
    Model to store basic vulnerability details fetched from the NVD API
    and to allow users to save it to their watchlist.
    """
    cve_id = models.CharField(max_length=50, unique=True, primary_key=True)
    description = models.TextField()
    severity = models.CharField(max_length=20)
    cvss_score = models.FloatField(null=True, blank=True)
    published_date = models.DateTimeField()

    def __str__(self):
        return self.cve_id


class WatchlistItem(models.Model):
    """
    Model linking a User to a specific Vulnerability they want to track.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vulnerability = models.ForeignKey(Vulnerability, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'vulnerability')
        verbose_name_plural = "Watchlist Items"

    def __str__(self):
        return f'{self.user.username} watching {self.vulnerability.cve_id}'