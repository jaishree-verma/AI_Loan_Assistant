#!/usr/bin/env python3
"""
AGENCY AI BANKING CHATBOT - COMPLETE WORKING PROTOTYPE
Master Agent orchestrates Worker Agents for end-to-end loan sales

Run: python app.py
Access: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from io import BytesIO
import re

# ==================== HELPERS ====================

def is_yes(text: str) -> bool:
    t = text.strip().lower()
    return t in ["yes", "yeah", "yep", "ok", "okay", "sure", "confirm"]

def is_no(text: str) -> bool:
    t = text.strip().lower()
    return t in ["no", "nope", "nah"]

# ==================== MOCK DATA ====================

CRM_DATABASE = {
    "9876543210": {
        "name": "Rahul Kumar",
        "age": 28,
        "city": "Bangalore",
        "phone": "9876543210",
        "pan": "AAUPA1234K",
        "address": "123 MG Road, Bangalore",
        "salary": 50000,
        "existing_loans": [{"type": "auto", "emi": 8000}],
        "pre_approved_limit": 200000
    },
    "8765432109": {
        "name": "Priya Sharma",
        "age": 26,
        "city": "Delhi",
        "phone": "8765432109",
        "pan": "BBUPB5678L",
        "address": "456 Park St, Delhi",
        "salary": 45000,
        "existing_loans": [],
        "pre_approved_limit": 180000
    },
    "7654321098": {
        "name": "Amit Patel",
        "age": 32,
        "city": "Mumbai",
        "phone": "7654321098",
        "pan": "CCUPC9012M",
        "address": "789 Marine Drive, Mumbai",
        "salary": 60000,
        "existing_loans": [{"type": "home", "emi": 25000}],
        "pre_approved_limit": 250000
    },
    "6543210987": {
        "name": "Neha Singh",
        "age": 29,
        "city": "Pune",
        "phone": "6543210987",
        "pan": "DDUPD3456N",
        "address": "321 Bund Garden, Pune",
        "salary": 40000,
        "existing_loans": [],
        "pre_approved_limit": 150000
    },
    "5432109876": {
        "name": "Vikas Verma",
        "age": 35,
        "city": "Hyderabad",
        "phone": "5432109876",
        "pan": "EEPUE7890O",
        "address": "654 HITEC City, Hyderabad",
        "salary": 55000,
        "existing_loans": [{"type": "auto", "emi": 12000}],
        "pre_approved_limit": 220000
    },
    "4321098765": {
        "name": "Anjali Desai",
        "age": 27,
        "city": "Ahmedabad",
        "phone": "4321098765",
        "pan": "FFUPF2345P",
        "address": "987 CG Road, Ahmedabad",
        "salary": 48000,
        "existing_loans": [],
        "pre_approved_limit": 190000
    },
    "3210987654": {
        "name": "Ravi Tiwari",
        "age": 31,
        "city": "Jaipur",
        "phone": "3210987654",
        "pan": "GGUPG6789Q",
        "address": "147 MI Road, Jaipur",
        "salary": 52000,
        "existing_loans": [{"type": "personal", "emi": 6000}],
        "pre_approved_limit": 210000
    },
    "2109876543": {
        "name": "Sneha Nair",
        "age": 25,
        "city": "Kochi",
        "phone": "2109876543",
        "pan": "HHUGH1234R",
        "address": "258 Fort Kochi, Kochi",
        "salary": 42000,
        "existing_loans": [],
        "pre_approved_limit": 160000
    },
    "1098765432": {
        "name": "Nikhil Reddy",
        "age": 33,
        "city": "Bangalore",
        "phone": "1098765432",
        "pan": "IIPUI5678S",
        "address": "369 Koramangala, Bangalore",
        "salary": 58000,
        "existing_loans": [{"type": "auto", "emi": 10000}],
        "pre_approved_limit": 230000
    },
    "9123456789": {
        "name": "Divya Kapoor",
        "age": 30,
        "city": "NCR",
        "phone": "9123456789",
        "pan": "JJUPJ9012T",
        "address": "741 Golf Course Rd, Gurgaon",
        "salary": 51000,
        "existing_loans": [],
        "pre_approved_limit": 205000
    }
}

# Mock Credit Bureau - Credit Scores
CREDIT_SCORES = {
    "AAUPA1234K": 750,
    "BBUPB5678L": 680,  # Low score
    "CCUPC9012M": 800,
    "DDUPD3456N": 720,
    "EEPUE7890O": 765,
    "FFUPF2345P": 700,
    "GGUPG6789Q": 810,
    "HHUGH1234R": 740,
    "IIPUI5678S": 695,  # Low score
    "JJUPJ9012T": 755
}

# ==================== AGENT RESPONSES ====================

def sales_agent_response(customer_name, loan_amount, tenure_months, purpose):
    base_rate = 12.0
    emi_per_lakh = 3220
    emi = (loan_amount / 100000) * emi_per_lakh * (tenure_months / 36)

    response = f"""
Great choice, {customer_name}! 💡

For a ₹{loan_amount:,} personal loan over {tenure_months} months, here is a tailored offer:

• Loan Amount: ₹{loan_amount:,}
• Tenure: {tenure_months} months ({tenure_months//12} years)
• Indicative Interest Rate: {base_rate}% p.a.
• Estimated Monthly EMI: ₹{int(emi):,}
• Estimated Total Payable: ₹{int(loan_amount + (emi * tenure_months)):,}

If this looks reasonable, we will proceed with your verification as per  Non-Banking Financial Company's personal loan policy.
"""
    return response.strip()

def verification_agent_response(customer, verified):
    if verified:
        return f"""
KYC verification completed as per RBI and Non-Banking Financial Company guidelines.

Verified profile:
• Name: {customer['name']}
• Registered Mobile: {customer['phone']}
• Address: {customer['address']}
• PAN: {customer['pan']}
• City: {customer['city']}

Proceeding to credit assessment and eligibility evaluation.
"""
    else:
        return "Unable to find your record. Please re-enter your registered mobile number."

def underwriting_agent_response(customer, loan_amount, tenure, credit_score, eligible, reason=""):
    pre_approved = customer['pre_approved_limit']

    if credit_score < 700:
        return f"""
Credit assessment result: Not approved.

• Credit score: {credit_score}/900 (below internal cut-off of 700)
• Requested amount: ₹{loan_amount:,}
• Indicative pre-approved limit: ₹{pre_approved:,}

You may improve your credit profile (timely repayments, lower utilization) and reapply after a few months.
"""
    elif loan_amount <= pre_approved:
        return f"""
Pre‑approved criteria met. Your request qualifies for instant approval.

• Credit score: {credit_score}/900
• Pre‑approved limit: ₹{pre_approved:,}
• Requested amount: ₹{loan_amount:,}

We will now generate a formal sanction letter with final terms and conditions.
"""
    elif loan_amount <= 2 * pre_approved:
        return f"""
Requested amount is higher than your current pre‑approved limit but within the permissible extended range.

• Credit score: {credit_score}/900
• Pre‑approved limit: ₹{pre_approved:,}
• Requested amount: ₹{loan_amount:,}

To proceed, please provide your latest salary slip so we can confirm that the EMI remains within 50% of your net monthly income.
"""
    else:
        return f"""
Requested amount exceeds the maximum permissible limit on your current profile.

• Pre‑approved limit: ₹{pre_approved:,}
• Maximum permissible (2x limit): ₹{2 * pre_approved:,}
• Requested amount: ₹{loan_amount:,}

You may proceed with a lower amount up to ₹{2 * pre_approved:,} or within your pre‑approved limit for faster approval.
"""

def sanction_agent_response(customer, loan_amount, tenure, emi):
    return f"""
Loan approved in principle.

Key sanction details:
• Applicant: {customer['name']}
• Approved Amount: ₹{loan_amount:,}
• Tenure: {tenure} months
• Indicative EMI: ₹{int(emi):,} (subject to final agreement)
• Indicative Rate of Interest: 12.0% p.a.
• Sanction Date: {datetime.now().strftime('%d-%b-%Y')}
A detailed sanction letter in PDF format is ready for download. Please review the terms and confirm your acceptance to proceed towards disbursal.
"""

# ==================== PERSUASIVE FOLLOW-UP LOGIC ====================

def persuasive_followup_response(user_message):
    text = user_message.lower()

    if "emi" in text or "installment" in text:
        return (
            "Thank you for sharing that the EMI feels high.\n\n"
            "We can explore either a slightly lower loan amount or a longer tenure so that the EMI fits comfortably "
            "within your monthly budget. Would you like to see one or two lower‑EMI options before deciding?"
        )

    if "interest" in text or "rate" in text or "other bank" in text or "another bank" in text:
        return (
            "Comparing interest rates is a good step.\n\n"
            "The advantage of this offer is that it is already pre‑screened on your profile, so you can get a decision "
            "and sanction letter within minutes. I can also show you a clear EMI and total‑interest breakup so you "
            "can compare with other lenders. Would you like to see that?"
        )

    if "not now" in text or "later" in text or "think" in text or "maybe" in text:
        return (
            "It is completely fine to take time to think.\n\n"
            "However, pre‑approved offers can change if your income or credit profile changes. If you wish, I can show "
            "you two quick scenarios—taking the loan now versus later—so you can decide more confidently."
        )

    if ("not interested" in text or "don't want" in text or "dont want" in text or
        text.strip() == "no" or "no thanks" in text or "no thank" in text):
        return (
            "Understood. It is good to be cautious before taking a loan.\n\n"
            "May I know what concerns you the most—EMI amount, interest rate, or adding a new commitment? If you share "
            "one main concern, I can either adjust the offer or honestly tell you if it is better not to take a loan now."
        )

    return (
        "Thank you for sharing your view.\n\n"
        "Before we close this, is there any specific concern—EMI size, rate of interest, impact on credit score, or "
        "existing EMIs—that you would like clarity on? I can answer that directly so you can decide comfortably."
    )

# ==================== APPLICATION STATE ====================

class LoanApplication:
    def __init__(self, customer_id):
        self.customer_id = customer_id
        self.stage = "intro"
        self.messages = []
        self.customer = None
        self.loan_amount = 0
        self.tenure = 0
        self.purpose = ""
        self.credit_score = 0
        self.status = "pending"
        self.emi = 0
        self.salary_verified = False
        self.monthly_salary = 0

    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "stage": self.stage,
            "status": self.status,
            "loan_amount": self.loan_amount,
            "tenure": self.tenure,
            "emi": self.emi,
            "messages": self.messages
        }

app_sessions = {}

# ==================== FLASK APP ====================

app = Flask(__name__)
CORS(app)

def extract_phone_number(text):
    match = re.search(r'\b\d{10}\b', text)
    return match.group(0) if match else None

def extract_loan_amount(text):
    text = text.lower()
    lakh_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lakh|lac|l)', text)
    if lakh_match:
        return int(float(lakh_match.group(1)) * 100000)
    number_match = re.search(r'₹?(\d{4,8})', text)
    if number_match:
        amount = int(number_match.group(1))
        if amount > 1000:
            return amount
    return None

def extract_tenure(text):
    text = text.lower()
    years_match = re.search(r'(\d+)\s*(?:year|yr)', text)
    if years_match:
        return int(years_match.group(1)) * 12
    months_match = re.search(r'(\d+)\s*(?:month|mon)', text)
    if months_match:
        return int(months_match.group(1))
    return None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip()
    session_id = data.get('session_id', 'default')

    if session_id not in app_sessions:
        app_sessions[session_id] = LoanApplication(session_id)

    app_data = app_sessions[session_id]
    app_data.messages.append({"role": "user", "content": user_message})

    agent_response = ""
    next_stage = app_data.stage
    text_lower = user_message.lower()

    # Global persuasive handling in sales-like stages
    if app_data.stage in ["sales", "underwriting", "salary_verification"]:
        if any(phrase in text_lower for phrase in [
            "not interested", "dont want", "don't want",
            "leave it", "cancel", "drop", "no thanks", "no thank",
        ]) or text_lower.strip() == "no":
            agent_response = persuasive_followup_response(user_message)
            next_stage = app_data.stage
            app_data.stage = next_stage
            app_data.messages.append({"role": "assistant", "content": agent_response})
            return jsonify({
                "response": agent_response,
                "stage": next_stage,
                "status": app_data.status,
                "session_id": session_id,
                "customer": app_data.customer['name'] if app_data.customer else None,
                "loan_amount": app_data.loan_amount,
                "emi": int(app_data.emi) if app_data.emi else 0
            })

    # ========== MASTER AGENT ORCHESTRATION LOGIC ==========

    if app_data.stage == "intro":
        if any(p in text_lower for p in ["not interested", "dont want", "don't want"]) or text_lower.strip() == "no":
            agent_response = persuasive_followup_response(user_message)
            next_stage = "intro"
        elif (
            "yes" in text_lower
            or "ok" in text_lower
            or any(word in text_lower for word in ["loan", "need", "borrow", "interest", "emi","education", "travel", "home", "renovation", "wedding", "upgrade"])
        ):
            agent_response = (
                "Great, that sounds like an important goal.\n\n"
                "To check a personal loan offer with instant eligibility, please share your 10‑digit mobile number "
                "registered with Non-Banking Financial Company so we can retrieve your profile as per KYC guidelines."
            )
            next_stage = "getting_phone"
        else:
            agent_response = (
                "Welcome to Non-Banking Financial Company.\n\n"
                "If you wish to check a personal loan offer, you can say something like \"I need a loan\" or simply \"yes\"."
            )

    elif app_data.stage == "getting_phone":
        phone = extract_phone_number(user_message)
        if phone and phone in CRM_DATABASE:
            app_data.customer = CRM_DATABASE[phone]
            agent_response = (
                f"Thank you. Your profile has been retrieved.\n\n"
                f"Customer: {app_data.customer['name']} ({app_data.customer['city']})\n\n"
                "Please mention:\n"
                "1) Required loan amount (e.g., 2 lakh or 200000)\n"
                "2) Preferred tenure (e.g., 3 years or 36 months)\n"
                "3) Purpose of the loan (e.g., wedding, education, home renovation)."
            )
            next_stage = "sales"
        elif phone:
            agent_response = (
                f"No customer record was found for {phone}.\n"
                "Please re-enter the registered mobile number, or use an existing customer number."
            )
        else:
            agent_response = "Please provide a valid 10-digit mobile number to proceed with your application."

    elif app_data.stage == "sales":
        loan_amount = extract_loan_amount(user_message)
        tenure = extract_tenure(user_message)

        if loan_amount and tenure:
            app_data.loan_amount = loan_amount
            app_data.tenure = tenure
            app_data.purpose = user_message

            base_rate = 12.0
            monthly_rate = base_rate / 12 / 100
            emi = loan_amount * (monthly_rate * (1 + monthly_rate)**tenure) / ((1 + monthly_rate)**tenure - 1)
            app_data.emi = emi

            agent_response = sales_agent_response(
                app_data.customer['name'],
                loan_amount,
                tenure,
                app_data.purpose
            )
            next_stage = "verification"
        else:
            agent_response = (
                "To proceed, please mention both amount and tenure in one message.\n"
                "Example: \"I need 2 lakh for 3 years for my wedding\"."
            )

    elif app_data.stage == "verification":
        if "confirm" in text_lower or "yes" in text_lower or "ok" in text_lower:
            verified = True
            agent_response = verification_agent_response(app_data.customer, verified)
            next_stage = "underwriting"
        else:
            agent_response = (
                "Please confirm that the displayed KYC details are correct by replying \"yes\" or \"confirm\" "
                "so that we can proceed to credit assessment."
            )

    elif app_data.stage == "underwriting":
        if app_data.credit_score == 0:
            app_data.credit_score = CREDIT_SCORES.get(app_data.customer['pan'], 700)

        loan_amount = app_data.loan_amount
        pre_approved = app_data.customer['pre_approved_limit']
        credit_score = app_data.credit_score
        tenure = app_data.tenure

        if credit_score < 700:
            agent_response = underwriting_agent_response(
                app_data.customer, loan_amount, tenure, credit_score, False, "Low credit score"
            )
            app_data.status = "rejected"
            next_stage = "end"
        elif loan_amount <= pre_approved:
            agent_response = underwriting_agent_response(
                app_data.customer, loan_amount, tenure, credit_score, True, "Instant approval"
            )
            app_data.status = "approved_instant"
            next_stage = "sanction"
        elif loan_amount <= 2 * pre_approved:
            agent_response = underwriting_agent_response(
                app_data.customer, loan_amount, tenure, credit_score, True, "Needs salary slip"
            )
            app_data.status = "needs_salary_slip"
            next_stage = "salary_verification"
        else:
            agent_response = underwriting_agent_response(
                app_data.customer, loan_amount, tenure, credit_score, False, "Amount exceeds limit"
            )
            app_data.status = "rejected"
            next_stage = "end"

    elif app_data.stage == "salary_verification":
        if "upload" in text_lower or "file" in text_lower:
            agent_response = (
                "Please upload your latest salary slip (PDF or image) in the file upload option of this interface.\n"
                "We will verify your income and re-check that the EMI stays within 50% of your monthly salary."
            )
        elif any(word in text_lower for word in ["yes", "ok", "ready", "uploaded"]):
            app_data.monthly_salary = app_data.customer['salary']
            emi_percentage = (app_data.emi / app_data.monthly_salary) * 100

            if emi_percentage <= 50:
                agent_response = (
                    f"Salary verification completed.\n\n"
                    f"Monthly salary: ₹{app_data.monthly_salary:,}\n"
                    f"Indicative EMI: ₹{int(app_data.emi):,}\n"
                    f"EMI as % of salary: {emi_percentage:.1f}% (within 50% policy limit).\n\n"
                    "Your application is approved in principle. We will now generate the sanction letter."
                )
                app_data.status = "approved_salary_verified"
                next_stage = "sanction"
                app_data.salary_verified = True
            else:
                agent_response = (
                    f"Based on your salary details, the EMI would be {emi_percentage:.1f}% of your monthly income, "
                    "which exceeds the 50% internal limit.\n\n"
                    "You may consider reducing the loan amount or extending the tenure to lower the EMI."
                )
                app_data.status = "rejected"
                next_stage = "end"
        else:
            agent_response = "Please confirm once you have uploaded the salary slip by replying \"uploaded\" or \"yes\"."

    elif app_data.stage == "sanction":
        if "yes" in text_lower or "download" in text_lower or "sanction" in text_lower:
            agent_response = sanction_agent_response(
                app_data.customer,
                app_data.loan_amount,
                app_data.tenure,
                app_data.emi
            )
            next_stage = "completed"
            app_data.status = "completed"
        else:
            agent_response = "Would you like me to generate and share your sanction letter now? Reply \"yes\" to proceed."

    elif app_data.stage == "completed":
        agent_response = (
            "Thank you for choosing Non-Banking Financial Company.\n\n"
            "Your loan has been sanctioned in principle. After you review and digitally accept the sanction letter, "
            "funds will be disbursed to your registered bank account subject to final checks.\n\n"
            "If you need any further assistance, you can continue to chat here."
        )

    elif app_data.stage == "end":
        agent_response = (
            "Your application has been closed based on the current assessment.\n"
            "You may revisit this chat anytime to explore alternate amounts or tenures."
        )

    app_data.stage = next_stage
    app_data.messages.append({"role": "assistant", "content": agent_response})

    return jsonify({
        "response": agent_response,
        "stage": next_stage,
        "status": app_data.status,
        "session_id": session_id,
        "customer": app_data.customer['name'] if app_data.customer else None,
        "loan_amount": app_data.loan_amount,
        "emi": int(app_data.emi) if app_data.emi else 0
    })

@app.route('/api/generate-sanction/<session_id>', methods=['GET'])
def generate_sanction(session_id):
    if session_id not in app_sessions:
        return jsonify({"error": "Session not found"}), 404

    app_data = app_sessions[session_id]
    if not app_data.customer or app_data.status not in ["approved_instant", "approved_salary_verified", "completed"]:
        return jsonify({"error": "Loan not approved"}), 400

    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#003366'),
        spaceAfter=12,
        alignment=1
    )
    story.append(Paragraph("LOAN SANCTION LETTER", title_style))
    story.append(Spacer(1, 0.3*inch))

    bank_info = [
        ["Non-Banking Financial Company", ""],
        ["Registered Office: Mumbai, India", ""],
        ["www.NonBankingFinancialCompany.com", ""]
    ]
    bank_table = Table(bank_info, colWidths=[4*inch, 2.5*inch])
    story.append(bank_table)
    story.append(Spacer(1, 0.3*inch))

    sanction_date = datetime.now().strftime('%d-%B-%Y')

    details = [
        ["Date", sanction_date],
        ["Applicant Name", app_data.customer['name']],
        ["PAN", app_data.customer['pan']],
        ["Mobile No", app_data.customer['phone']],
        ["Address", app_data.customer['address']],
        ["", ""],
        ["LOAN DETAILS", ""],
        ["Approved Amount", f"₹{app_data.loan_amount:,}"],
        ["Tenor (Months)", str(app_data.tenure)],
        ["Indicative Rate of Interest", "12.00% p.a."],
        ["Indicative Monthly EMI", f"₹{int(app_data.emi):,}"],
    ]

    details_table = Table(details, colWidths=[2.5*inch, 4*inch])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#E8F4F8')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey)
    ]))
    story.append(details_table)
    story.append(Spacer(1, 0.3*inch))

    terms_style = ParagraphStyle('Terms', parent=styles['Normal'], fontSize=9)
    story.append(Paragraph("<b>Key Terms & Conditions (summary)</b>", terms_style))
    story.append(Paragraph("1. Final terms are subject to execution of the loan agreement and standard KYC checks.", terms_style))
    story.append(Paragraph("2. Processing fees, taxes and other charges will be as per the sanctioned terms.", terms_style))
    story.append(Paragraph("3. This sanction is valid for 30 days from the date of issue.", terms_style))
    story.append(Spacer(1, 0.3*inch))

    story.append(Paragraph("_" * 50, styles['Normal']))
    story.append(Paragraph("Authorised Signatory<br/>Non-Banking Financial Company LIMITED", styles['Normal']))

    doc.build(story)
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"Sanction_Letter_{app_data.customer['name']}.pdf"
    )

@app.route('/api/status/<session_id>', methods=['GET'])
def get_status(session_id):
    if session_id not in app_sessions:
        return jsonify({"error": "Session not found"}), 404
    app_data = app_sessions[session_id]
    return jsonify(app_data.to_dict())

if __name__ == '__main__':
    app.run(debug=True, port=5000)
