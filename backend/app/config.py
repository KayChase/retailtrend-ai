import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAMPLE_SALES_CSV = DATA_DIR / "sample_sales.csv"
UPLOADED_SALES_CSV = DATA_DIR / "uploaded_sales.csv"
FORECAST_LOG_JSON = DATA_DIR / "forecast_log.json"
STORE_LOCATIONS_CSV = DATA_DIR / "store_locations.csv"

# Fallback location used for the weather outlook when the user hasn't set one.
DEFAULT_WEATHER_LOCATION = "New York, NY"

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if origin.strip()
]

# Store departments tracked across the whole app. Keep the Google Trends
# search term and the internal sales-data category key in sync here.
CATEGORIES = {
    "pharmacy": "pharmacy",
    "health": "health products",
    "beauty": "beauty products",
    "personal_care": "personal care products",
    "oral_care": "oral care products",
    "baby": "baby products",
    "grocery": "grocery",
    "candy_snacks": "candy and snacks",
    "beverages": "beverages",
    "household": "household supplies",
    "pet_care": "pet supplies",
    "seasonal": "seasonal decorations",
    "electronics": "electronics",
    "toys": "toys",
    "greeting_cards_gift_wrap": "greeting cards",
    "photo_center": "photo printing",
    "checkout_impulse": "impulse buy items",
}

# Display labels for categories whose punctuation/casing can't be derived
# from the key via a simple title-case (e.g. "Candy & Snacks").
CATEGORY_LABELS = {
    "pharmacy": "Pharmacy",
    "health": "Health",
    "beauty": "Beauty",
    "personal_care": "Personal Care",
    "oral_care": "Oral Care",
    "baby": "Baby",
    "grocery": "Grocery",
    "candy_snacks": "Candy & Snacks",
    "beverages": "Beverages",
    "household": "Household",
    "pet_care": "Pet Care",
    "seasonal": "Seasonal",
    "electronics": "Electronics",
    "toys": "Toys",
    "greeting_cards_gift_wrap": "Greeting Cards & Gift Wrap",
    "photo_center": "Photo Center",
    "checkout_impulse": "Checkout / Impulse Items",
}

# Representative products shown when a department is selected. These are
# generic, publicly-known brand names (not tied to any specific store's
# proprietary sales/margin data) used to drive per-product trend lookups.
PRODUCTS = {
    "pharmacy": [
        "Tylenol Extra Strength", "Advil", "Excedrin", "Bayer Aspirin",
        "Mucinex", "NyQuil", "ZzzQuil", "Aleve", "Pepto-Bismol", "Claritin",
    ],
    "health": [
        "Vitamin C", "Vitamin D3", "Fish Oil", "Multivitamin", "Melatonin",
        "Probiotics", "Zinc Supplement", "Elderberry Gummies", "Biotin", "Magnesium",
    ],
    "beauty": [
        "Maybelline Mascara", "L'Oreal Foundation", "e.l.f. Cosmetics", "NYX Lipstick",
        "CeraVe Moisturizer", "Neutrogena Sunscreen", "Olay Regenerist",
        "Revlon Nail Polish", "Burt's Bees Lip Balm", "Garnier Micellar Water",
    ],
    "personal_care": [
        "Dove Soap", "Old Spice Deodorant", "Secret Antiperspirant", "Nivea Body Lotion",
        "Gillette Razors", "Axe Body Spray", "Suave Shampoo", "Vaseline",
        "Degree Deodorant", "Softsoap",
    ],
    "oral_care": [
        "Crest Toothpaste", "Colgate Toothpaste", "Oral-B Toothbrush", "Listerine Mouthwash",
        "Sensodyne", "Scope Mouthwash", "Waterpik", "Crest Whitestrips",
        "Reach Floss", "ACT Mouthwash",
    ],
    "baby": [
        "Pampers Diapers", "Huggies Diapers", "Enfamil Formula", "Similac Formula",
        "Baby Wipes", "Johnson's Baby Shampoo", "Gerber Baby Food", "Desitin",
        "Baby Orajel", "Aveeno Baby Lotion",
    ],
    "grocery": [
        "Coca-Cola", "Lay's Chips", "Oreo Cookies", "Doritos", "Pringles",
        "Cheerios", "Campbell's Soup", "Kraft Mac and Cheese", "Ritz Crackers", "Folgers Coffee",
    ],
    "candy_snacks": [
        "M&M's", "Kit Kat", "Skittles", "Reese's Peanut Butter Cups", "Hershey's Kisses",
        "Ferrero Rocher", "Twix", "Snickers", "Cadbury Mini Eggs", "Lindt Truffles",
    ],
    "beverages": [
        "Gatorade", "Red Bull", "Coca-Cola", "Pepsi", "Poland Spring Water",
        "Monster Energy", "Sprite", "Dunkin Iced Coffee", "Celsius", "Powerade",
    ],
    "household": [
        "Bounty Paper Towels", "Scott Toilet Paper", "Clorox Wipes", "Tide Detergent",
        "Dawn Dish Soap", "Glad Trash Bags", "Lysol Spray", "Febreze", "Swiffer", "Windex",
    ],
    "pet_care": [
        "Purina Dog Food", "Friskies Cat Food", "Milk-Bone Treats", "Pedigree Dog Food",
        "Greenies", "Tidy Cats Litter", "Kong Dog Toys", "Frontline Flea Treatment",
        "Blue Buffalo", "Whisker City Cat Toys",
    ],
    "seasonal": [
        "Halloween Candy", "Christmas Lights", "Easter Eggs", "Valentine's Chocolate Box",
        "Pumpkin Decor", "Christmas Ornaments", "Easter Basket", "Fourth of July Decorations",
        "Advent Calendar", "Gift Wrap Rolls",
        "FIFA Panini Singular Packs", "FIFA Panini 50 Pack",
    ],
    "electronics": [
        "Apple AirPods", "Phone Charger", "Portable Power Bank", "Bluetooth Speaker",
        "Phone Case", "USB Cable", "Wireless Earbuds", "AA Batteries",
        "Selfie Stick", "Screen Protector",
    ],
    "toys": [
        "Pokemon Trading Cards", "LEGO Sets", "Barbie Dolls", "Hot Wheels",
        "Squishmallows", "Nerf Blasters", "Beanie Babies", "Play-Doh",
        "Action Figures", "Jigsaw Puzzles",
    ],
    "greeting_cards_gift_wrap": [
        "Hallmark Birthday Card", "Christmas Cards", "Gift Bags", "Wrapping Paper",
        "Ribbon and Bows", "Valentine's Day Cards", "Mother's Day Cards",
        "Gift Tags", "Tissue Paper", "Anniversary Cards",
    ],
    "photo_center": [
        "Photo Prints", "Photo Book", "Canvas Print", "Passport Photo",
        "Photo Christmas Cards", "Photo Calendar", "Disposable Camera",
        "Photo Mug", "Collage Poster", "Wallet Photos",
    ],
    "checkout_impulse": [
        "Chewing Gum", "Altoids Mints", "Candy Bar", "Phone Charger",
        "Chapstick", "Hand Sanitizer", "Gift Card", "AA Batteries",
        "Sunglasses", "Lottery Scratchers",
    ],
}

# (peak_month 1-12, strength 0-1) used to make the sample/fallback trend data
# reflect the time of year instead of being purely random — e.g. "Fourth of
# July Decorations" should outrank "Pumpkin Decor" in early July. Strength 0
# would mean no seasonality at all; low strength (0.05-0.15) is used for
# products with only a mild/steady demand pattern.
PRODUCT_SEASONALITY = {
    # pharmacy
    "Tylenol Extra Strength": (1, 0.30),
    "Advil": (1, 0.15),
    "Excedrin": (1, 0.10),
    "Bayer Aspirin": (1, 0.10),
    "Mucinex": (1, 0.50),
    "NyQuil": (1, 0.55),
    "ZzzQuil": (12, 0.20),
    "Aleve": (1, 0.10),
    "Pepto-Bismol": (12, 0.20),
    "Claritin": (4, 0.60),
    # health
    "Vitamin C": (1, 0.30),
    "Vitamin D3": (1, 0.35),
    "Fish Oil": (1, 0.25),
    "Multivitamin": (1, 0.30),
    "Melatonin": (12, 0.15),
    "Probiotics": (1, 0.25),
    "Zinc Supplement": (1, 0.30),
    "Elderberry Gummies": (11, 0.45),
    "Biotin": (1, 0.20),
    "Magnesium": (1, 0.20),
    # beauty
    "Maybelline Mascara": (6, 0.10),
    "L'Oreal Foundation": (6, 0.10),
    "e.l.f. Cosmetics": (6, 0.10),
    "NYX Lipstick": (2, 0.25),
    "CeraVe Moisturizer": (1, 0.30),
    "Neutrogena Sunscreen": (7, 0.70),
    "Olay Regenerist": (6, 0.10),
    "Revlon Nail Polish": (5, 0.20),
    "Burt's Bees Lip Balm": (1, 0.30),
    "Garnier Micellar Water": (6, 0.10),
    # personal_care
    "Dove Soap": (6, 0.10),
    "Old Spice Deodorant": (7, 0.30),
    "Secret Antiperspirant": (7, 0.30),
    "Nivea Body Lotion": (1, 0.25),
    "Gillette Razors": (6, 0.25),
    "Axe Body Spray": (7, 0.30),
    "Suave Shampoo": (6, 0.10),
    "Vaseline": (1, 0.20),
    "Degree Deodorant": (7, 0.30),
    "Softsoap": (6, 0.10),
    # oral_care
    "Crest Toothpaste": (6, 0.10),
    "Colgate Toothpaste": (6, 0.10),
    "Oral-B Toothbrush": (6, 0.10),
    "Listerine Mouthwash": (6, 0.10),
    "Sensodyne": (6, 0.10),
    "Scope Mouthwash": (6, 0.10),
    "Waterpik": (1, 0.25),
    "Crest Whitestrips": (1, 0.30),
    "Reach Floss": (6, 0.10),
    "ACT Mouthwash": (6, 0.10),
    # baby
    "Pampers Diapers": (6, 0.05),
    "Huggies Diapers": (6, 0.05),
    "Enfamil Formula": (6, 0.05),
    "Similac Formula": (6, 0.05),
    "Baby Wipes": (6, 0.05),
    "Johnson's Baby Shampoo": (6, 0.05),
    "Gerber Baby Food": (6, 0.05),
    "Desitin": (6, 0.05),
    "Baby Orajel": (6, 0.05),
    "Aveeno Baby Lotion": (6, 0.05),
    # grocery
    "Coca-Cola": (7, 0.20),
    "Lay's Chips": (7, 0.20),
    "Oreo Cookies": (6, 0.10),
    "Doritos": (6, 0.10),
    "Pringles": (6, 0.10),
    "Cheerios": (6, 0.05),
    "Campbell's Soup": (1, 0.35),
    "Kraft Mac and Cheese": (6, 0.10),
    "Ritz Crackers": (12, 0.20),
    "Folgers Coffee": (1, 0.15),
    # candy_snacks
    "M&M's": (12, 0.20),
    "Kit Kat": (10, 0.30),
    "Skittles": (10, 0.25),
    "Reese's Peanut Butter Cups": (10, 0.35),
    "Hershey's Kisses": (12, 0.30),
    "Ferrero Rocher": (12, 0.40),
    "Twix": (10, 0.20),
    "Snickers": (10, 0.20),
    "Cadbury Mini Eggs": (4, 0.60),
    "Lindt Truffles": (12, 0.40),
    # beverages
    "Gatorade": (7, 0.40),
    "Red Bull": (6, 0.15),
    "Pepsi": (7, 0.20),
    "Poland Spring Water": (7, 0.40),
    "Monster Energy": (6, 0.15),
    "Sprite": (7, 0.20),
    "Dunkin Iced Coffee": (7, 0.35),
    "Celsius": (7, 0.25),
    "Powerade": (7, 0.40),
    # household
    "Bounty Paper Towels": (6, 0.10),
    "Scott Toilet Paper": (6, 0.05),
    "Clorox Wipes": (1, 0.30),
    "Tide Detergent": (6, 0.10),
    "Dawn Dish Soap": (11, 0.20),
    "Glad Trash Bags": (11, 0.20),
    "Lysol Spray": (1, 0.35),
    "Febreze": (6, 0.10),
    "Swiffer": (3, 0.30),
    "Windex": (3, 0.25),
    # pet_care
    "Purina Dog Food": (6, 0.05),
    "Friskies Cat Food": (6, 0.05),
    "Milk-Bone Treats": (12, 0.15),
    "Pedigree Dog Food": (6, 0.05),
    "Greenies": (6, 0.05),
    "Tidy Cats Litter": (6, 0.05),
    "Kong Dog Toys": (12, 0.20),
    "Frontline Flea Treatment": (6, 0.50),
    "Blue Buffalo": (6, 0.05),
    "Whisker City Cat Toys": (12, 0.15),
    # seasonal
    "Halloween Candy": (10, 0.90),
    "Christmas Lights": (12, 0.95),
    "Easter Eggs": (4, 0.85),
    "Valentine's Chocolate Box": (2, 0.90),
    "Pumpkin Decor": (10, 0.90),
    "Christmas Ornaments": (12, 0.95),
    "Easter Basket": (4, 0.85),
    "Fourth of July Decorations": (7, 0.95),
    "Advent Calendar": (11, 0.80),
    "Gift Wrap Rolls": (12, 0.70),
    "FIFA Panini Singular Packs": (7, 0.99),
    "FIFA Panini 50 Pack": (7, 0.97),
    # electronics
    "Apple AirPods": (12, 0.50),
    "Phone Charger": (6, 0.10),
    "Portable Power Bank": (7, 0.25),
    "Bluetooth Speaker": (7, 0.30),
    "Phone Case": (12, 0.20),
    "USB Cable": (6, 0.10),
    "Wireless Earbuds": (12, 0.40),
    "AA Batteries": (12, 0.30),
    "Selfie Stick": (7, 0.30),
    "Screen Protector": (9, 0.25),
    # toys
    "Pokemon Trading Cards": (12, 0.20),
    "LEGO Sets": (12, 0.60),
    "Barbie Dolls": (12, 0.60),
    "Hot Wheels": (12, 0.50),
    "Squishmallows": (12, 0.50),
    "Nerf Blasters": (12, 0.50),
    "Beanie Babies": (6, 0.15),
    "Play-Doh": (12, 0.40),
    "Action Figures": (12, 0.50),
    "Jigsaw Puzzles": (12, 0.40),
    # greeting_cards_gift_wrap
    "Hallmark Birthday Card": (6, 0.10),
    "Christmas Cards": (12, 0.90),
    "Gift Bags": (12, 0.30),
    "Wrapping Paper": (12, 0.60),
    "Ribbon and Bows": (12, 0.40),
    "Valentine's Day Cards": (2, 0.85),
    "Mother's Day Cards": (5, 0.85),
    "Gift Tags": (12, 0.30),
    "Tissue Paper": (12, 0.20),
    "Anniversary Cards": (6, 0.10),
    # photo_center
    "Photo Prints": (7, 0.20),
    "Photo Book": (12, 0.40),
    "Canvas Print": (12, 0.35),
    "Passport Photo": (6, 0.30),
    "Photo Christmas Cards": (11, 0.85),
    "Photo Calendar": (12, 0.60),
    "Disposable Camera": (7, 0.30),
    "Photo Mug": (12, 0.40),
    "Collage Poster": (6, 0.15),
    "Wallet Photos": (6, 0.10),
    # checkout_impulse
    "Chewing Gum": (6, 0.10),
    "Altoids Mints": (6, 0.10),
    "Candy Bar": (10, 0.20),
    "Chapstick": (1, 0.30),
    "Hand Sanitizer": (1, 0.30),
    "Gift Card": (12, 0.60),
    "Sunglasses": (7, 0.50),
    "Lottery Scratchers": (12, 0.20),
}

# Fixed trend override for products that should always rank at the very top
# of their department's trending list, regardless of the date-driven
# seasonality curve or any live Google Trends result. Overrides both the
# fallback and live paths in product_trends.get_product_trends.
FEATURED_TOP_TREND_PCT = {
    "FIFA Panini Singular Packs": 180.0,
    "FIFA Panini 50 Pack": 155.0,
}

# (weather_type "hot"|"cold", strength 0-1) for products whose demand is
# genuinely weather-driven (heat waves sell sunscreen and cold drinks, cold
# snaps sell cold/flu remedies and lip balm). Only products with a real,
# grounded weather link are included — everything else simply has no entry
# and gets no weather adjustment.
WEATHER_SENSITIVITY = {
    "Neutrogena Sunscreen": ("hot", 0.80),
    "Gatorade": ("hot", 0.50),
    "Powerade": ("hot", 0.50),
    "Poland Spring Water": ("hot", 0.50),
    "Celsius": ("hot", 0.30),
    "Dunkin Iced Coffee": ("hot", 0.30),
    "Sprite": ("hot", 0.20),
    "Coca-Cola": ("hot", 0.20),
    "Pepsi": ("hot", 0.20),
    "Monster Energy": ("hot", 0.20),
    "Old Spice Deodorant": ("hot", 0.30),
    "Secret Antiperspirant": ("hot", 0.30),
    "Axe Body Spray": ("hot", 0.30),
    "Degree Deodorant": ("hot", 0.30),
    "Sunglasses": ("hot", 0.60),
    "Portable Power Bank": ("hot", 0.20),
    "Frontline Flea Treatment": ("hot", 0.40),
    "NyQuil": ("cold", 0.40),
    "Mucinex": ("cold", 0.40),
    "Tylenol Extra Strength": ("cold", 0.30),
    "Clorox Wipes": ("cold", 0.30),
    "Lysol Spray": ("cold", 0.30),
    "Hand Sanitizer": ("cold", 0.30),
    "CeraVe Moisturizer": ("cold", 0.30),
    "Burt's Bees Lip Balm": ("cold", 0.30),
    "Chapstick": ("cold", 0.30),
    "Vaseline": ("cold", 0.20),
    "Nivea Body Lotion": ("cold", 0.20),
}

STATES = [
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
]

# Google Trends' live interest_by_region() returns full state names
# ("California"), not the two-letter codes used everywhere else in this app
# (STATES above, store_locations.csv, PRODUCT_SEASONALITY). This maps live
# results back to the abbreviations so the region heat map, store lookup,
# and everything else stay on one consistent key.
STATE_NAME_TO_ABBR = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "Florida": "FL", "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID",
    "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS",
    "Missouri": "MO", "Montana": "MT", "Nebraska": "NE", "Nevada": "NV",
    "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC",
    "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX", "Utah": "UT",
    "Vermont": "VT", "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY",
}

