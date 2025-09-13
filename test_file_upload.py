import requests
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf():
    """Create a simple valid PDF for testing"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Add some text content
    p.drawString(100, 750, "BUSINESS CONTINUITY PLAN")
    p.drawString(100, 720, "Executive Summary:")
    p.drawString(100, 700, "This document outlines our crisis management strategy")
    p.drawString(100, 680, "Key risks include cyber attacks and natural disasters")
    p.drawString(100, 660, "Recovery procedures and emergency contacts are included")
    p.drawString(100, 640, "Regular testing and updates are scheduled quarterly")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    return buffer.getvalue()

def test_pdf_upload():
    """Test PDF upload with a properly formatted PDF"""
    # This would need to be run with proper authentication
    # Just demonstrating how to create a valid PDF for testing
    pdf_content = create_test_pdf()
    print(f"Created PDF with {len(pdf_content)} bytes")
    
    # Save to file for manual testing if needed
    with open('/app/test_business_plan.pdf', 'wb') as f:
        f.write(pdf_content)
    print("PDF saved to /app/test_business_plan.pdf")

if __name__ == "__main__":
    test_pdf_upload()