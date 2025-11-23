# YTS Budget Analysis Project - AI Coding Agent Instructions

## Project Overview
This is a Flask-based web application for data mining and visualizing Yewtree Square Owner's Management Company (OMC) service charges from AGM documents. The app extracts budget information from various document formats (PDF, etc.) and presents trend analysis via an interactive dashboard.

## Project Purpose
- Extract service charge data from documents in: `C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\AGM`
- Track service charges over multiple years
- Identify cost trends, new charges, and terminated charges
- Visualize data through a Flask dashboard

## Tech Stack
- **Backend**: Flask (Python 3.13.7)
- **Database**: SQLite (local database - `db.sqlite3`)
- **CSS Framework**: Bootstrap (latest CDN)
- **Icons**: Font Awesome (latest free CDN)
- **Custom Styling**: Separate CSS stylesheet
- **Custom Scripts**: Separate JavaScript file
- **Environment**: `.env` file for secrets
- **Virtual Environment**: `.venv` (already configured)

## Critical Development Rules

### Character Encoding
**CRITICAL**: Never use emoji character codes in any Python scripts. They will break the application. Use only standard ASCII characters and Unicode text when necessary.

### Code Organization
- Flask routes in main application file
- Static assets in `static/` directory:
  - `static/css/` for custom stylesheets
  - `static/js/` for custom JavaScript
- Templates in `templates/` directory
- Document processing utilities in separate modules

### External Resources
- Always use CDN for Bootstrap and Font Awesome (no local copies)
- Keep CDN versions up to date
- Example Bootstrap CDN: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.x/dist/css/bootstrap.min.css`
- Example Font Awesome CDN: `https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.x.x/css/all.min.css`

## Document Processing Strategy

### Data Source
- Source directory: `C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\AGM`
- Multiple subdirectories with various document formats
- Primarily PDF documents containing budget information

### Required Capabilities
1. **Directory traversal** - scan all subdirectories
2. **Document parsing** - extract text from PDFs and other formats
3. **Data identification** - distinguish budget data from other content
4. **Data extraction** - parse service charges, dates, amounts
5. **Data normalization** - standardize extracted information

### Tool Development Guidelines
- Build minimal necessary toolset to avoid MCP server performance degradation
- Reuse existing Python libraries (PyPDF2, pdfplumber, or similar)
- Implement robust error handling for malformed documents
- Log extraction success/failure for monitoring

## Data Model Considerations
- **Database**: SQLite database (`db.sqlite3`)
- Service charge categories (e.g., management fees, insurance, maintenance)
- Temporal data (year, quarter, or specific dates)
- Amount values (currency normalization)
- Status tracking (active, terminated, new)
- Suggested tables:
  - `documents` - track processed AGM documents
  - `service_charges` - extracted charge line items with year, category, amount
  - `charge_categories` - normalize charge types
  - `processing_log` - track parsing success/failures

## Dashboard Features
- Multi-year trend visualization (line charts, bar charts)
- Service charge comparison tables
- Filter by charge category
- Highlight new charges and terminated charges
- Year-over-year percentage changes

## Environment Configuration
- Store sensitive data in `.env` file (never commit to git)
- Required environment variables:
  - `FLASK_SECRET_KEY`
  - `DOCUMENT_SOURCE_PATH` (defaults to `C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\AGM`)
  - `DATABASE_PATH` (defaults to `db.sqlite3`)
- SQLite database file (`db.sqlite3`) should be gitignored

## Permissions & Access
- May require Windows file system permissions to access OneDrive directories
- Implement graceful fallback if directories are inaccessible
- Log permission errors clearly

## Development Workflow
1. Set up virtual environment: `.venv` is already configured
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with required secrets
4. Run Flask app: `flask run` or `python app.py`
5. Access dashboard at `http://localhost:5000`

## Testing Strategy
- Test document parsing with sample PDFs from various years
- Verify data extraction accuracy
- Test dashboard responsiveness across devices
- Validate trend calculations

## Performance Considerations
- Store parsed document data in SQLite to avoid re-processing
- Track document modification times to detect changes
- Use pagination for large datasets in dashboard
- Minimize MCP tool usage to maintain server performance
- Implement lazy loading for document processing
- Create database indexes on frequently queried fields (year, category)

## File Structure (Target)
```
yts-budget/
├── .github/
│   └── copilot-instructions.md (this file)
├── .venv/
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
├── templates/
│   ├── base.html
│   ├── index.html
│   └── dashboard.html
├── utils/
│   ├── document_parser.py
│   ├── data_extractor.py
│   └── budget_analyzer.py
├── .env (gitignored)
├── .gitignore
├── app.py
├── db.sqlite3 (gitignored)
├── requirements.txt
└── README.md
```

## Dependencies to Install
- Flask
- Flask-SQLAlchemy (or raw sqlite3 module - comes with Python)
- python-dotenv
- PDF parsing library (PyPDF2, pdfplumber, or pypdf)
- pandas (for data manipulation)
- Optional: matplotlib/plotly for backend chart generation

## Notes for AI Agents
- This file is read at the start of each new chat session
- Always check this file for project-specific conventions
- When suggesting changes, consider the minimal MCP toolset requirement
- Prioritize code that works on Windows with cmd.exe shell
- Remember: NO EMOJI characters in any code files
