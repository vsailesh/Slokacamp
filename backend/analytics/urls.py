from django.urls import path
from .views import (
    DiscussionListCreateView, DiscussionDetailView,
    DiscussionReplyCreateView, DiscussionReplyUpvoteView
)

app_name = 'analytics'

urlpatterns = [
    path('discussions/', DiscussionListCreateView.as_view(), name='discussion_list'),
    path('discussions/<uuid:pk>/', DiscussionDetailView.as_view(), name='discussion_detail'),
    path('discussions/<uuid:discussion_id>/replies/', DiscussionReplyCreateView.as_view(), name='discussion_reply'),
    path('discussion-replies/<uuid:pk>/upvote/', DiscussionReplyUpvoteView.as_view(), name='reply_upvote'),
]
