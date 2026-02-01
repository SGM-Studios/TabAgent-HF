/**
 * Tab Agent Pro - Webflow API Client
 * Connect your Webflow site to the HuggingFace Space
 * 
 * Usage in Webflow:
 * 1. Add this script to your page (Custom Code → Footer)
 * 2. Replace SPACE_URL with your actual HuggingFace Space URL
 * 3. Use the TabAgentClient class to interact with the API
 */

const SPACE_URL = "https://YOUR_USERNAME-tab-agent-pro.hf.space";

class TabAgentClient {
    constructor(spaceUrl = SPACE_URL) {
        this.spaceUrl = spaceUrl.replace(/\/$/, '');
        this.client = null;
    }

    /**
     * Initialize the Gradio client connection
     */
    async connect() {
        try {
            // Import Gradio client dynamically
            const { Client } = await import("https://cdn.jsdelivr.net/npm/@gradio/client@latest/+esm");
            this.client = await Client.connect(this.spaceUrl);
            console.log("✅ Connected to Tab Agent Pro");
            return true;
        } catch (error) {
            console.error("❌ Failed to connect:", error);
            return false;
        }
    }

    /**
     * Transcribe audio to tablature
     * @param {File} audioFile - Audio file to transcribe
     * @param {Object} options - Transcription options
     * @returns {Object} - { status, zipUrl, tabPreview }
     */
    async transcribe(audioFile, options = {}) {
        if (!this.client) {
            await this.connect();
        }

        const {
            instrument = "Guitar",
            tuning = "Guitar (Standard)",
            includeMidi = true,
            includeTab = true,
            includeJson = true,
            detectSuno = true
        } = options;

        try {
            const result = await this.client.predict("/process_audio", {
                audio_file: audioFile,
                instrument: instrument,
                tuning: tuning,
                include_midi: includeMidi,
                include_tab: includeTab,
                include_json: includeJson,
                detect_suno: detectSuno
            });

            return {
                success: true,
                status: result.data[0],
                zipUrl: result.data[1],
                tabPreview: result.data[2]
            };
        } catch (error) {
            console.error("Transcription failed:", error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    /**
     * Generate audio-reactive video
     * @param {File} audioFile - Audio file
     * @param {Object} options - Video options
     * @returns {Object} - { status, videoUrl }
     */
    async generateVideo(audioFile, options = {}) {
        if (!this.client) {
            await this.connect();
        }

        const {
            style = "guitar_hero",
            customPrompt = "",
            maxSeconds = 10
        } = options;

        try {
            const result = await this.client.predict("/generate_video", {
                video_audio_input: audioFile,
                style_preset: style,
                custom_prompt: customPrompt,
                max_duration: maxSeconds
            });

            return {
                success: true,
                status: result.data[0],
                videoUrl: result.data[1]
            };
        } catch (error) {
            console.error("Video generation failed:", error);
            return {
                success: false,
                error: error.message
            };
        }
    }
}

// ============================================================================
// Webflow Integration Helpers
// ============================================================================

/**
 * Initialize Tab Agent on page load
 */
async function initTabAgent() {
    window.tabAgent = new TabAgentClient();
    await window.tabAgent.connect();
}

/**
 * Handle file upload from Webflow form
 * @param {HTMLInputElement} fileInput - File input element
 * @param {string} type - "transcribe" or "video"
 */
async function handleUpload(fileInput, type = "transcribe") {
    const file = fileInput.files[0];
    if (!file) {
        alert("Please select a file");
        return;
    }

    // Show loading state
    showLoading(true);

    try {
        let result;
        
        if (type === "transcribe") {
            result = await window.tabAgent.transcribe(file, {
                instrument: document.querySelector('[data-instrument]')?.value || "Guitar",
                tuning: document.querySelector('[data-tuning]')?.value || "Guitar (Standard)"
            });

            if (result.success) {
                // Update UI with results
                updateTranscriptionResults(result);
            } else {
                alert("Error: " + result.error);
            }
        } else if (type === "video") {
            result = await window.tabAgent.generateVideo(file, {
                style: document.querySelector('[data-style]')?.value || "guitar_hero",
                maxSeconds: parseInt(document.querySelector('[data-duration]')?.value) || 10
            });

            if (result.success) {
                updateVideoResults(result);
            } else {
                alert("Error: " + result.error);
            }
        }
    } catch (error) {
        console.error("Upload failed:", error);
        alert("Upload failed. Please try again.");
    } finally {
        showLoading(false);
    }
}

/**
 * Update UI with transcription results
 */
function updateTranscriptionResults(result) {
    // Status message
    const statusEl = document.querySelector('[data-status]');
    if (statusEl) {
        statusEl.innerHTML = result.status;
    }

    // Tab preview
    const previewEl = document.querySelector('[data-tab-preview]');
    if (previewEl) {
        previewEl.textContent = result.tabPreview;
    }

    // Download button
    const downloadEl = document.querySelector('[data-download]');
    if (downloadEl && result.zipUrl) {
        downloadEl.href = result.zipUrl;
        downloadEl.style.display = 'block';
    }

    // Show results container
    const resultsEl = document.querySelector('[data-results]');
    if (resultsEl) {
        resultsEl.style.display = 'block';
    }
}

/**
 * Update UI with video results
 */
function updateVideoResults(result) {
    // Status message
    const statusEl = document.querySelector('[data-video-status]');
    if (statusEl) {
        statusEl.innerHTML = result.status;
    }

    // Video player
    const videoEl = document.querySelector('[data-video-player]');
    if (videoEl && result.videoUrl) {
        videoEl.src = result.videoUrl;
        videoEl.style.display = 'block';
    }
}

/**
 * Show/hide loading state
 */
function showLoading(isLoading) {
    const loader = document.querySelector('[data-loader]');
    const content = document.querySelector('[data-content]');
    
    if (loader) {
        loader.style.display = isLoading ? 'flex' : 'none';
    }
    if (content) {
        content.style.opacity = isLoading ? '0.5' : '1';
        content.style.pointerEvents = isLoading ? 'none' : 'auto';
    }
}

// ============================================================================
// Drag & Drop Support
// ============================================================================

function initDragDrop() {
    const dropZones = document.querySelectorAll('[data-dropzone]');
    
    dropZones.forEach(zone => {
        zone.addEventListener('dragover', (e) => {
            e.preventDefault();
            zone.classList.add('drag-over');
        });

        zone.addEventListener('dragleave', () => {
            zone.classList.remove('drag-over');
        });

        zone.addEventListener('drop', (e) => {
            e.preventDefault();
            zone.classList.remove('drag-over');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const fileInput = zone.querySelector('input[type="file"]');
                if (fileInput) {
                    // Create a new FileList-like object
                    const dt = new DataTransfer();
                    dt.items.add(files[0]);
                    fileInput.files = dt.files;
                    
                    // Trigger change event
                    fileInput.dispatchEvent(new Event('change'));
                }
            }
        });
    });
}

// ============================================================================
// Initialize on DOM Ready
// ============================================================================

document.addEventListener('DOMContentLoaded', async () => {
    await initTabAgent();
    initDragDrop();
    
    // Attach handlers to file inputs
    document.querySelectorAll('[data-transcribe-input]').forEach(input => {
        input.addEventListener('change', () => handleUpload(input, 'transcribe'));
    });
    
    document.querySelectorAll('[data-video-input]').forEach(input => {
        input.addEventListener('change', () => handleUpload(input, 'video'));
    });
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { TabAgentClient, initTabAgent, handleUpload };
}
