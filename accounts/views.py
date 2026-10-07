import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from .models import User, Address, Wishlist, RecentlyViewed
from .forms import UserRegistrationForm, UserProfileUpdateForm, AddressForm
from cart.utils import get_or_create_cart
from catalog.models import Product

def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    if request.method == 'POST':
        # Anti-bot honeypot trap
        if request.POST.get('website'):
            return redirect('core:home')

        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.verification_token = uuid.uuid4().hex
            user.is_verified = True  # Automatically verified for seamless local dev & staging
            user.save()

            old_session_key = request.session.session_key
            login(request, user)

            # Merge guest cart into user cart
            if old_session_key:
                from cart.models import Cart
                guest_cart = Cart.objects.filter(session_key=old_session_key, is_active=True, user__isnull=True).first()
                if guest_cart:
                    guest_cart.merge_with_user(user)

            lang = getattr(request, 'LANGUAGE_CODE', 'en')
            welcome_msg = f"خوش آمدید {user.get_full_name()}! حساب کاربری شما با موفقیت ایجاد شد." if lang == 'fa' else f"Welcome {user.get_full_name()}! Your account has been created."
            messages.success(request, welcome_msg)
            return redirect('accounts:profile')
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:profile')

    next_url = request.GET.get('next') or request.POST.get('next') or 'accounts:profile'

    if request.method == 'POST':
        # Anti-bot honeypot trap
        if request.POST.get('website'):
            return redirect('core:home')

        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')
        remember_me = request.POST.get('remember_me') == 'on'

        # Rate limiting: max 5 failed attempts per 5 minutes per IP + email
        from django.core.cache import cache
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', '127.0.0.1')).split(',')[0].strip()
        cache_key = f"login_failures_{client_ip}_{email}"
        failed_count = cache.get(cache_key, 0)

        if failed_count >= 5:
            lang = getattr(request, 'LANGUAGE_CODE', 'en')
            lock_msg = "تعداد تلاش‌های ناموفق بیش از حد مجاز است. لطفاً ۵ دقیقه دیگر دوباره تلاش کنید." if lang == 'fa' else "Too many failed login attempts. Please wait 5 minutes before trying again."
            messages.error(request, lock_msg)
            return render(request, 'accounts/login.html', {'email': email, 'next': next_url})

        user = authenticate(request, username=email, password=password)
        if user:
            cache.delete(cache_key)
            if not user.is_active:
                lang = getattr(request, 'LANGUAGE_CODE', 'en')
                inactive_msg = "حساب کاربری شما غیرفعال شده است. لطفاً با پشتیبانی تماس بگیرید." if lang == 'fa' else "Your account is disabled. Please contact support."
                messages.error(request, inactive_msg)
                return render(request, 'accounts/login.html', {'email': email, 'next': next_url})

            old_session_key = request.session.session_key
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)  # Expires when browser closes
            else:
                request.session.set_expiry(1209600)  # 2 weeks

            # Merge guest cart
            if old_session_key:
                from cart.models import Cart
                guest_cart = Cart.objects.filter(session_key=old_session_key, is_active=True, user__isnull=True).first()
                if guest_cart:
                    guest_cart.merge_with_user(user)

            lang = getattr(request, 'LANGUAGE_CODE', 'en')
            welcome_back = f"با موفقیت وارد شدید. خوش آمدید {user.get_full_name()}!" if lang == 'fa' else f"Signed in successfully. Welcome back, {user.get_full_name()}!"
            messages.success(request, welcome_back)
            return redirect(next_url)
        else:
            cache.set(cache_key, failed_count + 1, timeout=300)
            lang = getattr(request, 'LANGUAGE_CODE', 'en')
            err_msg = "ایمیل یا رمز عبور وارد شده نادرست است." if lang == 'fa' else "Invalid email or password."
            messages.error(request, err_msg)

    return render(request, 'accounts/login.html', {'next': next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "شما با موفقیت از حساب کاربری خود خارج شدید.")
    return redirect('core:home')


def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        user = User.objects.filter(email=email).first()
        if user:
            token = uuid.uuid4().hex
            user.verification_token = token
            user.save(update_fields=['verification_token'])

            reset_link = request.build_absolute_uri(
                reverse('accounts:reset_password', kwargs={'token': token})
            )
            # Send password reset email
            subject = "بازیابی رمز عبور فروشگاه اینترنتی"
            message = f"درود {user.get_full_name()}،\n\nبرای بازیابی رمز عبور خود روی لینک زیر کلیک کنید:\n{reset_link}\n\nاگر این درخواست توسط شما ثبت نشده، این پیام را نادیده بگیرید."
            try:
                send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=True)
            except Exception:
                pass

        messages.success(request, "اگر ایمیل وارد شده در سامانه موجود باشد، دستورالعمل بازیابی رمز عبور ارسال شد.")
        return redirect('accounts:login')

    return render(request, 'accounts/forgot_password.html')


def reset_password_view(request, token):
    user = get_object_or_404(User, verification_token=token)
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            user.verification_token = ""
            user.save(update_fields=['verification_token'])
            messages.success(request, "رمز عبور شما با موفقیت تغییر یافت. اکنون می‌توانید وارد شوید.")
            return redirect('accounts:login')
    else:
        form = SetPasswordForm(user)

    return render(request, 'accounts/reset_password.html', {'form': form, 'token': token})


def verify_email_view(request, token):
    user = get_object_or_404(User, verification_token=token)
    user.is_verified = True
    user.verification_token = ""
    user.save(update_fields=['is_verified', 'verification_token'])
    messages.success(request, "ایمیل شما با موفقیت تایید شد.")
    return redirect('accounts:profile')


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            # Update user model fields
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.phone_number = form.cleaned_data['phone_number']
            request.user.save()
            messages.success(request, "اطلاعات حساب کاربری شما با موفقیت به‌روزرسانی شد.")
            return redirect('accounts:profile')
    else:
        form = UserProfileUpdateForm(instance=profile, user=request.user)

    recent_orders = request.user.orders.prefetch_related('items').all()[:5]
    addresses = request.user.addresses.all()
    wishlist_count = request.user.wishlist_items.count()

    context = {
        'form': form,
        'profile': profile,
        'recent_orders': recent_orders,
        'addresses': addresses,
        'wishlist_count': wishlist_count,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "رمز عبور شما با موفقیت تغییر یافت.")
            return redirect('accounts:profile')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {'form': form})


# Address Management with Strict IDOR Protection
@login_required
def address_list_view(request):
    if request.user.is_staff:
        messages.warning(request, "این بخش برای حساب‌های مدیریتی در دسترس نیست.")
        return redirect('accounts:profile')
    addresses = request.user.addresses.all()
    return render(request, 'accounts/address_list.html', {'addresses': addresses})


@login_required
def address_create_view(request):
    if request.user.is_staff:
        messages.warning(request, "این بخش برای حساب‌های مدیریتی در دسترس نیست.")
        return redirect('accounts:profile')
    next_url = request.GET.get('next') or 'accounts:address_list'
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, "آدرس جدید با موفقیت اضافه شد.")
            return redirect(next_url)
    else:
        form = AddressForm()
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'افزودن آدرس جدید'})


@login_required
def address_edit_view(request, pk):
    if request.user.is_staff:
        messages.warning(request, "این بخش برای حساب‌های مدیریتی در دسترس نیست.")
        return redirect('accounts:profile')
    address = get_object_or_404(Address, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, "آدرس پستی با موفقیت ویرایش شد.")
            return redirect('accounts:address_list')
    else:
        form = AddressForm(instance=address)
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'ویرایش آدرس'})


@login_required
@require_POST
def address_delete_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.delete()
    messages.success(request, "آدرس پستی حذف شد.")
    return redirect('accounts:address_list')


@login_required
@require_POST
def set_default_address_view(request, pk):
    address = get_object_or_404(Address, pk=pk, user=request.user)
    address.is_default = True
    address.save()
    messages.success(request, f"آدرس «{address.title}» به عنوان آدرس پیش‌فرض تنظیم شد.")
    return redirect('accounts:address_list')


# Wishlist
@login_required
def wishlist_view(request):
    if request.user.is_staff:
        messages.warning(request, "این بخش برای حساب‌های مدیریتی در دسترس نیست.")
        return redirect('accounts:profile')
    items = request.user.wishlist_items.select_related('product', 'product__category').prefetch_related('product__images')
    return render(request, 'accounts/wishlist.html', {'wishlist_items': items})


@login_required
@require_POST
def wishlist_toggle_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    existing = Wishlist.objects.filter(user=request.user, product=product).first()
    if existing:
        existing.delete()
        is_in_wishlist = False
        message = "کالا از لیست علاقه‌مندی‌ها حذف شد."
    else:
        Wishlist.objects.create(user=request.user, product=product)
        is_in_wishlist = True
        message = "کالا به لیست علاقه‌مندی‌ها اضافه شد."

    count = request.user.wishlist_items.count()
    return JsonResponse({
        'status': 'success',
        'is_in_wishlist': is_in_wishlist,
        'wishlist_count': count,
        'message': message
    })


# Order History with IDOR Protection
@login_required
def order_history_view(request):
    if request.user.is_staff:
        messages.warning(request, "این بخش برای حساب‌های مدیریتی در دسترس نیست.")
        return redirect('accounts:profile')
    orders = request.user.orders.prefetch_related('items').order_by('-created_at')
    return render(request, 'accounts/order_history.html', {'orders': orders})


@login_required
def order_detail_view(request, order_number):
    if request.user.is_staff:
        messages.warning(request, "این بخش برای حساب‌های مدیریتی در دسترس نیست.")
        return redirect('accounts:profile')
    order = get_object_or_404(request.user.orders.prefetch_related('items', 'payments'), order_number=order_number)
    return render(request, 'accounts/order_detail.html', {'order': order})
