import requests
from django.conf import settings
from datetime import datetime, timedelta

NVD_API_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"


def fetch_recent_vulnerabilities(days=30, keyword=None):
    """
    Fetches vulnerabilities published in the last 'days' or by a keyword.

    The NVD API uses 'lastModStartDate' and 'lastModEndDate' for filtering.
    For simplicity here, we'll use a fixed time window.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    params = {
        'pubStartDate': start_date.isoformat() + 'Z',
        'pubEndDate': end_date.isoformat() + 'Z',
        'resultsPerPage': 50  # Default
    }

    if keyword:
        # NVD API search requires exact matches for some fields,
        # so using the 'keywordSearch' is the most flexible approach.
        params['keywordSearch'] = keyword

    headers = {}
    if settings.NVD_API_KEY:
        headers['apiKey'] = settings.NVD_API_KEY

    try:
        response = requests.get(NVD_API_BASE_URL, params=params, headers=headers, timeout=10)
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
                    published_date = datetime.fromisoformat(published_date.replace('Z', '+00:00'))

                if published_date:  # Only include if we have a published date
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