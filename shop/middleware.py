from users.models import CustomUser


def middleware_signal(get_response):
    def middleware(request):
        if request.get_full_path() == '/shop/test':
            user = CustomUser.objects.get(email=request.user)
            user.seller_status = 'pending'
            user.save()
        response = get_response(request)
        return response
    return middleware
