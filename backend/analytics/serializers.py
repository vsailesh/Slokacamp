from rest_framework import serializers
from .models import Discussion, DiscussionReply
from accounts.serializers import UserSerializer

class DiscussionReplySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = DiscussionReply
        fields = '__all__'
        read_only_fields = ('user', 'upvotes')

class DiscussionSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Discussion
        fields = '__all__'
        read_only_fields = ('user', 'views')
    
    def get_replies_count(self, obj):
        return obj.replies.count()

class DiscussionDetailSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = DiscussionReplySerializer(many=True, read_only=True)
    replies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Discussion
        fields = '__all__'
        read_only_fields = ('user', 'views')
    
    def get_replies_count(self, obj):
        return obj.replies.count()
