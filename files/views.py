from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
import os
import json
from pathlib import Path
import base64

# Default share root - change this to your desired folder
SHARE_ROOT = Path('/home/shahzan')

def index(request):
    """Main page with folder browser"""
    # Get current path from query param, default to SHARE_ROOT
    current_path = request.GET.get('path', str(SHARE_ROOT))
    
    # Security: ensure path is within SHARE_ROOT
    try:
        current = Path(current_path).resolve()
        root = SHARE_ROOT.resolve()
        
        # Only allow paths within share root
        if not str(current).startswith(str(root)):
            current = root
            current_path = str(root)
    except:
        current = SHARE_ROOT
        current_path = str(SHARE_ROOT)
    
    items = []
    
    # Build breadcrumb
    breadcrumb = []
    rel_parts = current.relative_to(SHARE_ROOT).parts if current != SHARE_ROOT else []
    breadcrumb.append({'name': 'Home', 'path': str(SHARE_ROOT)})
    for i, part in enumerate(rel_parts):
        part_path = str(SHARE_ROOT.joinpath(*rel_parts[:i+1]))
        breadcrumb.append({'name': part, 'path': part_path})
    
    # Add parent directory if not at root
    if current != SHARE_ROOT:
        parent = current.parent
        if str(parent).startswith(str(SHARE_ROOT)):
            items.append({
                'type': 'parent',
                'name': '..',
                'path': str(parent)
            })
    
    # List directories and files
    try:
        for item in sorted(current.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
            items.append({
                'type': 'dir' if item.is_dir() else 'file',
                'name': item.name,
                'path': str(item),
                'size': item.stat().st_size if item.is_file() else 0
            })
    except PermissionError:
        items.append({'type': 'error', 'name': 'Permission denied'})
    
    return render(request, 'files/index.html', {
        'items': items,
        'items_json': json.dumps(items),
        'current_path': str(current),
        'share_root': str(SHARE_ROOT),
        'breadcrumb': breadcrumb
    })

@csrf_exempt
def upload_file(request):
    """Handle file upload to current directory"""
    if request.method == 'POST':
        current_path = request.POST.get('path', str(SHARE_ROOT))
        uploaded_file = request.FILES.get('file')
        
        if uploaded_file:
            try:
                target_dir = Path(current_path).resolve()
                target_dir.mkdir(parents=True, exist_ok=True)
                
                save_path = target_dir / uploaded_file.name
                with open(save_path, 'wb+') as dest:
                    for chunk in uploaded_file.chunks():
                        dest.write(chunk)
                
                return JsonResponse({'success': True, 'name': uploaded_file.name})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False}, status=400)

def download_file(request):
    """Download a file"""
    # Get path from query param
    file_path = request.GET.get('path')
    
    if not file_path:
        return JsonResponse({'error': 'No file path provided'}, status=400)
    
    path = Path(file_path).resolve()
    
    # Security check
    root = SHARE_ROOT.resolve()
    if not str(path).startswith(str(root)):
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    if path.exists() and path.is_file():
        return FileResponse(open(path, 'rb'), as_attachment=True, filename=path.name)
    
    return JsonResponse({'error': 'File not found'}, status=404)

@csrf_exempt
def delete_file(request):
    """Delete a file or folder"""
    if request.method == 'DELETE':
        import json
        try:
            data = json.loads(request.body)
            file_path = data.get('path')
            
            if not file_path:
                return JsonResponse({'success': False, 'error': 'No path provided'}, status=400)
            
            path = Path(file_path).resolve()
            
            # Security check
            root = SHARE_ROOT.resolve()
            if not str(path).startswith(str(root)):
                return JsonResponse({'success': False, 'error': 'Access denied'}, status=403)
            
            if path.exists():
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    import shutil
                    shutil.rmtree(path)
                return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False}, status=404)

@csrf_exempt
def create_folder(request):
    """Create a new folder"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        folder_path = data.get('path')
        folder_name = data.get('name')
        
        if folder_path and folder_name:
            try:
                new_folder = Path(folder_path).resolve() / folder_name
                new_folder.mkdir(parents=True, exist_ok=True)
                return JsonResponse({'success': True})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    return JsonResponse({'success': False}, status=400)
