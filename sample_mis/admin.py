# from django.contrib import admin
# from .models import Sample, SampleTestResult, Label  # Add Label if needed
#
# @admin.register(Sample)
# class SampleAdmin(admin.ModelAdmin):
#     list_display = (
#         'sample_id',          # Changed from 'id'
#         'batch_number',
#         'sample_type',
#         'sample_origin',      # Changed from 'origin'
#         'testing_status',     # Changed from 'status'
#         'test_date'
#     )
#     list_filter = (
#         'testing_status',     # Changed from 'status'
#         'sample_type'
#     )
#     search_fields = (
#         'batch_number',
#         'sample_origin'       # Changed from 'origin'
#     )
#
# @admin.register(SampleTestResult)
# class SampleTestResultAdmin(admin.ModelAdmin):
#     list_display = (
#         'sample',
#         'compliance_status',
#         'test_date',
#         'expiry_date'
#     )
#     list_filter = (
#         'compliance_status',
#         'test_date'
#     )
#     search_fields = (
#         'sample__batch_number',
#         # 'sample__sample_id'    # Changed from 'sample__id'
#     )
#
# # Add this if you have a Label model
# @admin.register(Label)
# class LabelAdmin(admin.ModelAdmin):
#     list_display = (
#         'certification_number',
#         'expiry_date',
#         'sample'
#     )
#     search_fields = ('certification_number',)
from django.contrib import admin
from .models import Sample, SampleTestResult, Label

@admin.register(Sample)
class SampleAdmin(admin.ModelAdmin):
    list_display = ('sample_id', 'batch_number', 'sample_type', 'sample_origin', 'testing_status', 'test_date')
    list_filter = ('testing_status', 'sample_type')
    search_fields = ('batch_number', 'sample_origin')

@admin.register(SampleTestResult)
class SampleTestResultAdmin(admin.ModelAdmin):
    list_display = ('sample', 'compliance_status', 'test_date', 'expiry_date')
    list_filter = ('compliance_status', 'test_date')
    search_fields = ('sample__batch_number',)

@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('certification_number', 'expiry_date', 'sample')
    search_fields = ('certification_number',)

