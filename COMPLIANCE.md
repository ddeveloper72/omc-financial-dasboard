# Compliance and Documentation References

## EU AI Act Compliance

This document outlines how the YTS Budget Analysis application complies with the EU Artificial Intelligence Act (Regulation (EU) 2024/1689) and provides references to relevant documentation.

### 1. AI System Classification

**Classification**: This application is **NOT classified as a high-risk AI system** under the EU AI Act.

**Rationale**:
- The application does not fall under Annex III categories (high-risk AI systems)
- It does not perform critical infrastructure management
- It does not involve biometric identification or categorization of natural persons
- It does not make decisions affecting access to essential services
- It is used for internal management company financial analysis only

**Relevant References**:
- EU AI Act, Article 6: Classification rules for high-risk AI systems
- EU AI Act, Annex III: High-risk AI systems
- Regulation (EU) 2024/1689, adopted by the European Parliament on March 13, 2024

### 2. Application Purpose and Scope

**Primary Purpose**: 
Automated extraction and analysis of service charge data from Owner's Management Company (OMC) AGM documents for financial trend analysis and budget planning.

**Data Processing**:
- **Input**: PDF documents containing financial data (budgets, accounts, AGM minutes)
- **Processing**: Text extraction, data parsing, categorization, and trend analysis
- **Output**: Financial dashboards, charts, and reports
- **No Personal Data**: The system processes only financial service charge data, not personal information

**Relevant Standards**:
- ISO/IEC 23053:2022 - Framework for Artificial Intelligence (AI) Systems Using Machine Learning (ML)
- ISO/IEC 42001:2023 - Information technology — Artificial intelligence — Management system

### 3. Technical Documentation

#### 3.1 Data Sources

**Document Source**:
- Location: `C:\Users\Duncan\OneDrive\Documents\Yewtree Square Stuff\OMC\AGM`
- Document Types:
  - Proposed/Draft Budgets
  - Audited Financial Statements
  - AGM Minutes
  - Financial Reports

**Reference Standards**:
- PDF format specification (ISO 32000-2:2020)
- Companies Act 2014 (Ireland) - Financial reporting requirements for OMCs

#### 3.2 Processing Methods

**PDF Text Extraction**:
- Library: pypdf (Python PDF toolkit)
- Method: Direct text extraction from PDF text layer
- Fallback: None (documents without text layer are flagged as errors)
- Reference: [pypdf Documentation](https://pypdf.readthedocs.io/)

**Data Extraction Algorithm**:
- Pattern matching for financial line items
- Category classification based on charge descriptions
- Year identification from document metadata and content
- Amount parsing with currency normalization (EUR)

**No Machine Learning**:
- This application does NOT use machine learning algorithms
- All processing is rule-based and deterministic
- No training data or models are employed

### 4. Transparency and Documentation

**User Interface Transparency**:
- All data sources are clearly documented
- Processing status is logged and visible
- Error messages provide clear explanations
- Filter selections are always visible on reports

**Audit Trail**:
- Database table: `processing_log` records all document processing attempts
- Timestamps and status codes for each operation
- Error messages captured for troubleshooting

**Relevant EU AI Act Articles**:
- Article 13: Transparency and provision of information to deployers
- Article 52: Transparency obligations for certain AI systems

### 5. Data Governance

**Data Storage**:
- Local SQLite database (not cloud-based)
- No external data transmission
- No third-party API calls
- Database location: `instance/db.sqlite3` (gitignored)

**Data Retention**:
- Historical financial data retained indefinitely for trend analysis
- Documents are not modified or moved
- Original PDFs remain in source directory

**GDPR Compliance**:
- No personal data processing (financial charges only)
- Data minimization principle followed
- Purpose limitation respected (financial analysis only)

**Relevant Regulations**:
- GDPR (Regulation (EU) 2016/679)
- Data Protection Act 2018 (Ireland)

### 6. Technical Architecture References

**Backend Framework**:
- Flask 3.0.0 - [Official Documentation](https://flask.palletsprojects.com/)
- Python 3.13.7 - [Python Documentation](https://docs.python.org/3.13/)

**Database**:
- SQLAlchemy 2.0 - [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- SQLite 3 - [SQLite Documentation](https://www.sqlite.org/docs.html)

**Frontend**:
- Bootstrap 5.3 - [Bootstrap Documentation](https://getbootstrap.com/docs/5.3/)
- Chart.js 4.4 - [Chart.js Documentation](https://www.chartjs.org/docs/latest/)
- Font Awesome 6.5 - [Font Awesome Documentation](https://fontawesome.com/docs)

**PDF Processing**:
- pypdf - [GitHub Repository](https://github.com/py-pdf/pypdf)
- pdfplumber (alternative) - [Documentation](https://github.com/jsvine/pdfplumber)

### 7. Quality Assurance

**Testing Procedures**:
1. Manual verification of extracted data against source PDFs
2. Cross-year consistency checks
3. Category alignment verification
4. Subtotal/total validation to prevent false positives

**Error Handling**:
- Graceful degradation when PDFs cannot be parsed
- Clear error messages logged to database
- Manual correction capabilities through database scripts

**Data Quality Scripts**:
- `fix_gate_subtotal.py` - Corrects misidentified subtotals
- `match_2022_2023_categories.py` - Verifies category consistency
- `verify_alignment.py` - Validates charge alignment across years

### 8. Human Oversight

**Human-in-the-Loop**:
- All extracted data is reviewed through dashboard visualization
- Users can identify and correct errors using utility scripts
- Manual verification of unusual amounts or new charges
- Gap analysis reports require human interpretation

**Decision Support Only**:
- The system provides analysis and visualization
- Final budgeting decisions remain with OMC management
- No automated financial decisions are made

**Relevant EU AI Act Articles**:
- Article 14: Human oversight
- Recital 48: Human oversight should aim at preventing or minimizing risks

### 9. Security Measures

**Access Control**:
- Local application (no remote access)
- Single-user deployment
- No authentication required (private use)

**Data Protection**:
- Local storage only (no cloud transmission)
- Environment variables for sensitive paths
- Database file excluded from version control

### 10. Maintenance and Updates

**Version Control**:
- Git repository: `ddeveloper72/omc-financial-dasboard`
- Commit history provides full audit trail
- GitHub Copilot instructions document development rules

**Update Procedures**:
- Manual dependency updates via `pip`
- Testing after each update
- Database migrations tracked in `migrate_database.py`

**Dependency Management**:
- `requirements.txt` locks all package versions
- Regular security updates for vulnerable packages
- Python 3.13 receives security patches until October 2029

### 11. References and Citations

#### EU Regulations
1. **EU AI Act** - Regulation (EU) 2024/1689 of the European Parliament and of the Council of 13 June 2024 laying down harmonised rules on artificial intelligence
   - [EUR-Lex Official Text](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)

2. **GDPR** - Regulation (EU) 2016/679 on the protection of natural persons with regard to the processing of personal data
   - [EUR-Lex Official Text](https://eur-lex.europa.eu/eli/reg/2016/679/oj)

#### Technical Standards
1. **ISO/IEC 23053:2022** - Framework for Artificial Intelligence (AI) Systems Using Machine Learning (ML)
2. **ISO/IEC 42001:2023** - Artificial Intelligence Management System
3. **ISO 32000-2:2020** - Document management — Portable document format — Part 2: PDF 2.0

#### Irish Legislation
1. **Companies Act 2014** - Financial reporting requirements
   - [Irish Statute Book](https://www.irishstatutebook.ie/eli/2014/act/38/enacted/en/html)

2. **Data Protection Act 2018** - Implementation of GDPR in Ireland
   - [Irish Statute Book](https://www.irishstatutebook.ie/eli/2018/act/7/enacted/en/html)

#### Technical Documentation
1. Flask Framework - https://flask.palletsprojects.com/
2. SQLAlchemy - https://docs.sqlalchemy.org/
3. Chart.js - https://www.chartjs.org/
4. Bootstrap - https://getbootstrap.com/
5. pypdf Library - https://pypdf.readthedocs.io/

### 12. Contact and Responsibility

**Project Owner**: ddeveloper72 (GitHub)  
**Repository**: https://github.com/ddeveloper72/omc-financial-dasboard  
**Purpose**: Private financial analysis tool for Yewtree Square OMC  
**Scope**: Internal use only, not a commercial AI system

### 13. Declaration

This application:
- ✅ Does not use machine learning or AI algorithms as defined in EU AI Act Article 3(1)
- ✅ Processes only financial data, not personal information
- ✅ Is used solely for internal financial analysis
- ✅ Provides transparency through audit logs and documentation
- ✅ Maintains human oversight for all decisions
- ✅ Follows data minimization and purpose limitation principles
- ✅ Complies with GDPR data protection requirements

**Last Updated**: November 27, 2025  
**Review Frequency**: Annually or when EU AI Act requirements change
