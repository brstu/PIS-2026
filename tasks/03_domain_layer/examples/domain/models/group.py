"""
Domain Layer: Group (Поисковая группа)

Entity: Группа волонтёров для выполнения поисковой операции
Предметная область: ПСО «Юго-Запад»
"""
from typing import List


class Group:
    """
    Entity: Поисковая группа волонтёров
    
    Invariants:
        - Группа должна содержать от 3 до 5 участников
        - Нельзя изменить состав группы в статусе READY или DEPLOYED
        - Лидер группы обязателен
        - Участники уникальны (нет дублей)
    """
    
    MIN_MEMBERS = 3
    MAX_MEMBERS = 5
    
    def __init__(self, group_id: str, leader_id: str):
        """
        Создать новую группу
        
        Args:
            group_id: Идентификатор группы (G-01, G-02)
            leader_id: ID лидера группы
        """
        if not group_id:
            raise ValueError("Group ID cannot be empty")
        if not leader_id:
            raise ValueError("Leader ID cannot be empty")
        
        self._id = group_id
        self._leader_id = leader_id
        self._members: List[str] = []  # IDs волонтёров
        self._status = "FORMING"  # FORMING → READY → DEPLOYED
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def leader_id(self) -> str:
        return self._leader_id
    
    @property
    def members(self) -> List[str]:
        """Копия списка (защита от модификации снаружи)"""
        return self._members.copy()
    
    @property
    def member_count(self) -> int:
        return len(self._members)
    
    @property
    def status(self) -> str:
        return self._status
    
    def add_member(self, volunteer_id: str) -> None:
        """
        Добавить участника в группу
        
        Args:
            volunteer_id: ID волонтёра
        
        Raises:
            ValueError: если нарушен инвариант
        """
        # Инвариант: нельзя изменить готовую группу
        if self._status != "FORMING":
            raise ValueError(
                f"Cannot modify group in status {self._status}"
            )
        
        # Инвариант: максимум участников
        if len(self._members) >= self.MAX_MEMBERS:
            raise ValueError(
                f"Group already has maximum members ({self.MAX_MEMBERS})"
            )
        
        # Инвариант: уникальность участников
        if volunteer_id in self._members:
            raise ValueError(
                f"Volunteer {volunteer_id} is already in the group"
            )
        
        self._members.append(volunteer_id)
    
    def remove_member(self, volunteer_id: str) -> None:
        """
        Удалить участника из группы
        
        Args:
            volunteer_id: ID волонтёра
        
        Raises:
            ValueError: если нарушен инвариант
        """
        # Инвариант: нельзя изменить готовую группу
        if self._status != "FORMING":
            raise ValueError(
                f"Cannot modify group in status {self._status}"
            )
        
        if volunteer_id not in self._members:
            raise ValueError(
                f"Volunteer {volunteer_id} is not in the group"
            )
        
        self._members.remove(volunteer_id)
    
    def mark_ready(self) -> None:
        """
        Пометить группу как готовую к выходу
        
        Raises:
            ValueError: если недостаточно участников
        """
        # Инвариант: минимум участников
        if len(self._members) < self.MIN_MEMBERS:
            raise ValueError(
                f"Group must have at least {self.MIN_MEMBERS} members, "
                f"current: {len(self._members)}"
            )
        
        if self._status != "FORMING":
            raise ValueError(
                f"Cannot mark group as ready from status {self._status}"
            )
        
        self._status = "READY"
    
    def deploy(self) -> None:
        """
        Отправить группу на операцию
        
        Raises:
            ValueError: если группа не готова
        """
        if self._status != "READY":
            raise ValueError(
                f"Cannot deploy group in status {self._status}"
            )
        
        self._status = "DEPLOYED"
    
    def is_ready(self) -> bool:
        """Проверка готовности группы"""
        return (
            len(self._members) >= self.MIN_MEMBERS 
            and self._status == "READY"
        )
    
    def __eq__(self, other):
        """Равенство Entity по ID"""
        if not isinstance(other, Group):
            return False
        return self._id == other._id
    
    def __hash__(self):
        """Хэш по ID для использования в set/dict"""
        return hash(self._id)
    
    def __repr__(self):
        return (
            f"Group(id={self._id}, leader={self._leader_id}, "
            f"members={len(self._members)}, status={self._status})"
        )
