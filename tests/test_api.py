import pytest
from datetime import date
from app import create_app
from models import PriceRecord, db


@pytest.fixture
def app():
    test_config = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    }
    app = create_app(test_config=test_config)

    with app.app_context():
        db.create_all()
        records = [
            PriceRecord(
                crop_name="Wheat",
                market="Pune APMC",
                price_per_quintal=2450.00,
                price_date=date(2026, 11, 10),
            ),
            PriceRecord(
                crop_name="Wheat",
                market="Nagpur APMC",
                price_per_quintal=2550.00,
                price_date=date(2026, 11, 15),
            ),
            PriceRecord(
                crop_name="Rice",
                market="Pune APMC",
                price_per_quintal=3600.00,
                price_date=date(2026, 11, 12),
            ),
        ]
        db.session.bulk_save_objects(records)
        db.session.commit()

        yield app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_get_all_prices(client):
    response = client.get("/prices")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 3


def test_get_prices_filter_crop(client):
    response = client.get("/prices?crop=wheat")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    for item in data:
        assert item["crop_name"].lower() == "wheat"


def test_get_prices_filter_market(client):
    response = client.get("/prices?market=Pune%20APMC")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    for item in data:
        assert item["market"] == "Pune APMC"


def test_get_prices_filter_both(client):
    response = client.get("/prices?crop=Wheat&market=Pune%20APMC")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["crop_name"] == "Wheat"
    assert data[0]["market"] == "Pune APMC"


def test_get_price_by_id_success(client):
    response = client.get("/prices/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1
    assert data["crop_name"] == "Wheat"
    assert data["price_per_quintal"] == 2450.00
    assert data["price_date"] == "2026-11-10"


def test_get_price_by_id_not_found(client):
    response = client.get("/prices/999")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data
    assert data["error"] == "Price record not found"


def test_create_price_success(client):
    payload = {
        "crop_name": "Tomato",
        "market": "Nashik APMC",
        "price_per_quintal": 1850.50,
        "price_date": "2026-11-20",
    }
    response = client.post("/prices", json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["id"] is not None
    assert data["crop_name"] == "Tomato"
    assert data["market"] == "Nashik APMC"
    assert data["price_per_quintal"] == 1850.50
    assert data["price_date"] == "2026-11-20"
    assert data["created_at"] is not None


@pytest.mark.parametrize(
    "payload,expected_error_substring",
    [
        (None, "Request body must be JSON"),
        ({}, "Missing required field"),
        (
            {
                "crop_name": "",
                "market": "Pune APMC",
                "price_per_quintal": 2000,
                "price_date": "2026-11-10",
            },
            "non-empty string",
        ),
        (
            {
                "crop_name": "Wheat",
                "market": "   ",
                "price_per_quintal": 2000,
                "price_date": "2026-11-10",
            },
            "non-empty string",
        ),
        (
            {
                "crop_name": "Wheat",
                "market": "Pune APMC",
                "price_per_quintal": -50,
                "price_date": "2026-11-10",
            },
            "greater than 0",
        ),
        (
            {
                "crop_name": "Wheat",
                "market": "Pune APMC",
                "price_per_quintal": 0,
                "price_date": "2026-11-10",
            },
            "greater than 0",
        ),
        (
            {
                "crop_name": "Wheat",
                "market": "Pune APMC",
                "price_per_quintal": "not-a-number",
                "price_date": "2026-11-10",
            },
            "valid number",
        ),
        (
            {
                "crop_name": "Wheat",
                "market": "Pune APMC",
                "price_per_quintal": 2000,
                "price_date": "10-11-2026",
            },
            "YYYY-MM-DD",
        ),
        (
            {
                "crop_name": "Wheat",
                "market": "Pune APMC",
                "price_per_quintal": 2000,
                "price_date": "invalid-date",
            },
            "YYYY-MM-DD",
        ),
    ],
)
def test_create_price_invalid_inputs(
    client, payload, expected_error_substring
):
    if payload is None:
        response = client.post(
            "/prices", data="not json", content_type="text/plain"
        )
    else:
        response = client.post("/prices", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert expected_error_substring.lower() in data["error"].lower()


def test_update_price_success(client):
    payload = {
        "crop_name": "Wheat Updated",
        "market": "Pune APMC Updated",
        "price_per_quintal": 2600.00,
        "price_date": "2026-11-11",
    }
    response = client.put("/prices/1", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == 1
    assert data["crop_name"] == "Wheat Updated"
    assert data["market"] == "Pune APMC Updated"
    assert data["price_per_quintal"] == 2600.00
    assert data["price_date"] == "2026-11-11"


def test_update_price_not_found(client):
    payload = {
        "crop_name": "Wheat",
        "market": "Pune APMC",
        "price_per_quintal": 2500,
        "price_date": "2026-11-10",
    }
    response = client.put("/prices/999", json=payload)
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Price record not found"


def test_update_price_invalid_data(client):
    payload = {
        "crop_name": "Wheat",
        "market": "Pune APMC",
        "price_per_quintal": -100,
        "price_date": "2026-11-10",
    }
    response = client.put("/prices/1", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data


def test_delete_price_success(client):
    response = client.delete("/prices/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Price record deleted successfully"

    check_response = client.get("/prices/1")
    assert check_response.status_code == 404


def test_delete_price_not_found(client):
    response = client.delete("/prices/999")
    assert response.status_code == 404
    data = response.get_json()
    assert data["error"] == "Price record not found"


def test_get_latest_price_success(client):
    response = client.get("/prices/latest?crop=Wheat")
    assert response.status_code == 200
    data = response.get_json()
    assert data["crop_name"] == "Wheat"
    assert data["price_date"] == "2026-11-15"
    assert data["price_per_quintal"] == 2550.00


def test_get_latest_price_missing_crop(client):
    response = client.get("/prices/latest")
    assert response.status_code == 400
    data = response.get_json()
    assert "crop" in data["error"].lower()


def test_get_latest_price_no_data(client):
    response = client.get("/prices/latest?crop=Barley")
    assert response.status_code == 404
    data = response.get_json()
    assert "No price data found" in data["error"]


def test_get_average_price_success(client):
    response = client.get(
        "/prices/average?crop=Wheat&from=2026-11-01&to=2026-11-20"
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["crop"] == "Wheat"
    assert data["from"] == "2026-11-01"
    assert data["to"] == "2026-11-20"
    assert data["average_price_per_quintal"] == 2500.00
    assert data["record_count"] == 2


def test_get_average_price_missing_parameters(client):
    response = client.get("/prices/average?crop=Wheat&from=2026-11-01")
    assert response.status_code == 400
    assert "required" in response.get_json()["error"].lower()

    response = client.get("/prices/average?from=2026-11-01&to=2026-11-20")
    assert response.status_code == 400
    assert "crop" in response.get_json()["error"].lower()


def test_get_average_price_invalid_date_format(client):
    response = client.get(
        "/prices/average?crop=Wheat&from=01-11-2026&to=2026-11-20"
    )
    assert response.status_code == 400
    assert "YYYY-MM-DD" in response.get_json()["error"]


def test_get_average_price_invalid_range(client):
    response = client.get(
        "/prices/average?crop=Wheat&from=2026-11-25&to=2026-11-20"
    )
    assert response.status_code == 400
    assert "less than or equal" in response.get_json()["error"]


def test_get_average_price_no_records_found(client):
    response = client.get(
        "/prices/average?crop=Wheat&from=2025-01-01&to=2025-01-31"
    )
    assert response.status_code == 404
    assert "No price records found" in response.get_json()["error"]


def test_global_404_handler(client):
    response = client.get("/non-existent-endpoint")
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data


def test_global_500_handler(app):
    @app.route("/cause-error")
    def cause_error():
        raise RuntimeError("Something went wrong internally")

    app.config["PROPAGATE_EXCEPTIONS"] = False
    client = app.test_client()
    response = client.get("/cause-error")
    assert response.status_code == 500
    data = response.get_json()
    assert data == {"error": "Internal server error"}
