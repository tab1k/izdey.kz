from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import TemplateView, View
from users.models import *
from notifications.mixins import UnreadNotificationMixin
from favorites.mixins import *
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from .models import Deposit, Transaction
from .forms import TransferForm
from django.http import JsonResponse
import logging
from users.models import User


class WalletInfoPage(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, TemplateView):
    template_name = 'wallet/wallet_info.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location_choices'] = UserProfile.LOCATION_CHOICES
        context['user_amount'] = Deposit.objects.get(user=self.request.user).amount

        # Извлекаем транзакции, где текущий пользователь отправитель или получатель
        sent_transactions = Transaction.objects.filter(sender=self.request.user)
        received_transactions = Transaction.objects.filter(receiver=self.request.user)

        # Объединяем QuerySet'ы с использованием union()
        all_transactions = sent_transactions.union(received_transactions).order_by('-created_at')

        # Передаем только 10 последних транзакций
        context['transactions'] = all_transactions[:10]
        # Подсчитываем количество всех транзакций
        context['count'] = all_transactions.count()

        return context


class TransferView(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, FormView):
    template_name = 'wallet/transfer.html'
    form_class = TransferForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        receiver_user = None
        form = self.get_form()

        if form.is_bound and form.is_valid():
            receiver_username = form.cleaned_data.get('receiver_username')
            formatted_receiver_username = self.format_phone_number(receiver_username)
            receiver_user = User.objects.filter(phone_number=formatted_receiver_username).first()

        context['receiver_user'] = receiver_user
        context['user_amount'] = Deposit.objects.get(user=self.request.user).amount

        # Извлекаем транзакции, где текущий пользователь отправитель или получатель
        sent_transactions = Transaction.objects.filter(sender=self.request.user)
        received_transactions = Transaction.objects.filter(receiver=self.request.user)

        # Объединяем QuerySet'ы с использованием union() и подсчитываем количество транзакций
        all_transactions = sent_transactions.union(received_transactions)
        context['transaction_count'] = all_transactions.count()

        return context

    def format_phone_number(self, phone_number):
        # Удаление всех символов, кроме цифр и плюса
        phone_number = re.sub(r'\D', '', phone_number)
        # Убедимся, что номер начинается с 7
        if phone_number.startswith('7'):
            phone_number = '+7' + phone_number[1:]  # удаляем начальный 7 и добавляем +7
        elif not phone_number.startswith('+'):
            phone_number = '+7' + phone_number  # добавляем +7 если нет префикса
        return phone_number

    def form_valid(self, form):
        receiver_username = form.cleaned_data['receiver_username']
        amount = form.cleaned_data['amount']
        description = form.cleaned_data['description']

        formatted_receiver_username = self.format_phone_number(receiver_username)

        # Проверка, что отправитель и получатель не один и тот же пользователь
        sender_phone = self.request.user.phone_number
        if formatted_receiver_username == sender_phone:
            form.add_error('receiver_username', "Вы не можете перевести деньги самому себе.")
            print("Error: User is trying to transfer money to themselves.")
            return self.form_invalid(form)

        # Попробуем получить депозит отправителя
        try:
            sender_deposit = Deposit.objects.get(user=self.request.user)
        except Deposit.DoesNotExist:
            messages.error(self.request, "Не найден депозит для отправителя.")
            print("Error: Deposit for sender does not exist.")
            return self.form_invalid(form)

        # Попробуем получить получателя и депозит получателя
        try:
            receiver = User.objects.get(phone_number=formatted_receiver_username)
            receiver_deposit, created = Deposit.objects.get_or_create(user=receiver)
        except User.DoesNotExist:
            messages.error(self.request, f"Получатель с номером {formatted_receiver_username} не найден.")
            print(f"Error: User with phone number {formatted_receiver_username} does not exist.")
            return self.form_invalid(form)
        except Exception as e:
            messages.error(self.request, f"Ошибка при создании депозита для получателя: {e}")
            print(f"Error creating deposit for receiver: {e}")
            return self.form_invalid(form)

        # Проверка достаточности средств
        if sender_deposit.amount < amount:
            form.add_error(None, "Недостаточно средств на депозите.")
            print("Error: Not enough funds.")
            return self.form_invalid(form)

        # Выполнение перевода
        sender_deposit.amount -= amount
        receiver_deposit.amount += amount

        try:
            sender_deposit.save()
            receiver_deposit.save()
        except Exception as e:
            messages.error(self.request, f"Ошибка при сохранении депозитов: {e}")
            print(f"Error saving deposits: {e}")
            return self.form_invalid(form)

        # Создание записи транзакции
        try:
            Transaction.objects.create(
                sender=self.request.user,
                receiver=receiver,
                amount=amount,
                description=description
            )
        except Exception as e:
            messages.error(self.request, f"Ошибка при создании транзакции: {e}")
            print(f"Error creating transaction: {e}")
            return self.form_invalid(form)

        messages.success(self.request, "Перевод успешно выполнен.")
        return redirect('wallet:info')

    def form_invalid(self, form):
        print("Form is invalid. Errors:", form.errors)
        messages.error(self.request, "Ошибка при выполнении перевода.")
        return super().form_invalid(form)


def get_user_info(request, phone_number):
    try:
        if not phone_number.startswith('+'):
            phone_number = '+' + phone_number

        cleaned_phone_number = re.sub(r'[^\d]', '', phone_number)
        formatted_phone_number = f'+{cleaned_phone_number}'

        user = User.objects.get(phone_number=formatted_phone_number)
        data = {
            'name': user.first_name,
            'surname': user.last_name,
        }
        return JsonResponse(data)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Пользователь не найден'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


class ReplenishmentView(LoginRequiredMixin, FavoritesCountMixin, UnreadNotificationMixin, TemplateView):
    template_name = 'wallet/replenishment.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['location_choices'] = UserProfile.LOCATION_CHOICES
        context['user_amount'] = Deposit.objects.get(user=self.request.user).amount

        # Извлекаем транзакции, где текущий пользователь отправитель или получатель
        sent_transactions = Transaction.objects.filter(sender=self.request.user)
        received_transactions = Transaction.objects.filter(receiver=self.request.user)

        # Объединяем QuerySet'ы с использованием union()
        all_transactions = sent_transactions.union(received_transactions).order_by('-created_at')

        # Передаем только 10 последних транзакций
        context['transactions'] = all_transactions[:10]
        # Подсчитываем количество всех транзакций
        context['count'] = all_transactions.count()

        return context

