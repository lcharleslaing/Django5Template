// Copy prompt functionality and live JSON preview
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('prompt-form');
    const jsonPreview = document.getElementById('json-preview');
    const copyButton = document.getElementById('copy-button');
    
    // Live JSON preview update
    function updateJsonPreview() {
        const formData = new FormData(form);
        const promptData = {
            title: formData.get('title') || '',
            lyrics: formData.get('lyrics') || formData.get('subject') || '',
            styles: formData.get('styles') ? formData.get('styles').split(',').map(s => s.trim()).filter(s => s) : [],
            excluded_styles: formData.get('excluded_styles') ? formData.get('excluded_styles').split(',').map(s => s.trim()).filter(s => s) : [],
            weirdness: parseInt(formData.get('weirdness') || 50),
            style_influence: parseInt(formData.get('style_influence') || 50),
            instrumental: formData.get('is_instrumental') === 'on'
        };
        
        jsonPreview.textContent = JSON.stringify(promptData, null, 2);
    }
    
    // Add event listeners for live updates
    form.addEventListener('input', updateJsonPreview);
    form.addEventListener('change', updateJsonPreview);
    
    // Copy to clipboard functionality
    copyButton.addEventListener('click', async function() {
        try {
            const jsonText = jsonPreview.textContent;
            await navigator.clipboard.writeText(jsonText);
            
            // Show success feedback
            const originalText = copyButton.textContent;
            copyButton.textContent = 'Copied!';
            copyButton.classList.add('btn-success');
            copyButton.classList.remove('btn-primary');
            
            setTimeout(() => {
                copyButton.textContent = originalText;
                copyButton.classList.remove('btn-success');
                copyButton.classList.add('btn-primary');
            }, 2000);
            
        } catch (err) {
            console.error('Failed to copy: ', err);
            // Fallback for older browsers
            const textArea = document.createElement('textarea');
            textArea.value = jsonPreview.textContent;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            
            // Show success feedback
            const originalText = copyButton.textContent;
            copyButton.textContent = 'Copied!';
            copyButton.classList.add('btn-success');
            copyButton.classList.remove('btn-primary');
            
            setTimeout(() => {
                copyButton.textContent = originalText;
                copyButton.classList.remove('btn-success');
                copyButton.classList.add('btn-primary');
            }, 2000);
        }
    });
    
    // Save prompt functionality
    const saveButton = document.getElementById('save-button');
    saveButton.addEventListener('click', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = {
            title: formData.get('title') || '',
            lyrics: formData.get('lyrics') || '',
            subject: formData.get('subject') || '',
            styles: formData.get('styles') || '',
            excluded_styles: formData.get('excluded_styles') || '',
            weirdness: formData.get('weirdness') || 50,
            style_influence: formData.get('style_influence') || 50,
            is_instrumental: formData.get('is_instrumental') === 'on'
        };
        
        try {
            const response = await fetch('/suno-prompt-builder/save/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                },
                body: JSON.stringify(data)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Show success message
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-success mt-4';
                alertDiv.textContent = 'Prompt saved successfully!';
                form.parentNode.insertBefore(alertDiv, form.nextSibling);
                
                // Clear form
                form.reset();
                updateJsonPreview();
                
                // Remove alert after 3 seconds
                setTimeout(() => {
                    alertDiv.remove();
                }, 3000);
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('Error saving prompt:', error);
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-error mt-4';
            alertDiv.textContent = 'Error saving prompt: ' + error.message;
            form.parentNode.insertBefore(alertDiv, form.nextSibling);
            
            setTimeout(() => {
                alertDiv.remove();
            }, 5000);
        }
    });
    
    // Initialize JSON preview
    updateJsonPreview();
});