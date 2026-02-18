"""
Circuit Breaker: Защита от каскадных сбоев

Предметная область: ПСО «Юго-Запад»
"""
from pybreaker import CircuitBreaker, CircuitBreakerError
import requests
from typing import Optional, Dict, Any


class GroupServiceClient:
    """
    HTTP Client для Group Service с Circuit Breaker
    
    Паттерн: Circuit Breaker (Michael Nygard)
    Ответственность: Предотвращение каскадных сбоев при вызове Group Service
    
    Состояния Circuit Breaker:
    - CLOSED: Нормальная работа, запросы проходят
    - OPEN: Сервис недоступен, запросы блокируются (fail fast)
    - HALF_OPEN: Проверка восстановления сервиса
    """
    
    def __init__(self, base_url: str = "http://group-service:8000"):
        self.base_url = base_url
        
        # Circuit Breaker configuration
        self.breaker = CircuitBreaker(
            fail_max=5,              # Открыть после 5 неудач
            timeout_duration=60,     # Ждать 60 секунд перед HALF_OPEN
            expected_exception=requests.RequestException
        )
    
    def get_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить группу по ID (с Circuit Breaker)
        
        Raises:
            CircuitBreakerError: Если circuit открыт (сервис недоступен)
        """
        try:
            return self._get_group_protected(group_id)
        except CircuitBreakerError:
            print(f"⚠️ Circuit breaker is OPEN for Group Service")
            return None
    
    @CircuitBreaker(fail_max=5, timeout_duration=60)
    def _get_group_protected(self, group_id: str) -> Dict[str, Any]:
        """Защищённый вызов с Circuit Breaker"""
        response = requests.get(
            f"{self.base_url}/groups/{group_id}",
            timeout=5
        )
        response.raise_for_status()
        return response.json()
    
    def find_ready_group(self) -> Optional[Dict[str, Any]]:
        """
        Найти готовую группу (с fallback)
        
        Fallback: Если Group Service недоступен, вернуть None
        """
        try:
            return self._find_ready_group_protected()
        except (CircuitBreakerError, requests.RequestException) as e:
            print(f"⚠️ Failed to find ready group: {e}")
            # Fallback: использовать закешированные данные или вернуть None
            return self._get_cached_group()
    
    @CircuitBreaker(fail_max=5, timeout_duration=60)
    def _find_ready_group_protected(self) -> Dict[str, Any]:
        """Защищённый вызов"""
        response = requests.get(
            f"{self.base_url}/groups?status=READY",
            timeout=5
        )
        response.raise_for_status()
        groups = response.json()
        return groups[0] if groups else None
    
    def _get_cached_group(self) -> Optional[Dict[str, Any]]:
        """Fallback: кешированные данные (stub)"""
        # В реальности: Redis, Memcached
        return None


# === Пример использования ===

if __name__ == "__main__":
    client = GroupServiceClient(base_url="http://localhost:8002")
    
    # Попытка получить группу
    for i in range(10):
        group = client.get_group("G-01")
        if group:
            print(f"✅ Group found: {group['group_id']}")
        else:
            print(f"❌ Failed to get group (attempt {i+1})")
        
        import time
        time.sleep(1)
