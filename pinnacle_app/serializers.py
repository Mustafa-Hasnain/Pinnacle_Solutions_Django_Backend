from rest_framework import serializers
from .models import (User, BasicContactInformation, BusinessDetails, FundingRequirements, FinancialInformation, 
                     DocumentUpload, ApplicationStatus, ApplicationActivityLog, AdminMessage, Referral, Application, Commission)
from django.utils.crypto import get_random_string
import os
from django.utils.text import slugify
from .models import DocumentUpload, DocumentLabel
from decimal import Decimal


class CommissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commission
        fields = ['application', 'commission_percentage', 'commission_amount']


class UserSerializer(serializers.ModelSerializer):
    referral_code = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'referral_code', 'is_active','is_superAdmin','is_admin','steps_completed','profile_picture','admin_name','last_login','last_location', 'last_location_ip']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()

        # Generate and assign referral code for this user (referrer)
        referral_code = get_random_string(10).upper()
        Referral.objects.create(referrer=user, referral_code=referral_code)

        # Create a new application
        application = Application.objects.create(user=user)

        # Create an application status with default values
        ApplicationStatus.objects.create(
            application=application,
            status='in_progress',  
            review_percentage=Decimal('0.00')
        )

        # Log user creation activity
        ApplicationActivityLog.objects.create(
            application=application,
            user=user,
            activity=f"User created with referral code {referral_code}"
        )
        
        return user

    def get_referral_code(self, obj):
        referral = Referral.objects.filter(referrer=obj).first()
        return referral.referral_code if referral else None
    
    # def to_representation(self, instance):
    #     # Override to_representation to include password (decrypted format)
    #     data = super().to_representation(instance)
    #     # Get password from instance
    #     data['password'] = instance.password  # You can directly access the password if required
    #     return data


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentUpload
        fields = ['id', 'application', 'label', 'file', 'status', 'remarks']

    def create(self, validated_data):
        document = validated_data['file']
        file_name, file_extension = os.path.splitext(document.name)
        document_name = slugify(file_name)

        # Ensure the document name is unique by adding a number if it already exists
        similar_files = DocumentUpload.objects.filter(file__icontains=document_name).count()
        if similar_files:
            document.name = f"{document_name} ({similar_files + 1}){file_extension}"
        else:
            document.name = f"{document_name}{file_extension}"

        # Create the document upload instance
        instance = super().create(validated_data)

        # Log the document upload activity
        ApplicationActivityLog.objects.create(
            application=instance.application,
            user=instance.application.user,
            activity=f"Document uploaded: {instance.label.label} with name {instance.file.name}"
        )
        return instance

    
    def update(self, instance, validated_data):
        old_status = instance.status
        instance = super().update(instance, validated_data)

        # Log document upload status changes
        if old_status != instance.status:
            ApplicationActivityLog.objects.create(
                application=instance.application,
                user=instance.application.user,
                activity=f"Document {instance.label.label} status changed from {old_status} to {instance.status}"
            )

        return instance

class ApplicationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationStatus
        fields = ['application', 'status', 'review_percentage', 'last_updated']

    def update(self, instance, validated_data):
        old_status = instance.status
        instance = super().update(instance, validated_data)

        # Update review percentage based on status
        status_to_percentage = {
            'submitted': 50,
            'in_progress': 20,
            'under_review': 70,
            'completed': 100,
            'approved': 100,
            'rejected': 0,
        }
        instance.review_percentage = status_to_percentage.get(instance.status, 0)
        instance.save()

        # Log status changes
        if old_status != instance.status:
            ApplicationActivityLog.objects.create(
                application=instance.application,
                user=instance.application.user,
                activity=f"Application status changed from {old_status} to {instance.status}"
            )

        return instance


class BasicContactInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicContactInformation
        fields = '__all__'

    def create(self, validated_data):
        instance = super().create(validated_data)

        # Log activity
        ApplicationActivityLog.objects.create(
            application=instance.application,
            user=instance.application.user,
            activity=f"Basic contact information created for application {instance.application.id}"
        )
        return instance

class BusinessDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessDetails
        fields = '__all__'

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        # Log activity
        ApplicationActivityLog.objects.create(
            application=instance.application,
            user=instance.application.user,
            activity=f"Business details updated for application {instance.application.id}"
        )
        return instance

class FinancialInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialInformation
        fields = '__all__'

    def create(self, validated_data):
        instance = super().create(validated_data)

        # Log activity
        ApplicationActivityLog.objects.create(
            application=instance.application,
            user=instance.application.user,
            activity=f"Financial information created for application {instance.application.id}"
        )
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        # Log activity
        ApplicationActivityLog.objects.create(
            application=instance.application,
            user=instance.application.user,
            activity=f"Financial information updated for application {instance.application.id}"
        )
        return instance

class FundingRequirementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundingRequirements
        fields = '__all__'

    def create(self, validated_data):
        instance = super().create(validated_data)

        # Log activity
        ApplicationActivityLog.objects.create(
            application=instance.application,
            user=instance.application.user,
            activity=f"Funding requirements created for application {instance.application.id}"
        )
        return instance

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)

        # Log activity
        ApplicationActivityLog.objects.create(
            application=instance.application,
            user=instance.application.user,
            activity=f"Funding requirements updated for application {instance.application.id}"
        )
        return instance

# Similarly for other models like FundingRequirements, FinancialInformation

class AdminMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminMessage
        fields = [
            'application', 'user', 'message', 'is_reminder', 'document', 
            'ask_additional_document', 'additional_document_label', 
            'sent_at', 'read'
        ]

    def validate(self, data):
        """
        Ensure proper validation based on the type of message being sent.
        """
        if data.get('is_reminder') and not data.get('document'):
            raise serializers.ValidationError("A document must be provided when sending a reminder.")

        if data.get('ask_additional_document') and not data.get('additional_document_label'):
            raise serializers.ValidationError("Document name must be provided when asking for additional documents.")

        return data

    def create(self, validated_data):
        # Create the admin message
        instance = super().create(validated_data)

        # Process based on the message type
        if instance.is_reminder and instance.document:
            # Send a reminder and update the document status
            instance.send_reminder_message(instance.document)

        elif instance.ask_additional_document and instance.additional_document_label:
            # Ask for additional documents
            instance.ask_for_additional_document(instance.additional_document_label)

        # Log the admin message activity
        ApplicationActivityLog.objects.create(
            application=instance.application,
            user=instance.user,
            activity=f"Admin message sent: {instance.message}"
        )

        return instance

    
class ApplicationSerializer(serializers.ModelSerializer):
    commission = CommissionSerializer()

    class Meta:
        model = Application
        fields = '__all__'

    def create(self, validated_data):
        instance = super().create(validated_data)

        # Log application creation
        ApplicationActivityLog.objects.create(
            application=instance,
            user=instance.user,
            activity=f"Application created: {instance.application_name}"
        )
        ApplicationStatus.objects.create(
            application=instance,
            status='in_progress',  # Default status
            review_percentage=Decimal('20.00')  # Default review percentage
        )

         # Create a Commission instance tied to this application with default values
        Commission.objects.create(
            application=instance,
            commission_percentage=Decimal('0.00')  # Default commission percentage, adjust as needed
        )

        return instance

    def update(self, instance, validated_data):
        funding_amount = validated_data.get('funding_amount', instance.funding_amount)
        instance.funding_amount = funding_amount
        instance.save()

        # Calculate commission for the application
        if instance.commission:
            instance.commission.calculate_commission(funding_amount)

        # Update referral wallet if there's a referral
        referral = Referral.objects.filter(referee=instance.user).first()
        if referral:
            referral.update_wallet_balance(funding_amount)


        instance = super().update(instance, validated_data)

        # Log application updates
        ApplicationActivityLog.objects.create(
            application=instance,
            user=instance.user,
            activity=f"Application updated: {instance.application_name}"
        )
        return instance

class ReferralSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = ['referrer', 'referee', 'referral_code', 'progress_percentage', 'referral_reward_percentage', 'wallet_balance']

    def update_wallet_balance(self, instance, funding_amount):
        # Update wallet balance based on the reward percentage
        instance.wallet_balance += funding_amount * (instance.referral_reward_percentage / 100)
        instance.save()

        # Log wallet balance update
        ApplicationActivityLog.objects.create(
            application=instance.referee.application_set.first(),  # Assuming one application per user for simplicity
            user=instance.referrer,
            activity=f"Wallet balance updated. New balance: {instance.wallet_balance}"
        )
        return instance

    
class DocumentLabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentLabel
        fields = '__all__'

class ReferralUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Referral
        fields = ['referral_code', 'progress_percentage', 'wallet_balance']

    def update(self, instance, validated_data):
        instance = super().update(validated_data)

        # Log referral progress updates
        ApplicationActivityLog.objects.create(
            application=instance.referee.application_set.first(),
            user=instance.referrer,
            activity=f"Referral progress updated to {instance.progress_percentage}% for referral code {instance.referral_code}"
        )
        return instance
    
class ApplicationActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model:ApplicationActivityLog
        fields = '__all__'


class ApplicationSerializer(serializers.ModelSerializer):
    basic_contact_information = BasicContactInformationSerializer()
    business_details = BusinessDetailsSerializer()
    funding_requirements = FundingRequirementsSerializer()
    financial_information = FinancialInformationSerializer()
    documents = DocumentUploadSerializer(many=True, write_only=True)

    class Meta:
        model = Application
        fields = ['basic_contact_information', 'business_details', 'funding_requirements', 'financial_information', 'documents']