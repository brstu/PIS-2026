"""
gRPC Server: Request Service

Предметная область: ПСО «Юго-Запад»
"""
import grpc
from concurrent import futures
import time
import sys
import os

# Добавление generated/ в sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from generated import request_service_pb2, request_service_pb2_grpc


class RequestServiceServicer(request_service_pb2_grpc.RequestServiceServicer):
    """
    gRPC Server: Request Service
    
    Реализует все RPC методы из request_service.proto
    """
    
    def __init__(self):
        # In-memory storage (в реальности: PostgreSQL через Repository)
        self.requests = {}
        self.counter = 1
        
        # Предзаполнение данных для демонстрации
        self._seed_data()
    
    def _seed_data(self):
        """Создание тестовых заявок"""
        test_requests = [
            ("COORD-1", "North", 52.0, 52.5, 23.5, 24.0, "ACTIVE"),
            ("COORD-2", "South", 51.5, 52.0, 23.5, 24.0, "ACTIVE"),
            ("COORD-3", "East", 52.0, 52.5, 24.0, 24.5, "COMPLETED"),
        ]
        
        for coord_id, zone_name, lat_min, lat_max, lon_min, lon_max, status in test_requests:
            request_id = f"REQ-2024-{self.counter:04d}"
            
            zone = request_service_pb2.Zone(
                name=zone_name,
                lat_min=lat_min,
                lat_max=lat_max,
                lon_min=lon_min,
                lon_max=lon_max
            )
            
            req = request_service_pb2.Request(
                request_id=request_id,
                coordinator_id=coord_id,
                zone=zone,
                status=status,
                created_at=int(time.time()) - 3600,
                activated_at=int(time.time()) - 1800 if status == "ACTIVE" else 0,
                completed_at=int(time.time()) if status == "COMPLETED" else 0
            )
            
            self.requests[request_id] = req
            self.counter += 1
    
    def CreateRequest(self, request, context):
        """
        Unary RPC: Создать заявку
        
        Args:
            request: CreateRequestRequest
            context: grpc.ServicerContext
        
        Returns:
            CreateRequestResponse
        """
        request_id = f"REQ-2024-{self.counter:04d}"
        self.counter += 1
        
        # Создание Request
        new_request = request_service_pb2.Request(
            request_id=request_id,
            coordinator_id=request.coordinator_id,
            zone=request.zone,
            status="DRAFT",
            created_at=int(time.time())
        )
        
        self.requests[request_id] = new_request
        
        print(f"✅ Request created: {request_id}")
        
        return request_service_pb2.CreateRequestResponse(
            request_id=request_id,
            status="SUCCESS"
        )
    
    def GetRequest(self, request, context):
        """
        Unary RPC: Получить заявку по ID
        
        Args:
            request: GetRequestRequest
            context: grpc.ServicerContext
        
        Returns:
            GetRequestResponse
        """
        req = self.requests.get(request.request_id)
        
        if req:
            print(f"📦 Request found: {request.request_id}")
            return request_service_pb2.GetRequestResponse(
                request=req,
                found=True
            )
        else:
            print(f"❌ Request not found: {request.request_id}")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Request {request.request_id} not found")
            return request_service_pb2.GetRequestResponse(found=False)
    
    def ListRequests(self, request, context):
        """
        Unary RPC: Список заявок
        
        Args:
            request: ListRequestsRequest
            context: grpc.ServicerContext
        
        Returns:
            ListRequestsResponse
        """
        # Фильтрация по статусу
        filtered = [
            req for req in self.requests.values()
            if not request.status_filter or req.status == request.status_filter
        ]
        
        # Применение лимита
        limit = request.limit if request.limit > 0 else 100
        results = filtered[:limit]
        
        print(f"📋 Listing {len(results)} requests (filter: {request.status_filter or 'ALL'})")
        
        return request_service_pb2.ListRequestsResponse(
            requests=results,
            total_count=len(filtered)
        )
    
    def ActivateRequest(self, request, context):
        """
        Unary RPC: Активировать заявку
        
        Args:
            request: ActivateRequestRequest
            context: grpc.ServicerContext
        
        Returns:
            ActivateRequestResponse
        """
        req = self.requests.get(request.request_id)
        
        if not req:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return request_service_pb2.ActivateRequestResponse(
                success=False,
                error_message="Request not found"
            )
        
        if req.status != "DRAFT":
            return request_service_pb2.ActivateRequestResponse(
                success=False,
                error_message=f"Cannot activate request with status {req.status}"
            )
        
        # Изменение статуса
        req.status = "ACTIVE"
        req.activated_at = int(time.time())
        
        print(f"🚀 Request activated: {request.request_id}")
        
        return request_service_pb2.ActivateRequestResponse(success=True)
    
    def StreamActiveRequests(self, request, context):
        """
        Server-side Streaming: Стрим активных заявок
        
        Отправляет активные заявки каждые 2 секунды (real-time мониторинг)
        
        Args:
            request: StreamActiveRequestsRequest
            context: grpc.ServicerContext
        
        Yields:
            Request (stream)
        """
        print("📡 Starting stream of active requests...")
        
        try:
            while not context.is_active():
                # Поиск активных заявок
                active_requests = [
                    req for req in self.requests.values()
                    if req.status == "ACTIVE"
                ]
                
                # Отправка каждой заявки
                for req in active_requests:
                    yield req
                    time.sleep(0.5)
                
                # Пауза перед следующей итерацией
                time.sleep(2)
        
        except Exception as e:
            print(f"❌ Stream error: {e}")


def serve():
    """Запуск gRPC сервера"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    request_service_pb2_grpc.add_RequestServiceServicer_to_server(
        RequestServiceServicer(), server
    )
    
    server.add_insecure_port('[::]:50051')
    server.start()
    
    print("🚀 gRPC Server started on port 50051")
    print("📡 Listening for requests...")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("\n⏹️  Stopping server...")
        server.stop(0)


if __name__ == '__main__':
    serve()
