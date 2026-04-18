from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, ScraperView, RagQueryView, HealthCheckView, RequestOTPView, VerifyOTPView, RegisterWithPasswordView

router = DefaultRouter()
router.register(r'books', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('scrape/', ScraperView.as_view(), name='scrape'),
    path('query/', RagQueryView.as_view(), name='query'),
    path('health/', HealthCheckView.as_view(), name='health'),
    path('otp/request/', RequestOTPView.as_view(), name='otp_request'),
    path('otp/verify/', VerifyOTPView.as_view(), name='otp_verify'),
    path('otp/register-password/', RegisterWithPasswordView.as_view(), name='otp_register_password'),
]
