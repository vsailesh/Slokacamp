from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Discussion, DiscussionReply
from .serializers import DiscussionSerializer, DiscussionDetailSerializer, DiscussionReplySerializer

class DiscussionListCreateView(generics.ListCreateAPIView):
    queryset = Discussion.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        return DiscussionSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        course_id = self.request.query_params.get('course', None)
        search = self.request.query_params.get('search', None)
        
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        if search:
            queryset = queryset.filter(title__icontains=search)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DiscussionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Discussion.objects.all()
    serializer_class = DiscussionDetailSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"detail": "You can only edit your own discussions"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user and not request.user.role == 'admin':
            return Response(
                {"detail": "You can only delete your own discussions"},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().destroy(request, *args, **kwargs)

class DiscussionReplyCreateView(generics.CreateAPIView):
    serializer_class = DiscussionReplySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        discussion_id = self.kwargs['discussion_id']
        discussion = Discussion.objects.get(id=discussion_id)
        serializer.save(user=self.request.user, discussion=discussion)

class DiscussionReplyUpvoteView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        try:
            reply = DiscussionReply.objects.get(id=pk)
            reply.upvotes += 1
            reply.save()
            return Response({'upvotes': reply.upvotes})
        except DiscussionReply.DoesNotExist:
            return Response(
                {"detail": "Reply not found"},
                status=status.HTTP_404_NOT_FOUND
            )
