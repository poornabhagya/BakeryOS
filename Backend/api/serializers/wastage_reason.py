from rest_framework import serializers
from api.models import WastageReason


class WastageReasonListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing all wastage reasons.
    Used for GET /api/wastage-reasons/
    """

    class Meta:
        model = WastageReason
        fields = ['id', 'reason_id', 'reason', 'description']
        read_only_fields = ['id', 'reason_id']


class WastageReasonDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving detailed wastage reason information.
    Includes timestamps and full details.
    """

    class Meta:
        model = WastageReason
        fields = ['id', 'reason_id', 'reason', 'description', 'created_at']
        read_only_fields = ['id', 'reason_id', 'created_at']


class WastageReasonCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new wastage reasons.
    Validates required fields and ensures unique reason names.
    """

    class Meta:
        model = WastageReason
        fields = ['id', 'reason_id', 'reason', 'description']
        read_only_fields = ['id', 'reason_id']

    def validate_reason(self, value):
        """Validate reason is unique and not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Reason cannot be empty")

        if WastageReason.objects.filter(reason__iexact=value.strip()).exists():
            raise serializers.ValidationError(
                "A wastage reason with this name already exists"
            )

        return value.strip()

    def validate_description(self, value):
        """Validate description if provided"""
        if value and not value.strip():
            return None
        return value.strip() if value else None
