
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from django.contrib import messages
from apps.core_management.decorators import allowed_roles
from django.contrib.auth import get_user_model

User = get_user_model()


# apps/bgv_sytem/views.py
from django.shortcuts import render
from django.contrib import messages
from .models import UnknownCandidateBGVCheck

def bgv_dashboard_view(request):
    workforce_queryset = UnknownCandidateBGVCheck.objects.all().order_by('-created_at')

    stats = {
        'total_checks': workforce_queryset.count(),
        'awaiting_review': workforce_queryset.filter(is_sent_to_bgv=False).count(),
        'cleared_staff': workforce_queryset.filter(is_sent_to_bgv=True).count(),
    }

    context = {
        'profiles': workforce_queryset,
        'stats': stats,
        'active_section': 'bgv_system_dashboard'
    }
    return render(request, "bgv_system/dashboard.html", context)







from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.core_management.decorators import allowed_roles
from django.contrib.auth import get_user_model

User = get_user_model()

# apps/bgv_sytem/views.py
from django.shortcuts import render
from .models import UnknownCandidateBGVCheck

def bgv_officer_dashboard(request):
    # Only show candidates already sent to BGV agency
    sent_queryset = UnknownCandidateBGVCheck.objects.filter(is_sent_to_bgv=True).order_by('-created_at')

    stats = {
        'total_sent': sent_queryset.count(),
    }

    context = {
        'profiles': sent_queryset,
        'stats': stats,
        'active_section': 'bgv_officer_dashboard'
    }
    return render(request, "bgv_system/bgv_officer.html", context)


# apps/bgv_sytem/views.py
import uuid
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UnknownCandidateBGVCheck

@login_required
def upload_documents(request):
    if request.method == "POST":
        aadhaar = request.POST.get("aadhaar")
        pan = request.POST.get("pan")
        course_type = request.POST.get("courseType")
        marksheet_file = request.FILES.get("marksheet_doc")
        experience_file = request.FILES.get("experience_doc")

        # Basic validation
        if not aadhaar or not pan or not marksheet_file:
            messages.error(request, "Aadhaar, PAN, and Marksheet are required.")
            return redirect("upload_documents")

        submission = UnknownCandidateBGVCheck.objects.create(
            submission_id=str(uuid.uuid4()),
            aadhaar=aadhaar,
            pan=pan,
            course_type=course_type,
            marksheet_file=marksheet_file,
            experience_file=experience_file if experience_file else None,
        )

        messages.success(request, f"Documents uploaded successfully! Ref ID: {submission.submission_id}")
        return redirect("upload_documents")

    return render(request, "authentication/upload_documents.html")


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import UnknownCandidateBGVCheck

@require_POST
def send_to_bgv(request, submission_id):
    candidate = get_object_or_404(UnknownCandidateBGVCheck, submission_id=submission_id)
    candidate.is_sent_to_bgv = True
    candidate.save()
    messages.success(request, f"Candidate {candidate.submission_id} sent to BGV agency.")
    return redirect("bgvdashboard")




from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import UnknownCandidateBGVCheck
def generate_offer_letter(request, submission_id):
    candidate = UnknownCandidateBGVCheck.objects.get(submission_id=submission_id)

    html_content = render_to_string("bgv_system/offer_letter.html", {"candidate": candidate})

    return HttpResponse(html_content)





# Open apps/bgv_system/views.py




# ReportLab Components




from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from apps.core_management.decorators import allowed_roles
from .models import UnknownCandidateBGVCheck
import io
import os
from django.conf import settings








# ReportLab Layout Components
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Open apps/bgv_system/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from apps.core_management.decorators import allowed_roles
from .models import UnknownCandidateBGVCheck
from django.utils import timezone
from django.conf import settings
import io
import os
# Open apps/bgv_system/views.py -> Paste this helper right above your view function

from reportlab.platypus import Flowable

class GradientTextFlowable(Flowable):
    """
    Custom Flowable component that renders text with a smooth 
    horizontal multi-color gradient blend across the characters.
    """
    def __init__(self, text, font_name='Helvetica-Bold', font_size=18, start_color="#F2A900", end_color="#72BB12"):
        Flowable.__init__(self)
        self.text = text
        self.font_name = font_name
        self.font_size = font_size
        self.start_color = colors.HexColor(start_color)
        self.end_color = colors.HexColor(end_color)
        
    def draw(self):
        self.canv.saveState()
        self.canv.setFont(self.font_name, self.font_size)
        
        # Calculate text width dynamically to constrain the color blend boundary box exactly to the word
        text_width = self.canv.stringWidth(self.text, self.font_name, self.font_size)
        
        # Create a text clipping path to mask the gradient blend inside the font lines natively
        text_path = self.canv.beginPath()
        
        # Enforce linear gradient blending vectors across the text block path metrics coordinates
        # (Transitions from your brand Gold/Orange on the left to Lime Green on the right)
        self.canv.linearGradient(0, 0, text_width, 0, (self.start_color, self.end_color))
        self.canv.drawString(0, 0, self.text)
        self.canv.restoreState()
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import letter
import os
from reportlab.platypus import NextPageTemplate
# Add these right alongside your existing Platypus importers at the top of views.py:
from reportlab.platypus import Table, TableStyle



# Background functions
def background_page1(canvas, doc):
    path = os.path.join(settings.BASE_DIR, 'static', 'images', 'template1.png')
    if os.path.exists(path):
        canvas.drawImage(path, 0, 0, width=612, height=792, mask='auto')

def background_page2(canvas, doc):
    path = os.path.join(settings.BASE_DIR, 'static', 'images', 'template2.png')
    if os.path.exists(path):
        canvas.drawImage(path, 0, 0, width=612, height=792, mask='auto')

def background_page3(canvas, doc):
    path = os.path.join(settings.BASE_DIR, 'static', 'images', 'watermark.png')
    if os.path.exists(path):
        canvas.drawImage(path, 0, 0, width=612, height=792, mask='auto')

def background_page4(canvas, doc):
    path = os.path.join(settings.BASE_DIR, 'static', 'images', 'watermark.png')
    if os.path.exists(path):
        canvas.drawImage(path, 0, 0, width=612, height=792, mask='auto')
    else:
        # Fallback to standard color bars if template4 image asset is missing from storage drives
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#72BB12"))
        canvas.setLineWidth(4)
        canvas.line(38, 750, 574, 750)
        canvas.restoreState()
def background_page5(canvas, doc):
    path = os.path.join(settings.BASE_DIR, 'static', 'images', 'watermark.png')
    if os.path.exists(path):
        canvas.drawImage(path, 0, 0, width=612, height=792, mask='auto')



def generate_offer_letter_pdf_view(request, submission_id):
    record = get_object_or_404(UnknownCandidateBGVCheck, submission_id=submission_id)

    if request.method == "POST":
        candidate_name = request.POST.get("candidate_name", "").strip()
        candidate_city = request.POST.get("candidate_city", "Tirunelveli").strip()
        candidate_email = request.POST.get("candidate_email", "-").strip()


        designation = request.POST.get("designation", "").strip()
        joining_date = request.POST.get("joining_date", "").strip()
        expiry_days = request.POST.get("expiry_days", "7 days").strip()
        recruiter_name = request.POST.get("sender_name", "").strip()
        recruiter_id_token = request.POST.get("recruiter_id", "").strip()

        company_name = "Voxlom Innovative Solution"
        buffer = io.BytesIO()

        # Use BaseDocTemplate instead of SimpleDocTemplate
        doc = BaseDocTemplate(buffer, pagesize=letter,
                              rightMargin=45, leftMargin=38,
                              topMargin=105, bottomMargin=50)
        reg_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Poppins-Regular.ttf')
        bold_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'Poppins-Bold.ttf')

        if os.path.exists(reg_path) and os.path.exists(bold_path):
            pdfmetrics.registerFont(TTFont('Poppins', reg_path))
            pdfmetrics.registerFont(TTFont('Poppins-Bold', bold_path))
            pdfmetrics.registerFontFamily('Poppins', normal='Poppins', bold='Poppins-Bold')

            FONT_NAME_BODY = 'Poppins'
            FONT_NAME_BOLD = 'Poppins-Bold'
        else:
              FONT_NAME_BODY = 'Helvetica'
              FONT_NAME_BOLD = 'Helvetica-Bold'

                              

                # --- BEFORE (Monolithic Shared Frame Dimensions): ---
        # frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')

        # --- AFTER (🎯 THE FIXED SPECIFIC BOUNDARY MATRICES): ---
        frame1 = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='frame_p1')
        frame2 = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='frame_p2')
        
        # 🚀 EXPANDED VERTICAL FRAME: Lifted the height by 45 pixels to safely fit clauses 1 to 13 on page 3!
        frame3 = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height + 65, id='frame_p3')
        
        # 🚀 EXPANDED VERTICAL FRAME: Lifted the height to prevent Annexure III from overflowing onto page 5!
        frame4 = Frame(doc.leftMargin, doc.bottomMargin - 15, doc.width, doc.height + 45, id='frame_p4')
        frame5 = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='frame_p5')

        # Bind the isolated frame boundaries straight to your template page templates list
        doc.addPageTemplates([
            PageTemplate(id='page1', frames=frame1, onPage=background_page1),
            PageTemplate(id='page2', frames=frame2, onPage=background_page2),
            PageTemplate(id='page3', frames=frame3, onPage=background_page3),
            PageTemplate(id='page4', frames=frame4, onPage=background_page4),
            PageTemplate(id='page5', frames=frame5, onPage=background_page5),
        ])



        styles = getSampleStyleSheet()
        body_style = ParagraphStyle(
            'SinglePageBody', parent=styles['Normal'],
            fontName='Helvetica', fontSize=9.9,
            leading=14.5, textColor=colors.HexColor("#1E293B"),
            spaceAfter=4, alignment=4
        )
        bold_style = ParagraphStyle('SinglePageBold', parent=body_style, fontName='FONT_NAME_BOLD')

        story = []

        # === Page 1 content (your full offer letter text, unchanged) ===
        story.append(Spacer(1, 2))
        story.append(Paragraph(f"Dear <b>{candidate_name}</b>,", body_style))
        bold_style = ParagraphStyle('SinglePageBold', parent=body_style, fontName=FONT_NAME_BOLD)


        # =========================================================================
        # 📄 NARRATIVE DATA CONTENT BLOCKS (Overlays seamlessly on top of background)
        # =========================================================================
   
        
        story.append(Paragraph(
            f"<b>Congratulations!</b> With reference to your application and subsequent interview with us for a career in our organization, "
            f"we are pleased to inform you that you have been selected for employment in our organization as <b>{designation}</b>. "
            f"In the coming year, keep aspiring for change and be known for your thoughts and your work; be the catalyst that this fast "
            f"changing world needs; keep sharpening your skills and investing in yourself; and last but not the least – keep your "
            f"work and life in perfect balance, because that is the prerequisite for success.", body_style
        ))

        story.append(Paragraph(
            f"We take this opportunity to thank & appreciate your decision to join Voxlom Innovative Solution. You are requested to join us "
            f"on or before <b>{joining_date}</b>. You will be on probation for a period of 12 months from the date of your joining. "
            f"Your compensation would be as outlined in a separate document “Salary Structure”. The general terms and conditions governing "
            f"your employment are outlined in Annexure II.", body_style
        ))

        story.append(Paragraph(
            f"On the date of joining, you would be required to furnish photocopies of the original documents and other listed information "
            f"in Annexure III. Please note that the submission of all the documents is mandatory to facilitate joining, background verification "
            f"/ validation and appointment process at {company_name}. Annexure I provides details on the various compensation "
            f"components and selected benefits that we offer you as a part of the Voxlom family.", body_style
        ))

        story.append(Paragraph(
            f"As confirmation of your acceptance, please sign the duplicate copy of this Offer cum Appointment Letter and Annexure and "
            f"submit the same within <b>{expiry_days}</b> to at the address given below:<br/>"
            f"<b>Recruiter:</b> {recruiter_name}<br/>"
            f"<b>Recruiter Address:</b> Voxlom Innovative Solution Ltd. Tirunelveli.", 
            body_style
        ))

        story.append(Paragraph(
            f"This offer will be valid subject to successful clearance of your pre-employment background verification check conducted "
            f"by <b>{company_name}</b>. Your written consent and requisite copies of documents is necessary to complete the pre-employment "
            f"check. You are requested to complete the submission of requisite documents for pre-employment background check within two business "
            f"days from the date of acceptance of our offer of employment.", 
            body_style
        ))

        story.append(Paragraph(
            "Your cooperation is solicited in this regard to enable us complete the necessary pre-employment check on time and enable you "
            "onboard us. Any change in the date of joining needs to be communicated to the concerned recruiter at least one week in advance. "
            "Looking ahead, we see exciting times – we look up to you to provide impetus in accomplishing our mutual endeavor of being the best "
            "in the business of IT Services.", 
            body_style
        ))

        story.append(Paragraph("<b>Welcome to our Organization!</b> We look forward to a mutually fruitful association.", body_style))
        
        # Compacted Signatures Block
        story.append(Spacer(1, 6))
        story.append(Paragraph(f"For <b>{company_name} Ltd.</b>,", body_style))
        story.append(Spacer(1, 14)) # Tightened vertical signature clearance spacing
        story.append(Paragraph(f"<b>{recruiter_name}</b> ({recruiter_id_token})", bold_style))
        story.append(Paragraph("HR Team", body_style))
       
    

                # Switch to page2 template background
        story.append(NextPageTemplate('page2'))
        story.append(PageBreak())

        # =========================================================================
        # 📄 PAGE 2 CONTENT: ANNEXURE I (COMPENSATION BREAKDOWN MATRIX)
        # =========================================================================
        story.append(Spacer(1, 80))
        
        # Section Header Definition Title
        story.append(Paragraph("<b>ANNEXURE I</b>", ParagraphStyle('AnnexNum', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=11, alignment=1, spaceAfter=14)))
        
        story.append(Paragraph("<b>EXPLANATION OF COMPENSATION STRUCTURE AND EMPLOYEE BENEFITS</b>", ParagraphStyle('AnnexTitle', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=10, textColor=colors.HexColor("#0F172A"), spaceAfter=10)))
        
        story.append(Paragraph(
            f"To facilitate an easy understanding of your compensation structure (Cost to Company, CTC), the various "
            f"components have been categorized under the following broad heads:", body_style
        ))
        
        # Bulleted List Block Elements Group
        bullet_style = ParagraphStyle('BulletText', parent=body_style, leftIndent=15, bulletIndent=5, spaceAfter=3)
        story.append(Paragraph("• Basic Salary", bullet_style))
        story.append(Paragraph("• Monthly Allowances", bullet_style))
        story.append(Paragraph("• Variable Pay", bullet_style))
        story.append(Paragraph("• Social Security & Health Benefits", bullet_style))
        
        story.append(Paragraph("The details for each component falling under these heads are explained as following:", body_style))
        story.append(Spacer(1, 4))

        # --- BASIC SALARY HEADER BLOCK ---
        story.append(Paragraph("<b><u>BASIC SALARY</u></b>", ParagraphStyle('SubHeader', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=9.5, spaceAfter=6)))
        story.append(Paragraph(
            "The Basic Salary is standard across organization and brought to a certain value of the CTC. Basic salary has "
            "an impact on various other components such as the PF contribution, medical insurance cover, Gratuity, "
            "HRA etc. and hence has to be balanced so as not to substantially reduce the employee's take home salary.", body_style
        ))
        story.append(Spacer(1, 4))

        # --- MONTHLY ALLOWANCES HEADER BLOCK ---
        story.append(Paragraph("<b><u>MONTHLY ALLOWANCES</u></b>", ParagraphStyle('SubHeader2', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=9.5, spaceAfter=6)))
        
        story.append(Paragraph(
            "<b>House Rent Allowance (HRA):</b> The HRA is payable maximum Up to 125% of the Basic Salary and paid "
            "monthly. This includes the Company Leased Accommodation value. For those who are not staying in a "
            "rented accommodation, can declare the same in the system post joining and this amount would be paid "
            "as taxable component.", body_style
        ))
        
        story.append(Paragraph(
            "<b>City Compensatory Allowance (CCA):</b><br/>"
            "CCA is a work location based monthly component to adjust cost of living expenses on the basis of "
            "specified locations. CCA component is subject to change for an employee in the event of relocation "
            "between different zones / locations max. Limits of payout will be as follows:", body_style
        ))
        story.append(Spacer(1, 4))

        # =========================================================================
        # 📊 DYNAMIC DATA MATRIX TABLE REGISTRATION (Matches your screenshot exactly)
        # =========================================================================
        # Cell typography content labels definitions mapping 
        th_style = ParagraphStyle('TH', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=9, textColor=colors.HexColor("#1E293B"))
        td_style = ParagraphStyle('TD', parent=body_style, fontSize=9, textColor=colors.HexColor("#334155"))

        table_data_matrix = [
            [Paragraph("<b>Zones</b>", th_style), Paragraph("<b>Cities</b>", th_style), Paragraph("<b>INR / Month</b>", th_style)],
            [Paragraph("Zone A+", td_style), Paragraph("Panagudi", td_style), Paragraph("1000", td_style)],
            [Paragraph("Zone A", td_style), Paragraph("Tirunelveli", td_style), Paragraph("1200", td_style)]
        ]

        # Explicitly declare static column pixel bounds to maintain precise alignments metrics
        cca_table = Table(table_data_matrix, colWidths=[130, 160, 130], hAlign='LEFT')
        
        # Draw clean, professional grid border lines matching your document sheet
        cca_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94A3B8")), # Faint gray grid lines
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")), # Ghost white heading row background
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        
        story.append(cca_table)
        story.append(Spacer(1, 10))

        # --- FOOTER CLAUSES ON PAGE 2 ---
        story.append(Paragraph("<b>Conveyance Allowance:</b> Conveyance Allowance is payable max. Upto Rs.2000/- per month", body_style))
        story.append(Paragraph("<b>Holiday Allowance:</b> Holiday Allowance is payable maximum up to INR 5,000 spread over 24 months.", body_style))
        story.append(Paragraph("<b>Advance Statutory Bonus: :</b>Applicable where monthly gross is less than INR 5,000 excluding variable component and HRA as per the statutory norms", body_style))


                # Switch to page3 template background
        story.append(NextPageTemplate('page3'))
        story.append(PageBreak())

        # 📄 PAGE 3 CONTENT: ANNEXURE II (COMPRESSED TO FORCE EXACTLY 3 PAGES)
        story.append(Spacer(1,4))
        
        # 🎯 COMPRESSED TYPOGRAPHY DESIGN MATRIX FOR PAGE 3
        page3_body_style = ParagraphStyle(
            'Page3Body', parent=styles['Normal'],
            fontName=FONT_NAME_BODY, fontSize=9.5,       
            leading=12.5, textColor=colors.HexColor("#1E293B"), 
            spaceAfter=3, alignment=4                    
        )
        
        page3_head_style = ParagraphStyle(
            'Page3ClauseHead', parent=page3_body_style, 
            fontName=FONT_NAME_BOLD, fontSize=9.0, 
            spaceBefore=3, spaceAfter=1                  
        )

        # Main Titles Section
        story.append(Paragraph("<b>ANNEXURE II</b>", ParagraphStyle('Annex2Num', parent=page3_body_style, fontName=FONT_NAME_BOLD, fontSize=10, alignment=1, spaceAfter=2)))
        story.append(Paragraph("<b>GENERAL TERMS AND CONDITIONS OF EMPLOYMENT</b>", ParagraphStyle('Annex2Title', parent=page3_body_style, fontName=FONT_NAME_BOLD, fontSize=9.5, textColor=colors.HexColor("#0F172A"), alignment=1, spaceAfter=8)))
        
        # --- 1. Location ---
        story.append(Paragraph("<b>1. Location</b>", page3_head_style))
        story.append(Paragraph(
            "As you are aware that Voxlom is coming up with IT/ITES Operating Unit in Panagudi "
            "city; till the time Panagudi campus becomes operational, you may be assigned to "
            "another facility in the city of posting – Tirunelveli District.", page3_body_style
        ))

        # --- 2. Medical Check up ---
        story.append(Paragraph("<b>2. Medical Check up</b>", page3_head_style))
        story.append(Paragraph(
            "Your employment is subject to you being declared medically fit by the company doctor.", page3_body_style
        ))

        # --- 3. Increments and promotions ---
        story.append(Paragraph("<b>3. Increments and promotions</b>", page3_head_style))
        story.append(Paragraph(
            "Your growth in terms of role, compensation etc. in the company will solely be based "
            "on your performance. Unless notified in writing, you will be deemed as \"confirmed\" "
            "on completion of your probation period i.e. 12 months from date of joining. "
            "Subsequently, your annual performance appraisal and compensation review will be "
            "aligned and effected from the first day of the subsequent quarter thereafter.", page3_body_style
        ))

        # --- 4. Notice Period/ Separation ---
        story.append(Paragraph("<b>4. Notice Period/ Separation</b>", page3_head_style))
        story.append(Paragraph(
            "Your employment with the Company can also be terminated either by the Company "
            "or by you by giving the other party three months advance notice. If the Company "
            "terminates the employment and decides to relieve you before the completion of "
            "the notice period, the “Basic” component of the salary for the balance notice period "
            "would be paid to you. If at your request, the Company agrees to relieve you before "
            "serving the full notice period, you will be liable to pay the Company the “3 months” "
            "component of the salary for the balance notice period. However, please note that "
            "accepting any such early relieving request would be entirely at the discretion of the "
            "Company. On termination of your employment for any reason, you shall comply "
            "with the Company’s termination procedures, sign all documents and return all "
            "Company property. The Company will not be bound to pay the dues, if any, till you "
            "have completed all the separation procedures.", page3_body_style
        ))

        # --- 5. Agreements ---
        story.append(Paragraph("<b>5. Agreements</b>", page3_head_style))
        story.append(Paragraph(
            "You may be required to sign necessary agreements with the Company or any other "
            "client as required and complete various formalities as per the agreements at the "
            "time of joining and during the tenure with the company. You may also be required "
            "to sign other Agreements with the Company, as the Company may decide from "
            "time to time, in order to secure the interests of the Company as also to ensure your "
            "performance and adherence to all terms, conditions, rules and regulations of the "
            "Company.", page3_body_style
        ))

        # --- 6. Background and Reference Check ---
        story.append(Paragraph("<b>6. Background and Reference Check</b>", page3_head_style))
        story.append(Paragraph(
            "The company will undertake the background verification / validation process of "
            "employees in terms of education, previous employment(s), claims made against "
            "achievements in the resumes/CVs of the employees etc. with the help of a third "
            "party as and when required. You would be required to submit photocopies of "
            "documents detailed in Annexure III to facilitate the joining and background "
            "verification process. The company may also undertake reference check through at "
            "least two professional references submitted during the process of selection.", page3_body_style
        ))

        # --- 7. Working Hours ---
        story.append(Paragraph("<b>7. Working Hours</b>", page3_head_style))
        story.append(Paragraph(
            "You will be governed by the normal working hours as existing in the company. You "
            "may be required to work in shifts and/or in extended working hours, as permitted "
            "by law, if required as per business needs. The same are subject to change from "
            "time to time.", page3_body_style
        ))

        # --- 8. Mobility ---
        
        story.append(Paragraph("<b>8. Mobility</b>", page3_head_style))
        
        story.append(Paragraph(
            "The Company may require you to perform duties and undertake assignments for "
            "the Company in any part of India or abroad, whether at the Company’s premises or "
            "that of its customers/clients. You are also liable to be transferred to any office or "
            "branch of the Company anywhere in India or abroad. During deputation to any "
            "customer/client’s premises you shall abide by the terms and conditions pertaining "
            "to such premises.", page3_body_style
        ))

        # --- 9. Deputation/ Transfer ---
        # 🎯 FIXED BUG: Changed 'clause_head_style' to your active compressed 'page3_head_style'
        story.append(Paragraph("<b>9. Deputation/ Transfer</b>", page3_head_style))
        story.append(Paragraph(
            "Company may also depute you to work with any of the Group Companies or "
            "transfer your services to any Group Company. On such transfer of your "
            "employment, the present terms and conditions will cease and the employment will "
            "be governed by the terms of employment of the Company you are transferred to. "
           , page3_body_style
        ))


        # --- 10. Retirement ---
        story.append(Paragraph("<b>10. Retirement</b>", page3_head_style))
        story.append(Paragraph(
            "You will retire from service on attaining superannuation at the age of 55 years.", page3_body_style
        ))

        # --- 11. Other benefits ---
        story.append(Paragraph("<b>11. Other benefits</b>", page3_head_style))
        story.append(Paragraph(
            "You shall be eligible for other benefits related to leaves, perquisites etc. in "
            "accordance with the prevailing terms of employment in the Company. "
            "Notwithstanding the above, the Company reserves the right to change the above "
            "mentioned benefits as and when it deems necessary and you will be notified "
            "accordingly.", page3_body_style
        ))

        # --- 12. Correctness of the Details Furnished ---
        story.append(Paragraph("<b>12. Correctness of the Details Furnished</b>", page3_head_style))
        story.append(Paragraph(
            "You have been appointed on the presumption that the particulars furnished in "
            "your application and resume are correct. In the event the said particulars are found "
            "to be incorrect or that you have concluded or withheld some other relevant facts, "
            "your appointment with the Company shall stand terminated/cancelled without any notice.", page3_body_style
        ))
         # 🎯 --- NEW ADDED: 13. Other Rules and Regulations of the Company ---
        story.append(Paragraph("<b>13. Other Rules and Regulations of the Company</b>", page3_head_style))
        story.append(Paragraph(
            "Your appointment will be governed by the policies, rules, regulations, practices, processes and "
            "procedures of VOXLOM as applicable to you and the changes therein from time to time.<br/><br/>"
            "Further, during the period of your employment with VOXLOM, you will be required to inter alia "
            "comply with the Company’s Code of Business Ethics & Conduct, Anti Bribery & Anti Corruption, "
            "Business Gift and Entertainment Policy and failure to do so shall entitle VOXLOM to take appropriate "
            "disciplinary action which may lead & include upto termination of your employment with VOXLOM.<br/><br/>"
            "You agree not to undertake employment whether full time or part time, as the Director/ Partner/member/employee "
            "of any other organization or entity engaged in any form of business activity without the consent of Voxlom "
            "Innovative Solution. The consent may be given subject to any terms and conditions that the company may "
            "think fit and may be withdrawn at the discretion of the company.", page3_body_style
        ))

                # 🎯 SWITCH RUNTIME ROUTINGS TO PAGE 4 BACKGROUND FOR ANNEXURE III:
        

        # =========================================================================
        # 📄 PAGE 4 CONTENT: ANNEXURE III (LIST OF MANDATORY ONBOARDING DOCUMENTS)
        # =========================================================================
        story.append(Spacer(1, 20))
        
        # Main Document Titles Section
        story.append(Paragraph("<b>ANNEXURE III</b>", ParagraphStyle('Annex3Num', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=11, alignment=1, spaceAfter=4)))
        
        title_box_style = ParagraphStyle(
            'Annex3TitleBox', parent=body_style,
            fontName=FONT_NAME_BOLD, fontSize=9.0,
            leading=13, textColor=colors.HexColor("#0F172A"),
            alignment=1, spaceAfter=14
        )
        story.append(Paragraph(
            "LIST OF DOCUMENTS/INFORMATION TO BE SUBMITTED ON DATE OF JOINING TO FACILITATE "
            "JOINING, BACKGROUND VERIFICATION / VALIDATION AND APPOINTMENT PROCESS AT Voxlom "
            "Innovative Solution", title_box_style
        ))

        # Shared Compact Table Typography Layout Styles Tokens
        table_th_style = ParagraphStyle('T3Head', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.5, textColor=colors.HexColor("#0F172A"))
        table_td_style = ParagraphStyle('T3Body', parent=body_style, fontName=FONT_NAME_BODY, fontSize=8.5, leading=11, textColor=colors.HexColor("#334155"))
        table_sno_style = ParagraphStyle('T3Sno', parent=body_style, fontName=FONT_NAME_BODY, fontSize=8.5, alignment=1)

        # -------------------------------------------------------------------------
        # 📊 GRID AREA A: PRE-EMPLOYMENT BACKGROUND VERIFICATION CHECKLIST TABLE
        # -------------------------------------------------------------------------
        story.append(Paragraph("<b>PRE-EMPLOYMENT BACKGROUND VERIFICATION</b>", ParagraphStyle('T3SubTitle1', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=9, textColor=colors.HexColor("#1E3A8A"), spaceAfter=6)))
        
        bgv_table_headers = [
            [Paragraph("<b>S.No</b>", table_th_style), Paragraph("<b>Particulars (To be Submitted)</b>", table_th_style)]
        ]
        
        bgv_table_rows = [
            [Paragraph("1", table_sno_style), Paragraph("Highest Qualification, Degree Certificate, All Mark sheets", table_td_style)],
            [Paragraph("2", table_sno_style), Paragraph("Permanent/Current Address proof – Passport, Ration Card, Voter ID, Driving License, UID unique Identification card.", table_td_style)],
            [Paragraph("3", table_sno_style), Paragraph("Previous Employer – Relieving and Experience Letter with Employee ID Number", table_td_style)],
            [Paragraph("4", table_sno_style), Paragraph("A duly filled and signed copy of the BG Form and CID form", table_td_style)]
        ]
        
        bgv_matrix_data = bgv_table_headers + bgv_table_rows
        # Set column width allocation to perfectly fit your margins boundaries
        bgv_render_table = Table(bgv_matrix_data, colWidths=[45, 484], hAlign='LEFT')
        
        bgv_render_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(bgv_render_table)
        story.append(Spacer(1, 14))
        # -------------------------------------------------------------------------
        # 📊 GRID AREA B: DOCUMENTS NEEDED FOR JOINING ON-BOARDING DAY TABLE
        # -------------------------------------------------------------------------
        story.append(Paragraph("<b>DOCUMENTS NEEDED FOR JOINING</b>", ParagraphStyle('T3SubTitle2', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.5, textColor=colors.HexColor("#1E3A8A"), spaceBefore=4, spaceAfter=4)))
        
        joining_matrix_data = [
            [Paragraph("<b>S.No.</b>", table_th_style), Paragraph("<b>Particulars</b>", table_th_style)],
            [Paragraph("<b>(A)</b>", table_sno_style), Paragraph("<b>One Set of Photocopy of Following Documents</b>", table_th_style)],
            [Paragraph("1", table_sno_style), Paragraph("Date of Birth Certificate", table_td_style)],
            [Paragraph("2", table_sno_style), Paragraph("Copy of PAN Card or acknowledgement slip of Form 49, if applied for PAN No.", table_td_style)],
            [Paragraph("3", table_sno_style), Paragraph("Copy of full set of offer letter, self attested on all the pages. The offer letter should be digitally signed and accepted.", table_td_style)],
            [Paragraph("4", table_sno_style), Paragraph(
                "Professional/ Educational Certificates and Mark sheets:<br/>"
                "• 10th std or equivalent mark card and certificate<br/>"
                "• 12th std, diploma or equivalent mark card and certificate<br/>"
                "• Graduation mark card and certificate<br/>"
                "• Post Graduate certificate mark card and certificate Other relevant skill/ educational certifications", table_td_style)],
            [Paragraph("5", table_sno_style), Paragraph("Experience Letter (s) from all your PAST employers including details of period of employment", table_td_style)],
            [Paragraph("6", table_sno_style), Paragraph("Latest Pay-slip / Salary Certificate from the last two employers", table_td_style)],
            [Paragraph("7", table_sno_style), Paragraph("Passport- All non-blank pages (if applicable)", table_td_style)],
            [Paragraph("8", table_sno_style), Paragraph("Permanent & current Residential address proof (Ration Card / Voter ID Card / License Copy etc.,)", table_td_style)],
            [Paragraph("9", table_sno_style), Paragraph("Three COLOUR PHOTOGRAPH5 with WHITE BACKGROUND (Name & blood group to be mentioned at the back of photographs) - Passport Size", table_td_style)],
            [Paragraph("10", table_sno_style), Paragraph("Previous Employment PF Account No. And Pension Account No with complete address of PF Trust (In case joinees wish to Transfer their PF)", table_td_style)],
            [Paragraph("11", table_sno_style), Paragraph("Bank Account No. (ICICI/HDFC) (If Any)", table_td_style)],
            [Paragraph("12", table_sno_style), Paragraph("Joinees family (Parents, Spouse, Children) details including their DOB", table_td_style)],
            [Paragraph("13", table_sno_style), Paragraph("Blood Group of Self and Family", table_td_style)],
            [Paragraph("<b>(B)</b>", table_sno_style), Paragraph("<b>Two Sets of Photocopy of Following Documents</b>", table_th_style)],
            [Paragraph("14", table_sno_style), Paragraph("Resignation/ Relieving letter of last 2 employers", table_td_style)]
        ]
        
        
        joining_render_table = Table(joining_matrix_data, colWidths=[48, 480], hAlign='LEFT')
        
        joining_render_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 3),      # Tightened cell vertical padding to squeeze text onto page 4
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),   # Tightened cell vertical padding
            ('LEFTPADDING', (0,0), (-1,-1), 6),
            ('RIGHTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(joining_render_table)
        
        # 🎯 TIGHTENED SPACER: Changed from 80 down to 8 to prevent pushing items onto an accidental 5th page!
        story.append(Spacer(1, 8))

        # --- MANDATORY REPORTING CLAUSE TIMELINE SUMMARY FOOTER ---
        story.append(Paragraph(
            "You are required to report at the <b>HS (HR Services) desk</b> for completing joining formalities on the "
            "day of joining by <b>10:00 a.m.</b> at your respective location of joining as following.", page3_body_style
        ))
                # =========================================================================
        # 📊 LAYER C: HS DESK LOCATION ADDRESS TABLE (Matches MS Word Layout)
        # =========================================================================
        story.append(Spacer(1, 4))
        story.append(Paragraph("<b>Location of HS (HR Services) desk for joining formalities:</b>", ParagraphStyle('HsLabel', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.5, spaceAfter=4)))

        # Define compact typography inside table grid cells
        t4_th_style = ParagraphStyle('T4Head', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0, textColor=colors.HexColor("#0F172A"))
        t4_td_style = ParagraphStyle('T4Body', parent=body_style, fontName=FONT_NAME_BODY, fontSize=8.0, leading=11, textColor=colors.HexColor("#334155"))

        location_matrix_data = [
            [Paragraph("<b>Location</b>", t4_th_style), Paragraph("<b>Address</b>", t4_th_style)],
            [
                Paragraph("Panagudi, Tirunelveli", t4_td_style), 
                Paragraph("Kamaraj Tech Campus, 2039/128, Gandhi East Street,<br/>Panagudi Post, Radhapuram Taluk,<br/>Tirunelveli DT, Pin 627109<br/>Land Mark: VAO office (Panagudi Bypass Road)", t4_td_style)
            ]
        ]

        # Total explicit column widths = 528px (fits standard letter page bounds cleanly)
        location_table = Table(location_matrix_data, colWidths=[150, 378], hAlign='LEFT')
        location_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#94A3B8")),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(location_table)
        story.append(Spacer(1, 14))

        # =========================================================================
        # 📊 LAYER D: COST TO COMPANY (CTC) COMPENSATION COMPONENT TABLE
        # =========================================================================
        # Primary Table Title Heading Panel Row
        ctc_title_style = ParagraphStyle('CtcTitle', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.5, textColor=colors.HexColor("#0F172A"), alignment=1)
        
        ctc_matrix_data = [
            # Main Header Banner Span
            [Paragraph(f"<b>COST TO COMPANY (CTC) FOR {candidate_name.upper()}</b>", ctc_title_style), ""],
            
            # 🎯 PLACED INSIDE THE VARIABLE ARRAY LIST ELEMENT:
            [
                Paragraph("Email:", t4_td_style), 
                Paragraph(f"{candidate_email}", t4_td_style)
            ],
            
            [Paragraph("Band:", t4_td_style), Paragraph("", t4_td_style)],
            [Paragraph("Designation:", t4_td_style), Paragraph(f"<b>{designation}</b>", t4_td_style)],
            [Paragraph("Issued Date:", t4_td_style), Paragraph(f"{joining_date}", t4_td_style)],
            
            # Sub Heading Row Span
            [Paragraph("<b>Monthly Compensation (In Rs.)</b>", ParagraphStyle('CtcSub', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0, alignment=1)), ""],
            
            # Itemized Compensation Component Cells
            [Paragraph("Basic Salary", t4_td_style), Paragraph("1000", t4_td_style)],
            [Paragraph("House Rent Allowance/Company Leased Accommodation", t4_td_style), Paragraph("1000", t4_td_style)],
            [Paragraph("Conveyance Allowance", t4_td_style), Paragraph("1000", t4_td_style)],
            [Paragraph("Medical Allowance", t4_td_style), Paragraph("1000", t4_td_style)],
            [Paragraph("Holiday Allowance", t4_td_style), Paragraph("1000", t4_td_style)],
            [Paragraph("City Compensatory Allowance###", t4_td_style), Paragraph("1000", t4_td_style)],
            [Paragraph("Compensatory Allowance", t4_td_style), Paragraph("1000", t4_td_style)],
            
            # Summary Calculation Row
            [Paragraph("<b>TOTAL Monthly (A)</b>", ParagraphStyle('CtcTotal', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0)), Paragraph("<b>7000</b>", ParagraphStyle('CtcVal', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0))]
        ]

        # Uniform layout block column sizing dimensions [col1=378px, col2=150px]
        ctc_table = Table(ctc_matrix_data, colWidths=[378, 150], hAlign='LEFT')
        ctc_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#475569")), # Crisp dark gray grid lines
            
            # 🎯 SPANNING CONFIGURATIONS: Merges column cells natively to mimic MS Word headers
            ('SPAN', (0,0), (1,0)), # Merges row 0 (Main Title)
            ('SPAN', (0,5), (1,5)), # Merges row 5 (Monthly Compensation label)
            
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F1F5F9")), # Soft slate background for top banner
            ('BACKGROUND', (0,5), (-1,5), colors.HexColor("#F8FAFC")), # Light background for compensation subtitle
            
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(ctc_table)
                # Inside apps/bgv_system/views.py -> right below story.append(ctc_table)
                # Inside apps/bgv_system/views.py -> directly below story.append(ctc_table)
        story.append(Spacer(1, 4))

        # =========================================================================
        # 📊 NEW CORRECTED LAYOUT: STANDALONE ANNUALISED TOTAL (B) ROW
        # =========================================================================
        annualised_matrix_data = [
            [
                Paragraph("<b>TOTAL: Monthly : Annualised (B)</b>", ParagraphStyle('BTotal', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0)), 
                Paragraph("<b>84000</b>", ParagraphStyle('BVal', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0))
            ]
        ]
        
        # Matches the exact column width tracking bounds [col1=378px, col2=150px]
        annualised_table = Table(annualised_matrix_data, colWidths=[378, 150], hAlign='LEFT')
        annualised_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#475569")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(annualised_table)
        story.append(Spacer(1, 10))

        # =========================================================================
        # 📊 LAYER E: ANNUAL COMPONENTS TABLE GRID
        # =========================================================================
        annual_matrix_data = [
            [Paragraph("<b>Annual Components (In Rs.)</b>", ParagraphStyle('AnnSub', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0, alignment=1)), ""],
            [Paragraph("Provident Fund", t4_td_style), Paragraph("NA", t4_td_style)],
            [Paragraph("Gratuity", t4_td_style), Paragraph("NA", t4_td_style)],
            [Paragraph("Insurance & Medical Benefits", t4_td_style), Paragraph("NA", t4_td_style)],
            [Paragraph("<b>TOTAL Annual (C)</b>", ParagraphStyle('AnnTot', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0)), Paragraph("<b>NA</b>", ParagraphStyle('AnnVal', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0))]
        ]

        annual_table = Table(annual_matrix_data, colWidths=[378, 150], hAlign='LEFT')
        annual_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#475569")),
            ('SPAN', (0,0), (1,0)),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(annual_table)
        story.append(Spacer(1, 10))

        # =========================================================================
        # 📊 LAYER F: VARIABLE COMPONENTS TABLE GRID (Annualised row removed from here)
        # =========================================================================
        variable_matrix_data = [
            [Paragraph("<b>Variable Components (In Rs.)</b>", ParagraphStyle('VarSub', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0, alignment=1)), ""],
            [Paragraph("Engagement PB @ 100% achievement levels (paid monthly)", t4_td_style), Paragraph("NA", t4_td_style)],
            [Paragraph("Performance Bonus @ 100% achievement levels+", t4_td_style), Paragraph("NA", t4_td_style)],
            [Paragraph("<b>TOTAL Variable Components (D)</b>", ParagraphStyle('VarTot', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0)), Paragraph("<b>NA</b>", ParagraphStyle('VarVal', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0))],
            [Paragraph("<b>Total Annual Earning Opportunity (A) + (C) + (D)</b>", ParagraphStyle('AnnEarn', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0)), Paragraph("<b>84000</b>", ParagraphStyle('EarnVal', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0))]
        ]
        

        variable_table = Table(variable_matrix_data, colWidths=[378, 150], hAlign='LEFT')
        variable_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#475569")),
            ('SPAN', (0,0), (1,0)),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
            ('BACKGROUND', (0,4), (-1,4), colors.HexColor("#E2E8F0")), 
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(variable_table)
        # Inside apps/bgv_system/views.py -> right below story.append(earning_table)
        story.append(Spacer(1, 6))

        # =========================================================================
        # 📊 LAYER G: INSURANCE & MEDICAL SUB-LIMITS SUMMARY TABLE
        # =========================================================================
        insurance_matrix_data = [
            [
                Paragraph("<b>$ INSURANCE & MEDICAL BENEFITS (in Rs.)</b>", ParagraphStyle('InsSub', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0)), 
                Paragraph("<b>MAX SUB-LIMITS (per annum)</b>", ParagraphStyle('InsLimit', parent=body_style, fontName=FONT_NAME_BOLD, fontSize=8.0))
            ],
            [Paragraph("Hospitalization cost reimbursement limit", t4_td_style), Paragraph("", t4_td_style)],
            [Paragraph("Term life Insurance Cover (including EDLI)", t4_td_style), Paragraph("", t4_td_style)],
            [Paragraph("Disability cover due to accident (upto)", t4_td_style), Paragraph("", t4_td_style)]
        ]

        insurance_table = Table(insurance_matrix_data, colWidths=[378, 150], hAlign='LEFT')
        insurance_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#475569")),
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F8FAFC")),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 4),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(insurance_table)
        story.append(Spacer(1, 10))

        # =========================================================================
        # 📑 LAYER H: LEGAL FOOTNOTES & EXPLANATIONS BORDER BOX (Matches Word Image)
        # =========================================================================
        footnote_style = ParagraphStyle(
            'CtcFinePrint', parent=body_style,
            fontName=FONT_NAME_BODY, fontSize=7.5,
            leading=10.0, spaceAfter=2, alignment=4 # Justified text alignments
        )
        
        # Build out cell layout text segments manually
        footnote_story = []
        footnote_story.append(Paragraph("+ Year-end Performance Bonus is not payable on prorate basis in the event of employee leaving the organization prior to the completion of the performance review cycle.", footnote_style))
        footnote_story.append(Paragraph("Holiday Allowance can be converted into LTA. Please refer guidelines and contact the respective HR Person.", footnote_style))
        footnote_story.append(Paragraph("### Your CCA amount will be subject to your working location - City / Zone classification as per the Policy. Component will subject to change if there is a change in your band or working location (City)", footnote_style))
        footnote_story.append(Paragraph("Engagement PB will be payable on a monthly basis as per EPB guidelines", footnote_style))
        footnote_story.append(Paragraph("Relocation expenses will be applicable as per Relocation Expenses for New Employees Policy on which will be recovered if you leave Voxlom before 12 months of your joining.", footnote_style))
        
        # NOTE Block items
        footnote_story.append(Spacer(1, 2))
        footnote_story.append(Paragraph("<b>NOTE :</b>", ParagraphStyle('NoteHeading', parent=footnote_style, fontName=FONT_NAME_BOLD)))
        footnote_story.append(Paragraph("All salary components are governed by the company policies and statutory guidelines.", footnote_style))
        footnote_story.append(Paragraph("This salary sheet is strictly confidential and must not be discussed with anyone other than your Voxlom Reporting Manager", footnote_style))
        footnote_story.append(Paragraph("All personal tax liability arising out of compensation and joining expense (if any) will be borne solely by the employee", footnote_style))

        # Pack the entire footnote array story inside a single bounded box cell table
        notes_matrix_data = [[footnote_story]]
        notes_outer_table = Table(notes_matrix_data, colWidths=[528], hAlign='LEFT')
        notes_outer_table.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#475569")), # Matches outer table borders matching image
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(notes_outer_table)
        story.append(Spacer(1, 10))


        story.append(NextPageTemplate('page5'))
        story.append(PageBreak())

        # =========================================================================
        # 🚀 EMBED STRUCTURAL RENDERING ENGINE BUILD TO BUFFER STREAM
        # =========================================================================
        doc.build(story)
        buffer.seek(0)

        # Dispatches binary stream values directly to response layer to eliminate crashes
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        
        # Change 'attachment' to 'inline' so the browser opens it natively on screen instantly!
        response['Content-Disposition'] = f'inline; filename="Official_Offer_Letter_{candidate_name.replace(" ", "_")}.pdf"'
        return response

    # Default fallback routing gate if accessed via standard HTTP GET loops instead of form POST submissions
    return redirect('bgv_dashboard')







def verify_candidate(request, submission_id):
    candidate = get_object_or_404(UnknownCandidateBGVCheck, submission_id=submission_id)
    candidate.is_verified_by_officer = True
    candidate.save()
    messages.success(request, f"Candidate {candidate.submission_id} verified by officer.")
    return redirect("bgv_officer_desk")