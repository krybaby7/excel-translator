// Excel Translator - Cloud Frontend (Supabase + Vercel)

// Import Supabase client (this will be loaded from CDN in HTML)
// Initialize Supabase client with your project credentials
const SUPABASE_URL = 'https://miodbpwlebiidcvrlvmc.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1pb2RicHdsZWJpaWRjdnJsdm1jIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjAzMjE5MzUsImV4cCI6MjA3NTg5NzkzNX0.WsBJJaXzPCB7gxL8tOdv-tznQv4jGABbvcYV9JKgb0Q';

const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

class ExcelTranslatorCloud {
    constructor() {
        this.uploadArea = document.getElementById('upload-area');
        this.fileInput = document.getElementById('file-input');
        this.fileInfo = document.getElementById('file-info');
        this.fileName = document.getElementById('file-name');
        this.fileSize = document.getElementById('file-size');
        this.removeFileBtn = document.getElementById('remove-file');
        this.translateBtn = document.getElementById('translate-btn');
        this.progressContainer = document.getElementById('progress-container');
        this.progressFill = document.getElementById('progress-fill');
        this.progressText = document.getElementById('progress-text');
        this.resultSection = document.getElementById('result-section');
        this.downloadBtn = document.getElementById('download-btn');
        this.errorMessage = document.getElementById('error-message');
        this.errorText = document.getElementById('error-text');
        this.sourceLang = document.getElementById('source-lang');
        this.targetLang = document.getElementById('target-lang');
        this.swapBtn = document.getElementById('swap-languages');

        this.selectedFile = null;
        this.currentJobId = null;
        this.realtimeChannel = null;

        this.init();
    }

    init() {
        // Upload area events
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', (e) => this.handleDragLeave(e));
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));

        // File input change
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));

        // Remove file button
        this.removeFileBtn.addEventListener('click', () => this.removeFile());

        // Translate button
        this.translateBtn.addEventListener('click', () => this.translateFile());

        // Download button
        this.downloadBtn.addEventListener('click', () => this.downloadFile());

        // Swap languages button
        this.swapBtn.addEventListener('click', () => this.swapLanguages());

        // Smooth scroll for navigation
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({ behavior: 'smooth' });
                }
            });
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    handleFileSelect(e) {
        const files = e.target.files;
        if (files.length > 0) {
            this.processFile(files[0]);
        }
    }

    processFile(file) {
        // Validate file type
        const validExtensions = ['.xls', '.xlsx'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

        if (!validExtensions.includes(fileExtension)) {
            this.showError('Please upload a valid Excel file (.xls or .xlsx)');
            return;
        }

        // Validate file size (4.5MB max for free tier)
        // Vercel free tier has 4.5MB request body limit
        const maxSize = 4.5 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showError('File size must be less than 4.5MB (Upgrade for larger files)');
            return;
        }

        this.selectedFile = file;
        this.showFileInfo(file);
        this.translateBtn.disabled = false;
        this.hideError();
    }

    showFileInfo(file) {
        this.uploadArea.style.display = 'none';
        this.fileInfo.style.display = 'flex';
        this.fileName.textContent = file.name;
        this.fileSize.textContent = this.formatFileSize(file.size);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
    }

    removeFile() {
        this.selectedFile = null;
        this.fileInput.value = '';
        this.uploadArea.style.display = 'block';
        this.fileInfo.style.display = 'none';
        this.translateBtn.disabled = true;
        this.hideError();
        this.hideResult();
        this.unsubscribeRealtime();
    }

    swapLanguages() {
        const temp = this.sourceLang.value;
        this.sourceLang.value = this.targetLang.value;
        this.targetLang.value = temp;
    }

    async translateFile() {
        if (!this.selectedFile) {
            this.showError('Please select a file first');
            return;
        }

        const sourceLang = this.sourceLang.value;
        const targetLang = this.targetLang.value;

        if (sourceLang === targetLang && sourceLang !== 'auto') {
            this.showError('Source and target languages must be different');
            return;
        }

        // Show progress
        this.translateBtn.disabled = true;
        this.showProgress();
        this.hideError();
        this.hideResult();

        try {
            // Convert file to base64
            const fileBase64 = await this.fileToBase64(this.selectedFile);

            // Create translation job via API
            const response = await fetch('/api/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    filename: this.selectedFile.name,
                    file: fileBase64,
                    source_lang: sourceLang === 'auto' ? 'fr' : sourceLang,
                    target_lang: targetLang
                })
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Translation failed');
            }

            const { task_id } = await response.json();
            this.currentJobId = task_id;

            // Subscribe to realtime updates
            this.subscribeToProgress(task_id);

            // Trigger background processing
            await fetch('/api/process_job', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ job_id: task_id })
            });

        } catch (error) {
            this.hideProgress();
            this.showError(error.message || 'An error occurred during translation');
            this.translateBtn.disabled = false;
        }
    }

    fileToBase64(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = () => {
                // Remove data URL prefix (data:*/*;base64,)
                const base64 = reader.result.split(',')[1];
                resolve(base64);
            };
            reader.onerror = error => reject(error);
        });
    }

    subscribeToProgress(jobId) {
        // Unsubscribe from any existing channel
        this.unsubscribeRealtime();

        // Subscribe to translation_jobs table changes for this specific job
        this.realtimeChannel = supabase
            .channel(`translation_job_${jobId}`)
            .on(
                'postgres_changes',
                {
                    event: 'UPDATE',
                    schema: 'public',
                    table: 'translation_jobs',
                    filter: `id=eq.${jobId}`
                },
                (payload) => {
                    this.handleProgressUpdate(payload.new);
                }
            )
            .subscribe();

        // Also poll status endpoint as fallback
        this.pollStatus(jobId);
    }

    async pollStatus(jobId) {
        const maxAttempts = 120; // 2 minutes max polling
        let attempts = 0;

        const poll = async () => {
            if (attempts >= maxAttempts) {
                this.showError('Translation timed out. Please try again.');
                this.hideProgress();
                this.translateBtn.disabled = false;
                return;
            }

            try {
                const response = await fetch(`/api/status?job_id=${jobId}`);
                const data = await response.json();

                this.handleProgressUpdate(data);

                // Continue polling if still processing
                if (data.status === 'processing' || data.status === 'pending') {
                    attempts++;
                    setTimeout(poll, 1000);
                }
            } catch (error) {
                console.error('Polling error:', error);
                attempts++;
                setTimeout(poll, 1000);
            }
        };

        poll();
    }

    handleProgressUpdate(data) {
        // Update progress bar
        const percentage = data.progress_percentage || 0;
        this.progressFill.style.width = percentage + '%';
        this.progressText.textContent = data.progress_message || data.message || 'Processing...';

        // Check if complete
        if (data.status === 'complete') {
            this.hideProgress();
            this.showResult();
            this.unsubscribeRealtime();
        } else if (data.status === 'error') {
            this.hideProgress();
            this.showError(data.error_message || data.error || 'Translation failed');
            this.translateBtn.disabled = false;
            this.unsubscribeRealtime();
        }
    }

    unsubscribeRealtime() {
        if (this.realtimeChannel) {
            supabase.removeChannel(this.realtimeChannel);
            this.realtimeChannel = null;
        }
    }

    async downloadFile() {
        if (!this.currentJobId) {
            this.showError('No translated file available');
            return;
        }

        try {
            const response = await fetch(`/api/download?job_id=${this.currentJobId}`);

            if (!response.ok) {
                throw new Error('Failed to download translated file');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            const baseName = this.selectedFile.name.replace(/\.[^/.]+$/, '');
            a.href = url;
            a.download = `translated_${baseName}.xlsx`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);

            // Reset for next translation
            setTimeout(() => {
                this.removeFile();
                this.hideResult();
                this.currentJobId = null;
            }, 1000);
        } catch (error) {
            this.showError(error.message || 'Failed to download translated file');
        }
    }

    showProgress() {
        this.progressContainer.style.display = 'block';
        this.progressFill.style.width = '0%';
        this.progressText.textContent = 'Starting translation...';
    }

    hideProgress() {
        this.progressFill.style.width = '100%';
        setTimeout(() => {
            this.progressContainer.style.display = 'none';
            this.progressFill.style.width = '0%';
        }, 500);
    }

    showResult() {
        this.resultSection.style.display = 'block';
        this.resultSection.classList.add('fade-in');
    }

    hideResult() {
        this.resultSection.style.display = 'none';
    }

    showError(message) {
        this.errorMessage.style.display = 'flex';
        this.errorText.textContent = message;
        this.errorMessage.classList.add('fade-in');
    }

    hideError() {
        this.errorMessage.style.display = 'none';
    }
}

// Initialize the app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new ExcelTranslatorCloud();
});
