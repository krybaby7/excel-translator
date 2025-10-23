"""
Integration tests for Flask API
"""
import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check(self, client):
        """Test that health endpoint returns 200"""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json['status'] == 'healthy'


class TestLanguagesEndpoint:
    """Test languages endpoint"""

    def test_get_languages(self, client):
        """Test getting supported languages"""
        response = client.get('/languages')
        assert response.status_code == 200
        languages = response.json
        assert 'en' in languages
        assert 'fr' in languages
        assert 'es' in languages


class TestTranslateEndpoint:
    """Test translation endpoint"""

    def test_translate_xlsx_file(self, client):
        """Test translating a .xlsx file via API"""
        with open('test_data/simple_french.xlsx', 'rb') as f:
            data = {
                'file': (f, 'simple_french.xlsx'),
                'source_lang': 'fr',
                'target_lang': 'en'
            }
            response = client.post('/translate', data=data, content_type='multipart/form-data')

        assert response.status_code == 200
        assert response.headers['Content-Type'].startswith('application/')

    def test_translate_xls_file(self, client):
        """Test translating a .xls file via API"""
        with open('test_data/old_format.xls', 'rb') as f:
            data = {
                'file': (f, 'old_format.xls'),
                'source_lang': 'fr',
                'target_lang': 'en'
            }
            response = client.post('/translate', data=data, content_type='multipart/form-data')

        assert response.status_code == 200

    def test_translate_no_file(self, client):
        """Test error when no file is provided"""
        response = client.post('/translate', data={}, content_type='multipart/form-data')
        assert response.status_code == 400
        assert 'error' in response.json

    def test_translate_empty_filename(self, client):
        """Test error when filename is empty"""
        from io import BytesIO
        data = {
            'file': (BytesIO(b''), '')
        }
        response = client.post('/translate', data=data, content_type='multipart/form-data')
        assert response.status_code == 400

    def test_translate_with_custom_languages(self, client):
        """Test translation with different language pairs"""
        with open('test_data/simple_french.xlsx', 'rb') as f:
            data = {
                'file': (f, 'simple_french.xlsx'),
                'source_lang': 'fr',
                'target_lang': 'es'
            }
            response = client.post('/translate', data=data, content_type='multipart/form-data')

        assert response.status_code == 200

    def test_translate_default_languages(self, client):
        """Test that default languages are used when not specified"""
        with open('test_data/simple_french.xlsx', 'rb') as f:
            data = {
                'file': (f, 'simple_french.xlsx')
            }
            response = client.post('/translate', data=data, content_type='multipart/form-data')

        assert response.status_code == 200

    def test_translate_multi_sheet_file(self, client):
        """Test translating a file with multiple sheets"""
        with open('test_data/multi_sheet_french.xlsx', 'rb') as f:
            data = {
                'file': (f, 'multi_sheet_french.xlsx'),
                'source_lang': 'fr',
                'target_lang': 'en'
            }
            response = client.post('/translate', data=data, content_type='multipart/form-data')

        assert response.status_code == 200

    @pytest.mark.slow
    @pytest.mark.skip(reason="Large file test takes too long (10k cells), run manually if needed")
    def test_translate_large_file(self, client):
        """Test translating a larger file (marked as slow test - SKIPPED by default)"""
        with open('test_data/large_french.xlsx', 'rb') as f:
            data = {
                'file': (f, 'large_french.xlsx'),
                'source_lang': 'fr',
                'target_lang': 'en'
            }
            response = client.post('/translate', data=data, content_type='multipart/form-data')

        assert response.status_code == 200


class TestConcurrency:
    """Test concurrent requests"""

    def test_multiple_concurrent_uploads(self, client):
        """Test handling multiple file uploads"""
        # This is a simple sequential test
        # For true concurrency testing, you'd need threading/async
        files_to_test = [
            'test_data/simple_french.xlsx',
            'test_data/formatted_french.xlsx',
            'test_data/single_cell.xlsx'
        ]

        for file_path in files_to_test:
            with open(file_path, 'rb') as f:
                data = {
                    'file': (f, os.path.basename(file_path)),
                    'source_lang': 'fr',
                    'target_lang': 'en'
                }
                response = client.post('/translate', data=data, content_type='multipart/form-data')
                assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
