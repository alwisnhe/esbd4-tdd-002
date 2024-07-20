from django.shortcuts import redirect, render
from lists.models import Item, List

def home_page(request):
	return render(request, 'home.html')

def view_list(request, list_id):
    try:
        list_ = List.objects.get(id=list_id)
    except List.DoesNotExist:
        max_id = List.objects.latest('id').id
        list_id = int(list_id) 
        if list_id > max_id:
            return redirect(f'/lists/{max_id}/')
        else:
            # Se o ID for menor que 1 ou não existir uma lista anterior, redirecione para a primeira lista
            return redirect('/lists/1/')
    return render(request, 'list.html', {'list': list_})
def new_list(request):
	list_ = List.objects.create()
	Item.objects.create(text=request.POST['item_text'], list=list_)
	return redirect(f'/lists/{list_.id}/')

def add_item(request, list_id):
	list_ = List.objects.get(id=list_id)
	Item.objects.create(text=request.POST['item_text'], list=list_)
	return redirect(f'/lists/{list_.id}/')