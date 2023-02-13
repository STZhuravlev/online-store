from django.views.generic import DetailView
from product.services import get_category
from product.models import Offer
from .models import Seller
from orders.models import OrderItem


class SellerInfo(DetailView):
    model = Seller
    template_name = 'shop/seller.html'
    context_object_name = 'seller'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        popular = {}
        popular_queryset = OrderItem.objects.filter(offer__seller_id=kwargs['object'].id).\
            values_list('offer__id', 'quantity')
        for i in popular_queryset:
            if i[0] in popular:
                popular[str(i[0])] += int(i[1])
            else:
                popular[str(i[0])] = int(i[1])
        context['popular'] = Offer.objects.filter(pk__in=sorted(popular, reverse=True)[:10])
        context['categories'] = get_category()
        return context
