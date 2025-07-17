from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# Puedes poner este token en settings.py y leerlo desde allí si lo prefieres
NODE_RED_TOKEN = "TU_TOKEN_SEGURO"

@csrf_exempt
def node_red_receiver(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Método no permitido'}, status=405)

    token = request.headers.get('X-API-TOKEN')
    if token != NODE_RED_TOKEN:
        return JsonResponse({'error': 'Token inválido'}, status=401)

    try:
        data = json.loads(request.body)
        # Aquí puedes procesar los datos recibidos
        print("Datos recibidos desde Node-RED:", data)
        return JsonResponse({'success': True, 'received': data})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
