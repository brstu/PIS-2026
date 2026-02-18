"""
Domain Layer: Group (Группа)

Entity для управления поисковыми группами.

Business Rules:
- ID формата: G-NN
- Минимум 3 участника, максимум 5
- Один участник назначается лидером
"""
from typing import List


class Group:
    """Entity: Поисковая группа"""
    
    def __init__(self, group_id: str):
        """
        Создать группу
        
        Args:
            group_id: ID группы (например, "G-01")
        """
        self._id = group_id
        self._member_ids: List[str] = []
        self._leader_id: str | None = None
    
    def add_member(self, member_id: str) -> None:
        """
        Добавить участника в группу
        
        Args:
            member_id: ID участника
            
        Raises:
            ValueError: если группа уже полная или участник уже добавлен
        """
        if len(self._member_ids) >= 5:
            raise ValueError(
                "Группа уже полная (максимум 5 участников)"
            )
        
        if member_id in self._member_ids:
            raise ValueError(
                f"Участник {member_id} уже в группе"
            )
        
        self._member_ids.append(member_id)
        
        # Первый участник автоматически становится лидером
        if len(self._member_ids) == 1:
            self._leader_id = member_id
    
    def assign_leader(self, member_id: str) -> None:
        """
        Назначить лидера группы
        
        Args:
            member_id: ID участника (должен быть в группе)
            
        Raises:
            ValueError: если участника нет в группе
        """
        if member_id not in self._member_ids:
            raise ValueError(
                f"Участник {member_id} не найден в группе"
            )
        self._leader_id = member_id
    
    def remove_member(self, member_id: str) -> None:
        """
        Удалить участника из группы
        
        Args:
            member_id: ID участника
            
        Raises:
            ValueError: если это лидер группы
        """
        if member_id == self._leader_id:
            raise ValueError(
                "Нельзя удалить лидера группы. Сначала назначьте другого лидера."
            )
        
        self._member_ids.remove(member_id)
    
    @property
    def is_ready(self) -> bool:
        """
        Проверка готовности группы
        
        Returns:
            True если группа имеет 3-5 участников и назначен лидер
        """
        return (
            3 <= len(self._member_ids) <= 5
            and self._leader_id is not None
        )
    
    @property
    def id(self) -> str:
        return self._id
    
    @property
    def member_ids(self) -> List[str]:
        """Возвращает копию списка участников"""
        return self._member_ids.copy()
    
    @property
    def member_count(self) -> int:
        return len(self._member_ids)
    
    @property
    def leader_id(self) -> str | None:
        return self._leader_id
    
    def __str__(self) -> str:
        return (
            f"Group(id={self._id}, members={self.member_count}, "
            f"leader={self._leader_id}, ready={self.is_ready})"
        )
    
    def __repr__(self) -> str:
        return self.__str__()
