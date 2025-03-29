document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("searchButton").addEventListener("click", searchSample);
});

function searchSample() {
    const query = document.getElementById('searchInput').value.trim();
    const labelSection = document.getElementById('labelSection');
    const errorMessage = document.getElementById('errorMessage');

    if (!query) {
        showError("Please enter a Sample ID or Batch Number.");
        return;
    }

    fetch(`/generate-label/?query=${query}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }

            // Update UI with returned data
            document.getElementById('labelSampleId').textContent = data.sample_id;
            document.getElementById('labelBatchNumber').textContent = data.batch_number;
            document.getElementById('labelCertification').textContent = data.certification_number;
            document.getElementById('labelExpiryDate').textContent = data.expiry_date;

            // Show QR code if available
            if (data.qr_code_url) {
                document.getElementById('qrCodePreview').innerHTML = `
                    <img src="${data.qr_code_url}" class="img-fluid" alt="QR Code">
                `;
            } else {
                document.getElementById('qrCodePreview').innerHTML = '<p>No QR code available</p>';
            }

            labelSection.classList.remove('d-none');
            errorMessage.classList.add('d-none');
        })
        .catch(error => {
            showError(error.message || 'Error fetching sample data');
        });
}

function showError(message) {
    const errorMessage = document.getElementById('errorMessage');
    errorMessage.textContent = message;
    errorMessage.classList.remove('d-none');
    document.getElementById('labelSection').classList.add('d-none');
}
