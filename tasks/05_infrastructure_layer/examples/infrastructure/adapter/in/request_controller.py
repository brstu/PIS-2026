"""
RequestController: FastAPI REST endpoints

Входящий адаптер (Driving Adapter)
Предметная область: ПСО «Юго-Запад»
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Tuple
from application.command.create_request_command import CreateRequestCommand
from application.command.handlers.create_request_handler import CreateRequestHandler
from application.query.get_request_by_id_query import GetRequestByIdQuery
from application.query.handlers.get_request_by_id_handler import GetRequestByIdHandler
from application.query.dto.request_dto import RequestDto

router = APIRouter(prefix="/api/requests", tags=["Requests"])


# === Request DTOs (HTTP Layer) ===

class CreateRequestRequest(BaseModel):
    """HTTP DTO: Запрос на создание заявки"""
    coordinator_id: str = Field(..., example="COORD-1")
    zone_name: str = Field(..., example="North")
    zone_bounds: Tuple[float, float, float, float] = Field(
        ..., 
        example=[52.0, 52.5, 23.5, 24.0],
        description="lat_min, lat_max, lon_min, lon_max"
    )


class CreateRequestResponse(BaseModel):
    """HTTP DTO: Ответ с ID созданной заявки"""
    request_id: str = Field(..., example="REQ-2024-0001")


class AssignGroupRequest(BaseModel):
    """HTTP DTO: Назначить группу на заявку"""
    group_id: str = Field(..., example="G-01")


# === Endpoints ===

@router.post("", status_code=status.HTTP_201_CREATED, response_model=CreateRequestResponse)
def create_request(
    request_data: CreateRequestRequest,
    handler: CreateRequestHandler = Depends()
):
    """
    Создать новую заявку на поисково-спасательную операцию
    
    **Пример запроса:**
    ```json
    {
      "coordinator_id": "COORD-1",
      "zone_name": "North",
      "zone_bounds": [52.0, 52.5, 23.5, 24.0]
    }
    ```
    
    **Возвращает:**
    - ID созданной заявки (REQ-2024-NNNN)
    """
    command = CreateRequestCommand(
        coordinator_id=request_data.coordinator_id,
        zone_name=request_data.zone_name,
        zone_bounds=request_data.zone_bounds
    )
    
    request_id = handler.handle(command)
    
    return CreateRequestResponse(request_id=request_id)


@router.get("/{request_id}", response_model=RequestDto)
def get_request(
    request_id: str,
    handler: GetRequestByIdHandler = Depends()
):
    """
    Получить заявку по ID
    
    **Параметры:**
    - `request_id`: ID заявки (например, REQ-2024-0001)
    
    **Возвращает:**
    - Детали заявки (RequestDto)
    
    **Ошибки:**
    - 404: Заявка не найдена
    """
    query = GetRequestByIdQuery(request_id=request_id)
    
    try:
        dto = handler.handle(query)
        return dto
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{request_id}/assign-group", status_code=status.HTTP_200_OK)
def assign_group_to_request(
    request_id: str,
    data: AssignGroupRequest,
    # handler: AssignGroupHandler = Depends()  # TODO: implement
):
    """
    Назначить группу на заявку
    
    **Параметры:**
    - `request_id`: ID заявки
    - `group_id`: ID группы (G-NN)
    
    **Возвращает:**
    - 200 OK при успешном назначении
    
    **Ошибки:**
    - 404: Заявка или группа не найдены
    - 400: Группа не готова (недостаточно участников)
    """
    # TODO: Implement AssignGroupToRequestHandler
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.get("", response_model=List[RequestDto])
def list_active_requests(
    # handler: ListActiveRequestsHandler = Depends()  # TODO: implement
):
    """
    Получить список всех активных заявок
    
    **Возвращает:**
    - Массив RequestDto в статусе ACTIVE
    """
    # TODO: Implement ListActiveRequestsHandler
    raise HTTPException(status_code=501, detail="Not implemented yet")


@router.post("/{request_id}/activate", status_code=status.HTTP_200_OK)
def activate_request(
    request_id: str,
    # handler: ActivateRequestHandler = Depends()  # TODO: implement
):
    """
    Активировать заявку (начать операцию)
    
    **Требования:**
    - Заявка должна быть в статусе DRAFT
    - Группа должна быть назначена
    
    **Ошибки:**
    - 404: Заявка не найдена
    - 400: Нельзя активировать без группы
    """
    # TODO: Implement ActivateRequestHandler
    raise HTTPException(status_code=501, detail="Not implemented yet")
