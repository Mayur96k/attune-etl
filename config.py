from google.cloud import secretmanager

PROJECT_ID = "attune-data-platform"

# ==========================================
# DATA LAKE CONFIGURATION
# ==========================================

REGION = "AFRICA_raw"
SITE = "SCAST"

BUCKET_NAME = "attune-raw-prod"

# ==========================================
# SECRET MANAGER
# ==========================================

def get_secret(secret_name):

    client = secretmanager.SecretManagerServiceClient()

    secret_path = (
        f"projects/{PROJECT_ID}/secrets/"
        f"{secret_name}/versions/latest"
    )

    response = client.access_secret_version(
        request={"name": secret_path}
    )

    return response.payload.data.decode("UTF-8")


# ==========================================
# ATTUNE CONFIGURATION
# ==========================================

CONFIG = {
    "organization": get_secret("attune-organization").strip(),
    "base_url": get_secret("attune-baseurl").strip(),
    "tenant": get_secret("attune-tenant").strip(),
    "api_key": get_secret("attune-apikey").strip()
}