from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Doctor
from .serializers import DoctorSerializer
from .permissions import IsStaffUser


class DoctorViewSet(viewsets.ModelViewSet):
    """
    Doctor profiles visible on the public 'Who We Are' page.
    Anyone can read; only staff can create/update/delete.
    """

    serializer_class = DoctorSerializer
    queryset = Doctor.objects.filter(is_active=True)

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [AllowAny()]
        return [IsAuthenticated(), IsStaffUser()]
