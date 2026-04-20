"""
RAG (Retrieval-Augmented Generation) module
Creates ChromaDB collection with 10 HR policy documents
Implements retrieval function
"""

import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple


# Initialize embedder
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# HR Policy Documents - 10 comprehensive documents
HR_DOCUMENTS = [
    {
        "id": "doc_1_leave_policy",
        "topic": "Leave Policy",
        "content": """Leave Policy - Comprehensive Guidelines

All employees are entitled to annual leave as per company policy. Employees with less than 1 year of service are entitled to 10 casual leave days. Employees with 1-5 years of service receive 15 casual leave days annually. Employees with more than 5 years of service receive 20 casual leave days annually. Sick leave is unlimited and does not require medical documentation for up to 2 consecutive days. For absences exceeding 2 days, valid medical certification is mandatory. Earned leave must be taken in blocks of at least 1 day and must be approved by the direct manager. Leave cannot be carried forward to the next financial year except in exceptional circumstances approved by HR. Festival holidays are provided as per the national calendar and are paid holidays. Employees must submit leave requests at least 5 working days in advance. In case of emergency, immediate notification to the manager is required. Leave during probation period is limited to 5 days per year. Any unused leave at the end of financial year will be forfeited."""
    },
    {
        "id": "doc_2_working_hours",
        "topic": "Working Hours",
        "content": """Working Hours Policy

Standard working hours for all employees are Monday to Friday, 9:00 AM to 6:00 PM, with a 1-hour lunch break from 1:00 PM to 2:00 PM, making it 8 hours of work per day. The company operates on a 5-day work week. All employees are expected to be at their desks by 9:00 AM. Flexi-time arrangements are available with manager approval, allowing start times between 8:00 AM and 10:00 AM, provided work hours total 8 hours daily. Early departures require manager approval and must be compensated with overtime. Weekend work is compensated at 1.5x normal pay. Overtime during weekdays is paid at 1.5x normal hourly rate. Maximum overtime per week is 10 hours. Employees working overtime must maintain a record in the HR system. Break times are not deducted from working hours. All working hours must be logged in the attendance system."""
    },
    {
        "id": "doc_3_salary_payment",
        "topic": "Salary Payment",
        "content": """Salary and Payment Policy

Salary is paid on the 25th of every month through bank transfer. All salary components including basic pay, HRA, conveyance, and special allowances are credited together. Salary structure is confidential and individual to each employee based on role and experience. Increment reviews occur annually in January. Performance bonus is paid in March based on appraisal ratings. If the 25th falls on a weekend, salary is credited on the last working day before the weekend. Tax deductions follow government guidelines and are automatically deducted. Provident fund contributions are deducted at 12% from salary and matched by the company. Loan facilities are available with HR approval and deducted from monthly salary. Gratuity is payable at the end of employment based on years of service. Medical insurance premiums are deducted monthly. Expense reimbursements are processed within 15 days of submission with valid receipts. Advance salary is available up to 50% of monthly salary with manager approval."""
    },
    {
        "id": "doc_4_attendance_rules",
        "topic": "Attendance Rules",
        "content": """Attendance and Punctuality Rules

Employees must maintain minimum 80% attendance in a financial year to be eligible for annual benefits. Attendance is marked through biometric system or manual entry by supervisor. Late arrival beyond 30 minutes is considered as half-day absence. Employees late by more than 30 minutes must inform their manager before 9:30 AM. Excessive absenteeism (more than 8 unauthorized absences in a month) is grounds for disciplinary action. Unauthorized absence for 3 consecutive days will result in suspension of salary. Attendance records are maintained in the HR system and accessible to employees. Weekly off is Saturday and Sunday. Any deviation from weekly off requires manager and HR approval. Working on weekly off must be compensated with compensatory off within 30 days. Sick leave can be used for 2 consecutive days without documentation. Attendance for remote workers is marked through login in company systems. Employees must clock in and clock out using the attendance system."""
    },
    {
        "id": "doc_5_work_from_home",
        "topic": "Work From Home Policy",
        "content": """Work From Home (WFH) Policy

Employees can apply for work from home up to 3 days per week with manager approval. WFH is not available during probation period. New joiners can apply for WFH after 6 months of service. WFH requests must be submitted 2 days in advance through HR portal. Emergency WFH is allowed with immediate manager notification. During WFH, employees must be available on video calls during designated meeting times. Internet connectivity must be stable; any issues should be reported to IT. Lunch break rules remain the same - 1 hour unpaid break. Overtime during WFH is allowed with manager approval and must be logged. Office attendance is mandatory at least 2 days per week for team collaboration. Employees must maintain professional appearance during video meetings. Home office setup is the employee's responsibility. Company provides VPN access for secure connection. Attendance will be marked through system login and regular status updates. WFH can be revoked if performance or attendance is affected."""
    },
    {
        "id": "doc_6_employee_benefits",
        "topic": "Employee Benefits",
        "content": """Employee Benefits Package

All employees receive comprehensive health insurance covering self and dependent family members. Dental insurance is included in the health insurance package. Life insurance cover is provided up to 5x annual salary for all permanent employees. Maternity benefits include 6 months leave (3 months paid, 3 months unpaid) for female employees. Paternity leave is 15 days for male employees at full pay. Annual medical check-up is free for all employees and their dependents. Wellness programs include yoga classes and gym membership reimbursement. Festival bonuses are given during major festivals. Employee referral program offers rewards up to Rs. 10,000 per successful hire. Skill development training is provided free once per financial year. Commuter benefits include subsidized transportation. Children education scholarship is available for employees with children. Counseling services are available for mental health support. Employees get one complimentary meal per day in office cafeteria."""
    },
    {
        "id": "doc_7_holiday_list",
        "topic": "Holiday List",
        "content": """Company Holiday List - Financial Year 2025-2026

Republic Day - January 26 (Monday) - National Holiday
Holi - March 7-8 - 2 days (Festival Holiday)
Good Friday - April 18 - National Holiday
Eid-ul-Fitr - April 1 (Date subject to moon sighting) - National Holiday
Eid-ul-Adha - June 15 (Date subject to confirmation) - National Holiday
Independence Day - August 15 - National Holiday
Ganesh Chaturthi - September 7 - State Holiday
Dussehra - October 4 - Festival Holiday
Diwali - October 20-21 - 2 days (Festival Holiday)
Thanksgiving - November 28 - Optional Holiday
Christmas - December 25 - National Holiday
New Year - January 1, 2026 - National Holiday
Mahavir Jayanti - April 10 - State Holiday

All employees are entitled to 2 optional holidays which can be taken on any date. Employees must inform HR at least 5 days in advance for optional holiday. In lieu of optional holidays, employees can choose any festival celebration based on their religion. Holidays falling on weekends will not be compensated. If a holiday falls on a working day and an employee cannot take it off, compensation will be provided at 2x normal pay."""
    },
    {
        "id": "doc_8_resignation_policy",
        "topic": "Resignation and Exit Policy",
        "content": """Resignation and Exit Policy

Employees must provide a written resignation notice. Notice period is 30 days for employees below management level and 60 days for management level. During notice period, employee continues to receive full salary and benefits. Employees cannot rescind resignation after 2 weeks of submission. Exit formalities include submission of company assets, access card, and keys. Final salary is processed within 15 days of exit date including pending dues. Full and Final settlement includes: base salary, pending leaves encashed at normal rate, and dues from last working day. Employees are required to hand over all ongoing projects and documentation. Relieving letter is issued after completion of all formalities. Employees are subject to 6-month non-compete clause after resignation. Experience certificate is issued on request after proper notice period is completed. Employees on probation must give 7 days notice. Employees cannot be terminated without 30 days notice during employment. Employees are eligible for gratuity after 5 years of continuous service."""
    },
    {
        "id": "doc_9_dress_code",
        "topic": "Dress Code Policy",
        "content": """Dress Code and Professional Conduct

Office dress code is business formal on all working days. For male employees: formal shirts/shirts with tie or without tie, formal trousers, and formal shoes. For female employees: formal shirts, blouses, sarees, or formal dress with formal footwear. Friday dress code is business casual: formal shirts without tie, chinos/formal trousers, and shoes. Jeans, t-shirts, and casual wear are not permitted in office except on designated casual days. Casual Fridays occur once a month with prior announcement. Employees meeting with clients must wear formal attire regardless of day. Sneakers and sports shoes are not permitted except during office sports activities. During remote work, professional appearance during video calls is mandatory. Grooming standards: neat hair, clean appearance, and minimal jewelry. Footwear must be closed-toe in office premises. No promotional clothing or offensive prints allowed. Violation of dress code will result in a warning. Employees must ensure uniform appearance at company events. Exception for dress code can be granted for medical or religious reasons."""
    },
    {
        "id": "doc_10_id_card_rules",
        "topic": "ID Card and Access Rules",
        "content": """Employee ID Card and Office Access Policy

All employees must wear company ID card at all times in office premises. ID card must display employee name, employee ID, photo, and validity date. New joiners receive ID card on day 1 of employment. ID card validity is for 2 years from date of issue. Renewal of ID card is done 30 days before expiry through HR department. Replacement ID card is issued within 3 days in case of loss or damage. Replacement fee is Rs. 100 for damaged ID card. Lost ID card must be reported immediately to security and HR. ID card grants access to office building, parking, and facilities. Access levels are based on designation and department. Contractors and visitors must wear temporary ID issued by security. ID card should not be given to anyone else; unauthorized access using another's card is disciplinary offense. Biometric system also tracks entry and exit automatically. During notice period or termination, ID card must be surrendered. After resignation, access is revoked immediately. Duplicate ID card should be immediately reported to HR. Any misuse of ID card can result in termination."""
}
]


def initialize_chromadb() -> chromadb.Collection:
    """
    Initialize ChromaDB collection with HR policy documents.
    Creates persistent in-memory collection with embeddings.
    
    Returns:
        chromadb.Collection: Initialized collection with documents
    """
    # Create client (in-memory)
    client = chromadb.Client()
    
    # Create collection
    collection = client.get_or_create_collection(
        name="hr_policies",
        metadata={"hnsw:space": "cosine"}
    )
    
    # Prepare documents, embeddings, and metadata
    documents = []
    embeddings = []
    ids = []
    metadatas = []
    
    for doc in HR_DOCUMENTS:
        documents.append(doc["content"])
        embeddings.append(embedder.encode(doc["content"]).tolist())
        ids.append(doc["id"])
        metadatas.append({
            "topic": doc["topic"],
            "source": f"HR Policy - {doc['topic']}"
        })
    
    # Add documents to collection
    collection.add(
        documents=documents,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )
    
    return collection


def retrieve_documents(query: str, collection: chromadb.Collection, top_k: int = 3) -> Tuple[str, List[Dict]]:
    """
    Retrieve top-k most relevant documents from ChromaDB.
    
    Args:
        query: User question or query
        collection: ChromaDB collection
        top_k: Number of documents to retrieve (default 3)
    
    Returns:
        Tuple of (formatted_context_string, list_of_source_metadata)
    """
    # Encode query
    query_embedding = embedder.encode(query).tolist()
    
    # Query collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    # Format retrieved documents
    context_parts = []
    sources = []
    
    if results["documents"] and len(results["documents"]) > 0:
        for i, (doc, metadata) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
            topic = metadata.get("topic", "Unknown")
            context_parts.append(f"[{topic}]\n{doc}")
            sources.append({
                "topic": topic,
                "source": metadata.get("source", "Unknown"),
                "rank": i + 1
            })
    
    formatted_context = "\n\n---\n\n".join(context_parts) if context_parts else ""
    
    return formatted_context, sources
