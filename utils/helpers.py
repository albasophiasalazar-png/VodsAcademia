def extraer_url_de_iframe(texto):
    """
    Extrae la URL de un iframe de OneDrive o devuelve el texto si ya es una URL
    
    Ejemplo:
    Input: '<iframe src="https://1drv.ms/v/c/xxx/..." width="1920" height="1080"></iframe>'
    Output: 'https://1drv.ms/v/c/xxx/...'
    
    Input: 'https://1drv.ms/v/c/xxx/...'
    Output: 'https://1drv.ms/v/c/xxx/...'
    """
    import re
    
    # Si ya es una URL simple, devolverla
    if texto.startswith('http') and '<iframe' not in texto.lower():
        return texto.strip()
    
    # Buscar src="..." o src='...' en el iframe
    match = re.search(r'src=["\']([^"\']+)["\']', texto)
    if match:
        return match.group(1).strip()
    
    # Si no encuentra nada, devolver el texto original
    return texto.strip()

def formatear_fecha(fecha_str):
    """
    Convierte una fecha en formato YYYY-MM-DD a DD/MM/YYYY
    
    Ejemplo:
    Input: '2025-12-30'
    Output: '30/12/2025'
    
    Input: None o ''
    Output: 'Sin fecha'
    """
    if not fecha_str:
        return 'Sin fecha'
    
    try:
        from datetime import datetime
        # Intentar parsear la fecha
        if isinstance(fecha_str, str):
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
        else:
            fecha = fecha_str
        return fecha.strftime('%d/%m/%Y')
    except:
        return fecha_str if fecha_str else 'Sin fecha'

def convertir_url_onedrive_embed(url):
    """
    Convierte una URL de OneDrive para compartir en una URL de embed
    
    Ejemplo:
    De: https://onedrive.live.com/?id=ABC123
    A: https://onedrive.live.com/embed?resid=ABC123&authkey=...
    """
    if "embed" in url:
        return url
    
    # Si es un link de compartir, intentar convertir
    if "onedrive.live.com" in url or "1drv.ms" in url:
        # Aquí puedes agregar lógica adicional si es necesario
        return url
    
    return url

def extraer_video_id_onedrive(url):
    """Extrae el ID del video de una URL de OneDrive"""
    if "resid=" in url:
        parts = url.split("resid=")
        if len(parts) > 1:
            video_id = parts[1].split("&")[0]
            return video_id
    return None

def formatear_duracion(segundos):
    """Convierte segundos a formato HH:MM:SS o MM:SS"""
    if not segundos:
        return "N/A"
    
    try:
        segundos = int(segundos)
        horas = segundos // 3600
        minutos = (segundos % 3600) // 60
        segs = segundos % 60
        
        if horas > 0:
            return f"{horas:02d}:{minutos:02d}:{segs:02d}"
        else:
            return f"{minutos:02d}:{segs:02d}"
    except:
        return segundos
