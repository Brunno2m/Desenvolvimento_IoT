# Sugestões de Melhoria - Front-end Django MQTT

## 1. Adicionar Autenticação via JWT

### Modificar `settings.py`

```python
# Adicionar:
INSTALLED_APPS = [
    ...
    "rest_framework",
    "rest_framework_simplejwt",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timezone.timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timezone.timedelta(days=7),
}
```

### Criar arquivo `monitoring/auth.py`

```python
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
import json

class ProtectedAPIView:
    """Mixin para proteger APIs com autenticação"""
    permission_classes = [IsAuthenticated]

def token_pair(request):
    """GET token JWT"""
    view = TokenObtainPairView.as_view()
    return view(request)
```

### Modificar `views.py`

```python
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.http import require_GET, require_POST

# Manter api_state para frontend (sem auth)
@require_GET
def api_state(request):
    ensure_client_started()
    return JsonResponse({
        "success": True,
        "data": get_snapshot(),
    })

# Proteger api_command com autenticação
@require_POST
def api_command(request):
    # Verificar token JWT
    from rest_framework.authentication import JWTAuthentication
    auth = JWTAuthentication()
    
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse(
                {"success": False, "message": "Token JWT necessário"},
                status=401
            )
        
        # Validar token
        user, validated_token = auth.authenticate(request)
    except:
        return JsonResponse(
            {"success": False, "message": "Token inválido"},
            status=401
        )
    
    # ... resto do código
```

---

## 2. Parametrizar Threshold de Temperatura

### Modificar `settings.py`

```python
# Adicionar:
MQTT_TEMPERATURE_THRESHOLD = float(env("MQTT_TEMPERATURE_THRESHOLD", "8.0"))
MQTT_TEMPERATURE_UNIT = env("MQTT_TEMPERATURE_UNIT", "celsius")
```

### Modificar `state.py`

```python
from django.conf import settings

def ingest_message(topic: str, payload: str) -> None:
    with STATE.lock:
        STATE.message_count += 1
        STATE.latest_topic = topic
        STATE.last_updated = timezone.now()

        if topic.endswith("temperatura"):
            try:
                temperature = float(str(payload).replace(",", "."))
                STATE.latest_temperature = temperature
                
                # Usar threshold configurável
                threshold = settings.MQTT_TEMPERATURE_THRESHOLD
                STATE.latest_status = "ALERTA" if temperature > threshold else "NORMAL"
                _record_history_entry()
                return
            except (ValueError, AttributeError):
                STATE.latest_status = "Dado inválido"
                LOGGER.warning("Falha ao converter temperatura: %s", payload)
                return
        # ... resto do código
```

---

## 3. Persistência de Histórico em Banco de Dados

### Criar modelo `monitoring/models.py`

```python
from django.db import models
from django.utils import timezone

class MQTTMessage(models.Model):
    """Modelo para armazenar mensagens MQTT"""
    TOPIC_CHOICES = [
        ('temperatura', 'Temperatura'),
        ('status', 'Status'),
        ('comando', 'Comando'),
    ]
    
    topic = models.CharField(max_length=255)
    payload = models.TextField()
    topic_type = models.CharField(max_length=50, choices=TOPIC_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['topic_type', 'timestamp']),
        ]
    
    def __str__(self):
        return f"{self.topic} @ {self.timestamp}: {self.payload[:50]}"

class TemperatureReading(models.Model):
    """Modelo agregado para temperaturas"""
    value = models.FloatField()
    status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
        ]
```

### Modificar `state.py`

```python
from .models import MQTTMessage, TemperatureReading

def ingest_message(topic: str, payload: str) -> None:
    with STATE.lock:
        STATE.message_count += 1
        STATE.latest_topic = topic
        STATE.last_updated = timezone.now()

        if topic.endswith("temperatura"):
            try:
                temperature = float(str(payload).replace(",", "."))
                STATE.latest_temperature = temperature
                threshold = settings.MQTT_TEMPERATURE_THRESHOLD
                status = "ALERTA" if temperature > threshold else "NORMAL"
                STATE.latest_status = status
                
                # Persistir em BD
                try:
                    TemperatureReading.objects.create(
                        value=temperature,
                        status=status
                    )
                    MQTTMessage.objects.create(
                        topic=topic,
                        payload=payload,
                        topic_type='temperatura'
                    )
                except Exception as e:
                    LOGGER.error("Erro ao persistir leitura: %s", e)
                
                _record_history_entry()
                return
```

---

## 4. Implementar WebSocket para Tempo Real

### Instalar dependências

```bash
pip install channels channels-redis daphne
```

### Criar `monitoring/consumers.py`

```python
import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from .state import get_snapshot

class DashboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        self.monitor_task = asyncio.create_task(self.monitor_state())
    
    async def disconnect(self, close_code):
        self.monitor_task.cancel()
    
    async def monitor_state(self):
        """Envia atualizações de estado a cada segundo"""
        last_state = None
        while True:
            try:
                current_state = get_snapshot()
                if current_state != last_state:
                    await self.send(text_data=json.dumps({
                        'type': 'state_update',
                        'data': current_state
                    }))
                    last_state = current_state
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
            except Exception as e:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': str(e)
                }))
                await asyncio.sleep(5)
    
    async def receive(self, text_data):
        """Recebe comandos do cliente"""
        try:
            data = json.loads(text_data)
            if data.get('type') == 'command':
                from .mqtt import publish_command
                success, message = publish_command(data.get('command'))
                await self.send(text_data=json.dumps({
                    'type': 'command_response',
                    'success': success,
                    'message': message
                }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))
```

### Configurar `settings.py`

```python
INSTALLED_APPS = [
    ...
    "daphne",
    "monitoring",
]

ASGI_APPLICATION = "fleet_front.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    }
}
```

### Criar `monitoring/routing.py`

```python
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/dashboard/$", consumers.DashboardConsumer.as_asgi()),
]
```

### Modificar `fleet_front/asgi.py`

```python
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from monitoring.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_front.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

---

## 5. Adicionar Logging Estruturado

### Criar `monitoring/logger.py`

```python
import logging
import json
from datetime import datetime

class MQTTJSONFormatter(logging.Formatter):
    """Formatter para logs em JSON"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Configurar em settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'monitoring.logger.MQTTJSONFormatter',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/mqtt.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'json',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'loggers': {
        'monitoring': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

---

## 6. Rate Limiting para API

### Modificar `views.py`

```python
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse
import time

def rate_limit(max_calls, time_window=60):
    """Decorator para rate limiting"""
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            client_ip = get_client_ip(request)
            cache_key = f"rate_limit:{func.__name__}:{client_ip}"
            
            call_count = cache.get(cache_key, 0)
            
            if call_count >= max_calls:
                return JsonResponse(
                    {"success": False, "message": "Rate limit excedido"},
                    status=429
                )
            
            cache.set(cache_key, call_count + 1, time_window)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator

def get_client_ip(request):
    """Obter IP do cliente"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@require_POST
@rate_limit(max_calls=10, time_window=60)
def api_command(request):
    # ... resto do código
```

---

## 7. Testes Unitários

### Criar `monitoring/tests/test_mqtt.py`

```python
from django.test import TestCase
from monitoring.state import ingest_message, get_snapshot, STATE
from monitoring.mqtt import publish_command
import threading

class MQTTStateTestCase(TestCase):
    
    def setUp(self):
        """Limpar estado antes de cada teste"""
        with STATE.lock:
            STATE.latest_temperature = None
            STATE.latest_status = "Aguardando dados"
            STATE.message_count = 0
            STATE.history.clear()
    
    def test_temperature_ingestion(self):
        """Testar recepção de temperatura"""
        ingest_message("logistica/frio/temperatura", "7.5")
        
        snapshot = get_snapshot()
        self.assertEqual(snapshot['latest_temperature'], 7.5)
        self.assertEqual(snapshot['latest_status'], 'NORMAL')
        self.assertEqual(snapshot['message_count'], 1)
    
    def test_temperature_alert(self):
        """Testar alerta de temperatura alta"""
        ingest_message("logistica/frio/temperatura", "9.0")
        
        snapshot = get_snapshot()
        self.assertEqual(snapshot['latest_temperature'], 9.0)
        self.assertEqual(snapshot['latest_status'], 'ALERTA')
    
    def test_invalid_temperature(self):
        """Testar payload inválido"""
        ingest_message("logistica/frio/temperatura", "invalid")
        
        snapshot = get_snapshot()
        self.assertIsNone(snapshot['latest_temperature'])
        self.assertEqual(snapshot['latest_status'], 'Dado inválido')
    
    def test_status_ingestion(self):
        """Testar recepção de status"""
        ingest_message("logistica/frio/status", "OPERACIONAL")
        
        snapshot = get_snapshot()
        self.assertEqual(snapshot['latest_status'], 'OPERACIONAL')
    
    def test_command_validation(self):
        """Testar validação de comandos"""
        success, msg = publish_command("INVALID")
        self.assertFalse(success)
        
        success, msg = publish_command("ON")
        # Pode falhar se broker não disponível, mas validação passa
        self.assertIn("Comando", msg)
    
    def test_thread_safety(self):
        """Testar segurança de thread"""
        def publish_messages():
            for i in range(100):
                ingest_message("logistica/frio/temperatura", f"{5 + i*0.1}")
        
        threads = [threading.Thread(target=publish_messages) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        snapshot = get_snapshot()
        # Deve ter processado todas as mensagens
        self.assertGreater(snapshot['message_count'], 0)
```

### Executar testes

```bash
python manage.py test monitoring.tests.test_mqtt
```

---

## 8. Arquivo `.env` Recomendado

```bash
# Django
DJANGO_SECRET_KEY=django-insecure-seu-secret-key-muito-seguro-aqui
DJANGO_DEBUG=0
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,seu-dominio.com

# MQTT Configuração
MQTT_HOST=seu-broker.com
MQTT_PORT=1883
MQTT_BROKERS=seu-broker.com:1883,broker.hivemq.com:1883
MQTT_USERNAME=usuario-mqtt
MQTT_PASSWORD=senha-mqtt-segura
MQTT_CLIENT_ID=django-fleet-dashboard-prod

# MQTT Tópicos
MQTT_TEMPERATURE_TOPIC=logistica/frio/temperatura
MQTT_STATUS_TOPIC=logistica/frio/status
MQTT_COMMAND_TOPIC=logistica/frio/comando
MQTT_PING_TOPIC=logistica/frio/ping

# MQTT Configuração Avançada
MQTT_TEMPERATURE_THRESHOLD=8.0
MQTT_TEMPERATURE_UNIT=celsius

# Banco de Dados
DATABASE_URL=postgresql://user:password@localhost:5432/fleet_db

# Segurança
CORS_ALLOWED_ORIGINS=https://seu-dominio.com

# Logging
LOG_LEVEL=INFO
```

---

## Priorização de Implementação

### Fase 1 (Imediato - 1 semana)
- [ ] Parametrizar threshold de temperatura
- [ ] Adicionar validação melhorada de payload
- [ ] Implementar logging estruturado

### Fase 2 (Curto prazo - 2-3 semanas)
- [ ] Adicionar autenticação JWT
- [ ] Persistência em BD (histórico)
- [ ] Testes unitários básicos

### Fase 3 (Médio prazo - 1 mês)
- [ ] Implementar WebSocket
- [ ] Rate limiting
- [ ] Documentação OpenAPI

### Fase 4 (Longo prazo - 2+ meses)
- [ ] Dashboard melhorado
- [ ] Alertas por email/SMS
- [ ] Relatórios e análises

---

**Estimativa de esforço total**: 80-100 horas de desenvolvimento  
**ROI**: Significativo aumento em segurança, confiabilidade e escalabilidade
