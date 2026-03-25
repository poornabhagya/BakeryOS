from rest_framework import serializers
from api.models import Notification, NotificationReceipt, User


class NotificationSerializer(serializers.ModelSerializer):
    """Base serializer for Notification model"""
    
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'type', 'icon', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationListSerializer(serializers.ModelSerializer):
    """List serializer for notifications with read status"""
    is_read = serializers.SerializerMethodField()
    read_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'type', 'icon', 'is_read', 'read_at', 'created_at']
        read_only_fields = fields
    
    def get_is_read(self, obj):
        """Get read status for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                receipt = obj.receipts.get(user=request.user)
                return receipt.is_read
            except NotificationReceipt.DoesNotExist:
                return False
        return False
    
    def get_read_at(self, obj):
        """Get read timestamp for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                receipt = obj.receipts.get(user=request.user)
                return receipt.read_at
            except NotificationReceipt.DoesNotExist:
                return None
        return None


class NotificationDetailSerializer(serializers.ModelSerializer):
    """Detail serializer with read status"""
    is_read = serializers.SerializerMethodField()
    read_at = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'type', 'icon', 'is_read', 'read_at', 'created_at']
        read_only_fields = fields
    
    def get_is_read(self, obj):
        """Get read status for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                receipt = obj.receipts.get(user=request.user)
                return receipt.is_read
            except NotificationReceipt.DoesNotExist:
                return False
        return False
    
    def get_read_at(self, obj):
        """Get read timestamp for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                receipt = obj.receipts.get(user=request.user)
                return receipt.read_at
            except NotificationReceipt.DoesNotExist:
                return None
        return None


class NotificationReceiptSerializer(serializers.ModelSerializer):
    """Serializer for NotificationReceipt"""
    notification = NotificationListSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = NotificationReceipt
        fields = ['id', 'notification', 'user', 'is_read', 'read_at', 'created_at']
        read_only_fields = fields


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications (admin/system use only)"""
    
    class Meta:
        model = Notification
        fields = ['title', 'message', 'type', 'icon']
    
    def validate_type(self, value):
        """Validate notification type"""
        valid_types = [choice[0] for choice in Notification.TYPE_CHOICES]
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid notification type. Choose from {valid_types}")
        return value


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics"""
    total = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    read_count = serializers.IntegerField()
