import json
import logging
from datetime import datetime, timezone

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from core.helpers.conversation import ConversationIdManager
from core.helpers.user_object import UserObjectBuilder
from core.helpers.html_sanitizer import HTMLSanitizer
from core.serializers.chat_serializers import RequestPayloadSerializer, ResponsePayloadSerializer
from core.clients.n8n_client import (
    N8nClient,
    N8nClientError,
    N8nConnectionError,
    N8nTimeoutError,
    N8nInvalidResponseError,
)

logger = logging.getLogger(__name__)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        email = request.POST.get('email', '')
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            if remember_me:
                request.session.set_expiry(1209600)  # 2 semanas
            else:
                request.session.set_expiry(0)  # sesión de navegador
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Email o contraseña incorrectos'})

    return render(request, 'login.html')


@login_required
def home_view(request):
    user = request.user
    roles_list = list(user.roles.values_list('name', flat=True))
    context = {
        'user': user,
        'perfil': user.perfil,
        'roles': user.roles.all(),
        'ps_user_data': {
            'firstName': user.first_name or user.username,
            'username': user.username,
            'email': user.email,
            'perfil': user.perfil,
            'roles': roles_list,
        }
    }
    return render(request, 'home.html', context)


def logout_view(request):
    logout(request)
    return redirect('/login/')


@login_required
@require_http_methods(["POST"])
@csrf_protect
def chat_view(request):
    try:
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        query = body.get('query', '').strip()
        agent_type = body.get('agentType', 'auto')

        if not query:
            return JsonResponse({'error': 'Query is required'}, status=400)

        conversation_id = ConversationIdManager.get_or_create(request.session)
        user_object = UserObjectBuilder.build(request.user)

        # 8.4: Construir Request_Payload
        request_payload = {
            'conversationId': conversation_id,
            'query': query,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'user': user_object,
            'agentType': agent_type,
        }

        # 8.4: Validar Request_Payload con serializer
        serializer = RequestPayloadSerializer(data=request_payload)
        if not serializer.is_valid():
            logger.error("Payload validation failed: %s", serializer.errors)
            return JsonResponse(
                {'error': 'Validation failed', 'details': serializer.errors},
                status=400
            )

        validated_payload = serializer.validated_data

        # 8.5: Enviar a n8n con N8nClient
        try:
            client = N8nClient()
            response_data = client.send(validated_payload)
        except N8nTimeoutError as e:
            logger.error(
                "N8n request timed out",
                extra={
                    'user_id': request.user.id,
                    'conversation_id': conversation_id,
                    'query': query[:100],
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                },
            )
            return JsonResponse(
                {'error': 'El sistema tardó demasiado en responder. Por favor, intentá de nuevo.'},
                status=504,
            )
        except N8nInvalidResponseError as e:
            logger.error(
                "N8n invalid response",
                extra={
                    'user_id': request.user.id,
                    'conversation_id': conversation_id,
                    'query': query[:100],
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                },
            )
            return JsonResponse(
                {'error': f'Error procesando respuesta de n8n: {str(e)}'},
                status=502,
            )
        except (ValueError, N8nConnectionError) as e:
            logger.error(
                "N8n unavailable",
                extra={
                    'user_id': request.user.id,
                    'conversation_id': conversation_id,
                    'query': query[:100],
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                },
            )
            return JsonResponse(
                {'error': f'Error conectando con n8n: {str(e)}'},
                status=503,
            )
        except N8nClientError as e:
            logger.error(
                "N8n client error",
                extra={
                    'user_id': request.user.id,
                    'conversation_id': conversation_id,
                    'query': query[:100],
                    'error_type': type(e).__name__,
                    'error_message': str(e),
                },
            )
            return JsonResponse(
                {'error': f'Error conectando con n8n: {str(e)}'},
                status=503,
            )

        # 8.6: Sanitizar HTML (defense in depth — zero trust external systems)
        if 'output' in response_data:
            response_data['output'] = HTMLSanitizer.sanitize(response_data['output'])

        # 8.6: Validar Response_Payload
        response_serializer = ResponsePayloadSerializer(data=response_data)
        if not response_serializer.is_valid():
            logger.error("Response validation failed: %s", response_serializer.errors)
            return JsonResponse(
                {'error': 'Invalid response from orchestrator'},
                status=502,
            )

        logger.info(
            "Chat request processed successfully",
            extra={
                'user_id': request.user.id,
                'conversation_id': conversation_id,
                'query': query[:100],
                'agent_used': response_serializer.validated_data.get('metadata', {}).get('agent_used', 'unknown'),
            },
        )
        return JsonResponse(response_serializer.validated_data, status=200)

    except Exception as e:
        logger.exception("Unexpected error in chat_view")
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)
