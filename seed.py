from datetime import date
from app import create_app
from models import PriceRecord, db

SAMPLE_DATA = [
    {
        "crop_name": "Wheat",
        "market": "Pune APMC",
        "price_per_quintal": 2450.00,
        "price_date": date(2026, 11, 10),
    },
    {
        "crop_name": "Wheat",
        "market": "Pune APMC",
        "price_per_quintal": 2480.00,
        "price_date": date(2026, 11, 15),
    },
    {
        "crop_name": "Wheat",
        "market": "Nagpur APMC",
        "price_per_quintal": 2510.50,
        "price_date": date(2026, 11, 18),
    },
    {
        "crop_name": "Rice",
        "market": "Nashik APMC",
        "price_per_quintal": 3600.00,
        "price_date": date(2026, 11, 12),
    },
    {
        "crop_name": "Rice",
        "market": "Pune APMC",
        "price_per_quintal": 3720.00,
        "price_date": date(2026, 11, 16),
    },
    {
        "crop_name": "Rice",
        "market": "Mumbai APMC",
        "price_per_quintal": 3850.00,
        "price_date": date(2026, 11, 19),
    },
    {
        "crop_name": "Onion",
        "market": "Lasalgaon APMC",
        "price_per_quintal": 2100.00,
        "price_date": date(2026, 11, 8),
    },
    {
        "crop_name": "Onion",
        "market": "Pune APMC",
        "price_per_quintal": 2300.00,
        "price_date": date(2026, 11, 14),
    },
    {
        "crop_name": "Onion",
        "market": "Lasalgaon APMC",
        "price_per_quintal": 2250.00,
        "price_date": date(2026, 11, 19),
    },
    {
        "crop_name": "Tomato",
        "market": "Nashik APMC",
        "price_per_quintal": 1850.00,
        "price_date": date(2026, 11, 9),
    },
    {
        "crop_name": "Tomato",
        "market": "Pune APMC",
        "price_per_quintal": 1950.00,
        "price_date": date(2026, 11, 13),
    },
    {
        "crop_name": "Tomato",
        "market": "Mumbai APMC",
        "price_per_quintal": 2100.00,
        "price_date": date(2026, 11, 18),
    },
    {
        "crop_name": "Potato",
        "market": "Indore APMC",
        "price_per_quintal": 1400.00,
        "price_date": date(2026, 11, 11),
    },
    {
        "crop_name": "Potato",
        "market": "Pune APMC",
        "price_per_quintal": 1550.00,
        "price_date": date(2026, 11, 17),
    },
    {
        "crop_name": "Maize",
        "market": "Kolhapur APMC",
        "price_per_quintal": 2050.00,
        "price_date": date(2026, 11, 12),
    },
    {
        "crop_name": "Maize",
        "market": "Pune APMC",
        "price_per_quintal": 2120.00,
        "price_date": date(2026, 11, 16),
    },
]


def seed_database():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        records = [PriceRecord(**item) for item in SAMPLE_DATA]
        db.session.bulk_save_objects(records)
        db.session.commit()

        count = PriceRecord.query.count()
        print(f"Successfully seeded {count} price records into the database.")


if __name__ == "__main__":
    seed_database()
