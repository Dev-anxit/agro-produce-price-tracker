from datetime import date, datetime, timezone
from typing import Optional
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


class PriceRecord(db.Model):
    __tablename__ = "price_records"

    id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True
    )
    crop_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    market: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    price_per_quintal: Mapped[float] = mapped_column(
        nullable=False
    )
    price_date: Mapped[date] = mapped_column(
        nullable=False, index=True
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        date_str = (
            self.price_date.strftime("%Y-%m-%d")
            if self.price_date
            else None
        )
        created_str = (
            self.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if self.created_at
            else None
        )
        return {
            "id": self.id,
            "crop_name": self.crop_name,
            "market": self.market,
            "price_per_quintal": round(self.price_per_quintal, 2),
            "price_date": date_str,
            "created_at": created_str,
        }
