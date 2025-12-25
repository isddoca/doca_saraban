import os
import uuid
from django.utils.text import slugify
from pathlib import Path

def handle_unicode_file(uploaded_file):
    """
    Handle file uploads with Unicode characters in filename
    """
    try:
        original_name = uploaded_file.name
        
        # Check if filename contains non-ASCII characters
        if any(ord(char) > 127 for char in original_name):
            name, ext = os.path.splitext(original_name)
            safe_name = slugify(name, allow_unicode=True)
            if not safe_name:
                safe_name = str(uuid.uuid4())[:8]
            uploaded_file.name = f"{safe_name}{ext}"
        
        return uploaded_file
    except UnicodeEncodeError:
        # Emergency fallback: use UUID filename
        _, ext = os.path.splitext(uploaded_file.name)
        uploaded_file.name = f"{str(uuid.uuid4())[:8]}{ext}"
        return uploaded_file

def safe_delete_file(file_obj):
    """
    Safely delete a file with Unicode handling
    """
    try:
        if file_obj and file_obj.file:
            file_obj.file.delete(save=False)
        return True
    except Exception as e:
        try:
            # Fallback: Use pathlib
            from config import settings
            file_path = Path(settings.MEDIA_ROOT) / file_obj.file.name
            if file_path.exists():
                file_path.unlink()
            return True
        except Exception as e2:
            print(f"Error deleting file: {e2}")
            return False

def create_safe_docfile(uploaded_file, doc_model):
    """
    Create DocFile with Unicode-safe filename
    """
    from doc_record.models import DocFile
    
    try:
        safe_file = handle_unicode_file(uploaded_file)
        return DocFile.objects.create(file=safe_file, doc=doc_model)
    except Exception as e:
        print(f"Error creating DocFile: {e}")
        return None