from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter

# router = DefaultRouter()
# router.register('documents', views.DocumentUpload, basename='documents')


urlpatterns = [
    path('applications/<int:application_id>/basic-contact/', views.basic_contact_information_view),
    path('applications/<int:application_id>/business-details/', views.business_details_view),
    path('applications/<int:application_id>/financial-information/', views.financial_information_view),
    path('applications/<int:application_id>/funding-requirements/', views.funding_requirements_view),
    path('applications/<int:application_id>/', views.application_view),
    path('applications/<int:application_id>/documents/', views.document_upload_view),
    path('applications/<int:application_id>/additional-documents/', views.additional_document_upload_view),
    path('application/<int:application_id>/status/', views.update_application_status, name='update_application_status'),
    path('applications/<int:application_id>/set-funding-and-pay-commission/', views.set_funding_and_pay_commission, name='set-funding-and-pay-commission'),
    path('document/<int:document_id>/update/', views.update_document_upload, name='update_document_upload'),
    path('create_application/', views.create_application, name='create_application'),
    path('delete_application/<int:application_id>/', views.delete_application, name='delete_application'),
    path('admin-message/send/', views.send_admin_message, name='send_admin_message'),
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('verify-email/<str:token>/', views.VerifyEmailView.as_view(), name='verify-email'),
    path('login/', views.login_user, name='login_user'),
    path('resend-verification-email/', views.resend_verification_email, name='resend-verification-email'),
    path('applications/get-labels/<int:application_id>/', views.get_labels_of_financeType, name='get_labels_of_financeType'),
    path('documents/get-fiance-labels/<str:finance_type>/', views.get_financeType_labels, name='get_financeType_labels'),
    path('update-steps-completed/', views.update_steps_completed, name='update-steps-completed'),
    path('application-counts/', views.get_application_counts, name='application-counts'),
    path('application-graph-data/', views.get_application_graph_data, name='application-graph-data'),
    path('latest-5-users/', views.get_latest_5_users, name='latest-5-users'),
    path('get_clients/', views.get_clients, name='get_clients'),
    path('get_all_applications/', views.get_all_applications, name='get_all_applications'),
    path('admin_applications/<int:application_id>/', views.admin_application_view),
    path('user/dashboard/<int:user_id>/', views.get_user_application_details, name='user-application-details'),
    path('user/myapplications/<int:user_id>/', views.get_user_dashboard_data, name='user_my_applications'),
    # path('new_application/create/<int:user_id>/', views.ApplicationCreateView.as_view(), name='new-application'),
    path('new_application/create/<int:user_id>/', views.new_application, name='new-application'),
    path('new_application/upload_files/<int:application_id>/', views.upload_files, name='new-application_upload_files'),
    path('referral-summary/<int:user_id>/', views.get_referral_summary, name='referral-summary'),
    path('send-referral-invites/<int:user_id>/', views.send_referral_invites, name='send-referral-invites'),
    path('send-invitation/', views.send_invitation, name='send_invitation'),
    path('notifications/<int:user_id>/', views.get_notifications, name='get_notifications'),
    path('notifications/mark_seen/', views.mark_notification_seen, name='mark_notification_seen'),
    path('application-statistics/', views.application_statistics, name='application_statistics'),










    # path('basic-contact-info/', views.BasicContactInformationView.as_view(), name='basic_contact_info'),  
    # path('basic-contact-info/<int:user_id>/', views.BasicContactInformationView.as_view(), name='basic_contact_info_with_id'), 
    # path('business-details/', views.BusinessDetailsView.as_view(), name='business-details'),
    # path('business-details/<int:user_id>/', views.BusinessDetailsView.as_view(), name='business-details-user'),   
    # path('funding-requirements/', views.FundingRequirementsView.as_view(), name='funding-requirements'),
    # path('funding-requirements/<int:user_id>/', views.FundingRequirementsView.as_view(), name='funding-requirements-user'),  
    # path('financial-information/', views.FinancialInformationView.as_view(), name='financial-information'),
    # path('financial-information/<int:user_id>/', views.FinancialInformationView.as_view(), name='financial-information-user'),
    # path('document-upload/', views.DocumentUploadView.as_view(), name='document-upload'),
    # path('document-upload/<int:user_id>/', views.DocumentUploadView.as_view(), name='document-upload-user'),
    # path('user-data/<int:user_id>/', views.UserProfileDataView.as_view(), name='user-data'),
    # path('applications/total/', views.ApplicationStatusViewSet.as_view({'get': 'get_total_applications'}), name='get-total-applications'),
    # path('applications/<int:pk>/update-status/', views.ApplicationStatusViewSet.as_view({'patch': 'update_status'}), name='update-application-status'),
    # path('documents/<int:pk>/accept/', views.DocumentStatusViewSet.as_view({'patch': 'accept_document'}), name='accept-document'),
    # path('documents/<int:pk>/reject/', views.DocumentStatusViewSet.as_view({'patch': 'reject_document'}), name='reject-document'),
    # path('documents/<int:pk>/request-reupload/', views.DocumentStatusViewSet.as_view({'patch': 'request_reupload'}), name='request-reupload'),
    # path('messages/send/', views.AdminMessageViewSet.as_view({'post': 'send_message'}), name='send-message'),
    # path('messages/<int:pk>/send-reminder/', views.AdminMessageViewSet.as_view({'patch': 'send_reminder'}), name='send-reminder'),
    # path('user-applications/', views.get_user_applications_data, name='user-applications'),

]
