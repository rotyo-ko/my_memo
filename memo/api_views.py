from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from .serializers import MemoSerializer 
from .models import Memo

class MemoViewSet(viewsets.ModelViewSet):
    serializer_class = MemoSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["priority", "updated_at", "created_at"]
    ordering = ["-priority", "-updated_at", "-created_at"]

    def get_queryset(self):
        return Memo.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)