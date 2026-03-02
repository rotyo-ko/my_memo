from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import MemoSerializer, SummarizeSerializer
from llm.services.gemini import summarize
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
        

    @action(detail=True, methods=["get", "post"])
    def summarize(self, request, pk=None):
        instance = self.get_object()
        if request.method == "POST":
            instance.generate_summary()
        serializer = MemoSerializer(instance)
        return Response(serializer.data)
    
class SummarizeAPIView(APIView):
    throttle_scope = "summarize"
    serializer_class = SummarizeSerializer
    def post(self, request):
        serializer = SummarizeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        summary = summarize(serializer.validated_data["text"])
        
        return Response({"summary": summary})



    

