from app import app, db
from models import ChargeGlossary

# Initial glossary entries
GLOSSARY_DATA = [
    {
        'charge_name': 'Professional Fees',
        'definition': 'Costs for specialist professional advice and consultancy services that are not specifically legal or accounting related.',
        'examples': 'Building surveyor fees, engineering consultations, health & safety consultants, tax advisory services, property management consultants, compliance specialists'
    },
    {
        'charge_name': 'Legal Fees',
        'definition': 'Costs for legal services and solicitor advice.',
        'examples': 'Contract reviews, dispute resolution, legal advice on OMC matters, property law consultations, lease agreements'
    },
    {
        'charge_name': 'Audit & Accountancy',
        'definition': 'Professional accounting services including annual audits and financial statement preparation.',
        'examples': 'Annual audit of accounts, preparation of financial statements, tax compliance, bookkeeping services'
    },
    {
        'charge_name': 'Managing Agent Fees',
        'definition': 'Fees paid to the property management company for day-to-day administration and management of the development.',
        'examples': 'Contract management, supplier coordination, maintenance oversight, AGM organization, financial administration, resident communications'
    },
    {
        'charge_name': 'Building Insurance',
        'definition': 'Insurance coverage for the building structure and common areas.',
        'examples': 'Buildings and contents insurance, public liability insurance, property damage cover, fire insurance'
    },
    {
        'charge_name': 'Electricity charges',
        'definition': 'Electricity costs for common areas and shared facilities.',
        'examples': 'Common area lighting, lift power, gate motors, external lighting, communal heating systems'
    },
    {
        'charge_name': 'Grounds Maintenance',
        'definition': 'Regular upkeep and maintenance of outdoor common areas.',
        'examples': 'Grass cutting, hedge trimming, tree maintenance, landscaping, seasonal planting, weed control'
    },
    {
        'charge_name': 'Cleaning',
        'definition': 'Regular cleaning services for common internal areas.',
        'examples': 'Lobby cleaning, stairwell cleaning, corridor maintenance, communal area upkeep'
    },
    {
        'charge_name': 'Window cleaning',
        'definition': 'Professional cleaning of windows in common areas and building exterior.',
        'examples': 'External window cleaning, communal area glass, entrance door glass'
    },
    {
        'charge_name': 'Bin store cleaning',
        'definition': 'Regular cleaning and maintenance of waste storage areas.',
        'examples': 'Bin store washing, sanitization, odor control, area maintenance'
    },
    {
        'charge_name': 'Domestic Waste Collections',
        'definition': 'Waste collection services for residential units.',
        'examples': 'Regular refuse collection, recycling collection, general waste disposal'
    },
    {
        'charge_name': 'Non-domestic Waste Collections',
        'definition': 'Waste collection services for commercial units.',
        'examples': 'Commercial waste collection, business refuse disposal'
    },
    {
        'charge_name': 'Lift Maintenance',
        'definition': 'Regular servicing and maintenance of lifts/elevators.',
        'examples': 'Quarterly inspections, safety checks, repairs, emergency callouts, compliance certificates'
    },
    {
        'charge_name': 'Gate',
        'definition': 'Maintenance, repairs and operation costs for security gates and access control systems.',
        'examples': 'Gate motor servicing, access control system maintenance, repairs, remote control replacement, security system upkeep'
    },
    {
        'charge_name': 'Building - General Repairs',
        'definition': 'Ongoing repairs and maintenance to the building structure and common areas.',
        'examples': 'Plumbing repairs, electrical repairs, painting, roof repairs, structural maintenance, weatherproofing'
    },
    {
        'charge_name': 'Fire Alarm maintenance and repairs',
        'definition': 'Regular servicing and maintenance of fire safety systems.',
        'examples': 'Fire alarm testing, emergency lighting checks, fire safety equipment maintenance, compliance inspections'
    },
    {
        'charge_name': 'Debt Collection',
        'definition': 'Costs associated with collecting unpaid service charges from owners.',
        'examples': 'Debt collection agency fees, legal costs for arrears, payment reminder services'
    },
    {
        'charge_name': 'Sinking Fund Contribution',
        'definition': 'Annual contribution to the reserve fund for major future capital works and replacements.',
        'examples': 'Building for future roof replacement, exterior painting, major repairs, lift replacement, common area renovations'
    },
    {
        'charge_name': 'Bank Charges',
        'definition': 'Banking fees and transaction costs for the OMC accounts.',
        'examples': 'Account maintenance fees, transaction charges, transfer fees'
    },
    {
        'charge_name': 'Postage & Stationery',
        'definition': 'Costs for postal services and office supplies.',
        'examples': 'Postage for AGM notices, letterheads, envelopes, printing costs, office supplies'
    },
    {
        'charge_name': 'MyBlockman - Annual charge',
        'definition': 'Annual subscription fee for MyBlockman property management software.',
        'examples': 'Online portal access, digital document management, resident communication platform'
    },
    {
        'charge_name': 'Miscellaneous Outlay',
        'definition': 'Small sundry expenses that don\'t fit other categories.',
        'examples': 'Minor purchases, emergency supplies, unforeseen small costs'
    }
]

with app.app_context():
    # Create the table
    db.create_all()
    print("Created charge_glossary table")
    
    # Add glossary entries
    added = 0
    updated = 0
    
    for entry in GLOSSARY_DATA:
        existing = ChargeGlossary.query.filter_by(charge_name=entry['charge_name']).first()
        
        if existing:
            existing.definition = entry['definition']
            existing.examples = entry['examples']
            updated += 1
            print(f"Updated: {entry['charge_name']}")
        else:
            glossary_entry = ChargeGlossary(
                charge_name=entry['charge_name'],
                definition=entry['definition'],
                examples=entry['examples']
            )
            db.session.add(glossary_entry)
            added += 1
            print(f"Added: {entry['charge_name']}")
    
    db.session.commit()
    
    print(f"\n✓ Glossary complete: {added} added, {updated} updated")
    print(f"Total entries: {ChargeGlossary.query.count()}")
