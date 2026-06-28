from rest_framework import serializers


class UserObjectSerializer(serializers.Serializer):
    userId = serializers.IntegerField(required=True)
    userEmail = serializers.EmailField(required=True)
    userName = serializers.CharField(required=True, allow_blank=False)
    profile = serializers.ChoiceField(
        choices=['Administrador', 'Usuario IC', 'Heavy user', 'Macro', 'Usuario'],
        required=True
    )
    roles = serializers.ListField(
        child=serializers.CharField(allow_blank=False),
        required=True,
        allow_empty=True
    )
    memoryEnabled = serializers.BooleanField(required=True)


class RequestPayloadSerializer(serializers.Serializer):
    conversationId = serializers.CharField(required=True, allow_blank=False)
    query = serializers.CharField(required=True, allow_blank=False)
    timestamp = serializers.DateTimeField(required=True)
    user = UserObjectSerializer(required=True)
    agentType = serializers.CharField(required=False, default='auto')

    def validate_conversationId(self, value):
        if not value.startswith('conv-'):
            raise serializers.ValidationError(
                "conversationId must start with 'conv-'"
            )
        parts = value.split('-')
        if len(parts) != 3:
            raise serializers.ValidationError(
                "conversationId must have format 'conv-<timestamp>-<random>'"
            )
        return value

    def validate_agentType(self, value):
        valid_agents = ['auto', 'rag-mails', 'trigger-comunicaciones']
        if value not in valid_agents:
            return 'auto'
        return value


class MetadataSerializer(serializers.Serializer):
    agent_used = serializers.CharField(required=True)
    execution_time_ms = serializers.IntegerField(required=True, min_value=0)
    records_found = serializers.IntegerField(required=False, allow_null=True)


class ResponsePayloadSerializer(serializers.Serializer):
    conversationId = serializers.CharField(required=True)
    output = serializers.CharField(required=True, allow_blank=True)
    html_render = serializers.BooleanField(required=True)
    metadata = MetadataSerializer(required=True)
    error = serializers.CharField(required=False, allow_blank=True)
