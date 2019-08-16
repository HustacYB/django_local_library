from django.shortcuts import render,get_object_or_404
from .models import Book,BookInstance,Genre,Author
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
import datetime
from .forms import RenewBookForm
from django.views.generic.edit import CreateView,UpdateView,DeleteView
from django.urls import reverse_lazy



# Create your views here.

def index(request):
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instance_available = BookInstance.objects.filter(status__exact='a').count()
    num_authors=Author.objects.count()
    
    num_visits=request.session.get('num_visits',0)
    request.session['num_visits']=num_visits+1
    context = {'num_books':num_books,'num_instances':num_instances,'num_instance_availabe':num_instance_available,'num_authors':num_authors,'num_visits':num_visits}
    return render(request,'catalog/index.html',context)


class AuthorListView(generic.ListView):
    model = Author
    context_object_name = 'author_list'
    queryset = Author.objects.all()
    template_name = 'catalog/authorlist.html'

class AuthorDetailView(generic.DetailView):
    model = Author    


class BookListView(generic.ListView):
    model = Book
    context_object_name = 'my_book_list'
    queryset = Book.objects.all()[:5]
    template_name = 'catalog/booklist.html'


class BookDetailView(generic.DetailView):
    model = Book
    
    paginate_by =  2

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).order_by('due_back')


def renew_book_librarian(request,pk):
    book_inst = get_object_or_404(BookInstance,pk = pk)
    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        if form.is_valid():
            book_inst.due_back = form.cleaned_data['renewal_date']
            book_inst.save()
            return HttpResponseRedirect(reverse('catalog:my-borrowed'))
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date':proposed_renewal_date,})
    return render(request,'catalog/book_renew_librarian.html',{'form':form,'bookinst':book_inst})

class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death':datetime.date.today(),}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name','last_name','date_of_birth','date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


    



