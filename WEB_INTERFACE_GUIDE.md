# Excel Translator - Web Interface Guide

## Overview

The Excel Translator now features a professional, user-friendly web interface that makes it easy to translate Excel files while preserving all formatting, formulas, and styling.

---

## Features

### 🎨 Modern & Professional Design
- Clean, intuitive interface
- Responsive design (works on desktop, tablet, and mobile)
- Smooth animations and transitions
- Professional color scheme

### 📤 Drag & Drop Upload
- Simply drag and drop your Excel file
- Or click to browse and select
- Real-time file validation
- Supports .xls and .xlsx formats

### 🌍 100+ Languages
- Translate between any language pair
- Easy language selection with dropdowns
- Swap languages with one click
- Auto-detect source language option

### 📊 Progress Tracking
- Visual progress indicator during translation
- Real-time status updates
- Estimated time remaining
- Clear error messages if something goes wrong

### ⚡ Fast Processing
- Quick file upload
- Efficient translation
- Instant download of translated files

---

## How to Run

### 1. Install Dependencies

First time setup:
```bash
pip install -r requirements.txt
```

### 2. Start the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

### 3. Open in Browser

Open your browser and navigate to:
```
http://localhost:5000
```

---

## Using the Web Interface

### Step 1: Navigate to the Translator
1. Open http://localhost:5000 in your browser
2. Scroll down to the "Translate Your Excel File" section or click "Start Translating" in the header

### Step 2: Select Languages
1. Choose your source language from the "From" dropdown
2. Choose your target language from the "To" dropdown
3. Use the swap button (⇄) to quickly reverse the language selection

### Step 3: Upload Your File
**Option A: Drag & Drop**
1. Drag your Excel file from your computer
2. Drop it into the upload area

**Option B: Browse**
1. Click anywhere in the upload area
2. Browse to select your Excel file
3. Click "Open"

### Step 4: Translate
1. Review the file information displayed
2. Click the "Translate File" button
3. Wait while the file is being translated (progress bar will show)

### Step 5: Download
1. Once translation is complete, a success message will appear
2. Click "Download Translated File"
3. Your translated file will download automatically

---

## Supported File Formats

- **.xls** - Excel 97-2003 format
- **.xlsx** - Excel 2007+ format

**Maximum file size:** 16MB

---

## Supported Languages

The interface supports 100+ languages including:

| Language | Code |
|----------|------|
| English | en |
| French | fr |
| Spanish | es |
| German | de |
| Italian | it |
| Portuguese | pt |
| Russian | ru |
| Japanese | ja |
| Korean | ko |
| Chinese (Simplified) | zh-CN |
| Arabic | ar |
| Hindi | hi |
| And many more... |

---

## What Gets Preserved

### ✅ Formatting
- Font styles (bold, italic, underline)
- Font sizes and colors
- Cell background colors
- Text alignment
- Borders and gridlines

### ✅ Structure
- All sheets in the workbook
- Sheet names
- Cell merging
- Row and column dimensions

### ✅ Content
- Formulas (remain functional)
- Numbers and dates
- Special characters
- Hyperlinks (preserved but not translated)

---

## Error Handling

The interface provides clear error messages for common issues:

### "Please upload a valid Excel file (.xls or .xlsx)"
- **Cause:** The file is not an Excel file
- **Solution:** Make sure you're uploading a .xls or .xlsx file

### "File size must be less than 16MB"
- **Cause:** The file is too large
- **Solution:** Try reducing the file size or splitting it into multiple files

### "Source and target languages must be different"
- **Cause:** You selected the same language for both source and target
- **Solution:** Choose different languages

### "Translation failed" or API errors
- **Cause:** Network issue or translation API problem
- **Solution:** Check your internet connection and try again

---

## Technical Details

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with flexbox and grid
- **Vanilla JavaScript** - No framework dependencies
- **Responsive Design** - Works on all devices

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin resource sharing
- **Google Translate API** - Translation service
- **openpyxl** - Excel file handling

### API Endpoints

#### `GET /`
Returns the main web interface

#### `POST /translate`
- **Parameters:**
  - `file`: Excel file
  - `source_lang`: Source language code
  - `target_lang`: Target language code
- **Returns:** Translated Excel file

#### `GET /health`
Health check endpoint

#### `GET /languages`
Returns list of supported languages

---

## Browser Compatibility

The interface works on all modern browsers:

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Opera 76+

**Note:** Internet Explorer is not supported

---

## Mobile Support

The interface is fully responsive and works great on:

- 📱 iPhones (iOS 14+)
- 📱 Android phones (Android 10+)
- 📱 Tablets (iPad, Android tablets)

---

## Customization

### Changing Colors

Edit `static/css/style.css` and modify the CSS variables:

```css
:root {
    --primary-color: #4F46E5;  /* Main brand color */
    --secondary-color: #10B981; /* Accent color */
    /* ... other colors ... */
}
```

### Adding Languages

To add more languages to the dropdowns, edit `templates/index.html`:

```html
<option value="language-code">Language Name</option>
```

### Modifying Text

All text is in `templates/index.html` - easy to customize or translate.

---

## Performance Tips

### For Large Files
- Files with 1,000+ cells may take 2-3 minutes
- Files with 10,000+ cells may take 20-30 minutes
- Consider splitting very large files

### For Faster Translation
- Reduce file size by removing unnecessary formatting
- Translate only the sheets you need
- Use a faster internet connection

---

## Security

### File Handling
- Files are processed in temporary directories
- Temporary files are automatically deleted after translation
- No files are stored permanently on the server

### Data Privacy
- Files are translated using Google Translate API
- See Google's privacy policy for details
- For sensitive documents, consider running on a private server

---

## Troubleshooting

### Interface doesn't load
1. Check that Flask is running (python app.py)
2. Verify you're accessing http://localhost:5000
3. Check browser console for errors

### Upload doesn't work
1. Check file size (must be < 16MB)
2. Verify file format (.xls or .xlsx)
3. Try a different browser

### Translation fails
1. Check internet connection
2. Verify API key if you're using one
3. Try with a smaller file
4. Check server logs for errors

### Download doesn't start
1. Check browser's download settings
2. Disable popup blockers
3. Try a different browser

---

## Production Deployment

### Requirements
- Python 3.7+
- Modern web server (Nginx, Apache)
- SSL certificate for HTTPS

### Recommended Setup
1. Use a production WSGI server (Gunicorn, uWSGI)
2. Set up reverse proxy (Nginx)
3. Enable HTTPS
4. Add rate limiting
5. Set up monitoring

### Example Gunicorn Command
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Future Enhancements

Potential features for future versions:

- [ ] User authentication
- [ ] Translation history
- [ ] Batch file processing
- [ ] Progress webhooks
- [ ] Custom glossaries
- [ ] API key management
- [ ] Usage analytics
- [ ] Dark mode
- [ ] Multi-language interface
- [ ] Cloud storage integration

---

## Support

### Getting Help
- Check this guide first
- Review the main [README.md](README.md)
- Check the [TESTING_GUIDE.md](TESTING_GUIDE.md)
- Review server logs for errors

### Reporting Issues
Include the following when reporting issues:
- Browser and version
- File size and format
- Source and target languages
- Error message (if any)
- Steps to reproduce

---

## Credits

**Built with:**
- Flask - Web framework
- Google Translate API - Translation service
- openpyxl - Excel file handling
- Modern web technologies

---

## License

See main [README.md](README.md) for license information.

---

**Last Updated:** 2025-10-12
**Version:** 1.0
**Status:** Production Ready

Enjoy translating your Excel files! 🚀
