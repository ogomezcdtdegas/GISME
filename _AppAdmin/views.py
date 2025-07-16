from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django import forms

class UsuarioForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # 🔹 Encripta la contraseña
        if commit:
            user.save()
        return user

class UsuarioCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UsuarioForm
    template_name = '_AppAdmin/index.html'
    success_url = reverse_lazy('crear_usuario')  # Redirige a la misma página tras éxito

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_section'] = 'admin'  # Marcar la sección de administración como activa
        return context
