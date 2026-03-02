"""
gRPC Client: Request Service

Предметная область: ПСО «Юго-Запад»
"""
import grpc
import sys
import os

# Добавление generated/ в sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from generated import request_service_pb2, request_service_pb2_grpc


def create_request(stub):
    """
    Unary RPC: Создать заявку

    Args:
        stub: RequestServiceStub

    Returns:
        request_id: str
    """
    print("\n=== CreateRequest ===")

    zone = request_service_pb2.Zone(
        name="North",
        lat_min=52.0,
        lat_max=52.5,
        lon_min=23.5,
        lon_max=24.0
    )

    request = request_service_pb2.CreateRequestRequest(
        coordinator_id="COORD-1",
        zone=zone
    )

    response = stub.CreateRequest(request)

    if response.status == "SUCCESS":
        print(f"✅ Request created: {response.request_id}")
        return response.request_id
    else:
        print(f"❌ Error: {response.error_message}")
        return None


def get_request(stub, request_id):
    """
    Unary RPC: Получить заявку по ID

    Args:
        stub: RequestServiceStub
        request_id: str
    """
    print(f"\n=== GetRequest({request_id}) ===")

    request = request_service_pb2.GetRequestRequest(request_id=request_id)

    try:
        response = stub.GetRequest(request)

        if response.found:
            req = response.request
            print(f"📦 Request ID: {req.request_id}")
            print(f"   Coordinator: {req.coordinator_id}")
            print(f"   Zone: {req.zone.name} ({req.zone.lat_min}, {req.zone.lat_max})")
            print(f"   Status: {req.status}")
            print(f"   Created: {req.created_at}")
        else:
            print("❌ Request not found")

    except grpc.RpcError as e:
        print(f"❌ RPC Error: {e.code()} - {e.details()}")


def list_requests(stub, status_filter=None):
    """
    Unary RPC: Список заявок

    Args:
        stub: RequestServiceStub
        status_filter: str ("ACTIVE", "COMPLETED", None)
    """
    print(f"\n=== ListRequests(filter={status_filter or 'ALL'}) ===")

    request = request_service_pb2.ListRequestsRequest(
        status_filter=status_filter or "",
        limit=10
    )

    response = stub.ListRequests(request)

    print(f"📋 Found {response.total_count} requests:")
    for req in response.requests:
        print(f"  → {req.request_id} ({req.status}) - {req.zone.name}")


def activate_request(stub, request_id):
    """
    Unary RPC: Активировать заявку

    Args:
        stub: RequestServiceStub
        request_id: str
    """
    print(f"\n=== ActivateRequest({request_id}) ===")

    request = request_service_pb2.ActivateRequestRequest(request_id=request_id)

    response = stub.ActivateRequest(request)

    if response.success:
        print(f"🚀 Request activated: {request_id}")
    else:
        print(f"❌ Error: {response.error_message}")


def stream_active_requests(stub):
    """
    Server-side Streaming: Стрим активных заявок

    Args:
        stub: RequestServiceStub
    """
    print("\n=== StreamActiveRequests ===")

    request = request_service_pb2.StreamActiveRequestsRequest()

    print("📡 Streaming active requests (press Ctrl+C to stop)...")

    try:
        for req in stub.StreamActiveRequests(request):
            print(f"  → {req.request_id} ({req.status}) - Zone: {req.zone.name}")

    except KeyboardInterrupt:
        print("\n⏹️  Stopped streaming")

    except grpc.RpcError as e:
        print(f"❌ RPC Error: {e.code()} - {e.details()}")


def run():
    """Основная логика клиента"""
    # Подключение к серверу
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = request_service_pb2_grpc.RequestServiceStub(channel)

        # 1. Создание заявки
        request_id = create_request(stub)

        if request_id:
            # 2. Получение заявки
            get_request(stub, request_id)

            # 3. Активация заявки
            activate_request(stub, request_id)

        # 4. Список всех заявок
        list_requests(stub)

        # 5. Список только активных заявок
        list_requests(stub, status_filter="ACTIVE")

        # 6. Стрим активных заявок (раскомментировать для тестирования)
        # stream_active_requests(stub)


if __name__ == '__main__':
    run()
