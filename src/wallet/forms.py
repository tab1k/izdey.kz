from django import forms
import re
from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from users.models import User
from .models import Transaction


class TransferForm(forms.Form):
    receiver_username = forms.CharField(
        max_length=150,
        label='Номер пользователя',
        widget=forms.TextInput(attrs={
            'class': 'formkz-control',
            'placeholder': 'Номер телефона получателя',
            'value': '+7 (',  # Начальное значение поля с префиксом +7 и открывающей скобкой
            'oninput': """if (!this.value.startsWith('+7 (')) {
                            this.value = '+7 (' + this.value.replace('+7 (', '');
                        } 
                        if (this.value.length === 8 && this.value[7] !== ')') {
                            this.value = this.value.slice(0, 7) + ')' + this.value.slice(7);
                        }
                        if (this.value.length === 9 && this.value[8] !== ' ') {
                            this.value = this.value.slice(0, 8) + ' ' + this.value.slice(8);
                        }
                        if (this.value.length === 13 && this.value[12] !== ' ') {
                            this.value = this.value.slice(0, 12) + ' ' + this.value.slice(12);
                        }""",  # Скрипт для автоматического добавления скобок и пробелов
        })
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label='Сумма',
        widget=forms.NumberInput(attrs={
            'class': 'formkz-control',
            'placeholder': 'Введите сумму'
        })
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'formkz-control',
            'rows': 3,
            'placeholder': 'Введите описание (необязательно)'
        }),
        required=False,
        label='Сообщение'
    )

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError("Сумма должна быть положительной.")
        return amount

    def clean_receiver_username(self):
        username = self.cleaned_data.get('receiver_username')
        # Удаление всех нецифровых символов из номера телефона для поиска пользователя
        cleaned_username = re.sub(r'[^\d]', '', username)

        # Убедимся, что номер начинается с 7
        if cleaned_username.startswith('7'):
            cleaned_username = '+7' + cleaned_username[1:]  # добавляем +7
        elif not cleaned_username.startswith('+'):
            cleaned_username = '+7' + cleaned_username  # добавляем +7 если нет префикса

        try:
            user = User.objects.get(phone_number=cleaned_username)
        except User.DoesNotExist:
            raise forms.ValidationError(f'Пользователь с таким номером не найден: {username}')

        # Возвращаем оригинальный формат номера для дальнейшего использования
        return cleaned_username
