function exportSelectedFeatures() {
    const selectedIds = Array.from(document.querySelectorAll('.feature-checkbox:checked'))
        .map(checkbox => checkbox.value);
    
    if (selectedIds.length === 0) {
        alert('Please select at least one feature to export');
        return;
    }

    fetch('/api/features/export', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ feature_ids: selectedIds })
    })
    .then(response => response.json())
    .then(data => {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `features_export_${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    });
}

function updateFeatureStatus(featureId, status) {
    fetch(`/api/feature2/${featureId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: status })
    })
    .then(response => {
        if (response.ok) {
            window.location.reload();
        }
    });
}

// 其他交互函数（create project/feature等）