// Excel Translator - Frontend JavaScript

class ExcelTranslator {
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
        this.translatedBlob = null;

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
        const validTypes = [
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        ];
        const validExtensions = ['.xls', '.xlsx'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

        if (!validExtensions.includes(fileExtension)) {
            this.showError('Please upload a valid Excel file (.xls or .xlsx)');
            return;
        }

        // Validate file size (16MB max)
        const maxSize = 16 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showError('File size must be less than 16MB');
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

        // Create form data
        const formData = new FormData();
        formData.append('file', this.selectedFile);
        formData.append('source_lang', sourceLang === 'auto' ? 'fr' : sourceLang);
        formData.append('target_lang', targetLang);

        try {
            // Start translation and get task ID
            const response = await fetch('/translate', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Translation failed');
            }

            const { task_id } = await response.json();

            // Connect to progress stream
            await this.watchProgress(task_id);

        } catch (error) {
            this.hideProgress();
            this.showError(error.message || 'An error occurred during translation');
            this.translateBtn.disabled = false;
        }
    }

    async watchProgress(taskId) {
        return new Promise((resolve, reject) => {
            const eventSource = new EventSource(`/progress/${taskId}`);

            eventSource.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);

                    if (data.error) {
                        eventSource.close();
                        reject(new Error(data.error));
                        return;
                    }

                    // Update progress bar
                    const percentage = data.total > 0 ? Math.round((data.current / data.total) * 100) : 0;
                    this.progressFill.style.width = percentage + '%';
                    this.progressText.textContent = data.message;

                    // Check if complete
                    if (data.status === 'complete') {
                        eventSource.close();
                        this.downloadTranslatedFile(taskId);
                        resolve();
                    } else if (data.status === 'error') {
                        eventSource.close();
                        reject(new Error(data.message));
                    }
                } catch (error) {
                    eventSource.close();
                    reject(error);
                }
            };

            eventSource.onerror = (error) => {
                eventSource.close();
                reject(new Error('Connection to server lost'));
            };
        });
    }

    async downloadTranslatedFile(taskId) {
        try {
            const response = await fetch(`/download/${taskId}`);

            if (!response.ok) {
                throw new Error('Failed to download translated file');
            }

            this.translatedBlob = await response.blob();

            // Show success
            this.hideProgress();
            this.showResult();

        } catch (error) {
            this.hideProgress();
            this.showError(error.message || 'Failed to download translated file');
            this.translateBtn.disabled = false;
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

    downloadFile() {
        if (!this.translatedBlob) {
            this.showError('No translated file available');
            return;
        }

        const url = window.URL.createObjectURL(this.translatedBlob);
        const a = document.createElement('a');
        // Remove any existing extension and ensure .xlsx
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
            this.translatedBlob = null;
        }, 1000);
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
    new ExcelTranslator();
});
