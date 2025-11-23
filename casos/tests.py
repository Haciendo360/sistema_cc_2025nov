from django.test import TestCase, Client
from django.urls import reverse
from usuarios.models import Usuario
from .models import Caso

class CasoTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.juez = Usuario.objects.create_user(
            username='juez_caso',
            password='password123',
            rol='juez',
            estado_aprobacion='aprobado',
            cedula='0000000004'
        )
        self.client.force_login(self.juez)

    def test_crear_caso(self):
        response = self.client.post(reverse('casos:crear_caso'), {
            'cedula_solicitante': '1234567890',
            'nombre_solicitante': 'Juan Perez',
            'telefono_solicitante': '0987654321',
            'direccion_solicitante': 'Calle 1',
            'cedula_involucrado': '0987654321',
            'nombre_involucrado': 'Maria Lopez',
            'telefono_involucrado': '1234567890',
            'direccion_involucrado': 'Calle 2',
            'tipo_conflicto': 'vecinal',
            'bloque_residencial': 'BLOQUE_15',
            'descripcion_caso': 'Ruido excesivo',
        })
        if response.status_code != 302:
            print(response.context['form'].errors)
        self.assertEqual(response.status_code, 302) 
        self.assertEqual(Caso.objects.count(), 1)

    def test_panel_juez_access(self):
        response = self.client.get(reverse('casos:panel_juez'))
        self.assertEqual(response.status_code, 200)
