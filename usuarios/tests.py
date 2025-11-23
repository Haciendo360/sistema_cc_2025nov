from django.test import TestCase, Client
from django.urls import reverse
from .models import Usuario

class UsuarioTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = Usuario.objects.create_superuser(
            username='admin_test',
            email='admin@test.com',
            password='password123',
            rol='admin',
            estado_aprobacion='aprobado',
            cedula='0000000001'
        )
        self.juez_user = Usuario.objects.create_user(
            username='juez_test',
            email='juez@test.com',
            password='password123',
            rol='juez',
            estado_aprobacion='aprobado',
            cedula='0000000002'
        )

    def test_login_admin(self):
        response = self.client.post(reverse('usuarios:login'), {
            'username': 'admin_test',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('casos:panel_admin'))

    def test_login_juez(self):
        response = self.client.post(reverse('usuarios:login'), {
            'username': 'juez_test',
            'password': 'password123'
        })
        self.assertRedirects(response, reverse('casos:panel_juez'))

    def test_usuario_creation(self):
        user = Usuario.objects.create_user(
            username='new_user',
            password='password123',
            cedula='0000000003'
        )
        self.assertEqual(user.estado_aprobacion, 'pendiente')
        self.assertEqual(user.rol, 'juez')
