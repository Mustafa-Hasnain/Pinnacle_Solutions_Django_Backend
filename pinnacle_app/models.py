from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.utils import timezone
from decimal import Decimal

# User Management Models
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=False)  # Email verification status
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    steps_completed = models.BooleanField(default=False)  # Track application steps completion

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

class VerificationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


# Application Models
class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # application_name = models.CharField(max_length=255)  # Optional identifier for the application
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    steps_completed = models.BooleanField(default=False)


class BasicContactInformation(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='basiccontactinformation')
    full_name = models.CharField(max_length=255)
    business_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=11)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

class BusinessDetails(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    business_type = models.CharField(max_length=255)
    industry_sector = models.CharField(max_length=255)
    business_start_date = models.DateField()
    number_of_employees = models.CharField(max_length=25)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

class FundingRequirements(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    finance_type = models.CharField(
        max_length=255,
        choices=[
            ('business_loan', 'Business Loan'),
            ('invoice_finance', 'Invoice Finance'),
            ('revolving_credit', 'Revolving Credit'),
            ('merchant_cash_advance', 'Merchant Cash Advance'),
            ('bridging_loan', 'Bridging Loan'),
            ('commercial_mortgage', 'Commercial Mortgage'),
            ('development_finance', 'Development Finance'),
            ('asset_finance', 'Asset Finance'),
            ('other', 'Other')
        ]
    )
    amount_required = models.DecimalField(max_digits=10, decimal_places=2)
    purpose = models.CharField(max_length=255)
    repayment_period = models.CharField(max_length=255)
    preferred_funding_timeline = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

class FinancialInformation(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    annual_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    net_profit = models.DecimalField(max_digits=10, decimal_places=2)
    outstanding_debt = models.DecimalField(max_digits=10, decimal_places=2)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

# Document Requirements Models
class DocumentLabel(models.Model):
    finance_type = models.CharField(max_length=255, null=True)
    label = models.CharField(max_length=255)  # e.g., "6 Months Bank Statements", "ID"
    required = models.BooleanField(default=True)

class DocumentUpload(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    label = models.ForeignKey(DocumentLabel, on_delete=models.CASCADE)
    file = models.FileField(upload_to='documents/')
    
    # Add new 'reminder_pending' status
    status = models.CharField(
        max_length=20,
        choices=[('under_review', 'Under Review'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('reminder_pending', 'Reminder Pending')],
        default='under_review'
    )
    remarks = models.TextField(blank=True, null=True)
    reminder_sent = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('application','file', 'label')

    def send_reminder(self):
        # Update document status to 'reminder_pending'
        self.status = 'reminder_pending'
        self.reminder_sent = True
        self.save()

    def mark_asked_for_upload_again(self):
        # Handle asking for additional documents logic
        self.status = 'reminder_pending'
        self.save()


# Status Models
class ApplicationStatus(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=[
            ('submitted', 'Submitted'),
            ('in_progress', 'In Progress'),
            ('under_review', 'Under Review'),
            ('completed', 'Completed'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected')
        ],
        default='in_progress'
    )
    review_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    last_updated = models.DateTimeField(auto_now=True)

# Activity & Messaging Models
class ApplicationActivityLog(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity = models.CharField(max_length=255)  # E.g., "Application submitted", "Document rejected"
    timestamp = models.DateTimeField(auto_now_add=True)

class AdminMessage(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    
    # New fields to handle specific document reminders or additional document requests
    is_reminder = models.BooleanField(default=False)  # Flag for document reminder messages
    document = models.ForeignKey(DocumentUpload, null=True, blank=True, on_delete=models.SET_NULL)  # Document for which reminder is sent
    
    # Additional document request related fields
    ask_additional_document = models.BooleanField(default=False)
    additional_document_label = models.CharField(max_length=255, blank=True, null=True)  # Name of additional document being requested

    def send_reminder_message(self, document):
        """Method to send reminder about a specific document."""
        self.is_reminder = True
        self.document = document
        self.message = f"Reminder to submit document: {document.label.label}"
        self.save()
        document.send_reminder()

    def ask_for_additional_document(self, document_name):
        """Method to ask for an additional document."""
        self.ask_additional_document = True
        self.additional_document_label = document_name
        self.message = f"Please provide additional document: {document_name}"
        self.save()


class Commission(models.Model):
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    def calculate_commission(self, funding_amount):
        """
        Calculate the commission based on the funding amount and percentage.
        """
        self.commission_amount = funding_amount * (self.commission_percentage / 100)
        self.save()
        return self.commission_amount


# Status Choices for Referral Invitations
class InvitationStatus(models.TextChoices):
    INVITATION_SENT = 'Invitation_Sent', 'Invitation Sent'
    INVITATION_ACCEPTED = 'Invitation_Accepted', 'Invitation Accepted'
    APPLICATION_COMPLETED = 'Application_Completed', 'Application Completed'
    APPLICATION_REJECTED = 'Application_Rejected', 'Application Rejected'


# Referral Invitation Model
class ReferralInvitation(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    # Optional referee, null until invitation is accepted
    referee_email = models.EmailField()
    referee = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='referrals_received', null=True, blank=True)
    
    # Invitation status and timestamp
    status = models.CharField(
        max_length=30,
        choices=InvitationStatus.choices,
        default=InvitationStatus.INVITATION_SENT
    )
    date_sent = models.DateTimeField(auto_now_add=True)
    date_accepted = models.DateTimeField(null=True, blank=True)
    date_completed = models.DateTimeField(null=True, blank=True)
    date_rejected = models.DateTimeField(null=True, blank=True)

    # Earned amounts from referrals
    referral_reward_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    earned_from_referral = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def update_status(self, new_status):
        self.status = new_status
        if new_status == InvitationStatus.INVITATION_ACCEPTED:
            self.date_accepted = timezone.now()  # Set to current time
        elif new_status == InvitationStatus.APPLICATION_COMPLETED:
            self.date_completed = timezone.now()  # Set to current time
        elif new_status == InvitationStatus.APPLICATION_REJECTED:
            self.date_rejected = timezone.now()  # Set to current time
        self.save()

    def update_earnings(self, funding_amount):
        """
        Update earned_from_referral based on a successful funding from the referee.
        """
        self.earned_from_referral += funding_amount * (self.referral_reward_percentage / 100)
        self.save()

    def __str__(self):
        return f"Referral invite from {self.referrer.email} to {self.referee_email}"


# Extending Referral Model to Track Earning through Referrals
class Referral(models.Model):
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referral')
    referee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='referee', null=True)
    
    referral_code = models.CharField(max_length=64)
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    referral_reward_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    def update_wallet_balance(self, funding_amount):
        self.wallet_balance += funding_amount * (self.referral_reward_percentage / 100)
        self.save()

    def __str__(self):
        return f"Referral from {self.referrer} for {self.referee}"