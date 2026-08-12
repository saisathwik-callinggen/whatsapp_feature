import os
from dotenv import load_dotenv

load_dotenv()

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")
EVOLUTION_INSTANCE_NAME = os.getenv("EVOLUTION_INSTANCE_NAME", "callinggen_default")

WA_BROCHURE_URL = os.getenv("WA_BROCHURE_URL")
WA_PRICING_URL = os.getenv("WA_PRICING_URL")
WA_CATALOGUE_URL = os.getenv("WA_CATALOGUE_URL")
WA_WEBSITE_URL = os.getenv("WA_WEBSITE_URL")
WA_BOOKING_URL = os.getenv("WA_BOOKING_URL")
WA_CONTACT_DETAILS = os.getenv("WA_CONTACT_DETAILS")
