from django import forms
from .models import Document

class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["title", "file"]

    def clean_file(self):
        f = self.cleaned_data["file"]
        if not f.name.lower().endswith(".pdf"):
            raise forms.ValidationError("Please upload a PDF.")
        # ~500+ pages PDFs are often ~5–50MB; adjust limit as needed
        if f.size > 200 * 1024 * 1024:
            raise forms.ValidationError("File too large (>200MB).")
        return f
