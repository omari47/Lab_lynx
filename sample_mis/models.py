from django.contrib.auth.models import User
from django.db import models
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils.timezone import now
from reportlab.pdfgen import canvas


class SampleTestResult(models.Model):
    COMPLIANCE_CHOICES = [
        (True, 'Compliant'),
        (False, 'Non-Compliant'),
    ]
    sample = models.ForeignKey(
        'Sample',
        on_delete=models.CASCADE,
        related_name='test_results'
    )
    quality_analysis = models.TextField()
    compliance_status = models.BooleanField(choices=COMPLIANCE_CHOICES, default=False)
    test_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    conducted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='conducted_tests'
    )

    class Meta:
        ordering = ['-test_date']

    def __str__(self):
        return f"Test Results for {self.sample.batch_number}"


class Sample(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    TYPE_CHOICES = [
        ('Food', 'Food'),
        ('Chemical', 'Chemical'),
        ('Textile', 'Textile'),
        ('Other', 'Other'),
    ]
    sample_id = models.AutoField(primary_key=True)
    sample_type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    sample_origin = models.CharField(max_length=100)
    batch_number = models.CharField(max_length=50, unique=True)
    testing_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    test_date = models.DateField(auto_now_add=True)
    metadata = models.TextField(blank=True, null=True)
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_samples'
    )
    submitted_at = models.DateTimeField(default=now)

    class Meta:
        ordering = ['-test_date', '-sample_id']

    def __str__(self):
        return f"Sample {self.sample_id} - {self.batch_number}"

    @property
    def latest_test_result(self):
        # Returns the first test result based on the ordering defined in SampleTestResult.Meta
        return self.test_results.first()


class Label(models.Model):
    sample = models.OneToOneField(
        Sample,
        on_delete=models.CASCADE,
        related_name='label'
    )
    label_data = models.JSONField()
    generated_date = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateField()
    certification_number = models.CharField(max_length=50, unique=True)
    pdf = models.FileField(upload_to='labels/')
    qr_code = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True
    )
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='generated_labels'
    )

    def generate_qr(self):
        qr = qrcode.make(f"KEBS-{self.sample.batch_number}-{self.certification_number}")
        buffer = BytesIO()
        qr.save(buffer, format='PNG')
        self.qr_code.save(f'qr_{self.certification_number}.png', File(buffer), save=False)

    def generate_pdf(self):
        buffer = BytesIO()
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, f"KEBS Certification: {self.certification_number}")
        p.drawString(100, 780, f"Batch: {self.sample.batch_number}")
        p.drawString(100, 760, f"Expiry: {self.expiry_date}")
        p.showPage()
        p.save()
        self.pdf.save(f'label_{self.certification_number}.pdf', File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only generate on first save
            self.generate_qr()
            self.generate_pdf()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Label for {self.sample.batch_number}"


class TestResultDetail(models.Model):
    test_result = models.OneToOneField(
        SampleTestResult,
        on_delete=models.CASCADE,
        related_name='detail'
    )
    # Store extra details in JSON format – you can later create custom fields if needed.
    parameters = models.JSONField(blank=True, null=True)
    additional_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Details for {self.test_result}"


from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=SampleTestResult)
def update_sample_status(sender, instance, created, **kwargs):
    """
    Update the testing_status of the related Sample based on test results.
    """
    sample = instance.sample
    latest_test_result = sample.test_results.first()

    if latest_test_result:
        if latest_test_result.compliance_status:  # If a test result exists and is compliant
            sample.testing_status = 'Completed'
        else:
            sample.testing_status = 'In Progress'
    else:
        sample.testing_status = 'Pending'  # If no test results exist

    sample.save()
