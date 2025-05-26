from django.urls import path
from .views import AgoraTokenView

urlpatterns = [
    path('token/<int:auction_id>/', AgoraTokenView.as_view(), name='agora-token'),
] 