import os
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from sqlalchemy import func

from models import PriceRecord, db


def parse_date(date_str):
    if not isinstance(date_str, str):
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


def validate_price_payload(data):
    if not isinstance(data, dict):
        return None, "Request payload must be a valid JSON object"

    required_fields = [
        "crop_name",
        "market",
        "price_per_quintal",
        "price_date",
    ]
    for field in required_fields:
        if field not in data or data[field] is None:
            return None, f"Missing required field: '{field}'"

    crop_name = data.get("crop_name")
    if not isinstance(crop_name, str) or not crop_name.strip():
        return None, "Field 'crop_name' must be a non-empty string"

    market = data.get("market")
    if not isinstance(market, str) or not market.strip():
        return None, "Field 'market' must be a non-empty string"

    price = data.get("price_per_quintal")
    if isinstance(price, bool) or not isinstance(price, (int, float)):
        return None, "Field 'price_per_quintal' must be a valid number"
    if price <= 0:
        return None, "Field 'price_per_quintal' must be greater than 0"

    date_obj = parse_date(data.get("price_date"))
    if not date_obj:
        return None, "Field 'price_date' must be in YYYY-MM-DD format"

    cleaned = {
        "crop_name": crop_name.strip(),
        "market": market.strip(),
        "price_per_quintal": float(price),
        "price_date": date_obj,
    }
    return cleaned, None


def create_app(test_config=None):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///agro_prices.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.errorhandler(400)
    def bad_request(error):
        description = getattr(error, "description", "Bad request")
        return jsonify({"error": description}), 400

    @app.errorhandler(404)
    def not_found(error):
        description = getattr(error, "description", "Resource not found")
        if "The requested URL was not found" in str(description):
            description = "Resource not found"
        return jsonify({"error": description}), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({"error": "Internal server error"}), 500

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/prices", methods=["GET"])
    def get_prices():
        crop_filter = request.args.get("crop")
        market_filter = request.args.get("market")

        query = PriceRecord.query

        if crop_filter and crop_filter.strip():
            crop_clean = crop_filter.strip().lower()
            query = query.filter(
                func.lower(PriceRecord.crop_name) == crop_clean
            )

        if market_filter and market_filter.strip():
            market_clean = market_filter.strip().lower()
            query = query.filter(
                func.lower(PriceRecord.market) == market_clean
            )

        records = query.order_by(
            PriceRecord.price_date.desc(), PriceRecord.id.desc()
        ).all()
        return jsonify([record.to_dict() for record in records]), 200

    @app.route("/prices/latest", methods=["GET"])
    def get_latest_price():
        crop = request.args.get("crop")
        if not crop or not crop.strip():
            return (
                jsonify({"error": "Query parameter 'crop' is required"}),
                400,
            )

        record = (
            PriceRecord.query.filter(
                func.lower(PriceRecord.crop_name) == crop.strip().lower()
            )
            .order_by(PriceRecord.price_date.desc(), PriceRecord.id.desc())
            .first()
        )

        if not record:
            return (
                jsonify(
                    {"error": f"No price data found for crop '{crop.strip()}'"}
                ),
                404,
            )

        return jsonify(record.to_dict()), 200

    @app.route("/prices/average", methods=["GET"])
    def get_average_price():
        crop = request.args.get("crop")
        from_str = request.args.get("from")
        to_str = request.args.get("to")

        if not crop or not crop.strip():
            return (
                jsonify({"error": "Query parameter 'crop' is required"}),
                400,
            )

        if not from_str or not to_str:
            return (
                jsonify(
                    {"error": "Query parameters 'from' and 'to' are required"}
                ),
                400,
            )

        from_date = parse_date(from_str)
        to_date = parse_date(to_str)

        if not from_date or not to_date:
            return (
                jsonify(
                    {"error": "Dates must be valid in YYYY-MM-DD format"}
                ),
                400,
            )

        if from_date > to_date:
            err_msg = "'from' date must be less than or equal to 'to' date"
            return jsonify({"error": err_msg}), 400

        records = (
            PriceRecord.query.filter(
                func.lower(PriceRecord.crop_name) == crop.strip().lower(),
                PriceRecord.price_date >= from_date,
                PriceRecord.price_date <= to_date,
            )
            .order_by(PriceRecord.price_date.asc())
            .all()
        )

        if not records:
            msg = (
                f"No price records found for crop '{crop.strip()}' "
                f"between {from_str} and {to_str}"
            )
            return jsonify({"error": msg}), 404

        avg_price = sum(r.price_per_quintal for r in records) / len(records)

        return (
            jsonify(
                {
                    "crop": crop.strip(),
                    "from": from_str,
                    "to": to_str,
                    "average_price_per_quintal": round(avg_price, 2),
                    "record_count": len(records),
                }
            ),
            200,
        )

    @app.route("/prices/<int:record_id>", methods=["GET"])
    def get_price_by_id(record_id):
        record = db.session.get(PriceRecord, record_id)
        if not record:
            return jsonify({"error": "Price record not found"}), 404
        return jsonify(record.to_dict()), 200

    @app.route("/prices", methods=["POST"])
    def create_price():
        if not request.is_json:
            return jsonify({"error": "Request body must be JSON"}), 400

        data = request.get_json(silent=True)
        cleaned_data, error_msg = validate_price_payload(data)
        if error_msg:
            return jsonify({"error": error_msg}), 400

        new_record = PriceRecord(
            crop_name=cleaned_data["crop_name"],
            market=cleaned_data["market"],
            price_per_quintal=cleaned_data["price_per_quintal"],
            price_date=cleaned_data["price_date"],
        )
        db.session.add(new_record)
        db.session.commit()

        return jsonify(new_record.to_dict()), 201

    @app.route("/prices/<int:record_id>", methods=["PUT"])
    def update_price(record_id):
        record = db.session.get(PriceRecord, record_id)
        if not record:
            return jsonify({"error": "Price record not found"}), 404

        if not request.is_json:
            return jsonify({"error": "Request body must be JSON"}), 400

        data = request.get_json(silent=True)
        cleaned_data, error_msg = validate_price_payload(data)
        if error_msg:
            return jsonify({"error": error_msg}), 400

        record.crop_name = cleaned_data["crop_name"]
        record.market = cleaned_data["market"]
        record.price_per_quintal = cleaned_data["price_per_quintal"]
        record.price_date = cleaned_data["price_date"]
        db.session.commit()

        return jsonify(record.to_dict()), 200

    @app.route("/prices/<int:record_id>", methods=["DELETE"])
    def delete_price(record_id):
        record = db.session.get(PriceRecord, record_id)
        if not record:
            return jsonify({"error": "Price record not found"}), 404

        db.session.delete(record)
        db.session.commit()
        return jsonify({"message": "Price record deleted successfully"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
