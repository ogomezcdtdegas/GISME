from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django import forms
from .models import UserRole

class UsuarioForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=UserRole.ROLES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Rol',
        initial='supervisor'
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'email': 'Correo Electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Verificar si el email ya existe (excepto si estamos editando el mismo usuario)
        if self.instance.pk:
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este correo electrónico ya está registrado.')
        else:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError('Este correo electrónico ya está registrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        # Usar email como username (Django lo requiere internamente)
        user.username = self.cleaned_data['email']
        # No establecer contraseña - se autentica por Azure AD
        user.set_unusable_password()
        
        if commit:
            user.save()
            # Crear o actualizar el rol del usuario
            role_obj, created = UserRole.objects.get_or_create(user=user)
            role_obj.role = self.cleaned_data['role']
            role_obj.save()
        return user

class UsuarioCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UsuarioForm
    template_name = '_AppAdmin/index.html'
    success_url = reverse_lazy('crear_usuario')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'admin'
        # Obtener usuarios con sus roles
        usuarios = User.objects.select_related('user_role').all().order_by('-date_joined')
        context['usuarios'] = usuarios
        return context

    def form_valid(self, form):
        messages.success(self.request, 'Usuario creado exitosamente.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Error al crear el usuario. Revise los datos ingresados.')
        return super().form_invalid(form)

class UsuarioUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UsuarioForm
    template_name = '_AppAdmin/index.html'
    success_url = reverse_lazy('crear_usuario')

    def get_initial(self):
        initial = super().get_initial()
        # Agregar el rol actual del usuario
        if hasattr(self.object, 'user_role'):
            initial['role'] = self.object.user_role.role
        return initial

    def form_valid(self, form):
        messages.success(self.request, 'Usuario actualizado exitosamente.')
        return super().form_valid(form)

@method_decorator(csrf_exempt, name='dispatch')
class UsuarioDeleteView(LoginRequiredMixin, UpdateView):
    def post(self, request, *args, **kwargs):
        user_id = request.POST.get('user_id')
        try:
            user = get_object_or_404(User, id=user_id)
            username = user.email
            user.delete()
            return JsonResponse({
                'success': True, 
                'message': f'Usuario {username} eliminado exitosamente.'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'message': f'Error al eliminar usuario: {str(e)}'
            })
