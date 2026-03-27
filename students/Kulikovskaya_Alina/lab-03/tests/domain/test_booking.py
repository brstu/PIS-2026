import pytest
from datetime import date, time, datetime, timedelta

from src.domain.models.booking import Booking
from src.domain.models.value_objects.slot import Slot
from src.domain.models.value_objects.money import Money
from src.domain.models.value_objects.booking_status import BookingStatus
from src.domain.specifications.cancellation_policy import CancellationPolicy
from src.domain.factories.booking_factory import BookingFactory
from src.domain.services.pricing_service import PricingService
from src.domain.models.value_objects.court_type import CourtType


class TestBooking:
    """Тесты агрегата Booking."""
    
    def test_create_booking(self):
        """Создание бронирования с валидными данными."""
        slot = Slot(
            court_id="court-001",
            date=date(2025, 3, 15),
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        
        booking = Booking(
            user_id="user-123",
            court_id="court-001",
            slot=slot,
            total_amount=Money(35.0)
        )
        
        assert booking.status == BookingStatus.PENDING_PAYMENT
        assert booking.is_pending_payment()
        assert booking.hours_until_start() > 0
    
    def test_confirm_booking(self):
        """Подтверждение бронирования."""
        slot = Slot(
            court_id="court-001",
            date=date(2025, 3, 15),
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        
        booking = Booking(
            user_id="user-123",
            court_id="court-001",
            slot=slot,
            total_amount=Money(35.0)
        )
        
        booking.confirm(payment_id="PAY-123")
        
        assert booking.status == BookingStatus.CONFIRMED
        assert booking.is_confirmed()
        assert booking.confirmed_at is not None
        assert len(booking.get_events()) == 2  # Created + Confirmed
    
    def test_cannot_cancel_confirmed_without_force(self):
        """Нельзя отменить подтверждённое бронирование без force."""
        slot = Slot(
            court_id="court-001",
            date=date(2025, 3, 15),
            start_time=time(18, 0),
            end_time=time(19, 0)
        )
        
        booking = Booking(
            user_id="user-123",
            court_id="court-001",
            slot=slot,
            total_amount=Money(35.0)
        )
        booking.confirm()
        
        # Проверка политики отмены
        policy = CancellationPolicy()
        result = policy.can_cancel(booking, now=datetime(2025, 3, 15, 10, 0))
        
        assert not result.can_cancel  # Меньше 24 часов (с 10:00 до 18:00 = 8 часов)


class TestPricingService:
    """Тесты сервиса ценообразования."""
    
    def test_base_price(self):
        """Базовая стоимость без наценок."""
        service = PricingService()
        
        price = service.calculate_price(
            CourtType.BADMINTON,
            date(2025, 3, 15),  # Суббота
            time(10, 0)         # Утро (не пик)
        )
        
        assert price.amount == 25.0  # Базовая цена бадминтона
    
    def test_peak_hour_surcharge(self):
        """Наценка в пиковые часы."""
        service = PricingService()
        
        # Будний день, 19:00 (пик)
        price = service.calculate_price(
            CourtType.BADMINTON,
            date(2025, 3, 12),  # Среда
            time(19, 0)
        )
        
        # 25 + 20% = 30
        assert price.amount == 30.0
    
    def test_weekend_is_always_peak(self):
        """Выходные всегда пиковые."""
        service = PricingService()
        
        price = service.calculate_price(
            CourtType.VOLLEYBALL,
            date(2025, 3, 15),  # Суббота, 10 утра
            time(10, 0)
        )
        
        # 35 + 20% = 42
        assert price.amount == 42.0


class TestBookingFactory:
    """Тесты фабрики бронирований."""
    
    def test_create_online_booking(self):
        """Создание online-бронирования."""
        factory = BookingFactory()
        
        booking = factory.create_online_booking(
            user_id="user-123",
            court_id="court-bd-01",
            slot_date=date(2025, 3, 15),
            start_time=time(18, 0),
            court_type=CourtType.BADMINTON
        )
        
        assert booking.status == BookingStatus.PENDING_PAYMENT
        assert booking.total_amount is not None
        assert not booking.created_by_admin
    
    def test_create_phone_booking(self):
        """Создание бронирования по телефону."""
        factory = BookingFactory()
        
        booking = factory.create_phone_booking(
            admin_id="admin-001",
            court_id="court-bd-01",
            slot_date=date(2025, 3, 15),
            start_time=time(18, 0),
            court_type=CourtType.BADMINTON,
            customer_name="Иван Петров",
            customer_phone="+375291234567"
        )
        
        assert booking.status == BookingStatus.CONFIRMED  # Сразу подтверждено!
        assert booking.created_by_admin
        assert "Иван Петров" in booking.notes
        assert "+375291234567" in booking.notes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])