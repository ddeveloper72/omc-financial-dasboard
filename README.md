# YTS Budget Analysis

A Flask-based web application for data mining and visualizing Yewtree Square Owner's Management Company (OMC) service charges from AGM documents.

**Documentation**: See [COMPLIANCE.md](COMPLIANCE.md) for EU AI Act compliance, data governance, and technical documentation references.

## Features

- **Document Processing**: Automatically scan and extract data from PDF documents
- **Data Extraction**: Extract service charge information (amounts, categories, dates)
- **Trend Analysis**: Visualize service charges over multiple years
- **Interactive Dashboard**: Filter and explore charges by year and category
- **Cost Tracking**: Identify new charges, terminated charges, and cost trends

## Tech Stack

- **Backend**: Flask (Python 3.13.7)
- **Database**: SQLite
- **Frontend**: Bootstrap 5.3, Font Awesome 6.5, Chart.js 4.4
- **PDF Processing**: pypdf
- **Data Analysis**: pandas

## Installation

1. **Clone the repository**
   ```cmd
   git clone <repository-url>
   cd yts-budget
   ```

2. **Activate virtual environment** (already created)
   ```cmd
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Configure environment**
   - The `.env` file is already configured
   - Update `DOCUMENT_SOURCE_PATH` if your AGM documents are in a different location

## Usage

1. **Start the application**
   ```cmd
   python app.py
   ```

2. **Access the application**
   - Open browser to `http://localhost:5000`

3. **Scan documents**
   - Click "Scan Documents" on the home page
   - The app will search for PDFs in the configured directory

4. **View dashboard**
   - Click "View Dashboard" to see trends and analysis
   - Use filters to explore data by year and category

## Project Structure

```
yts-budget/
├── .github/
│   └── copilot-instructions.md    # AI coding agent instructions
├── .venv/                          # Virtual environment
├── static/
│   ├── css/
│   │   └── style.css              # Custom styles
│   └── js/
│       └── main.js                # Custom JavaScript
├── templates/
│   ├── base.html                  # Base template
│   ├── index.html                 # Home page
│   └── dashboard.html             # Dashboard page
├── utils/
│   ├── document_scanner.py        # Directory scanning utility
│   ├── pdf_parser.py              # PDF text extraction
│   └── budget_extractor.py        # Budget data extraction
├── .env                           # Environment variables (not in git)
├── .gitignore                     # Git ignore rules
├── app.py                         # Main Flask application
├── models.py                      # Database models
├── db.sqlite3                     # SQLite database (not in git)
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Database Schema

### Tables

- **documents**: Track processed AGM documents
- **service_charges**: Extracted charge line items with year, category, amount
- **charge_categories**: Normalize charge types
- **processing_log**: Track parsing success/failures

## API Endpoints

- `GET /` - Home page
- `GET /dashboard` - Dashboard page
- `POST /api/scan-documents` - Scan directory for documents
- `POST /api/process-document/<id>` - Process a single document
- `GET /api/charges` - Get all charges (with optional filters)
- `GET /api/trends` - Get year-over-year trend data
- `GET /api/categories` - Get all charge categories

## Development

### Important Rules

- **No emoji characters**: Never use emoji character codes in Python scripts
- **Windows paths**: Use proper Windows path formatting
- **Virtual environment**: Always use the `.venv` environment
- **MCP performance**: Keep toolset minimal to avoid performance degradation

### Running Tests

Currently, document processing should be tested manually:
1. Ensure AGM documents are in the configured directory
2. Run the scan and process operations through the UI
3. Verify extracted data in the dashboard

## Environment Variables

- `FLASK_SECRET_KEY` - Flask session secret key
- `FLASK_ENV` - Environment (development/production)
- `FLASK_DEBUG` - Debug mode (True/False)
- `DOCUMENT_SOURCE_PATH` - Path to AGM documents directory
- `DATABASE_PATH` - Path to SQLite database file

## Troubleshooting

### Permission Errors
If you get permission errors when scanning documents:
- Ensure OneDrive is synced and files are downloaded
- Check Windows file permissions on the AGM folder

### PDF Extraction Issues
If PDF text extraction fails:
- Verify PDF is not encrypted
- Check if PDF contains actual text (not just images)
- Review processing logs in the database

## Compliance and Legal

### EU AI Act Compliance
This application complies with the EU Artificial Intelligence Act (Regulation (EU) 2024/1689). For detailed compliance documentation, see [COMPLIANCE.md](COMPLIANCE.md).

**Key Points**:
- Not classified as a high-risk AI system (EU AI Act, Article 6)
- No machine learning or AI algorithms employed
- Rule-based data extraction and analysis only
- Processes financial data only (no personal data)
- Full transparency and human oversight maintained

### Data Protection
- GDPR compliant (Regulation (EU) 2016/679)
- Data Protection Act 2018 (Ireland)
- Local data storage only
- No personal data processing

### Documentation References
All technical standards, regulations, and documentation sources are listed in [COMPLIANCE.md](COMPLIANCE.md), including:
- EU AI Act and GDPR official texts
- ISO/IEC standards for AI systems
- Technical library documentation
- Irish Companies Act requirements

## License

Private project for Yewtree Square OMC

## Contributing

This is a private project. Please contact the owner for contribution guidelines.

## References

- **EU AI Act**: [EUR-Lex Official Text](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- **GDPR**: [EUR-Lex Official Text](https://eur-lex.europa.eu/eli/reg/2016/679/oj)
- **Project Documentation**: [COMPLIANCE.md](COMPLIANCE.md)
