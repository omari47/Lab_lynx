# from datetime import datetime  # Keep this import
# from django.db.models import Q
# from rest_framework import viewsets, filters
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.generics import ListAPIView
# from django_filters.rest_framework import DjangoFilterBackend
#
# # Corrected imports
# from sample_mis.models import Sample, SampleTestResult, Label  # Changed TestResult to SampleTestResult
# from .serializers import SampleSerializer, SampleTestResultSerializer, LabelSerializer
#
# class SampleViewSet(viewsets.ModelViewSet):
#     queryset = Sample.objects.prefetch_related('test_results', 'labels').all()
#     serializer_class = SampleSerializer
#     filter_backends = [DjangoFilterBackend, filters.SearchFilter]
#     search_fields = ['batch_number', 'sample_type', 'origin']
#     filterset_fields = ['status', 'sample_type']
#
# class SampleTestResultViewSet(viewsets.ModelViewSet):
#     # Fixed queryset reference
#     queryset = SampleTestResult.objects.select_related('sample').all()  # Changed TestResult to SampleTestResult
#     serializer_class = SampleTestResultSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['compliance_status', 'sample__batch_number']
#
# class LabelViewSet(viewsets.ModelViewSet):
#     queryset = Label.objects.select_related('sample').all()
#     serializer_class = LabelSerializer
#     filter_backends = [DjangoFilterBackend]
#     filterset_fields = ['sample__batch_number', 'expiry_date']
#
#     def perform_create(self, serializer):
#         instance = serializer.save()
#         instance.generate_qr_code()
#         instance.generate_pdf()
#         instance.save()
#
# class SampleSearchAPI(ListAPIView):
#     serializer_class = SampleSerializer
#
#     def get_queryset(self):
#         query = self.request.query_params.get('q', '')
#         return Sample.objects.filter(
#             Q(batch_number__icontains=query) |
#             Q(origin__icontains=query) |
#             Q(id__icontains=query)
#         )
#
# class DashboardStatsAPI(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         user = request.user
#         return Response({
#             'samples_submitted': user.submitted_samples.count(),
#             'samples_tested': user.conducted_tests.count(),
#             'labels_generated': user.generated_labels.count()
#         })
#
# class RecentActivityAPI(APIView):
#     permission_classes = [IsAuthenticated]
#
#     def get(self, request):
#         activities = []
#
#         # Get sample submissions using test_date
#         samples = request.user.submitted_samples.order_by('-test_date')[:5]
#         activities += [{
#             'type': 'sample',
#             'action': 'submitted',
#             'date': s.test_date,
#             'target': s.batch_number
#         } for s in samples]
#
#         # Get test results using the renamed model
#         tests = request.user.conducted_tests.select_related('sample').order_by('-test_date')[:5]
#         activities += [{
#             'type': 'test',
#             'action': 'conducted',
#             'date': t.test_date,
#             'target': t.sample.batch_number
#         } for t in tests]
#
#         # Fixed datetime comparison
#         sorted_activities = sorted(
#             activities,
#             key=lambda x: x['date'] if isinstance(x['date'], datetime) else datetime.combine(x['date'], datetime.min.time()),
#             reverse=True
#         )[:5]
#         return Response(sorted_activities)
#
# @api_view(['GET'])
# def recent_activities(request):
#     activities = Sample.objects.filter(
#         submitted_by=request.user
#     ).order_by('-test_date')[:5].values(
#         'id', 'batch_number', 'test_date', 'status'
#     )
#
#     return Response([{
#         'type': 'sample',
#         'action': f"Sample {a['batch_number']} {a['status']}",
#         'date': a['test_date'],
#         'target': a['id']
#     } for a in activities])
from datetime import datetime
from django.db.models import Q
from rest_framework import viewsets, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend

from sample_mis.models import Sample, SampleTestResult, Label
from .serializers import SampleSerializer, SampleTestResultSerializer, LabelSerializer


class SampleViewSet(viewsets.ModelViewSet):
    queryset = Sample.objects.prefetch_related('test_results').select_related('label').all()
    serializer_class = SampleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['batch_number', 'sample_type', 'sample_origin']
    filterset_fields = ['testing_status', 'sample_type']

class SampleTestResultViewSet(viewsets.ModelViewSet):
    queryset = SampleTestResult.objects.select_related('sample').all()
    serializer_class = SampleTestResultSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['compliance_status', 'sample__batch_number']

class LabelViewSet(viewsets.ModelViewSet):
    queryset = Label.objects.select_related('sample').all()
    serializer_class = LabelSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['sample__batch_number', 'expiry_date']
    def perform_create(self, serializer):
        instance = serializer.save()
        instance.generate_qr()   # fixed method call
        instance.generate_pdf()
        instance.save()

class SampleSearchAPI(ListAPIView):
    serializer_class = SampleSerializer
    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Sample.objects.filter(
            Q(batch_number__icontains=query) |
            Q(sample_origin__icontains=query) |
            Q(sample_id__icontains=query)
        )

class DashboardStatsAPI(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        user = request.user
        return Response({
            'samples_submitted': user.submitted_samples.count(),
            'samples_tested': user.conducted_tests.count(),
            'labels_generated': user.generated_labels.count()
        })

from datetime import datetime, date, time
from django.utils import timezone

def parse_date(date_val):
    # If the value is already a datetime object:
    if isinstance(date_val, datetime):
        # If it's naive, assume the current timezone and make it aware.
        if timezone.is_naive(date_val):
            return timezone.make_aware(date_val, timezone.get_current_timezone())
        return date_val
    # If it's a date (without time), combine with a default time and make aware.
    elif isinstance(date_val, date):
        dt = datetime.combine(date_val, time.min)
        return timezone.make_aware(dt, timezone.get_current_timezone())
    # If it's a string, try parsing it.
    elif isinstance(date_val, str):
        try:
            dt = datetime.strptime(date_val, '%Y-%m-%d')
            return timezone.make_aware(dt, timezone.get_current_timezone())
        except Exception:
            return timezone.now()
    return timezone.now()

class RecentActivityAPI(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        activities = []
        samples = request.user.submitted_samples.order_by('-test_date')[:5]
        activities += [{
            'type': 'sample',
            'action': 'submitted',
            'date': s.test_date,
            'target': s.batch_number
        } for s in samples]
        tests = request.user.conducted_tests.select_related('sample').order_by('-test_date')[:5]
        activities += [{
            'type': 'test',
            'action': 'conducted',
            'date': t.test_date,
            'target': t.sample.batch_number
        } for t in tests]
        # sorted_activities = sorted(
        #     activities,
        #     key=lambda x: x['date'] if isinstance(x['date'], datetime) else datetime.combine(x['date'], datetime.min.time()),
        #     reverse=True
        # )[:5]
        sorted_activities = sorted(
            activities,
            key=lambda x: parse_date(x['date']),
            reverse=True
        )[:5]
        return Response(sorted_activities)

@api_view(['GET'])
def recent_activities(request):
    # Note: use correct field name 'testing_status'
    activities = Sample.objects.filter(
        submitted_by=request.user
    ).order_by('-test_date')[:5].values(
        'sample_id', 'batch_number', 'test_date', 'testing_status'
    )
    return Response([{
        'type': 'sample',
        'action': f"Sample {a['batch_number']} {a['testing_status']}",
        'date': a['test_date'],
        'target': a['sample_id']
    } for a in activities])
