# Excel Translator - Cloud Edition

Translate Excel files between languages while preserving all formatting, formulas, and styles. Now powered by Supabase and Vercel for serverless, scalable cloud deployment.

## ✨ NEW: Cloud Deployment Ready!

Now fully migrated to cloud infrastructure with Supabase + Vercel! Deploy your own scalable translation service in 30 minutes.

**Quick Deploy:**
See [QUICK_START.md](QUICK_START.md) for 30-minute deployment guide.

**Full Guide:**
See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for comprehensive instructions.

**Run Locally:**
```bash
python app.py
# Open http://localhost:5000 in your browser
```

---

## Features

- ✅ **Cloud-Native Architecture** - Serverless, auto-scaling, globally distributed
- ✅ **Real-time Progress Tracking** - Live updates via Supabase Realtime
- ✅ **Professional Web Interface** - Drag & drop, responsive design, beautiful UI
- ✅ Translate Excel files (.xls and .xlsx) between multiple languages
- ✅ Preserve formatting (fonts, colors, borders, alignment)
- ✅ Handle multiple sheets with smart formula translation
- ✅ Support for merged cells, formulas, and special characters
- ✅ RESTful API (Flask locally, Vercel serverless in cloud)
- ✅ Comprehensive test suite (78+ tests)
- ✅ Free tier available (200-300 translations/month)

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Generate Test Data

```bash
python generate_test_data.py
```

### Run the Application

#### Standalone Script

```python
from excel_translator import process_file

# Translate a file
output = process_file("input.xlsx", source_lang="fr", target_lang="en")
print(f"Translated file: {output}")
```

#### Flask API

```bash
python app.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### Health Check
```bash
GET /health
```

#### Get Supported Languages
```bash
GET /languages
```

#### Translate File
```bash
POST /translate
Content-Type: multipart/form-data

Parameters:
- file: Excel file (.xls or .xlsx)
- source_lang: Source language code (default: 'fr')
- target_lang: Target language code (default: 'en')
```

**Example using curl:**
```bash
curl -X POST http://localhost:5000/translate \
  -F "file=@input.xlsx" \
  -F "source_lang=fr" \
  -F "target_lang=en" \
  --output translated_output.xlsx
```

**Example using Python:**
```python
import requests

with open('input.xlsx', 'rb') as f:
    files = {'file': f}
    data = {'source_lang': 'fr', 'target_lang': 'en'}
    response = requests.post('http://localhost:5000/translate',
                            files=files, data=data)

with open('translated.xlsx', 'wb') as f:
    f.write(response.content)
```

## Testing

### Run All Tests

```bash
python run_tests.py
```

Or using pytest directly:

```bash
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest tests/test_unit.py -v

# Integration tests only
pytest tests/test_integration.py -v

# Performance tests
pytest tests/test_performance.py -v -s

# Data integrity tests
pytest tests/test_data_integrity.py -v

# Edge cases
pytest tests/test_edge_cases.py -v
```

### Run with Coverage

```bash
python run_tests.py --coverage
```

### Run Performance Benchmarks

```bash
python run_tests.py --performance
```

## Test Coverage

The test suite includes:

- **Unit Tests:** Test individual functions (conversion, translation)
- **Integration Tests:** Test Flask API endpoints
- **Edge Cases:** Test unusual scenarios (empty cells, special chars, etc.)
- **Performance Tests:** Benchmark translation speed and memory usage
- **Data Integrity Tests:** Verify no data loss or corruption

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing documentation.

## Project Structure

```
Excel Translator/
├── excel_translator.py        # Core translation functions
├── app.py                      # Flask API
├── generate_test_data.py      # Test data generator
├── run_tests.py                # Test runner script
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── README.md                   # This file
├── TESTING_GUIDE.md            # Comprehensive testing guide
├── tests/
│   ├── test_unit.py           # Unit tests
│   ├── test_integration.py    # Integration tests
│   ├── test_edge_cases.py     # Edge case tests
│   ├── test_performance.py    # Performance tests
│   └── test_data_integrity.py # Data integrity tests
├── test_data/                  # Generated test files
└── test_results/               # Test output files
```

## Supported Languages

The translator supports all languages available in Google Translate, including:

- English (en)
- French (fr)
- Spanish (es)
- German (de)
- Italian (it)
- Portuguese (pt)
- Russian (ru)
- Japanese (ja)
- Korean (ko)
- Chinese Simplified (zh-CN)
- Arabic (ar)
- Hindi (hi)
- And many more...

## Known Limitations

1. **Translation Quality:** Cells are translated independently without context
2. **Formatting:** Some advanced Excel features (macros, pivot tables) are not supported
3. **Performance:** Large files (>50,000 cells) may take significant time
4. **File Formats:** Only .xls and .xlsx formats are supported

## Requirements

- Python 3.7+
- openpyxl
- xlrd
- xlwt
- deep-translator
- flask
- pytest (for testing)

## Development

### Adding New Features

1. Write the feature code in `excel_translator.py` or `app.py`
2. Add corresponding tests in the appropriate test file
3. Run the test suite to ensure nothing breaks
4. Update documentation

### Running Tests During Development

```bash
# Watch mode (requires pytest-watch)
pip install pytest-watch
ptw tests/
```

## Cloud Architecture

### Current (v2.0) - Cloud-Native
- **Frontend**: Static HTML/CSS/JS hosted on Vercel
- **Backend**: Vercel Serverless Functions (Python)
- **Database**: Supabase PostgreSQL (job tracking)
- **Storage**: Supabase Storage (file uploads/downloads)
- **Realtime**: Supabase Realtime (progress updates)

### Legacy (v1.0) - Local
- **Frontend**: Static HTML/CSS/JS
- **Backend**: Flask API (Python)
- **Storage**: Local temporary files

## Future Enhancements

- [x] Supabase backend integration for file storage and tracking ✓
- [x] Progress tracking for large files via Realtime ✓
- [ ] User authentication and API keys
- [ ] Support for more file formats (CSV, ODS)
- [ ] Batch translation of multiple files
- [ ] Translation memory to improve consistency
- [ ] Custom glossaries for domain-specific terms
- [ ] Mobile app version

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues or questions:
- Check the [TESTING_GUIDE.md](TESTING_GUIDE.md)
- Review test outputs for detailed error messages
- Open an issue on GitHub

## Acknowledgments

- Google Translate API for translation services
- openpyxl for Excel file handling
- Flask for the web framework
- pytest for the testing framework

---

**Ready for Production?** ✓

Before deploying to production with Supabase:
1. Run the complete test suite: `python run_tests.py`
2. Review the [TESTING_GUIDE.md](TESTING_GUIDE.md)
3. Complete the Pre-Production Checklist
4. Test with real-world files
5. Set up monitoring and logging

Happy translating! 🌍📊
