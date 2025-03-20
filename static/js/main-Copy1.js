function confirmFeature(featureId) {
    fetch(`/feature/${featureId}/confirm`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Feature confirmed successfully');
            location.reload();
        }
    });
}

function deprecateFeature(featureId) {
    fetch(`/feature/${featureId}/deprecate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Feature deprecated successfully');
            location.reload();
        }
    });
}
