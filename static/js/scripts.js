function confirmFeature(featureId) {
    fetch(`/confirm_feature/${featureId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Feature confirmed!');
            location.reload();
        }
    });
}

function deprecateFeature(featureId) {
    fetch(`/deprecate_feature/${featureId}`, {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Feature deprecated!');
            location.reload();
        }
    });
}

function downloadFeatures() {
    window.location.href = '/download_features';
}
