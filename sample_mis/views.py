from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse, FileResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
import csv

from .models import Sample, SampleTestResult, Label
from .forms import SampleTestResultForm, SampleForm, LabelForm, RegistrationForm
from .api.serializers import SampleSerializer


# Common Views
def dashboard(request):
    # Now passing stats to the template for dynamic display.
    if request.user.is_authenticated:
        stats = {
            'samples_submitted': request.user.submitted_samples.count(),
            'samples_tested': request.user.conducted_tests.count(),
            'labels_generated': request.user.generated_labels.count()
        }
    else:
        stats = {}
    return render(request, 'dashboard.html', stats)


@login_required
def sample_submission(request):
    if request.method == 'POST':
        form = SampleForm(request.POST)
        if form.is_valid():
            sample = form.save(commit=False)
            if not sample.submitted_by:  # Ensure it gets assigned
                sample.submitted_by = request.user
            sample.save()
            return redirect('sample_details', sample_id=sample.sample_id)
    else:
        form = SampleForm()
    return render(request, 'sample_submission.html', {'form': form})


def sample_tracking(request):
    # Query samples to pass to the tracking page.
    samples = Sample.objects.all().order_by('-test_date')
    return render(request, 'sample_tracking.html', {'samples': samples})


def sample_details(request, sample_id):
    sample = get_object_or_404(Sample, sample_id=sample_id)
    test_result = sample.latest_test_result  # Get the latest test result dynamically
    return render(request, 'sample_details.html', {
        'sample': sample,
        'test_result': test_result
    })


@api_view(['GET'])
def sample_api(request):
    query = request.GET.get('search', '')
    samples = Sample.objects.filter(
        Q(batch_number__icontains=query) |
        Q(sample_id__icontains=query)
    )

    data = []
    for sample in samples:
        latest_result = sample.test_results.first()  # Assumes ordering by test_date descending
        detail = None
        if latest_result:
            try:
                detail = latest_result.detail.parameters  # or detail.additional_notes if you prefer
            except TestResultDetail.DoesNotExist:
                detail = None
        data.append({
            "id": sample.sample_id,
            "type": sample.sample_type,
            "status": sample.testing_status,
            "date": sample.test_date.strftime('%Y-%m-%d'),
            "result_detail": detail  # Add extra field(s) as needed
        })
    return JsonResponse(data, safe=False)


# Test Results Views
def test_results(request, sample_id):
    sample = get_object_or_404(Sample, pk=sample_id)
    if request.method == 'POST':
        form = SampleTestResultForm(request.POST)
        if form.is_valid():
            test_result = form.save(commit=False)
            test_result.sample = sample
            test_result.conducted_by = request.user
            test_result.save()
            # Update the sample's testing status once test result is saved.
            sample.testing_status = 'Completed'  # Change to desired status if needed.
            sample.save()
            return redirect('sample_details', sample_id=sample_id)
    else:
        form = SampleTestResultForm()
    return render(request, 'test_results.html', {'form': form, 'sample': sample})


def testing_results(request):
    query = request.GET.get('q', '')
    results = SampleTestResult.objects.select_related('sample').filter(
        Q(sample__sample_id__icontains=query) |
        Q(sample__batch_number__icontains=query)
    ).order_by('-test_date')

    return render(request, 'testing_results.html', {
        'results': results,
        'search_query': query
    })


@login_required
def label_generation(request):
    context = {}
    if request.method == 'GET' and 'query' in request.GET:
        query = request.GET.get('query')
        try:
            sample = Sample.objects.get(Q(sample_id=query) | Q(batch_number=query))
            # Fetch the latest test result for expiry date if it exists.
            latest_result = sample.test_results.first()  # assuming ordering is descending by test_date
            if latest_result:
                label, created = Label.objects.get_or_create(
                    sample=sample,
                    defaults={'expiry_date': latest_result.expiry_date}  # Use latest_result here
                )
                # context['label'] = label
                # context['sample'] = sample
                context = {
                    "sample_id": sample.sample_id,
                    "batch_number": sample.batch_number,
                    "expiry_date": label.expiry_date.strftime('%Y-%m-%d'),
                    "certification_number": label.certification_number,
                    "generated_date": label.generated_date.strftime('%Y-%m-%d'),
                    "label_id": label.id,
                    "qr_code_url": label.qr_code.url if label.qr_code else None
                }
            else:
                context['error'] = "Test results not found for the sample."
        except Sample.DoesNotExist:
            context['error'] = "Sample not found."
    return render(request, 'label_generation.html', context)


from django.shortcuts import get_object_or_404
from .models import Sample, Label


def generate_label(request):
    query = request.GET.get('query', '').strip()
    print("Received query:", query)  # Debugging - Check query in backend

    if not query:
        return JsonResponse({'error': 'No search query provided'}, status=400)

    try:
        sample = Sample.objects.get(batch_number=query)
        label = Label.objects.get(sample=sample)

        return JsonResponse({
            'sample_id': sample.sample_id,
            'batch_number': sample.batch_number,
            'expiry_date': label.expiry_date.strftime('%Y-%m-%d'),
            'certification_number': label.certification_number,
            'qr_code_url': label.qr_code.url if label.qr_code else None,
            'label_id': label.id,
        })
    except Sample.DoesNotExist:
        return JsonResponse({'error': 'Sample not found'}, status=404)
    except Label.DoesNotExist:
        return JsonResponse({'error': 'Label not generated for this sample'}, status=404)


def generate_label_api(request):
    query = request.GET.get('query', '').strip()

    if not query:
        return JsonResponse({"error": "Query parameter is required."}, status=400)

    try:
        sample = get_object_or_404(Sample, batch_number=query)  # Try batch_number first
    except:
        sample = get_object_or_404(Sample, sample_id=query)  # Fallback to sample_id

    # Ensure a label exists
    label = Label.objects.filter(sample=sample).first()
    if not label:
        return JsonResponse({"error": "Label not generated for this sample."}, status=404)

    return JsonResponse({
        "sample_id": sample.sample_id,
        "batch_number": sample.batch_number,
        "certification_number": label.certification_number,
        "expiry_date": label.expiry_date.strftime('%Y-%m-%d'),
        "qr_code_url": label.qr_code.url if label.qr_code else None
    })


def download_label(request, label_id):
    label = get_object_or_404(Label, id=label_id)
    return FileResponse(open(label.pdf.path, 'rb'), as_attachment=True)


from django.db.models import Q
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
import csv
from .models import Sample, SampleTestResult, Label

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Sample, SampleTestResult, Label


@login_required
def data_management(request):
    samples = Sample.objects.select_related('submitted_by').all().order_by('-sample_id')
    test_results = SampleTestResult.objects.select_related('sample', 'conducted_by').all().order_by('-test_date')
    labels = Label.objects.select_related('sample', 'generated_by').all().order_by('-generated_date')

    return render(request, 'data_management.html', {
        'samples': samples,
        'test_results': test_results,
        'labels': labels
    })


@login_required
def search_data(request):
    """
    Handles search queries in the Data Management page.
    """
    query = request.GET.get('q', '').strip()
    samples = Sample.objects.filter(
        Q(sample_id__icontains=query) | Q(batch_number__icontains=query) | Q(sample_origin__icontains=query)
    ).select_related('submitted_by')

    test_results = SampleTestResult.objects.filter(
        Q(sample__sample_id__icontains=query) | Q(sample__batch_number__icontains=query) | Q(
            quality_analysis__icontains=query)
    ).select_related('sample', 'conducted_by')

    labels = Label.objects.filter(
        Q(sample__batch_number__icontains=query) | Q(certification_number__icontains=query)
    ).select_related('sample', 'generated_by')

    return JsonResponse({
        'samples': list(samples.values('sample_id', 'batch_number', 'sample_origin', 'testing_status', 'test_date')),
        'test_results': list(
            test_results.values('sample__batch_number', 'quality_analysis', 'compliance_status', 'test_date')),
        'labels': list(labels.values('sample__batch_number', 'certification_number', 'expiry_date', 'generated_date'))
    }, safe=False)


@login_required
def export_data_csv(request):
    """
    Exports all data as a CSV file.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data_management_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Sample ID', 'Batch Number', 'Origin', 'Status', 'Test Date', 'Quality Analysis', 'Compliance',
                     'Label Cert No', 'Expiry Date'])

    samples = Sample.objects.prefetch_related('test_results', 'label').all()

    for sample in samples:
        latest_test_result = sample.test_results.first()
        compliance = latest_test_result.compliance_status if latest_test_result else 'N/A'
        quality_analysis = latest_test_result.quality_analysis if latest_test_result else 'N/A'
        label = sample.label if hasattr(sample, 'label') else None
        certification_number = label.certification_number if label else 'N/A'
        expiry_date = label.expiry_date if label else 'N/A'

        writer.writerow([
            sample.sample_id,
            sample.batch_number,
            sample.sample_origin,
            sample.testing_status,
            sample.test_date.strftime('%Y-%m-%d'),
            quality_analysis,
            compliance,
            certification_number,
            expiry_date
        ])

    return response


@api_view(['GET'])
def sample_api_advanced(request):
    query = request.GET.get('search', '')
    # Use correct related names: test_results (plural) and label (singular)
    samples = Sample.objects.select_related('label').prefetch_related('test_results')
    if query:
        samples = samples.filter(
            Q(sample_id__icontains=query) |
            Q(batch_number__icontains=query) |
            Q(sample_type__icontains=query)
        )
    serializer = SampleSerializer(samples, many=True)
    return Response(serializer.data)


def export_samples_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="samples_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Sample ID', 'Type', 'Origin', 'Batch', 'Status', 'Compliance', 'Label Status'])
    samples = Sample.objects.select_related('label').prefetch_related('test_results')
    for sample in samples:
        # Get latest test result if available
        latest_result = sample.test_results.first()
        compliance = latest_result.compliance_status if latest_result else 'N/A'
        label_status = 'Generated' if hasattr(sample, 'label') else 'Pending'
        writer.writerow([
            sample.sample_id,
            sample.sample_type,
            sample.sample_origin,
            sample.batch_number,
            sample.get_testing_status_display(),
            compliance,
            label_status
        ])
    return response


from django.contrib.auth import login as auth_login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


from django.shortcuts import render, redirect


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.http import require_GET


@require_GET
def logout_view(request):
    logout(request)
    return redirect('login')


from .models import Sample, SampleTestResult, Label, TestResultDetail


def test_results_detail(request, sample_id):
    # Retrieve the sample using sample_id
    sample = get_object_or_404(Sample, sample_id=sample_id)
    # Get the latest test result for that sample (as before)
    test_result = sample.test_results.first()
    detail = None
    if test_result:
        # Attempt to get the related TestResultDetail, if it exists.
        try:
            detail = test_result.detail
        except TestResultDetail.DoesNotExist:
            detail = None
    context = {
        'sample': sample,
        'test_result': test_result,
        'detail': detail,
    }
    return render(request, 'test_results_detail.html', context)
