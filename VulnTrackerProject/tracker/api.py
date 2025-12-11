import requests
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone  # <--- NEW IMPORT

NVD_API_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def fetch_recent_vulnerabilities(days=30, keyword=None):
    """
    Fetches vulnerabilities. Always uses the 'days' parameter to calculate
    the publication date range for filtering.
    """

    # 1. Calculate the required date range (using the 'days' argument)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # 2. Set base parameters: ALWAYS include the date range
    params = {
        'resultsPerPage': 50,
        'pubStartDate': start_date.isoformat() + 'Z',  # Now included unconditionally
        'pubEndDate': end_date.isoformat() + 'Z'  # Now included unconditionally
    }

    # 3. Add keyword filter if present
    if keyword:
        params['keywordSearch'] = keyword  # Included alongside the date filters

    headers = {}
    if settings.NVD_API_KEY:
        headers['apiKey'] = settings.NVD_API_KEY

    try:
        # Added a 15-second timeout for robustness
        response = requests.get(NVD_API_BASE_URL, params=params, headers=headers, timeout=15)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()

        vulnerabilities = []
        if 'vulnerabilities' in data:
            for item in data['vulnerabilities']:
                cve = item['cve']

                # Extract description
                description = "No description available."
                for desc in cve['descriptions']:
                    if desc['lang'] == 'en':
                        description = desc['value']
                        break

                # Extract CVSS v3.1 score and severity
                cvss_score = None
                severity = 'UNKNOWN'

                # Prioritize CVSS v3.1
                metrics = cve.get('metrics', {})
                if 'cvssMetricV31' in metrics:
                    metric = metrics['cvssMetricV31'][0]
                    cvss_score = metric['cvssData']['baseScore']
                    severity = metric['cvssData']['baseSeverity']
                elif 'cvssMetricV2' in metrics:
                    # Fallback to CVSS v2.0
                    metric = metrics['cvssMetricV2'][0]
                    cvss_score = metric['cvssData']['baseScore']
                    severity = metric['baseSeverity']

                # Extract published date
                published_date = cve.get('published')
                if published_date:
                    # 1. Create a naive datetime object
                    dt_obj = datetime.fromisoformat(published_date.replace('Z', '+00:00'))

                    # 2. FIX: Make the datetime object time-zone aware (assuming UTC from NVD's 'Z')
                    published_date = timezone.make_aware(dt_obj)  # <--- FIX

                if published_date:
                    vulnerabilities.append({
                        'cve_id': cve['id'],
                        'description': description,
                        'cvss_score': cvss_score,
                        'severity': severity,
                        'published_date': published_date,
                    })

        return vulnerabilities

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from NVD API: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return []