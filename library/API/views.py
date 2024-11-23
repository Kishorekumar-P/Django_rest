from rest_framework import status
from rest_framework.response import Response
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from .models import CustomUser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from datetime import date, timedelta
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from .models import CustomUser, Book, Rental, Request
from .serializers import UserSerializer, BookSerializer, RentalSerializer, RequestSerializer
from rest_framework.permissions import IsAuthenticated


@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)


        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
            except ObjectDoesNotExist:
                pass

        if not user:
            user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ApproveRegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if request.user.role != 'librarian':
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(CustomUser, pk=user_id, is_active=False)
        user.is_active = True
        user.save()
        return Response({"detail": "User approved"})

class BookListView(APIView):
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
    
class AddBooksView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'librarian':
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApproveBookRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        if request.user.role != 'librarian':
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        book_request = get_object_or_404(Request, pk=request_id, status='pending')
        if request.data['status'] == 'approved':
            book_request.status = 'approved'
            book_request.book.available_count -= 1
            book_request.book.save()
            Rental.objects.create(member=book_request.member, book=book_request.book)
        else:
            book_request.status = 'denied'
        book_request.save()
        return Response({"status": book_request.status})

class BookDetailView(APIView):
    def get(self, request, book_id):
        book = get_object_or_404(Book, pk=book_id)
        serializer = BookSerializer(book)
        return Response(serializer.data)

class RequestBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != 'member':
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
        if Rental.objects.filter(member=request.user, return_date__isnull=True).exists():
            return Response({"detail": "You already have a book borrowed"}, status=status.HTTP_400_BAD_REQUEST)
        book = get_object_or_404(Book, pk=request.data['book_id'])
        if book.available_count <= 0:
            return Response({"detail": "Book not available"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = RequestSerializer(data={'member': request.user.id, 'book': book.id})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReturnBookView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, rental_id):
        rental = get_object_or_404(Rental, pk=rental_id, member=request.user)
        rental.return_date = date.today()
        days_rented = (rental.return_date - rental.rental_date).days
        if days_rented > 7:
            rental.fine = 5 + (days_rented - 7) * 10
        else:
            rental.fine = 0
        rental.save()
        rental.book.available_count += 1
        rental.book.save()
        return Response({"fine": rental.fine})
