
class BitrixApiUrls:

    def __init__(self, base_url):
        self._base_url = self.normalize_url(base_url)

    def normalize_url(self, url):
        if url.endswith("/"):
            url = url[:-1]
        return url

    @property
    def create_lead_url(self):
        return f"{self._base_url}/crm.lead.add.json"
