// Camera control variables
let stream = null;
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const startBtn = document.getElementById('startBtn');
const captureBtn = document.getElementById('captureBtn');
const stopBtn = document.getElementById('stopBtn');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');
const resultBox = document.getElementById('resultBox');
const resultEmotion = document.getElementById('resultEmotion');
const resultDetails = document.getElementById('resultDetails');

/**
 * Start the camera and request user permission
 */
async function startCamera() {
    try {
        // Clear any previous errors
        hideError();
        
        // Request camera access
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                facingMode: 'user'
            }
        });
        
        // Set the stream to the video element
        video.srcObject = stream;
        
        // Update button states
        startBtn.disabled = true;
        captureBtn.disabled = false;
        stopBtn.disabled = false;
        
    } catch (error) {
        console.error('Error accessing camera:', error);
        showError('Camera access denied. Please enable camera permissions and try again.');
        captureBtn.disabled = true;
        stopBtn.disabled = true;
    }
}

/**
 * Stop the camera
 */
function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
        video.srcObject = null;
    }
    
    // Update button states
    startBtn.disabled = false;
    captureBtn.disabled = true;
    stopBtn.disabled = true;
    
    // Hide result box
    resultBox.classList.remove('visible');
}

/**
 * Capture current frame from video and send for emotion detection
 */
async function captureAndDetect() {
    try {
        // Check if video is ready
        if (!video.videoWidth || !video.videoHeight) {
            showError('Video stream not ready. Please wait a moment and try again.');
            return;
        }
        
        // Set canvas dimensions to match video
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        
        // Draw current video frame to canvas
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        
        // Convert canvas to base64 image data
        const imageData = canvas.toDataURL('image/jpeg', 0.9);
        
        // Remove the data URL prefix to get just the base64 string
        const base64Image = imageData.split(',')[1];
        
        // Show loading indicator
        showLoading();
        hideError();
        resultBox.classList.remove('visible');
        
        // Disable capture button during detection
        captureBtn.disabled = true;
        
        // Send image to backend for emotion detection
        const response = await fetch('/api/detect-combined-emotion', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image: base64Image
            })
        });
        
        const result = await response.json();
        
        // Hide loading indicator
        hideLoading();
        
        // Re-enable capture button
        captureBtn.disabled = false;
        
        if (response.ok) {
            // Display the detected emotion
            displayResult(result);
        } else {
            showError(result.error || 'Failed to detect emotion. Please try again.');
        }
        
    } catch (error) {
        console.error('Error capturing or analyzing image:', error);
        hideLoading();
        captureBtn.disabled = false;
        showError('An error occurred during emotion detection. Please try again.');
    }
}

/**
 * Display the emotion detection result
 */
function displayResult(result) {
    const emotion = result.emotion || 'Unknown';
    
    resultEmotion.textContent = emotion;
    
    // Build detailed information
    let details = '';
    if (result.confidence) {
        details += `Confidence: ${(result.confidence * 100).toFixed(1)}%<br>`;
    }
    if (result.custom_emotion) {
        details += `Custom Model: ${result.custom_emotion} (${(result.custom_confidence * 100).toFixed(1)}%)<br>`;
    }
    if (result.deepface_emotion) {
        details += `DeepFace: ${result.deepface_emotion} (${(result.deepface_confidence * 100).toFixed(1)}%)`;
    }
    
    resultDetails.innerHTML = details;
    
    // Show result box
    resultBox.classList.add('visible');
}

/**
 * Show loading indicator
 */
function showLoading() {
    loading.classList.add('active');
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    loading.classList.remove('active');
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('visible');
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.classList.remove('visible');
    errorMessage.textContent = '';
}

/**
 * Initialize: Check for camera support and set up event listeners
 */
document.addEventListener('DOMContentLoaded', function() {
    // Check if browser supports getUserMedia
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showError('Your browser does not support camera access. Please use a modern browser (Chrome, Firefox, Safari, or Edge).');
        startBtn.disabled = true;
    }
});

/**
 * Clean up camera when leaving the page
 */
window.addEventListener('beforeunload', function() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
    }
});
