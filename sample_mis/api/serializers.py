# from rest_framework import serializers
# from sample_mis.models import Sample, Label, SampleTestResult
#
# class SampleTestResultSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = SampleTestResult
#         fields = [
#             'id', 'quality_analysis', 'compliance_status',
#             'test_date', 'expiry_date', 'conducted_by', 'sample'
#         ]
#         read_only_fields = ('test_date', 'conducted_by', 'sample')
#         extra_kwargs = {
#             'expiry_date': {'required': True}
#         }
#
#     def validate_quality_analysis(self, value):
#         """Ensure quality analysis is not empty"""
#         if not value.strip():
#             raise serializers.ValidationError("Quality analysis cannot be empty")
#         return value
#
# class LabelSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Label
#         fields = [
#             'id', 'label_data', 'generated_date',
#             'qr_code', 'pdf', 'sample', 'expiry_date'
#         ]
#         read_only_fields = ('generated_date', 'qr_code', 'pdf', 'sample')
#
# class SampleSerializer(serializers.ModelSerializer):
#     status_display = serializers.CharField(
#         source='get_testing_status_display',
#         read_only=True,
#         help_text="Human-readable status of the sample"
#     )
#     compliance_status = serializers.SerializerMethodField(
#         help_text="Compliance status from test results"
#     )
#     label_status = serializers.SerializerMethodField(
#         help_text="Whether label has been generated"
#     )
#     test_results = SampleTestResultSerializer(
#         read_only=True,
#         help_text="Related test results"
#     )
#     label = LabelSerializer(
#         read_only=True,
#         help_text="Generated label details"
#     )
#
#     # Update field names to match the model
#     class Meta:
#         model = Sample
#         fields = [
#             'id', 'sample_type', 'sample_origin', 'batch_number',  # 'sample_origin' instead of 'origin'
#             'testing_status', 'status_display', 'test_date',  # 'testing_status' instead of 'status'
#             'compliance_status', 'label_status',
#             'test_results', 'label'
#         ]
#         extra_kwargs = {
#             'batch_number': {'required': True, 'allow_blank': False},
#             'sample_type': {'required': True}
#         }
#
#     def get_compliance_status(self, obj):
#         """Safely get compliance status with null check"""
#         if obj.test_results:
#             return obj.test_results.compliance_status
#         return 'N/A'
#
#     def get_label_status(self, obj):
#         """Check label existence with explicit query"""
#         return 'Generated' if hasattr(obj, 'label') else 'Pending'
#
#     def validate_batch_number(self, value):
#         """Ensure batch number is unique"""
#         if Sample.objects.filter(batch_number=value).exists():
#             raise serializers.ValidationError("Batch number must be unique")
#         return value
from rest_framework import serializers
from sample_mis.models import Sample, Label, SampleTestResult

class SampleTestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleTestResult
        fields = ['id', 'quality_analysis', 'compliance_status', 'test_date', 'expiry_date', 'conducted_by', 'sample']
        read_only_fields = ('test_date', 'conducted_by', 'sample')
        extra_kwargs = {
            'expiry_date': {'required': True}
        }
    def validate_quality_analysis(self, value):
        if not value.strip():
            raise serializers.ValidationError("Quality analysis cannot be empty")
        return value

class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = ['id', 'label_data', 'generated_date', 'qr_code', 'pdf', 'sample', 'expiry_date']
        read_only_fields = ('generated_date', 'qr_code', 'pdf', 'sample')
#
# class SampleSerializer(serializers.ModelSerializer):
#     status_display = serializers.CharField(
#         source='get_testing_status_display',
#         read_only=True,
#         help_text="Human-readable status of the sample"
#     )
#     compliance_status = serializers.SerializerMethodField(help_text="Compliance status from test results")
#     label_status = serializers.SerializerMethodField(help_text="Whether label has been generated")
#     test_results = SampleTestResultSerializer(read_only=True, help_text="Related test results")
#     label = LabelSerializer(read_only=True, help_text="Generated label details")
#     class Meta:
#         model = Sample
#         fields = ['sample_id', 'sample_type', 'sample_origin', 'batch_number', 'testing_status', 'status_display', 'test_date', 'compliance_status', 'label_status', 'test_results', 'label']
#         extra_kwargs = {
#             'batch_number': {'required': True, 'allow_blank': False},
#             'sample_type': {'required': True}
#         }
#     def get_compliance_status(self, obj):
#         if obj.test_results.exists():
#             latest_result = obj.test_results.first()
#             return latest_result.compliance_status
#         return 'N/A'
#     def get_label_status(self, obj):
#         return 'Generated' if hasattr(obj, 'label') else 'Pending'
#     def validate_batch_number(self, value):
#         if Sample.objects.filter(batch_number=value).exists():
#             raise serializers.ValidationError("Batch number must be unique")
#         return value
class SampleSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(
        source='get_testing_status_display',
        read_only=True,
        help_text="Human-readable status of the sample"
    )
    compliance_status = serializers.SerializerMethodField(help_text="Compliance status from test results")
    label_status = serializers.SerializerMethodField(help_text="Whether label has been generated")
    test_results = SampleTestResultSerializer(many=True, read_only=True, help_text="Related test results")
    label = LabelSerializer(read_only=True, help_text="Generated label details")

    class Meta:
        model = Sample
        fields = [
            'sample_id', 'sample_type', 'sample_origin', 'batch_number',
            'testing_status', 'status_display', 'test_date',
            'compliance_status', 'label_status', 'test_results', 'label'
        ]
        extra_kwargs = {
            'batch_number': {'required': True, 'allow_blank': False},
            'sample_type': {'required': True}
        }

    def get_compliance_status(self, obj):
        if obj.test_results.exists():
            latest_result = obj.test_results.first()
            return latest_result.compliance_status
        return 'N/A'

    def get_label_status(self, obj):
        return 'Generated' if hasattr(obj, 'label') else 'Pending'

    def validate_batch_number(self, value):
        if Sample.objects.filter(batch_number=value).exists():
            raise serializers.ValidationError("Batch number must be unique")
        return value
