from .models import Category

def category_context(request):
    categories = Category.objects.all()
    return {'categories':categories}