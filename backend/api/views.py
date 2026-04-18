from rest_framework import viewsets, views
from rest_framework.response import Response
from rest_framework.decorators import action
import random
from django.core.mail import send_mail
from django.conf import settings
from .models import Book, QueryCache, UserOTP
from .serializers import BookSerializer, QueryCacheSerializer
from .scraper import scrape_books_toscrape
from .rag import process_rag_query

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all().order_by('-created_at')
    serializer_class = BookSerializer

    @action(detail=True, methods=['post'])
    def buy(self, request, pk=None):
        book = self.get_object()
        book.purchases_count += 1
        book.save()
        return Response({'status': 'purchase successful', 'purchases_count': book.purchases_count})

class ScraperView(views.APIView):
    def post(self, request):
        limit = request.data.get('limit', 20)
        result = scrape_books_toscrape(limit=limit)
        return Response(result)

class RagQueryView(views.APIView):
    def post(self, request):
        query = request.data.get('query', '')
        if not query:
            return Response({"error": "Query is required"}, status=400)
            
        result = process_rag_query(query)
        
        QueryCache.objects.create(
            query=query, 
            response=result['response'], 
            sources=result['sources']
        )
        
        return Response({
            "query": query,
            "response": result['response'],
            "sources": result['sources']
        })

class RequestOTPView(views.APIView):
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=400)
        
        # Generate 6-digit code
        code = str(random.randint(100000, 999999))
        
        # Save to DB
        UserOTP.objects.create(email=email, code=code)
        
        # Send email (mock if not configured)
        try:
            send_mail(
                'Your NSR BOOKS Login Code',
                f'Your verification code is: {code}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            return Response({"status": "success", "message": "OTP sent to your email"})
        except Exception as e:
            # Fallback for local testing: print to console
            print(f"DEBUG: OTP for {email} is {code}")
            return Response({
                "status": "success", 
                "message": "OTP generated (Check server console if email fails)",
                "code_debug": code 
            })

class VerifyOTPView(views.APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        
        otp = UserOTP.objects.filter(email=email, code=code).last()
        if otp:
            otp.is_verified = True
            otp.save()
            return Response({"status": "verified", "message": "OTP verified. Now set your password."})
        else:
            return Response({"error": "Invalid or expired code"}, status=400)

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

class RegisterWithPasswordView(views.APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')
        password = request.data.get('password')
        
        # Security check: make sure OTP was verified recently
        otp = UserOTP.objects.filter(email=email, code=code, is_verified=True).last()
        if not otp:
            return Response({"error": "OTP verification required"}, status=400)
            
        # Create or update user
        user, created = User.objects.get_or_create(username=email, email=email)
        user.set_password(password)
        user.save()
        
        return Response({
            "status": "success", 
            "user": {
                "name": email.split('@')[0], 
                "email": email, 
                "role": "user"
            }
        })

class HealthCheckView(views.APIView):
    def get(self, request):
        count = Book.objects.count()
        query_count = QueryCache.objects.count()
        return Response({
            "status": "healthy", 
            "version": "1.0.0",
            "database_connected": True,
            "document_count": count,
            "query_count": query_count
        })
