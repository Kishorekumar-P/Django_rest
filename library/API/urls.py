from django.urls import path
from .views import register_user, user_login, user_logout,ApproveRegisterView, BookListView, AddBooksView, BookDetailView, RequestBookView, ApproveBookRequestView, ReturnBookView

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('approve-register/<int:user_id>/', ApproveRegisterView.as_view(), name='approve-register'),
    path('add-books/', AddBooksView.as_view(), name='add-books'),
    path('booklist/', BookListView.as_view(), name='booklist'),
    path('book/<int:book_id>/', BookDetailView.as_view(), name='book-detail'),
    path('request-book/', RequestBookView.as_view(), name='request-book'),
    path('approve-book-request/<int:request_id>/', ApproveBookRequestView.as_view(), name='approve-book-request'),
    path('return-book/<int:rental_id>/', ReturnBookView.as_view(), name='return-book'),
]
