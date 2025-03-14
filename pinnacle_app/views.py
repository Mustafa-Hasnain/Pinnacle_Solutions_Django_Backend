import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from .models import User, VerificationToken
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.decorators import action
from rest_framework import generics, status
from rest_framework.response import Response
from .models import BasicContactInformation, BusinessDetails, FundingRequirements, FinancialInformation,DocumentUpload, ApplicationStatus, ApplicationActivityLog, AdminMessage, Application, DocumentLabel, Referral, ReferralInvitation, Commission, AdminNotification, AdminEmailLog
from .serializers import (BasicContactInformationSerializer,
                            BusinessDetailsSerializer,
                            FundingRequirementsSerializer,
                            FinancialInformationSerializer,DocumentUploadSerializer, ApplicationStatusSerializer, AdminMessageSerializer,ApplicationSerializer, DocumentLabelSerializer, ApplicationActivityLogSerializer)
from rest_framework import viewsets
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.db import models
from django.db import transaction
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.db.models import Prefetch
from django.utils.timezone import localtime
from django.db.models import Q
from django.utils.timezone import now
from decimal import Decimal
from django.db.models import Sum  # Add this import
from django.contrib.auth.hashers import check_password, make_password
from datetime import datetime
import threading













# class SignUpView(APIView):
#     def post(self, request):
#         serializer = UserSerializer(data=request.data)
#         if serializer.is_valid():
#             user = serializer.save()
#             user.is_active = False  # Set user as inactive initially
#             user.save()

#             # Generate a verification token
#             token = get_random_string(64)
#             VerificationToken.objects.create(user=user, token=token)

#             # Send verification email manually via SMTP
#             try:
#                 sender_email = settings.EMAIL_HOST_USER
#                 sender_password = settings.EMAIL_HOST_PASSWORD
#                 recipient_email = user.email
#                 subject = "Verify your email"
#                 verification_link = f"http://localhost:3000/verify-email/{token}/"
#                 body = f"Click the link to verify your email: {verification_link}"

#                 # Create the email
#                 msg = MIMEMultipart()
#                 msg['From'] = sender_email
#                 msg['To'] = recipient_email
#                 msg['Subject'] = subject
#                 msg.attach(MIMEText(body, 'plain'))

#                 # Set up the SMTP server
#                 server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)  # SMTP server for Gmail
#                 server.starttls()  # Start TLS encryption
#                 server.login(sender_email, sender_password)  # Login to the email account
#                 server.send_message(msg)  # Send the email
#                 server.quit()  # Terminate the SMTP session

#                 return Response({"message": "Verification email sent."}, status=status.HTTP_201_CREATED)

#             except Exception as e:
#                 return Response({"message": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def admin_login(request):
    """
    Authenticate an admin user based on email and password, 
    update last login timestamp, and optionally update last location.
    """
    email = request.data.get('email')
    password = request.data.get('password')
    location_ip = request.data.get('location_ip', None)
    location = request.data.get('location', None)  # Optional location input

    if not email or not password:
        return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Authenticate the user
    user = authenticate(email=email, password=password)

    if user is None:
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_admin and not user.is_superAdmin:
        return Response({"error": "You are not authorized to access this resource."}, status=status.HTTP_403_FORBIDDEN)

    # Update last login timestamp
    user.last_login = datetime.now()

    # Update last location if provided and valid
    if location and location != "N/A":
        user.last_location = location
    
    if location_ip and location_ip != "N/A":
        user.last_location_ip = location_ip

    user.save()

    formatted_last_login = user.last_login.strftime("%d/%b/%Y - %I:%M %p")


    # Prepare user data response
    user_data = {
        "user_id": user.id,
        "email": user.email,
        "admin_name": user.admin_name,
        "is_superAdmin": user.is_superAdmin,
        "is_admin": user.is_admin,
        "last_login": formatted_last_login,  # Include updated last login
        "last_location": user.last_location,  # Include updated last location
        "last_location_ip": user.last_location_ip,  # Include updated last location
    }

    return Response(user_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def create_admin_user(request):
    """
    Create a new admin user with a default password and send email notification.
    """
    email = request.data.get('email')
    admin_name = request.data.get('name')

    if not email or not admin_name:
        return Response({"error": "Email and name are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the email already exists
    if User.objects.filter(email=email).exists():
        return Response({"error": "A user with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

    # Create the admin user
    password = "Abcd@1234"
    user = User.objects.create_user(
        email=email,
        password=password,
        is_admin=True,
        admin_name=admin_name
    )

    # Send email notification
    try:
        sender_email = "superadmin@pinnacleportal.co.uk"
        sender_password = "s6sz7yIL0,t)"  # Email sender's password
        recipient_email = email
        subject = "Welcome to Pinnacle Portal - Admin Access"
        body = f"""
        <html>
        <body>
            <h2>Hello {admin_name}!</h2>
            <p>You have been registered as an admin on Pinnacle Portal.</p>
            <p>Please visit the following link to log in:</p>
            <a href="https://pinnacleportal.co.uk/admin">https://pinnacleportal.co.uk/admin</a>
            <br><br>
            <h3>Your Credentials:</h3>
            <ul>
                <li><strong>Email:</strong> {email}</li>
                <li><strong>Temp Password:</strong> {password}</li>
            </ul>
            <p>For security purposes, we recommend changing your password after logging in for the first time.</p>
            <br>
            <p>Thank you,</p>
            <p><strong>Pinnacle Portal Team</strong></p>
        </body>
        </html>
        """

        # Compose the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        # Send the email
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        return Response({"message": "Admin user created successfully and email sent.", "user_id": user.id},
                        status=status.HTTP_201_CREATED)

    except Exception as e:
        # If email sending fails, return a response
        return Response({"error": "Admin created, but failed to send email.", "details": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_all_admin_users(request):
    """
    Get all users where is_admin is True.
    """
    admin_users = User.objects.filter(is_admin=True)
    serializer = UserSerializer(admin_users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['DELETE'])
def delete_user(request, user_id):
    """
    Delete a user based on user_id.
    """
    user = get_object_or_404(User, id=user_id)  # Fetch the user or return 404
    user.delete()  # Delete the user
    return Response({"message": f"User with ID {user_id} has been deleted successfully."}, status=status.HTTP_200_OK)


@api_view(['GET'])
def fetch_profile(request, user_id):
    """
    Fetch the admin profile data based on user_id.
    """
    user = get_object_or_404(User, id=user_id)  # Ensure user is an admin
    serializer = UserSerializer(user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def fetch_admin_profile(request, user_id):
    """
    Fetch the admin profile data based on user_id.
    """
    user = get_object_or_404(User, id=user_id)  # Ensure user is an admin
    serializer = UserSerializer(user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['PUT'])
def update_admin_profile(request, user_id):
    """
    Update the admin name and/or password based on the payload.
    """
    user = get_object_or_404(User, id=user_id)  # Ensure user is an admin

    admin_name = request.data.get('admin_name', None)
    password = request.data.get('password', None)
    old_password = request.data.get('old_password', None)

    # Update admin_name if provided
    if admin_name:
        user.admin_name = admin_name

    # Update password if provided
    if old_password and password:
        if not check_password(old_password, user.password):  # Check if old password matches
            return Response(
                {"error": "Old password is incorrect."},
                status=status.HTTP_403_FORBIDDEN
            )
        user.set_password(password)  # Set new password if old password matches

    user.save()  # Save the changes
    return Response({"message": "Admin profile updated successfully."}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_basic_contact_information(request, user_id):
    """
    Fetch the first application of a user and return the user, application, and basic contact information.
    """
    user = get_object_or_404(User, id=user_id)
    application = Application.objects.filter(user=user).first()
    if not application:
        return Response({"error": "No applications found for this user."}, status=status.HTTP_404_NOT_FOUND)

    basic_contact_info = getattr(application, 'basiccontactinformation', None)
    if not basic_contact_info:
        return Response({"error": "No basic contact information found for this application."}, status=status.HTTP_404_NOT_FOUND)

    # Serialize user and application data
    user_serializer = UserSerializer(user, context={'request': request})
    application_data = {
        "id": application.id,
        "date_created": application.date_created,
        "last_updated": application.last_updated,
        "steps_completed": application.steps_completed,
        "funding_amount": str(application.funding_amount),  # Ensure Decimal is serialized to string
    }
    basic_contact_info_serializer = BasicContactInformationSerializer(basic_contact_info)

    # Combine data into a single response
    response_data = {
        "user": user_serializer.data,
        "application": application_data,
        "basic_contact_info": basic_contact_info_serializer.data,
    }

    return Response(response_data, status=status.HTTP_200_OK)


@api_view(['PUT'])
def update_basic_contact_and_password(request, user_id):
    """
    Update the name, phone number, and password of a user and their first application.
    """
    user = get_object_or_404(User, id=user_id)
    application = Application.objects.filter(user=user).first()
    if not application:
        return Response({"error": "No applications found for this user."}, status=status.HTTP_404_NOT_FOUND)

    basic_contact_info = getattr(application, 'basiccontactinformation', None)
    if not basic_contact_info:
        return Response({"error": "No basic contact information found for this application."}, status=status.HTTP_404_NOT_FOUND)

    # Update fields
    name = request.data.get("name")
    phone_number = request.data.get("phone_number")
    password = request.data.get("password")
    old_password = request.data.get("old_password")

    if name:
        basic_contact_info.full_name = name
    if phone_number:
        basic_contact_info.phone_number = phone_number

    if old_password and password:
        if not check_password(old_password, user.password):  # Check if old password matches
            return Response(
                {"error": "Old password is incorrect."},
                status=status.HTTP_403_FORBIDDEN
            )
        user.set_password(password)  # Set new password if old password matches

    # Save updates
    basic_contact_info.save()
    user.save()

    return Response({"message": "Information updated successfully."}, status=status.HTTP_200_OK)

@api_view(['POST'])
def upload_profile_picture(request, user_id):
    """
    Upload or update the user's profile picture.
    """
    user = get_object_or_404(User, id=user_id)
    if 'profile_picture' not in request.FILES:
        return Response({"error": "No file uploaded."}, status=status.HTTP_400_BAD_REQUEST)

    profile_picture = request.FILES['profile_picture']

    # Save the new profile picture
    user.profile_picture = profile_picture
    user.save()

    profile_picture_url = request.build_absolute_uri(user.profile_picture.url)

    # Return updated profile picture URL
    return Response({
        "message": "Profile picture updated successfully.",
        "image_url": profile_picture_url
    }, status=status.HTTP_200_OK)


class SignUpView(APIView):
    def post(self, request):
        referral_code = request.data.get('referral_code', None)
        print("Referral Code: ",referral_code)
        referrer = None  # Initialize to avoid unbound error

        # If referral code is provided, validate it and get the referrer
        if referral_code:
            try:
                referrer_referral = Referral.objects.get(referral_code=referral_code)
                referrer = referrer_referral.referrer  # Get the referrer user
            except Referral.DoesNotExist:
                return Response({"error": "Invalid referral code."}, status=status.HTTP_400_BAD_REQUEST)
        
        user_email = request.data.get('email', '').strip()    
        try:
            existing_user = User.objects.get(email=user_email)
            if not existing_user.is_active:
                # Generate a new verification token
                token = get_random_string(64)
                last_verification_token = VerificationToken.objects.filter(user=existing_user).last()
                if last_verification_token:
                    last_verification_token.delete()

                VerificationToken.objects.create(user=existing_user, token=token)

                # Send verification email
                try:
                    sender_email = "no-reply@pinnacleportal.co.uk"
                    sender_password = "n-KyF~dNHTf]"
                    subject = "Verify Your Email - Pinnacle Solutions"
                    verification_link = f"https://pinnacleportal.co.uk/verify-email/{token}/"
                    
                    body = f"""
                    <html>
                    <body>
                        <p>Hello,</p>
                        <p>It seems you started registering with this email address but did not complete the verification process. Click the link below to verify your email:</p>
                        <a href="{verification_link}" target="_blank">Verify your email</a>
                        <p>If you did not attempt to register, please ignore this email.</p>
                    </body>
                    </html>
                    """

                    msg = MIMEMultipart()
                    msg['From'] = sender_email
                    msg['To'] = user_email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'html'))

                    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                    server.quit()

                    return Response(
                        {"message": "Verification email resent. Please check your inbox."},
                        status=status.HTTP_200_OK
                    )

                except Exception as e:
                    return Response({"message": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"error": "The email is already registered."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            pass  # Proceed with regular sign-up if the email is not registered
        
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False  # Set user as inactive until verification
            user.save()

            # Create a new referral record for the referee with the referrer info
            if referrer:
                Referral.objects.create(
                    referrer=referrer,
                    referee=user,  # Set the current user as the referee
                    referral_code=referral_code  # Save referral code for tracking
                )

            # Handle referral invitation
            referee_email = user.email
            try:
                invitation = ReferralInvitation.objects.get(referee_email=referee_email)
                invitation.update_status('Invitation_Accepted')
            except ReferralInvitation.DoesNotExist:
                if referrer:
                    ReferralInvitation.objects.create(
                        referrer=referrer,
                        referee_email=referee_email,
                        status='Invitation_Accepted'
                    )

            # Generate a verification token
            token = get_random_string(64)
            VerificationToken.objects.create(user=user, token=token)

            # Send verification email manually via SMTP
            try:
                sender_email = "no-reply@pinnacleportal.co.uk"
                sender_password = "n-KyF~dNHTf]"
                recipient_email = user.email
                subject = "Verify Your Email - Pinnacle Solutions"

                verification_link = f"https://pinnacleportal.co.uk/verify-email/{token}/"
                # verification_link = f"http://localhost:3000/verify-email/{token}/"
                
                # Creating the HTML body with a heading, welcome message, and verification link
                body = f"""
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background-color: #f4f4f4;
                            color: #333;
                            padding: 20px;
                        }}
                        .container {{
                            background-color: #fff;
                            padding: 20px;
                            border-radius: 10px;
                            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                            max-width: 600px;
                            margin: 0 auto;
                        }}
                        h1 {{
                            color: #2e6fba;
                            text-align: center;
                        }}
                        p {{
                            font-size: 16px;
                            line-height: 1.6;
                        }}
                        a {{
                            color: #1a73e8;
                            text-decoration: none;
                            font-weight: bold;
                        }}
                        a:hover {{
                            text-decoration: underline;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <h1>Pinnacle Solutions</h1>
                        <p>Welcome to Pinnacle Solutions! We're excited to have you on board. To complete your registration, we need to verify your email address.</p>
                        <p>Please click the link below to verify your email:</p>
                        <p>
                            <a href="{verification_link}" target="_blank">Verify your email</a>
                        </p>
                        <p>If you did not create this account, please ignore this email.</p>
                        <p>Thank you for choosing Pinnacle Solutions!</p>
                    </div>
                </body>
                </html>
                """

                # Send the email
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'html'))

                server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                server.quit()

                return Response({"message": "Verification email sent."}, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({"message": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class VerifyEmailView(APIView):
    def get(self, request, token):
        # verification_token = get_object_or_404(VerificationToken, token=token)
        verification_token = VerificationToken.objects.filter(token=token).last()

        # Activate the user
        user = verification_token.user
        user.is_active = True
        user.save()

        # Delete the token after verification
        # verification_token.delete()
        return Response({"message": "Email successfully verified."}, status=status.HTTP_200_OK)

# API to request a password reset
@api_view(['POST'])
def request_password_reset(request):
    try:
        email = request.data.get('email')
        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email, is_admin=False).first()
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Generate a password reset token
        token = get_random_string(64)
        VerificationToken.objects.update_or_create(user=user, defaults={"token": token})

        # Send password reset email
        sender_email = "no-reply@pinnacleportal.co.uk"
        sender_password = "n-KyF~dNHTf]"
        recipient_email = user.email
        subject = "Reset Your Password - Pinnacle Solutions"
        reset_link = f"https://pinnacleportal.co.uk/reset-password/{token}/"

        body = f"""
        <html>
        <body>
            <h1>Password Reset</h1>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_link}">Reset Password</a>
            <p>If you did not request a password reset, please ignore this email.</p>
        </body>
        </html>
        """

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        return Response({"message": "Password reset email sent successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# API to request a password reset
@api_view(['POST'])
def admin_request_password_reset(request):
    try:
        email = request.data.get('email')
        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(email=email, is_admin=True).first()
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Generate a password reset token
        token = get_random_string(64)
        VerificationToken.objects.update_or_create(user=user, defaults={"token": token})

        # Send password reset email
        sender_email = "no-reply@pinnacleportal.co.uk"
        sender_password = "n-KyF~dNHTf]"
        recipient_email = user.email
        subject = "Reset Your Password - Pinnacle Solutions"
        reset_link = f"https://pinnacleportal.co.uk/admin/reset-password/{token}"

        body = f"""
        <html>
        <body>
            <h1>Password Reset</h1>
            <p>Click the link below to reset your password:</p>
            <a href="{reset_link}">Reset Password</a>
            <p>If you did not request a password reset, please ignore this email.</p>
        </body>
        </html>
        """

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        return Response({"message": "Password reset email sent successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@api_view(['POST'])
def reset_password(request):
    try:
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        if not token or not new_password:
            return Response({"message": "Token and new password are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the token exists
        token_entry = VerificationToken.objects.filter(token=token).last()
        if not token_entry:
            return Response({"message": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)

        user = token_entry.user

        # Check if the user has verified their email
        # if not user.is_active:
        #     return Response({"message": "Please verify your email before resetting your password."}, status=status.HTTP_400_BAD_REQUEST)

        # Update the user's password
        user.password = make_password(new_password)
        user.save()

        # Delete the token after successful reset
        token_entry.delete()

        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": f"Error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
@api_view(['POST'])
def resend_verification_email(request):
    try:
        email = request.data.get('email')
        if not email:
            return Response({"message": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get user with the email
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            return Response({"message": "Email is already verified"}, status=status.HTTP_400_BAD_REQUEST)

        # Generate a new verification token
        token = get_random_string(64)
        
        last_verification_token = VerificationToken.objects.filter(user=user).last()
        if last_verification_token:
            last_verification_token.delete()

        VerificationToken.objects.create(user=user, token=token)

        # Send verification email manually via SMTP
        sender_email = "no-reply@pinnacleportal.co.uk"
        sender_password = "n-KyF~dNHTf]"
        recipient_email = user.email
        subject = "Resend: Verify Your Email - Pinnacle Solutions"

        # verification_link = f"http://localhost:3000/verify-email/{token}/"
        verification_link = f"https://pinnacleportal.co.uk/verify-email/{token}/"
        
        # Creating the HTML body with a heading, resend message, and verification link
        body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    color: #333;
                    padding: 20px;
                }}
                .container {{
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    max-width: 600px;
                    margin: 0 auto;
                }}
                h1 {{
                    color: #2e6fba;
                    text-align: center;
                }}
                p {{
                    font-size: 16px;
                    line-height: 1.6;
                }}
                a {{
                    color: #1a73e8;
                    text-decoration: none;
                    font-weight: bold;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Pinnacle Solutions</h1>
                <p>We noticed you haven't verified your email yet. No worries! We're resending the verification link below.</p>
                <p>Please click the link below to verify your email:</p>
                <p>
                    <a href="{verification_link}" target="_blank">Verify your email</a>
                </p>
                <p>If you did not request this, you can safely ignore this email.</p>
                <p>Thank you for choosing Pinnacle Solutions! We're looking forward to having you onboard.</p>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        return Response({"message": "Verification email sent successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"message": f"Failed to send email: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({"message": "Email and password are required"}, status=status.HTTP_400_BAD_REQUEST)

    # Authenticate the user
    user = authenticate(request, email=email, password=password)

    if user is None:
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

    # Check if the user is active (i.e., email verified)
    if not user.is_active:
         # Retrieve the existing verification token for the user
        token = VerificationToken.objects.get(user=user).token
        
        # Send verification email manually via SMTP
        sender_email = "no-reply@pinnacleportal.co.uk"
        sender_password = "n-KyF~dNHTf]"
        recipient_email = user.email
        subject = "Verify Your Email - Pinnacle Solutions"

        # verification_link = f"http://localhost:3000/verify-email/{token}/"
        verification_link = f"https://pinnacleportal.co.uk/verify-email/{token}/"
        
        # Creating the HTML body with a heading, welcome message, and verification link
        body = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    color: #333;
                    padding: 20px;
                }}
                .container {{
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    max-width: 600px;
                    margin: 0 auto;
                }}
                h1 {{
                    color: #2e6fba;
                    text-align: center;
                }}
                p {{
                    font-size: 16px;
                    line-height: 1.6;
                }}
                a {{
                    color: #1a73e8;
                    text-decoration: none;
                    font-weight: bold;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Pinnacle Solutions</h1>
                <p>Welcome to Pinnacle Solutions! We're excited to have you on board. To complete your registration, we need to verify your email address.</p>
                <p>Please click the link below to verify your email:</p>
                <p>
                    <a href="{verification_link}" target="_blank">Verify your email</a>
                </p>
                <p>If you did not create this account, please ignore this email.</p>
                <p>Thank you for choosing Pinnacle Solutions!</p>
            </div>
        </body>
        </html>
        """

        # Send the email
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()

        return Response({"message": "Email not verified. Please verify your email first."}, status=status.HTTP_403_FORBIDDEN)

    # Check if steps_completed is False and return the application_id
    application_id = None
    if not user.steps_completed:
        first_application = Application.objects.filter(user=user).first()
        if first_application:
            application_id = first_application.id

    # Login successful, return user details
    return Response({
        "message": "Login successful",
        "user_id": user.id,
        "email": user.email,
        "steps_completed": user.steps_completed,
        "application_id": application_id,  # This will be None if no application is found
        "is_admin": user.is_admin,
        "is_superAdmin": user.is_superAdmin
    }, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PUT'])
def basic_contact_information_view(request, application_id):
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        contact_info = BasicContactInformation.objects.filter(application=application).first()
        if not contact_info:
            return Response({"error": "Basic contact information not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BasicContactInformationSerializer(contact_info)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()
        data['application'] = application.id
        serializer = BasicContactInformationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        contact_info = BasicContactInformation.objects.filter(application=application).first()
        if not contact_info:
            return Response({"error": "Basic contact information not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BasicContactInformationSerializer(contact_info, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET', 'POST', 'PUT'])
def business_details_view(request, application_id):
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        business_details = BusinessDetails.objects.filter(application=application).first()
        if not business_details:
            return Response({"error": "Business details not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BusinessDetailsSerializer(business_details)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()
        data['application'] = application.id
        serializer = BusinessDetailsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        business_details = BusinessDetails.objects.filter(application=application).first()
        if not business_details:
            return Response({"error": "Business details not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BusinessDetailsSerializer(business_details, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST', 'PUT'])
def financial_information_view(request, application_id):
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        financial_info = FinancialInformation.objects.filter(application=application).first()
        if not financial_info:
            return Response({"error": "Financial information not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = FinancialInformationSerializer(financial_info)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()
        data['application'] = application.id
        serializer = FinancialInformationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        financial_info = FinancialInformation.objects.filter(application=application).first()
        if not financial_info:
            return Response({"error": "Financial information not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = FinancialInformationSerializer(financial_info, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST', 'PUT'])
def funding_requirements_view(request, application_id):
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        funding_requirements = FundingRequirements.objects.filter(application=application).first()
        if not funding_requirements:
            return Response({"error": "Funding requirements not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = FundingRequirementsSerializer(funding_requirements)
        return Response(serializer.data)

    elif request.method == 'POST':
        data = request.data.copy()
        data['application'] = application.id
        serializer = FundingRequirementsSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'PUT':
        funding_requirements = FundingRequirements.objects.filter(application=application).first()
        if not funding_requirements:
            return Response({"error": "Funding requirements not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = FundingRequirementsSerializer(funding_requirements, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def application_view(request, application_id):
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Initialize response data
    response_data = {}

     # Add user information
    user = application.user
    response_data['user_id'] = user.id
    response_data['user_email'] = user.email

    # Serialize and add BasicContactInformation data
    try:
        basic_info = BasicContactInformation.objects.get(application=application)
        response_data['basic_contact_information'] = BasicContactInformationSerializer(basic_info).data
    except BasicContactInformation.DoesNotExist:
        response_data['basic_contact_information'] = {}

    # Serialize and add BusinessDetails data
    try:
        business_details = BusinessDetails.objects.get(application=application)
        response_data['business_details'] = BusinessDetailsSerializer(business_details).data
    except BusinessDetails.DoesNotExist:
        response_data['business_details'] = {}

    # Serialize and add FundingRequirements data
    try:
        funding_requirements = FundingRequirements.objects.get(application=application)
        response_data['funding_requirements'] = FundingRequirementsSerializer(funding_requirements).data
    except FundingRequirements.DoesNotExist:
        response_data['funding_requirements'] = {}

    # Serialize and add FinancialInformation data
    try:
        financial_info = FinancialInformation.objects.get(application=application)
        response_data['financial_information'] = FinancialInformationSerializer(financial_info).data
    except FinancialInformation.DoesNotExist:
        response_data['financial_information'] = {}

    # Serialize and add DocumentUpload data with label
    documents = DocumentUpload.objects.filter(application=application)
    document_data = []
    for document in documents:
        document_info = {
            'id': document.id,
            'file': request.build_absolute_uri(document.file.url),
            'label_id': document.label.id,
            'label': document.label.label,  # Get the label name
            'status': document.status,
            'remarks': document.remarks,
            'date_created': document.date_created,
            'last_updated': document.last_updated,
        }
        document_data.append(document_info)
    response_data['document_uploads'] = document_data

    # Serialize and add ApplicationStatus data
    try:
        application_status = ApplicationStatus.objects.get(application=application)
        response_data['application_status'] = ApplicationStatusSerializer(application_status).data
    except ApplicationStatus.DoesNotExist:
        response_data['application_status'] = {}

    return Response(response_data)

    

@api_view(['GET', 'POST', 'PUT','DELETE'])
def document_upload_view(request, application_id):
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found."}, status=404)

    if request.method == 'GET':
        # Fetch all document uploads for the application
        documents = DocumentUpload.objects.filter(application=application)
        serializer = DocumentUploadSerializer(documents, many=True, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'POST':
        # Handle multiple document uploads in one request
        files = request.FILES.getlist('files')  # Get all files from request
        label_id = request.data.get('label_id')

        if not label_id or not files:
            return Response({"error": "Both label_id and files are required."}, status=400)

        try:
            label = DocumentLabel.objects.get(id=label_id)
        except DocumentLabel.DoesNotExist:
            return Response({"error": "Invalid label_id."}, status=400)

        uploaded_docs = []
        for file in files:
            data = {
                'application': application.id,
                'label': label.id,
                'file': file
            }
            serializer = DocumentUploadSerializer(data=data, context={'request': request})
            if serializer.is_valid():
                uploaded_docs.append(serializer.save())
            else:
                return Response(serializer.errors, status=400)

        # Serialize uploaded documents for response
        response_serializer = DocumentUploadSerializer(uploaded_docs, many=True, context={'request': request})
        return Response(response_serializer.data, status=201)

    elif request.method == 'PUT':
        # Update existing document (same as before)
        label_id = request.data.get('label_id')
        try:
            label = DocumentLabel.objects.get(id=label_id)
        except DocumentLabel.DoesNotExist:
            return Response({"error": "Invalid label_id."}, status=400)

        try:
            document = DocumentUpload.objects.get(application=application, label=label)
            serializer = DocumentUploadSerializer(document, data=request.data, partial=True, context={'request': request})

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=400)

        except DocumentUpload.DoesNotExist:
            return Response({"error": "Document not found."}, status=404)

    elif request.method == 'DELETE':
        # Delete existing document (same as before)
        document_id = request.data.get('document_id')

        try:
            document = DocumentUpload.objects.get(id=document_id, application=application)
            document.delete()
            return Response({"message": "Document deleted successfully."}, status=204)
        except DocumentUpload.DoesNotExist:
            return Response({"error": "Document not found."}, status=404)    



@api_view(['POST'])
def additional_document_upload_view(request, application_id):
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found."}, status=404)

    label_name = request.data.get('label')
    file = request.data.get('file')

    if not label_name or not file:
        return Response({"error": "Both label and file are required."}, status=400)

    # Check if the label exists, otherwise create it
    label, created = DocumentLabel.objects.get_or_create(label=label_name, defaults={'required': False})

    # Create the document upload
    data = {
        'application': application.id,
        'label': label.id,
        'file': file
    }
    serializer = DocumentUploadSerializer(data=data, context={'request': request})
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(['PUT'])
def update_application_status(request, application_id):
    try:
        application_status = ApplicationStatus.objects.get(application_id=application_id)
    except ApplicationStatus.DoesNotExist:
        return Response({"error": "Application status not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ApplicationStatusSerializer(application_status, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
def update_document_upload(request, document_id):
    try:
        document_upload = DocumentUpload.objects.get(id=document_id)
    except DocumentUpload.DoesNotExist:
        return Response({"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND)
    document_upload.status = "under_review"
    serializer = DocumentUploadSerializer(document_upload, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def send_admin_message(request):
    # Extract application_id from request data
    application_id = request.data.get('application_id', None)
    document_id = request.data.get('document_id', None)
    ask_additional_documents = request.data.get('ask_additional_documents', False)
    message = request.data.get('message', None)

    # Fetch user email from application_id
    if application_id:
        try:
            application = Application.objects.get(id=application_id)
            user = application.user
            recipient_email = user.email
            
            # Create the AdminMessage instance
            Admin_message = AdminMessage(
                application=application,
                user=user,
                message=message,
                ask_additional_document=ask_additional_documents
            )
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=status.HTTP_404_NOT_FOUND)
    else:
        return Response({'error': 'Application ID is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Prepare email content
    subject = "Important Message from Admin"

    # Sender and recipient email information
    sender_email = "admin@pinnacleportal.co.uk"
    sender_password = "?8Th(3xHJ7#f"
    recipient_email = user.email

    # Message from Admin
    admin_message = """
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                color: #333;
                padding: 20px;
            }}
            .container {{
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                margin: 0 auto;
            }}
            h1 {{
                color: #2e6fba;
                text-align: center;
            }}
            p {{
                font-size: 16px;
                line-height: 1.6;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Important Message from Pinnacle Solutions Admin</h1>
            <p>Dear User,</p>
            <p>We hope you're doing well! This is an important message from the Pinnacle Solutions admin. Please read the following information carefully:</p>
            <p>{message_content}</p>
            <br><br>
            <p>Thank you for being a valued member of Pinnacle Solutions.</p>
            <p>Best regards,</p>
            <p>Pinnacle Solutions Admin Team</p>
        </div>
    </body>
    </html>
    """.format(message_content=message)  # Insert the message content here

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Attach the HTML body to the email
    msg.attach(MIMEText(admin_message, 'html'))


    try:
        with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        return Response({'error': f'Failed to send email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Save the message data
    Admin_message.save()  # Save the admin message after populating the fields

    # If document_id is provided, update the DocumentUpload model
    if document_id:
        try:
            document = DocumentUpload.objects.get(id=document_id)
            document.reminder_sent = True
            document.status = 'reminder_pending'
            document.save()
            
            # Update ApplicationStatus to in_progress
            application_status = ApplicationStatus.objects.get(application=document.application)
            application_status.status = 'in_progress'
            application_status.save()
        except DocumentUpload.DoesNotExist:
            return Response({'error': 'Document not found'}, status=status.HTTP_404_NOT_FOUND)
        except ApplicationStatus.DoesNotExist:
            return Response({'error': 'Application status not found'}, status=status.HTTP_404_NOT_FOUND)

    # If ask_additional_documents is true, update the ApplicationStatus to in_progress
    if ask_additional_documents:
        try:
            application_status = ApplicationStatus.objects.get(application=application)
            application_status.status = 'in_progress'
            application_status.save()
        except ApplicationStatus.DoesNotExist:
            return Response({'error': 'Application status not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'message': 'Message sent successfully.'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_labels_of_financeType(request, application_id):
    # application_id = request.query_params.get('application_id')

    if not application_id:
        return Response({"error": "application_id is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        funding_requirements = FundingRequirements.objects.get(application__id=application_id)

        # Check if all required fields are filled
        if not all([funding_requirements.finance_type, funding_requirements.amount_required, 
                    funding_requirements.purpose, funding_requirements.repayment_period,
                    funding_requirements.preferred_funding_timeline]):
            return Response({"error": "Funding requirements are not completely filled."}, 
                            status=status.HTTP_403_FORBIDDEN)

        # Retrieve document labels based on the finance type
        document_labels = DocumentLabel.objects.filter(finance_type=funding_requirements.finance_type)
        serializer = DocumentLabelSerializer(document_labels, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except FundingRequirements.DoesNotExist:
        return Response({"error": "Funding requirements not found for the provided application ID."}, 
                        status=status.HTTP_404_NOT_FOUND)
    
@api_view(['GET'])
def get_financeType_labels(request, finance_type):
    if not finance_type:
        return Response({"error": "finance_type is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Retrieve document labels based on the finance type
        document_labels = DocumentLabel.objects.filter(finance_type=finance_type)

        if not document_labels.exists():
            return Response({"error": "No document labels found for the provided finance type."}, 
                            status=status.HTTP_404_NOT_FOUND)

        serializer = DocumentLabelSerializer(document_labels, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['POST'])
def create_application(request):
    user_id = request.data.get('user_id')

    # Validate user_id
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    # Create the application
    application = Application.objects.create(user=user)

    # Return the application's data as response
    application_data = {
        'id': application.id,
        'user_id': application.user.id,
        'date_created': application.date_created,
        'last_updated': application.last_updated,
        'steps_completed': application.steps_completed,
    }
    return Response(application_data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
def delete_application(request, application_id):
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

    application.delete()
    return Response({"message": "Application deleted successfully."}, status=status.HTTP_204_NO_CONTENT)    
    
# class ApplicationCreateView(APIView):
#     def post(self, request, user_id):
#         # Get user based on user_id
#         try:
#             user = User.objects.get(id=user_id)
#         except User.DoesNotExist:
#             return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

#         # Create the application
#         application = Application.objects.create(user=user)

#         # Create associated records using the data from the request
#         basic_contact_info_data = request.data.get('basic_contact_information')
#         business_details_data = request.data.get('business_details')
#         funding_requirements_data = request.data.get('funding_requirements')
#         financial_information_data = request.data.get('financial_information')
#         documents_data = request.data.get('documents')

#         # Save Basic Contact Information
#         BasicContactInformation.objects.create(application=application, **basic_contact_info_data)

#         # Save Business Details
#         BusinessDetails.objects.create(application=application, **business_details_data)

#         # Save Funding Requirements
#         FundingRequirements.objects.create(application=application, **funding_requirements_data)

#         # Save Financial Information
#         FinancialInformation.objects.create(application=application, **financial_information_data)

#         # Save Documents
#         for doc in documents_data:
#             label_id = doc.get('label_id')
#             file = doc.get('file')

#             if label_id is None or file is None:
#                 return Response({'error': 'Document label_id and file are required.'}, status=status.HTTP_400_BAD_REQUEST)

#             # Check if the label_id exists
#             try:
#                 document_label = DocumentLabel.objects.get(id=label_id)
#             except DocumentLabel.DoesNotExist:
#                 return Response({'error': f'Document label with id {label_id} not found.'}, status=status.HTTP_404_NOT_FOUND)

#             # Create the document upload
#             DocumentUpload.objects.create(application=application, label=document_label, file=file)
        
#         ApplicationStatus.objects.create(application=application, status='submitted')
        
#         return Response({'message': 'Application created successfully.'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def new_application(request, user_id):
    # Get user based on user_id
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Create the application
    application = Application.objects.create(user=user)

    # Extract data from request
    basic_contact_info_data = request.data.get('basic_contact_information')
    business_details_data = request.data.get('business_details')
    funding_requirements_data = request.data.get('funding_requirements')
    financial_information_data = request.data.get('financial_information')

    # Check for required fields
    if not all([basic_contact_info_data, business_details_data, funding_requirements_data, financial_information_data]):
        return Response({'error': 'All required fields must be provided.'}, status=status.HTTP_400_BAD_REQUEST)

    # Save Basic Contact Information
    BasicContactInformation.objects.create(application=application, **basic_contact_info_data)

    # Save Business Details
    BusinessDetails.objects.create(application=application, **business_details_data)

    # Save Funding Requirements
    FundingRequirements.objects.create(application=application, **funding_requirements_data)

    # Save Financial Information
    FinancialInformation.objects.create(application=application, **financial_information_data)

    return Response({'id': application.id, 'message': 'Application created successfully.'}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def upload_files(request, application_id):
    # Get the application
    try:
        application = Application.objects.get(id=application_id)
        user = application.user
    except Application.DoesNotExist:
        return Response({'error': 'Application not found.'}, status=status.HTTP_404_NOT_FOUND)

    documents_data = request.FILES.getlist('documents[]')
    documents_label_ids = request.data.getlist('documents_label_id[]')

    for file, label_id in zip(documents_data, documents_label_ids):
        if label_id is None or file is None:
            return Response({'error': 'Document label_id and file are required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the label_id exists
        try:
            document_label = DocumentLabel.objects.get(id=label_id)
        except DocumentLabel.DoesNotExist:
            return Response({'error': f'Document label with id {label_id} not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Create the document upload
        DocumentUpload.objects.create(application=application, label=document_label, file=file)

    application.steps_completed = True  # Set the attribute on the instance
    application.save()  # Save the instance

    ApplicationStatus.objects.create(application=application, status='submitted')

    AdminNotification.objects.create(
                application=application,
                message="New application received",
                seen=False
            )
    
    email_thread = threading.Thread(target=send_emails, args=(application, user))
    email_thread.start()

    return Response({'message': 'Documents uploaded successfully.'}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
def get_activity_logs(request, user_id):
    # Get user
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    # Get the last 20 activity logs for the user
    activity_logs = ApplicationActivityLog.objects.filter(user=user).order_by('-timestamp')[:20]

    # Serialize the data
    data = [
        {
            'id': log.id,
            'application_id': log.application.id,
            'user_id': log.user.id,
            'activity': log.activity,
            'timestamp': log.timestamp.isoformat()  # Convert to ISO format
        }
        for log in activity_logs
    ]

    return Response(data, status=status.HTTP_200_OK)
            
# class DocumentUploadView(generics.GenericAPIView):
#     serializer_class = DocumentUploadSerializer

#     def get(self, request, user_id):
#         document_upload = get_object_or_404(DocumentUpload, user_id=user_id)
#         serializer = self.serializer_class(document_upload, context={'request': request})
#         return Response(serializer.data, status=status.HTTP_200_OK)

#     def post(self, request):
#         user_id = request.data.get('user_id')

#         if not user_id:
#             return Response({"error": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

#         files = {}
#         for key in ['business_plan', 'financial_statement', 'personal_id']:
#             if key in request.FILES:
#                 # Ensure each file has a unique name
#                 file = request.FILES[key]
#                 filename = f"{user_id}_{key}_{file.name}"
#                 file.name = filename
#                 files[key] = file

#         # Use transaction.atomic() to manage transactions
#         try:
#             with transaction.atomic():
#                 # Update or create based on the user_id
#                 document_upload, created = DocumentUpload.objects.update_or_create(
#                     user_id=user_id,
#                     defaults=files
#                 )

#                 # Log the activity
#                 activity = "Document uploaded." if created else "Document updated."
#                 ApplicationActivityLog.objects.create(
#                     application=document_upload.user.basiccontactinformation_set.first(),
#                     user=document_upload.user,
#                     activity=activity
#                 )

#                 # Update DocumentStatus for each non-empty document field
#                 for field in ['business_plan', 'financial_statement', 'personal_id']:
#                     document = getattr(document_upload, field, None)
#                     if document:
#                         DocumentStatus.objects.update_or_create(
#                             document=document_upload,
#                             defaults={'status': 'under_review'}
#                         )

#                 serializer = self.serializer_class(document_upload, context={'request': request})

#                 if created:
#                     return Response(serializer.data, status=status.HTTP_201_CREATED)
#                 return Response(serializer.data, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
# class UserProfileDataView(APIView):
#     def get(self, request, user_id):
#         # Retrieve all related records for the user in a single request
#         basic_contact_info = get_object_or_404(BasicContactInformation, user_id=user_id)
#         business_details = get_object_or_404(BusinessDetails, user_id=user_id)
#         funding_requirements = get_object_or_404(FundingRequirements, user_id=user_id)
#         financial_information = get_object_or_404(FinancialInformation, user_id=user_id)
#         document_upload = get_object_or_404(DocumentUpload, user_id=user_id)
#         # application_Status = get_object_or_404(ApplicationStatus, user_id=user_id)
#         application_activity = ApplicationActivityLog.objects.filter(application_id=user_id).last()

#         # Serialize data
#         basic_contact_info_serialized = BasicContactInformationSerializer(basic_contact_info).data
#         business_details_serialized = BusinessDetailsSerializer(business_details).data
#         funding_requirements_serialized = FundingRequirementsSerializer(funding_requirements).data
#         financial_information_serialized = FinancialInformationSerializer(financial_information).data
#         document_upload_serialized = DocumentUploadSerializer(document_upload, context={'request': request}).data
#         # application_Status_serialized = ApplicationStatusSerializer(application_Status).data
#         application_Activity_serialized = ApplicationActivityLogSerializer(application_activity).data

#         # Combine all serialized data into a single response
#         user_data = {
#             'BasicContactInformation': basic_contact_info_serialized,
#             'BusinessDetails': business_details_serialized,
#             'FundingRequirements': funding_requirements_serialized,
#             'FinancialInformation': financial_information_serialized,
#             'DocumentUpload': document_upload_serialized,
#             # 'ApplicationStatus': application_Status_serialized,
#             'ApplicationActivity': application_Activity_serialized
#         }

#         return Response(user_data, status=status.HTTP_200_OK)
    
@csrf_exempt
def update_steps_completed(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            application_id = data.get('application_id')
            user_id = data.get('user_id')
            steps_completed = data.get('steps_completed')

            if application_id is None:
                return JsonResponse({'error': 'application_id is required.'}, status=400)

            # Fetch the application based on the application_id
            try:
                application = Application.objects.get(id=application_id)
                application_status = ApplicationStatus.objects.get(application = application)
            except Application.DoesNotExist:
                return JsonResponse({'error': 'Application not found.'}, status=404)

            # Update steps_completed for the application
            application.steps_completed = steps_completed if steps_completed is not None else application.steps_completed
            application_status.status = "submitted"
            application_status.review_percentage = "50.00"
            application.save()

            # Update steps_completed for the user if user_id is provided
            if user_id is not None:
                try:
                    user = User.objects.get(id=user_id)
                    user.steps_completed = steps_completed if steps_completed is not None else user.steps_completed
                    user.save()

                    ApplicationActivityLog.objects.create(
                        application=application,  # Use the fetched application
                        user=user,
                        activity="Steps Completed."
                    )

                except User.DoesNotExist:
                    return JsonResponse({'error': 'User not found.'}, status=404)
                
                AdminNotification.objects.create(
                application=application,
                message="New application received",
                seen=False
            )
            
            email_thread = threading.Thread(target=send_emails, args=(application, user))
            email_thread.start()

            return JsonResponse({'message': 'Steps completed status updated successfully.'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    return JsonResponse({'error': 'Invalid HTTP method.'}, status=405)

def send_emails(application, user):
    subject = "New Application Completion Notification"
    message = f"The user {user.admin_name} with email {user.email} has completed an application for the business type. Please check the portal for more details."

    # Create the email message
    admin_message = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                color: #333;
                padding: 20px;
            }}
            .container {{
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                margin: 0 auto;
            }}
            h1 {{
                color: #2e6fba;
                text-align: center;
            }}
            p {{
                font-size: 16px;
                line-height: 1.6;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Application Completion Notification</h1>
            <p>Dear Admin,</p>
            <p>The user <strong>{user.admin_name}</strong> with email <strong>{user.email}</strong> has completed an application.</p>
            <p>Please check the portal for more details.</p>
            <br><br>
            <p>Best regards,</p>
            <p>Pinnacle Solutions Admin Team</p>
        </div>
    </body>
    </html>
    """

    # Get all super admins and admins
    admin_emails = User.objects.filter(is_active=True, is_superAdmin=True).values_list('email', flat=True)
    admin_emails = list(admin_emails) + list(User.objects.filter(is_admin=True).values_list('email', flat=True))

    # Add the user email to the list
    recipient_emails = admin_emails + [user.email]

    for recipient_email in recipient_emails:
        try:
            msg = MIMEMultipart()
            msg['From'] = "admin@pinnacleportal.co.uk"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(admin_message, 'html'))

            with smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                server.starttls()
                server.login("admin@pinnacleportal.co.uk", "?8Th(3xHJ7#f")
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {str(e)}")

@csrf_exempt
def get_unseen_notifications(request):
    if request.method == 'GET':
        unseen_notifications = AdminNotification.objects.filter(seen=False)

        notifications_list = [
            {
                "id": notification.id,
                "application_id": notification.application.id,
                "message": notification.message,
                "seen": notification.seen,
                "created_at": notification.created_at.isoformat()
            }
            for notification in unseen_notifications
        ]

        return JsonResponse(notifications_list, safe=False, status=200)

    return JsonResponse({'error': 'Invalid HTTP method.'}, status=405)

@csrf_exempt
def update_notification_seen(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            notification_id = data.get('notification_id')

            if notification_id is None:
                return JsonResponse({'error': 'notification_id is required.'}, status=400)

            try:
                notification = AdminNotification.objects.get(id=notification_id)
                notification.seen = True
                notification.save()

                return JsonResponse({'message': 'Notification marked as seen successfully.'}, status=200)

            except AdminNotification.DoesNotExist:
                return JsonResponse({'error': 'Notification not found.'}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload.'}, status=400)

    return JsonResponse({'error': 'Invalid HTTP method.'}, status=405)


@api_view(['GET'])
def get_application_counts(request):
    total_applications = Application.objects.count()
    completed_or_approved = ApplicationStatus.objects.filter(status__in=['completed', 'approved']).count()
    in_progress = ApplicationStatus.objects.filter(status__in=['in_progress','submitted','under_review']).count()
    rejected = ApplicationStatus.objects.filter(status='rejected').count()

    return JsonResponse({
        'total_applications': total_applications,
        'completed': completed_or_approved,
        'in_progress': in_progress,
        'rejected': rejected
    }, status=200)


@api_view(['GET'])
def get_application_graph_data(request):
    today = timezone.now().date()
    
    # Applications per day (last 8 days)
    last_8_days = Application.objects.filter(date_created__gte=today - timedelta(days=7)).annotate(day=TruncDay('date_created')).values('day').annotate(count=Count('id')).order_by('day')
    
    # Applications per month (last 8 months)
    last_8_months = Application.objects.filter(date_created__gte=today - timedelta(days=240)).annotate(month=TruncMonth('date_created')).values('month').annotate(count=Count('id')).order_by('month')
    
    # Applications per year (last 8 years)
    last_8_years = Application.objects.filter(date_created__gte=today - timedelta(days=2920)).annotate(year=TruncYear('date_created')).values('year').annotate(count=Count('id')).order_by('year')

    return JsonResponse({
        'applications_per_day': list(last_8_days),
        'applications_per_month': list(last_8_months),
        'applications_per_year': list(last_8_years)
    }, status=200)


@api_view(['GET'])
def get_latest_5_users(request):
    # Get the latest 5 users
    latest_users = User.objects.order_by('-date_joined').prefetch_related(
        Prefetch('application_set', queryset=Application.objects.select_related('basiccontactinformation')),
        Prefetch('referee', queryset=Referral.objects.select_related('referee'))  # Corrected related_name here
    )[:10]

    user_data = []

    for user in latest_users:
        # Fetch the last application if available
        application = user.application_set.last()

        # Check for BasicContactInformation
        if application:
            try:
                business_info = application.basiccontactinformation
                full_name = business_info.full_name
                business_name = business_info.business_name
            except BasicContactInformation.DoesNotExist:
                full_name = 'N/A'
                business_name = 'N/A'
        else:
            full_name = 'N/A'
            business_name = 'N/A'

        if full_name == 'N/A' or business_name == 'N/A':
            continue

        # Fetching the referrer if available (using the related name 'referral')
        referrer_info = user.referral.first()  # Get the first referral for the user
        referrer_email = referrer_info.referrer.email if referrer_info and referrer_info.referrer else 'No Referrer'

        # Fetch application status if available
        status_info = ApplicationStatus.objects.filter(application=application).last() if application else None
        status = status_info.status if status_info else 'No Application'

        # Append user data to the list
        user_data.append({
            'full_name': full_name,
            'business_name': business_name,
            'application_status': status,
            'referrer': referrer_email,
            'application_id': application.id if application else None
        })

    return JsonResponse({
        'latest_users': user_data
    }, status=200)


@api_view(['GET'])
def get_clients(request):
    # Get all users ordered by date joined
    latest_users = User.objects.order_by('-date_joined').prefetch_related(
        Prefetch('application_set', queryset=Application.objects.select_related('basiccontactinformation')),
        Prefetch('referral', queryset=Referral.objects.select_related('referrer'))  # Corrected related_name here
    )

    user_data = []

    for user in latest_users:
        # Fetch the last application if available
        application = user.application_set.last()
        
        if not application:
            continue  # Skip if there's no application

        # Check for BasicContactInformation
        try:
            business_info = application.basiccontactinformation
        except BasicContactInformation.DoesNotExist:
            continue  # Skip this user if there's no BasicContactInformation

        # Fetch referrer if available
        referrer_info = Referral.objects.filter(referee=user).first()  # Use filter on the Referral model to find the referrer
        ref_info = Referral.objects.filter(referrer=user).first()
        referrer_email = referrer_info.referrer.email if referrer_info else 'No Referrer'

        # Fetch application status if available
        status_info = ApplicationStatus.objects.filter(application=application).last()
        status = status_info.status if status_info else 'No Application'

        # Get the last activity for the user
        last_activity = ApplicationActivityLog.objects.filter(user=user).last()

        # Append user data to the list
        user_data.append({
            'full_name': business_info.full_name,
            'email': user.email,
            'business_name': business_info.business_name,
            'phone_no': business_info.phone_number,
            'application_status': status,
            'referrer': referrer_email,
            'referral_percentage': ref_info.referral_reward_percentage if ref_info else 0,  # Safely handle potential None
            'lastActivity': last_activity.timestamp if last_activity else None,  # Safely handle potential None
            'application_id': application.id
        })

    return JsonResponse({
        'clients': user_data
    }, status=200)

# @api_view(['GET'])
# def get_all_applications(request):
#     # Get all applications with prefetched related models
#     applications = Application.objects.prefetch_related('basiccontactinformation', 'applicationstatus')

#     user_data = []

#     for application in applications:
#         # Attempt to access BasicContactInformation
#         try:
#             business_info = application.basiccontactinformation
#         except BasicContactInformation.DoesNotExist:
#             continue  # Skip this application if there's no BasicContactInformation

#         # Fetch the last status info
#         status_info = ApplicationStatus.objects.filter(application=application).last()

#         # Attempt to extract required information, skip if any field is missing
#         try:
#             user_data.append({
#                 'full_name': business_info.full_name,
#                 'email': application.user.email,  # Fetch user's email directly from the application
#                 'business_name': business_info.business_name,
#                 'phone_no': business_info.phone_number,
#                 'application_status': status_info.status if status_info else 'N/A',  # Use the latest status
#                 'lastActivity': status_info.last_updated if status_info else 'N/A',  # Use last updated timestamp from ApplicationStatus
#                 'application_id': application.id
#             })
#         except AttributeError:
#             continue  # Skip this application if any field is missing

#     return JsonResponse({
#         'applications': user_data
#     }, status=200)


@api_view(['GET'])
def get_all_applications(request):
    # Get all applications with prefetched related models
    applications = Application.objects.prefetch_related('basiccontactinformation', 'applicationstatus').order_by('id')

    user_data = []

    for application in applications:
        # Attempt to access BasicContactInformation
        try:
            business_info = application.basiccontactinformation
        except BasicContactInformation.DoesNotExist:
            continue  # Skip this application if there's no BasicContactInformation

        # Fetch the last status info
        status_info = ApplicationStatus.objects.filter(application=application).last()

        # Attempt to fetch commission information
        try:
            commission = Commission.objects.get(application=application)
            commission_data = {
                'commission_percentage': commission.commission_percentage,
                'commission_amount': commission.commission_amount,
                'commission_paid': commission.comission_paid
            }
        except Commission.DoesNotExist:
            commission_data = {
                'commission_percentage': None,
                'commission_amount': None,
                'commission_paid': False
            }

        # Check if the user has a referral
        try:
            has_referral = Referral.objects.filter(referee=application.user).exists()
        except Referral.DoesNotExist:
            has_referral = False

        # Attempt to extract required information, skip if any field is missing
        try:
            user_data.append({
                'full_name': business_info.full_name,
                'email': application.user.email,  # Fetch user's email directly from the application
                'business_name': business_info.business_name,
                'phone_no': business_info.phone_number,
                'application_status': status_info.status if status_info else 'N/A',  # Use the latest status
                'lastActivity': status_info.last_updated if status_info else 'N/A',  # Use last updated timestamp from ApplicationStatus
                'application_id': application.id,
                'commission': commission_data,  # Add commission data
                'has_referral': has_referral  # Add referral status flag
            })
        except AttributeError:
            continue  # Skip this application if any field is missing

    user_data = sorted(user_data, key=lambda x: x['application_id'])
    return JsonResponse({
        'applications': user_data
    }, status=200)

# @api_view(['GET'])
# def admin_application_view(request, application_id):
#     try:
#         application = Application.objects.get(id=application_id)
#     except Application.DoesNotExist:
#         return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
    
#     # Initialize response data
#     response_data = {}

#     user = application.user
#     response_data['user_id'] = user.id
#     response_data['user_email'] = user.email

#     # Serialize and add BasicContactInformation data
#     try:
#         basic_info = BasicContactInformation.objects.get(application=application)
#         response_data['basic_contact_information'] = BasicContactInformationSerializer(basic_info).data
#     except BasicContactInformation.DoesNotExist:
#         response_data['basic_contact_information'] = {}

#     # Serialize and add BusinessDetails data
#     try:
#         business_details = BusinessDetails.objects.get(application=application)
#         response_data['business_details'] = BusinessDetailsSerializer(business_details).data
#     except BusinessDetails.DoesNotExist:
#         response_data['business_details'] = {}

#     # Serialize and add FundingRequirements data
#     try:
#         funding_requirements = FundingRequirements.objects.get(application=application)
#         response_data['funding_requirements'] = FundingRequirementsSerializer(funding_requirements).data
#     except FundingRequirements.DoesNotExist:
#         response_data['funding_requirements'] = {}

#     # Serialize and add FinancialInformation data
#     try:
#         financial_info = FinancialInformation.objects.get(application=application)
#         response_data['financial_information'] = FinancialInformationSerializer(financial_info).data
#     except FinancialInformation.DoesNotExist:
#         response_data['financial_information'] = {}
    
#     try:
#         application_activity_log = ApplicationActivityLog.objects.filter(application=application).last()
#         response_data['application_activity_log'] = ApplicationActivityLogSerializer(application_activity_log).data
#     except Exception as e:
#         response_data['application_activity_log'] = {}

#     # Serialize and add DocumentUpload data with label
#     documents = DocumentUpload.objects.filter(application=application)
#     document_data = []
#     for document in documents:
#         document_info = {
#             'id': document.id,
#             'file': request.build_absolute_uri(document.file.url),
#             'label_id': document.label.id,
#             'label': document.label.label,  # Get the label name
#             'status': document.status,
#             'remarks': document.remarks,
#             'date_created': document.date_created,
#             'last_updated': document.last_updated,
#         }
#         document_data.append(document_info)
#     response_data['document_uploads'] = document_data

#     # Serialize and add ApplicationStatus data
#     try:
#         # application_status = ApplicationStatus.objects.get(application=application)
#         # application_status.status = 'under_review'
#         # application_status.save()
#         application_status = ApplicationStatus.objects.get(application=application)
#         response_data['application_status'] = ApplicationStatusSerializer(application_status).data
#     except ApplicationStatus.DoesNotExist:
#         response_data['application_status'] = {}

#     return Response(response_data)

@api_view(['GET'])
def admin_application_view(request, application_id):
    try:
        application = Application.objects.get(id=application_id)
    except Application.DoesNotExist:
        return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)
    
    # Initialize response data
    response_data = {}

    user = application.user
    response_data['user_id'] = user.id
    response_data['user_email'] = user.email

    # Serialize and add BasicContactInformation data
    try:
        basic_info = BasicContactInformation.objects.get(application=application)
        response_data['basic_contact_information'] = BasicContactInformationSerializer(basic_info).data
    except BasicContactInformation.DoesNotExist:
        response_data['basic_contact_information'] = {}

    # Serialize and add BusinessDetails data
    try:
        business_details = BusinessDetails.objects.get(application=application)
        response_data['business_details'] = BusinessDetailsSerializer(business_details).data
    except BusinessDetails.DoesNotExist:
        response_data['business_details'] = {}

    # Serialize and add FundingRequirements data
    try:
        funding_requirements = FundingRequirements.objects.get(application=application)
        response_data['funding_requirements'] = FundingRequirementsSerializer(funding_requirements).data
    except FundingRequirements.DoesNotExist:
        response_data['funding_requirements'] = {}

    # Serialize and add FinancialInformation data
    try:
        financial_info = FinancialInformation.objects.get(application=application)
        response_data['financial_information'] = FinancialInformationSerializer(financial_info).data
    except FinancialInformation.DoesNotExist:
        response_data['financial_information'] = {}

    # Add Referral Count for the User
    referral_count = Referral.objects.filter(referrer=user).count()
    response_data['referral_count'] = referral_count

    # Retrieve the last 3 applications and return their financeType and status
    last_three_applications = Application.objects.filter(user=user).order_by('-date_created')[:3]
    application_history = []
    for app in last_three_applications:
        try:
            finance_type = FundingRequirements.objects.get(application=app).finance_type
            status = ApplicationStatus.objects.get(application=app).status
            application_history.append({
                "application_id": app.id,
                "financeType": finance_type,
                "status": status
            })
        except (FundingRequirements.DoesNotExist, ApplicationStatus.DoesNotExist):
            continue  # Skip this application if data is missing

    response_data['application_history'] = application_history

    try:
        application_activity_log = ApplicationActivityLog.objects.filter(application=application).last()
        response_data['application_activity_log'] = ApplicationActivityLogSerializer(application_activity_log).data
    except Exception as e:
        response_data['application_activity_log'] = {}

    # Serialize and add DocumentUpload data with label
    documents = DocumentUpload.objects.filter(application=application)
    document_data = []
    for document in documents:
        document_info = {
            'id': document.id,
            'file': request.build_absolute_uri(document.file.url),
            'label_id': document.label.id,
            'label': document.label.label,  # Get the label name
            'status': document.status,
            'remarks': document.remarks,
            'date_created': document.date_created,
            'last_updated': document.last_updated,
        }
        document_data.append(document_info)
    response_data['document_uploads'] = document_data

    # Serialize and add ApplicationStatus data
    try:
        application_status = ApplicationStatus.objects.get(application=application)
        response_data['application_status'] = ApplicationStatusSerializer(application_status).data
    except ApplicationStatus.DoesNotExist:
        response_data['application_status'] = {}

    return Response(response_data)




# @api_view(['GET'])
# def get_user_application_details(request, user_id):
#     try:
#         first_application = Application.objects.prefetch_related('basiccontactinformation').first()
#         user_data = first_application.basiccontactinformation
#         # Fetch the user and their latest application
#         user = User.objects.get(id=user_id)
#         latest_application = Application.objects.filter(user=user).latest('date_created')

#         # Fetch application status and review percentage
#         application_status = ApplicationStatus.objects.get(application=latest_application)
#         status_data = {
#             'status': application_status.status,
#             'review_percentage': application_status.review_percentage,
#         }

#         # Fetch total number of referrals
#         referral_count = Referral.objects.filter(referrer=user).count()

#         # Fetch the latest 2 activity logs
#         activity_logs = ApplicationActivityLog.objects.filter(Q(application=latest_application) | Q(user=user_id)).order_by('-timestamp')[:2]
#         activities = [
#             {
#                 'activity': log.activity,
#                 'date': localtime(log.timestamp).date(),
#                 'time': localtime(log.timestamp).time(),
#                 'status': application_status.status,
#             }
#             for log in activity_logs
#         ]

#         # Fetch all documents with status "rejected" or "reminder_pending"
#         rejected_or_pending_docs = DocumentUpload.objects.filter(
#             application=latest_application, 
#             status__in=['rejected', 'reminder_pending']
#         )
#         documents = [
#             {
#                 'label': doc.label.label,
#                 'document_id': doc.id,
#                 'application_id': doc.application.id,
#                 'status': doc.status
#             }
#             for doc in rejected_or_pending_docs
#         ]

#         # Prepare the response
#         data = {
#             'full_name': user_data.full_name,  # Or 'user.full_name' if name is stored
#             'application_status': status_data,
#             'total_referrals': referral_count,
#             'recent_activities': activities,
#             'rejected_or_pending_documents': documents,
#         }

#         return Response(data, status=status.HTTP_200_OK)

#     except User.DoesNotExist:
#         return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
#     except Application.DoesNotExist:
#         return Response({'error': 'No application found for this user'}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_user_application_details(request, user_id):
    try:
        # Fetch the user
        user = get_object_or_404(User, id=user_id)
        applications = Application.objects.filter(user=user)

        first_application = Application.objects.filter(user=user).first()

        # Fetch the latest application for the user
        latest_application = Application.objects.filter(user=user).latest('date_created')

        user_data_1 = get_object_or_404(BasicContactInformation, application=first_application)
        # Fetch the BasicContactInformation associated with the latest application
        user_data = get_object_or_404(BasicContactInformation, application=latest_application)

        # Fetch application status and review percentage
        application_status = ApplicationStatus.objects.get(application=latest_application)
        status_data = {
            'status': application_status.status,
            'review_percentage': application_status.review_percentage,
        }

        # Fetch total number of referrals
        referral_count = Referral.objects.filter(referrer=user).count()

        # Fetch the latest 2 activity logs for the application or user
        activity_logs = ApplicationActivityLog.objects.filter(
            Q(application=latest_application) | Q(user=user)
        ).order_by('-timestamp')[:2]

        activities = [
            {
                'activity': log.activity,
                'date': localtime(log.timestamp).date(),
                'time': localtime(log.timestamp).time(),
                'status': application_status.status,
            }
            for log in activity_logs
        ]

        # Fetch all documents with status "rejected" or "reminder_pending"
        rejected_or_pending_docs = DocumentUpload.objects.filter(
            application__in=applications,  # Filter documents for all applications of the user
            status__in=['rejected', 'reminder_pending']
        )
        
        documents = [
            {
                'label': doc.label.label,
                'document_id': doc.id,
                'application_id': doc.application.id,
                'status': doc.status
            }
            for doc in rejected_or_pending_docs
        ]

        # Prepare the response
        data = {
            'full_name': user_data_1.full_name,
            'application_status': status_data,
            'total_referrals': referral_count-1,
            'recent_activities': activities,
            'rejected_or_pending_documents': documents,
        }

        return Response(data, status=status.HTTP_200_OK)

    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except Application.DoesNotExist:
        return Response({'error': 'No application found for this user'}, status=status.HTTP_404_NOT_FOUND)
    except BasicContactInformation.DoesNotExist:
        return Response({'error': 'No contact information found for this user\'s application'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
def get_user_dashboard_data(request, user_id):
    # Get counts
    in_progress_count = ApplicationStatus.objects.filter(
        application__user_id=user_id,
        status__in=['in_progress', 'submitted']
    ).count()

    completed_or_approved_count = ApplicationStatus.objects.filter(
        application__user_id=user_id,
        status__in=['completed', 'approved']
    ).count()

    rejected_documents_or_reminder_pending_count = DocumentUpload.objects.filter(
        application__user_id=user_id,
        status__in=['rejected', 'reminder_pending']
    ).count()

    rejected_applications_count = ApplicationStatus.objects.filter(
        application__user_id=user_id,
        status='rejected'
    ).count()

    # Get all user applications and their details
    user_applications = Application.objects.filter(user_id=user_id).select_related(
        'applicationstatus', 'fundingrequirements'
    )

    applications_data = []
    for app in user_applications:
        try:
            applications_data.append({
                'application_id': app.id,
                'finance_type': app.fundingrequirements.finance_type,
                'amount_required': str(app.fundingrequirements.amount_required),
                'date_submitted': app.date_created,
                'application_status': app.applicationstatus.status,
                'review_percentage': str(app.applicationstatus.review_percentage),
            })
        except Exception as e:
            # Skip this application if FundingRequirements does not exist
            continue

    # Prepare response data
    response_data = {
        'counts': {
            'in_progress': in_progress_count,
            'completed_or_approved': completed_or_approved_count,
            'rejected_documents_or_reminder_pending': rejected_documents_or_reminder_pending_count,
            'rejected_applications': rejected_applications_count,
        },
        'applications': applications_data
    }

    return JsonResponse(response_data)


@api_view(['GET'])
def search_user_applications(request, user_id):
    query = request.GET.get('q', '').strip()  # Get search query from request parameters

    # Build the base queryset for the user
    user_applications = Application.objects.filter(user_id=user_id).select_related(
        'applicationstatus', 'fundingrequirements'
    )

    # Apply filters based on the search query if it exists
    if query:
        user_applications = user_applications.filter(
            Q(id__icontains=query) |  # Search by application ID
            Q(fundingrequirements__finance_type__icontains=query) |  # Search by finance type
            Q(fundingrequirements__amount_required__icontains=query) |  # Search by amount required
            Q(date_created__icontains=query) |  # Search by date submitted
            Q(applicationstatus__status__icontains=query) |  # Search by application status
            Q(applicationstatus__review_percentage__icontains=query)  # Search by review percentage
        )

    applications_data = []
    for app in user_applications:
        try:
            applications_data.append({
                'application_id': app.id,
                'finance_type': app.fundingrequirements.finance_type,
                'amount_required': str(app.fundingrequirements.amount_required),
                'date_submitted': app.date_created,
                'application_status': app.applicationstatus.status,
                'review_percentage': str(app.applicationstatus.review_percentage),
            })
        except Exception as e:
            # Skip this application if FundingRequirements or ApplicationStatus does not exist
            continue

    return JsonResponse({'applications': applications_data}, status=200)


@api_view(['GET'])
def get_referral_summary(request, user_id):
    """
    Get referral details for a specific user including:
    - Total number of accepted invitations
    - Wallet balance
    - Email, status, and earnings of all invitations
    """
    # Get the user
    user = get_object_or_404(User, id=user_id)

    # Query total accepted invitations
    total_accepted_invitations = Referral.objects.filter(referrer=user).count()

    # Get the referrer's current wallet balance
    referral_obj = Referral.objects.filter(referrer=user).first()
    wallet_balance = Referral.objects.filter(referrer=user).aggregate(
        total_balance=Sum('wallet_balance')
    )['total_balance'] or 0


    # Get all the invitations details (email, status, earnings)
    invitations = ReferralInvitation.objects.filter(referrer=user).values(
        'referee_email', 'status', 'earned_from_referral', 'date_sent'
    )

    # Prepare the response data
    response_data = {
        "total_accepted_invitations": total_accepted_invitations-1,
        "wallet_balance": wallet_balance,
        "referral_code": referral_obj.referral_code,
        "invitations": list(invitations)
    }

    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['POST'])
def send_referral_invites(request, user_id):
    """
    API to send referral invitations via email and store the status in the database.
    """
    # Get the referrer (user sending the invites)
    referrer = User.objects.filter(id=user_id).first()
    if not referrer:
        return Response({'error': 'Referrer not found'}, status=status.HTTP_404_NOT_FOUND)

    # Get the email list from the request
    email_list = request.data.get('email_list', [])
    if not email_list:
        return Response({'error': 'Email list is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Check for the referral code
    referral = Referral.objects.filter(referrer=referrer).first()
    if not referral:
        return Response({'error': 'Referral not found for the user'}, status=status.HTTP_404_NOT_FOUND)

    # Loop through the email list to send invitations
    for recipient_email in email_list:
        # # Generate the referral URL with the referral code
        # referral_url = f"http://localhost:3000/?ref={referral.referral_code}/"

        # sender_email = settings.EMAIL_HOST_USER
        # sender_password = settings.EMAIL_HOST_PASSWORD
        # subject = "You're invited! Join our platform"
        # body = f"Hi, \n\n{referrer.email} has invited you to join our platform. Click the link to sign up: {referral_url}"

        # msg = MIMEMultipart()
        # msg['From'] = sender_email
        # msg['To'] = recipient_email
        # msg['Subject'] = subject
        # msg.attach(MIMEText(body, 'plain'))

        # Generate the referral URL with the referral code
        # referral_url = f"http://localhost:3000/?ref={referral.referral_code}/"
        referral_url = f"https://pinnacleportal.co.uk/?ref={referral.referral_code}/"

        # Email subject
        subject = "You're invited! Join Pinnacle Solutions"

        # Sender and recipient email information
        sender_email = "referral@pinnacleportal.co.uk"
        sender_password = "=K]wM.8)d[zG"  # Consider using environment variables for better security

        # Referral invitation email content
        referral_message = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    color: #333;
                    padding: 20px;
                }}
                .container {{
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    max-width: 600px;
                    margin: 0 auto;
                }}
                h1 {{
                    color: #2e6fba;
                    text-align: center;
                }}
                p {{
                    font-size: 16px;
                    line-height: 1.6;
                }}
                a {{
                    color: #1a73e8;
                    text-decoration: none;
                    font-weight: bold;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>You're Invited to Join Pinnacle Solutions!</h1>
                <p>Hi,</p>
                <p>{referrer.email} has invited you to join our platform. To get started, click the link below:</p>
                <p>
                    <a href="{referral_url}" target="_blank">Join Pinnacle Solutions</a>
                </p>
                <p>We're excited to have you with us! Click the link to start your journey.</p>
                <p>Best regards,<br>Pinnacle Solutions Team</p>
            </div>
        </body>
        </html>
        """

        # Prepare email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach the HTML body to the email
        msg.attach(MIMEText(referral_message, 'html'))


        try:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

            # Save the invitation in the database
            ReferralInvitation.objects.create(
                referrer=referrer,
                referee_email=recipient_email,
                status='Invitation_Sent',
                referral_reward_percentage=referral.referral_reward_percentage
            )
        except Exception as e:
            return Response({'error': f"Failed to send email to {recipient_email}: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Invitations sent successfully!'}, status=status.HTTP_200_OK)

@api_view(['POST'])
def send_Admin_referral_invites(request):
    """
    API to send referral invitations via email and store the status in the database.
    """
    # Get the referrer (user sending the invites)
    # Get the email list from the request
    email_list = request.data.get('email_list', [])
    admin_name = request.data.get('adminName')
    if not email_list or not admin_name:
        return Response({'error': 'Email list and admin name is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Check for the referral code    

    # Loop through the email list to send invitations
    for recipient_email in email_list:
        # # Generate the referral URL with the referral code
        # referral_url = f"http://localhost:3000/?ref={referral.referral_code}/"

        # sender_email = settings.EMAIL_HOST_USER
        # sender_password = settings.EMAIL_HOST_PASSWORD
        # subject = "You're invited! Join our platform"
        # body = f"Hi, \n\n{referrer.email} has invited you to join our platform. Click the link to sign up: {referral_url}"

        # msg = MIMEMultipart()
        # msg['From'] = sender_email
        # msg['To'] = recipient_email
        # msg['Subject'] = subject
        # msg.attach(MIMEText(body, 'plain'))

        # Generate the referral URL with the referral code
        # referral_url = f"http://localhost:3000/?ref={referral.referral_code}/"
        referral_url = f"https://pinnacleportal.co.uk/"

        # Email subject
        subject = "You're invited! Join Pinnacle Solutions"

        # Sender and recipient email information
        sender_email = "admin@pinnacleportal.co.uk"
        sender_password = "?8Th(3xHJ7#f"  # Consider using environment variables for better security

        # Referral invitation email content
        referral_message = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    color: #333;
                    padding: 20px;
                }}
                .container {{
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    max-width: 600px;
                    margin: 0 auto;
                }}
                h1 {{
                    color: #2e6fba;
                    text-align: center;
                }}
                p {{
                    font-size: 16px;
                    line-height: 1.6;
                }}
                a {{
                    color: #1a73e8;
                    text-decoration: none;
                    font-weight: bold;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>You're Invited to Join Pinnacle Solutions!</h1>
                <p>Hi,</p>
                <p> Pinnacle has invited you to join our platform. To get started, click the link below:</p>
                <p>
                    <a href="{referral_url}" target="_blank">Join Pinnacle Solutions</a>
                </p>
                <p>We're excited to have you with us! Click the link to start your journey.</p>
                <p>Best regards,<br>Pinnacle Solutions Team</p>
            </div>
        </body>
        </html>
        """

        # Check if the email exists in the User model
        user_exists = User.objects.filter(email=recipient_email).exists()

        try:
            # Check if email_to exists in AdminEmailLog
            email_log = AdminEmailLog.objects.filter(email_to=recipient_email).first()

            if user_exists:
                if email_log:
                    if email_log.status == "Sent":
                        email_log.status = "Accepted"
                        email_log.save()
                else:
                    AdminEmailLog.objects.create(email_to=recipient_email, email_by=admin_name, status="Sent")
            else:
                if email_log:
                    email_log.sent_at = now()  # Update timestamp
                    email_log.save()
                else:
                    AdminEmailLog.objects.create(email_to=recipient_email, email_by=admin_name, status="Sent")
        except Exception as e:
            print(e)


        # Prepare email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach the HTML body to the email
        msg.attach(MIMEText(referral_message, 'html'))


        try:
            server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()

        except Exception as e:
            return Response({'error': f"Failed to send email to {recipient_email}: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'Invitations sent successfully!'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def send_invitation(request):
    # Extracting data from the request body
    client_name = request.data.get('clientName')
    email = request.data.get('email')
    message = request.data.get('message')
    admin_name = request.data.get('adminName')

    # referral_url = f"http://localhost:3000/"
    referral_url = f"https://pinnacleportal.co.uk/"


    # Validate the input data
    if not client_name or not email or not message or not admin_name:
        return JsonResponse({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Email subject
    subject = "You're invited! Join Pinnacle Solutions"

    # Sender and recipient email information
    sender_email = "admin@pinnacleportal.co.uk"
    sender_password = "?8Th(3xHJ7#f"  # Suggestion: Use environment variables for better security
    recipient_email = email

    # Invitation message details
    invitation_message = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                color: #333;
                padding: 20px;
            }}
            .container {{
                background-color: #fff;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                max-width: 600px;
                margin: 0 auto;
            }}
            h1 {{
                color: #2e6fba;
                text-align: center;
            }}
            p {{
                font-size: 16px;
                line-height: 1.6;
            }}
            a {{
                color: #1a73e8;
                text-decoration: none;
                font-weight: bold;
            }}
            a:hover {{
                text-decoration: underline;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>You're Invited to Join Pinnacle Solutions!</h1>
            <p>Hi {client_name},</p>
            <p>{message}</p>
            <p>We would love to have you onboard. To get started, simply click the link below to sign up:</p>
            <p>
                <a href="{referral_url}" target="_blank">Join Pinnacle Solutions</a>
            </p>
            <p>We're excited to have you with us!</p>
            <p>Best regards,<br>Pinnacle Solutions Team</p>
        </div>
    </body>
    </html>
    """

     # Check if the email exists in the User model
    user_exists = User.objects.filter(email=email).exists()

    try:
        # Check if email_to exists in AdminEmailLog
        email_log = AdminEmailLog.objects.filter(email_to=email).first()

        if user_exists:
            if email_log:
                email_log.status = "Accepted"
                email_log.save()
            else:
                AdminEmailLog.objects.create(email_to=email, email_by=admin_name, status="Sent")
        else:
            if email_log:
                email_log.sent_at = now()  # Update timestamp
                email_log.save()
            else:
                AdminEmailLog.objects.create(email_to=email, email_by=admin_name, status="Sent")


        # Prepare email message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach the HTML body to the email
        msg.attach(MIMEText(invitation_message, 'html'))

        # Sending email
        server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        return JsonResponse({'message': 'Invitation sent successfully!'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@api_view(['GET'])
def get_email_logs(request):
    # Get all records where status is "Sent"
    pending_logs = AdminEmailLog.objects.filter(status="Sent")

    # Check if these emails exist in the User model
    user_emails = set(User.objects.values_list("email", flat=True))

    # Update status to "Accepted" for existing users
    for log in pending_logs:
        if log.email_to in user_emails:
            log.status = "Accepted"
            log.save()

    # Retrieve and return all updated records
    all_logs = AdminEmailLog.objects.all().values()
    
    return JsonResponse(list(all_logs), safe=False, status=status.HTTP_200_OK)
    

@api_view(['GET'])
def get_notifications(request, user_id):
    # Fetch only unread notifications for the user
    notifications = AdminMessage.objects.filter(user_id=user_id, read=False).select_related('application', 'document')
    
    notifications_data = []
    
    for notification in notifications:
        notifications_data.append({
            'notification_id': notification.id,
            'application_id': notification.application.id,
            'message': notification.message,
            'document_label': notification.document.label.label if notification.document else None,
            'sent_at': notification.sent_at,
            'is_reminder': notification.is_reminder,
            'ask_additional_document': notification.ask_additional_document,
            'additional_document_label': notification.additional_document_label,
        })
    
    return Response({'notifications': notifications_data}, status=200)

@api_view(['POST'])
def mark_notification_seen(request):
    notification_id = request.data.get('notification_id')
    
    try:
        notification = AdminMessage.objects.get(id=notification_id)
        # Here, you might want to set a field to mark it as seen (e.g., notification.read = True)
        notification.read = True
        notification.save()
        return Response({'message': 'Notification marked as seen'}, status=200)
    except AdminMessage.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=404)

# @api_view(['GET'])
# def application_statistics(request):
#     today = now().date()
#     start_of_year = today.replace(month=1, day=1)
#     start_of_month = today.replace(day=1)
#     seven_days_ago = today - timedelta(days=7)

#     # Aggregation for months
#     monthly_data = (
#         Application.objects
#         .filter(date_created__gte=start_of_year)
#         .annotate(month=TruncMonth('date_created'))
#         .values('month')
#         .annotate(
#             total=Count('id'),
#             success=Count('id', filter=Q(applicationstatus__status__in=['completed', 'approved'])),
#             rejected=Count('id', filter=Q(applicationstatus__status='rejected'))
#         )
#         .order_by('month')
#     )

#     # Aggregation for years
#     yearly_data = (
#         Application.objects
#         .annotate(year=TruncYear('date_created'))
#         .values('year')
#         .annotate(
#             total=Count('id'),
#             success=Count('id', filter=Q(applicationstatus__status__in=['completed', 'approved'])),
#             rejected=Count('id', filter=Q(applicationstatus__status='rejected'))
#         )
#         .order_by('year')
#     )

#     # Aggregation for last 7 days
#     last_seven_days_data = (
#         Application.objects
#         .filter(date_created__gte=seven_days_ago)
#         .annotate(day=TruncDay('date_created'))
#         .values('day')
#         .annotate(
#             total=Count('id'),
#             success=Count('id', filter=Q(applicationstatus__status__in=['completed', 'approved'])),
#             rejected=Count('id', filter=Q(applicationstatus__status='rejected'))
#         )
#         .order_by('day')
#     )

#     # Formatting the response for last 7 days
#     last_seven_days = [
#         {
#             'day': day_data['day'].strftime('%Y-%m-%d'),
#             'total': day_data['total'],
#             'success': day_data['success'],
#             'rejected': day_data['rejected']
#         }
#         for day_data in last_seven_days_data
#     ]

#     # Formatting the response for months
#     monthly_stats = [
#         {
#             'month': month_data['month'].strftime('%b'),  # Short month name
#             'total': month_data['total'],
#             'success': month_data['success'],
#             'rejected': month_data['rejected']
#         }
#         for month_data in monthly_data
#     ]

#     # Formatting the response for years
#     yearly_stats = [
#         {
#             'year': year_data['year'].year,  # Just the year number
#             'total': year_data['total'],
#             'success': year_data['success'],
#             'rejected': year_data['rejected']
#         }
#         for year_data in yearly_data
#     ]

#     # Return data in the required format
#     data = {
#         'last_7_days': last_seven_days,
#         'monthly': monthly_stats,
#         'yearly': yearly_stats
#     }

#     return Response(data)

@api_view(['GET'])
def application_statistics(request):
    # Get the 'days' parameter from the request query string, default to 7 if not provided
    days = int(request.query_params.get('days', 7))  # Default to last 7 days

    today = now().date()
    start_date = today - timedelta(days=days)  # Calculate the start date based on the 'days' input

    # Aggregation for the specified number of days
    filtered_data = (
        Application.objects
        .filter(date_created__gte=start_date)  # Filter applications starting from the calculated start date
        .annotate(day=TruncDay('date_created'))  # Truncate by day
        .values('day')
        .annotate(
            total=Count('id'),
            success=Count('id', filter=Q(applicationstatus__status__in=['completed', 'approved'])),
            rejected=Count('id', filter=Q(applicationstatus__status='rejected'))
        )
        .order_by('day')
    )

    # Formatting the response for React line chart
    statistics = [
        {
            'date': day_data['day'].strftime('%Y-%m-%d'),  # Format the date as 'YYYY-MM-DD'
            'total': day_data['total'],                   # Total applications
            'success': day_data['success'],               # Successful applications
            'rejected': day_data['rejected']              # Rejected applications
        }
        for day_data in filtered_data
    ]

    # Return the data for React chart mapping
    return Response(statistics)

@api_view(['GET'])
def approved_funding_last_5_months(request):
    # Get current date
    today = timezone.now()

    # Calculate the date for 5 months ago
    five_months_ago = today - timezone.timedelta(days=5*30)  # Approximation of 5 months

    # Filter FundingRequirements based on ApplicationStatus being 'approved' or 'Approved'
    # Also filter based on applications from the last 5 months
    data = (
        FundingRequirements.objects
        .filter(application__applicationstatus__status__iexact='approved', 
                application__date_created__gte=five_months_ago)
        .annotate(month=TruncMonth('application__date_created'))  # Group by month
        .values('month')
        .annotate(total_funding=Sum('amount_required'))  # Sum the amount_required
        .order_by('month')
    )

    # Prepare the response data
    response_data = {
        "months": [entry['month'].strftime("%B %Y") for entry in data],
        "total_funding": [entry['total_funding'] for entry in data]
    }

    return Response(response_data)

@api_view(['POST'])
def set_funding_and_pay_commission(request, application_id):
    # Step 1: Extract data from request
    commission_percentage = request.data.get('commission_percentage')
    commission_amount = request.data.get('commission_amount')

    if not commission_percentage or not commission_amount:
        return Response({"error": "Both commission_percentage and commission_amount are required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Convert to Decimal
        commission_percentage = Decimal(commission_percentage)
        commission_amount = Decimal(commission_amount)

        # Step 2: Use atomic transaction to ensure rollback in case of error
        with transaction.atomic():
            # Step 3: Get the Application and update the funding amount
            application = get_object_or_404(Application, id=application_id)
            application.funding_amount = commission_amount
            application.save()

            # Step 4: Handle the commission for the application
            commission, created = Commission.objects.get_or_create(application=application)
            commission.commission_percentage = commission_percentage
            commission.calculate_commission(funding_amount=commission_amount)

            # Step 5: Check if the user has a referral
            try:
                referral = Referral.objects.get(referee=application.user)
            except Referral.DoesNotExist:
                return Response({"error": "No referral found for this user."}, status=status.HTTP_400_BAD_REQUEST)

            # # Step 6: Update referral wallet balance
            # referral.update_wallet_balance(funding_amount=commission_amount)

            # # Step 7: Handle referral invitations
            # referral_invitation = ReferralInvitation.objects.filter(referee_email=application.user.email).first()
            # if referral_invitation:
            #     referral_invitation.update_earnings(funding_amount=commission_amount)
            #     referral_invitation.update_status('Application_Completed')

            # Step 6: Directly update referral wallet balance by adding the commission_amount
            referral.wallet_balance += commission_amount
            referral.save()

            # Step 7: Handle referral invitations
            referral_invitation = ReferralInvitation.objects.filter(referee_email=application.user.email).first()
            if referral_invitation:
                # Directly add the commission_amount to earned_from_referral
                referral_invitation.earned_from_referral += commission_amount
                referral_invitation.status = 'Application_Completed'
                referral_invitation.save()


            # Step 8: Return a success response
            return Response({"success": "Funding, commission, and referral updates completed successfully."}, status=status.HTTP_200_OK)

    except Exception as e:
        # Step 9: Rollback transaction if an error occurs
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
# # class DocumentUploadView(viewsets.ModelViewSet):
# #     queryset = DocumentUpload.objects.all()
# #     serializer_class = DocumentUploadSerializer

# class ApplicationStatusViewSet(viewsets.ModelViewSet):
#     queryset = ApplicationStatus.objects.all()
#     serializer_class = ApplicationStatusSerializer

#     @action(detail=False, methods=['get'])
#     def get_total_applications(self, request):
#         total_applications = self.queryset.count()
#         status_counts = self.queryset.values('status').annotate(count=models.Count('status'))
#         return Response({
#             'total_applications': total_applications,
#             'status_counts': status_counts
#         })

#     @action(detail=True, methods=['patch'])
#     def update_status(self, request, pk=None):
#         application_status = self.get_object()
#         status = request.data.get('status')
#         if status:
#             application_status.status = status
#             application_status.save()
#             return Response({'message': 'Status updated successfully'})
#         return Response({'error': 'Status not provided'}, status=status.HTTP_400_BAD_REQUEST)
    
# class DocumentStatusViewSet(viewsets.ModelViewSet):
#     queryset = DocumentStatus.objects.all()
#     serializer_class = DocumentStatusSerializer

#     @action(detail=True, methods=['patch'])
#     def accept_document(self, request, pk=None):
#         document_status = self.get_object()
#         document_status.status = 'accepted'
#         document_status.save()
#         return Response({'message': 'Document accepted successfully'})

#     @action(detail=True, methods=['patch'])
#     def reject_document(self, request, pk=None):
#         document_status = self.get_object()
#         remarks = request.data.get('remarks', 'Document rejected.')
#         document_status.status = 'rejected'
#         document_status.remarks = remarks
#         document_status.save()
#         return Response({'message': 'Document rejected successfully'})

#     @action(detail=True, methods=['patch'])
#     def request_reupload(self, request, pk=None):
#         document_status = self.get_object()
#         document_status.status = 'under_review'
#         document_status.save()
#         return Response({'message': 'Re-upload requested successfully'})

# class AdminMessageViewSet(viewsets.ModelViewSet):
#     queryset = AdminMessage.objects.all()
#     serializer_class = AdminMessageSerializer

#     @action(detail=False, methods=['post'])
#     def send_message(self, request):
#         application_id = request.data.get('application')
#         user_id = request.data.get('user')
#         message = request.data.get('message')
#         if application_id and user_id and message:
#             AdminMessage.objects.create(
#                 application_id=application_id,
#                 user_id=user_id,
#                 message=message
#             )
#             return Response({'message': 'Message sent successfully'})
#         return Response({'error': 'Invalid data'}, status=status.HTTP_400_BAD_REQUEST)

#     @action(detail=True, methods=['patch'])
#     def send_reminder(self, request, pk=None):
#         document_status = DocumentStatus.objects.get(document__user_id=pk)
#         if document_status.reminder_sent:
#             return Response({'error': 'Reminder already sent'}, status=status.HTTP_400_BAD_REQUEST)
#         # Simulate sending reminder (implement actual email sending here)
#         document_status.reminder_sent = True
#         document_status.save()
#         return Response({'message': 'Reminder sent successfully'})
    

# @api_view(['GET'])
# def get_user_applications_data(request):
#     try:
#         # Get all users
#         users = User.objects.all()

#         # Collect data for each user
#         user_data = []
#         for user in users:
#             contact_info = BasicContactInformation.objects.filter(user=user).first()
#             application_status = ApplicationStatus.objects.filter(user=user).first()
#             last_activity = ApplicationActivityLog.objects.filter(user=user).order_by('-timestamp').first()

#             # If there is no contact info, application status, or activity, skip the user
#             if not contact_info or not application_status:
#                 continue

#             user_data.append({
#                 "user_id": user.id,
#                 "full_name": contact_info.full_name,
#                 "email": user.email,
#                 "business_name": contact_info.business_name,
#                 "phone_number": contact_info.phone_number,
#                 "application_status": application_status.get_status_display(),
#                 "review_percentage": application_status.review_percentage,
#                 "last_activity": last_activity.activity if last_activity else "No activity yet",
#                 "last_activity_timestamp": last_activity.timestamp if last_activity else "N/A",
#             })

#         return Response({"data": user_data}, status=status.HTTP_200_OK)

#     except Exception as e:
#         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
