"""
Enhanced Authentication Service with password reset, email verification, and login tracking.
"""
from typing import Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import secrets
import logging
from functools import wraps

from models import User, PasswordResetToken, LoginHistory, db
from repositories import UserRepository

logger = logging.getLogger(__name__)


class EnhancedAuthenticationService:
    """Enhanced authentication service with comprehensive features."""
    
    def __init__(self):
        self.user_repo = UserRepository()
        self.token_expiration_hours = 24
    
    # ==================== PASSWORD RESET ====================
    
    def generate_password_reset_token(self, email: str) -> Dict[str, Any]:
        """
        Generate a password reset token for user.
        Returns: {'success': bool, 'message': str, 'token': str (optional), 'user': User (optional)}
        """
        try:
            user = self.user_repo.find_by_email(email)
            
            if not user:
                # Don't reveal if email exists (security best practice)
                return {
                    'success': True,
                    'message': 'If an account exists with this email, a password reset link will be sent.'
                }
            
            if not user.is_active:
                return {
                    'success': False,
                    'message': 'This account has been deactivated. Please contact support.'
                }
            
            # Invalidate any existing tokens
            PasswordResetToken.query.filter_by(user_id=user.id, is_used=False).update({'is_used': True})
            db.session.commit()
            
            # Generate new token
            token = secrets.token_urlsafe(32)
            expires_at = datetime.now(timezone.utc) + timedelta(hours=self.token_expiration_hours)
            
            reset_token = PasswordResetToken(
                user_id=user.id,
                token=token,
                expires_at=expires_at
            )
            
            db.session.add(reset_token)
            db.session.commit()
            
            logger.info(f"Password reset token generated for user: {user.email}")
            
            return {
                'success': True,
                'message': 'Password reset link has been sent to your email',
                'token': token,
                'user': user,
                'expires_in_hours': self.token_expiration_hours
            }
        
        except Exception as e:
            logger.error(f"Error generating reset token: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def validate_reset_token(self, token: str) -> Dict[str, Any]:
        """
        Validate password reset token.
        Returns: {'success': bool, 'message': str, 'user': User (optional)}
        """
        try:
            reset_token = PasswordResetToken.query.filter_by(token=token).first()
            
            if not reset_token:
                return {'success': False, 'message': 'Invalid or expired token'}
            
            if not reset_token.is_valid():
                return {'success': False, 'message': 'Token has expired. Please request a new password reset.'}
            
            user = reset_token.user
            if not user or not user.is_active:
                return {'success': False, 'message': 'User account is invalid or inactive'}
            
            return {
                'success': True,
                'message': 'Token is valid',
                'user': user,
                'token': token
            }
        
        except Exception as e:
            logger.error(f"Error validating reset token: {str(e)}")
            return {'success': False, 'message': 'Error validating token'}
    
    def reset_password_with_token(self, token: str, new_password: str) -> Dict[str, Any]:
        """
        Reset user password using valid token.
        Returns: {'success': bool, 'message': str}
        """
        try:
            # Validate token
            validation = self.validate_reset_token(token)
            if not validation['success']:
                return validation
            
            user = validation['user']
            
            # Validate new password
            if len(new_password) < 6:
                return {'success': False, 'message': 'Password must be at least 6 characters'}
            
            # Update password
            user.set_password(new_password)
            
            # Mark token as used
            reset_token = PasswordResetToken.query.filter_by(token=token).first()
            reset_token.mark_as_used()
            
            db.session.commit()
            
            logger.info(f"Password reset successful for user: {user.email}")
            
            return {
                'success': True,
                'message': 'Password has been reset successfully. Please log in with your new password.',
                'user': user
            }
        
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error resetting password: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    # ==================== LOGIN TRACKING ====================
    
    def record_login_attempt(self, user_id: int, success: bool = True, 
                           ip_address: str = None, user_agent: str = None,
                           failure_reason: str = None) -> LoginHistory:
        """Record login attempt in history."""
        try:
            login_record = LoginHistory(
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                login_status='success' if success else 'failed',
                failure_reason=failure_reason
            )
            
            db.session.add(login_record)
            db.session.commit()
            
            logger.info(f"Login attempt recorded for user_id: {user_id}, status: {'success' if success else 'failed'}")
            
            return login_record
        
        except Exception as e:
            logger.error(f"Error recording login attempt: {str(e)}")
            return None
    
    def record_logout(self, user_id: int) -> bool:
        """Record logout for active session."""
        try:
            # Get the most recent login without logout
            login_record = LoginHistory.query.filter_by(
                user_id=user_id,
                login_status='success',
                logout_at=None
            ).order_by(LoginHistory.login_at.desc()).first()
            
            if login_record:
                login_record.end_session()
                logger.info(f"Logout recorded for user_id: {user_id}")
                return True
            
            return False
        
        except Exception as e:
            logger.error(f"Error recording logout: {str(e)}")
            return False
    
    def get_login_history(self, user_id: int, limit: int = 10) -> Dict[str, Any]:
        """Get recent login history for user."""
        try:
            history = LoginHistory.query.filter_by(user_id=user_id).order_by(
                LoginHistory.login_at.desc()
            ).limit(limit).all()
            
            return {
                'success': True,
                'history': [record.to_dict() for record in history],
                'count': len(history)
            }
        
        except Exception as e:
            logger.error(f"Error getting login history: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    # ==================== SESSION MANAGEMENT ====================
    
    def create_persistent_session(self, user_id: int) -> Dict[str, Any]:
        """Create persistent session data for 'remember me' functionality."""
        try:
            user = self.user_repo.find_by_id(user_id)
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            session_data = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'created_at': datetime.now(timezone.utc).isoformat()
            }
            
            return {'success': True, 'session_data': session_data}
        
        except Exception as e:
            logger.error(f"Error creating persistent session: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def validate_persistent_session(self, user_id: int) -> Dict[str, Any]:
        """Validate if persistent session is still valid."""
        try:
            user = self.user_repo.find_by_id(user_id)
            
            if not user:
                return {'success': False, 'message': 'User not found'}
            
            if not user.is_active:
                return {'success': False, 'message': 'User account is inactive'}
            
            return {'success': True, 'user': user}
        
        except Exception as e:
            logger.error(f"Error validating persistent session: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}


class EmailService:
    """Service for sending authentication-related emails."""
    
    def __init__(self):
        self.from_email = "noreply@fashionbrand.com"
    
    def send_password_reset_email(self, user: User, reset_token: str, 
                                  reset_link: str) -> Dict[str, Any]:
        """
        Send password reset email to user.
        In production, integrate with actual email service (SendGrid, AWS SES, etc.)
        """
        try:
            email_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Password Reset Request</h2>
                    <p>Hello {user.first_name or user.username},</p>
                    <p>We received a request to reset your password. Click the link below to proceed:</p>
                    <p>
                        <a href="{reset_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                            Reset Password
                        </a>
                    </p>
                    <p>Or copy and paste this link in your browser:</p>
                    <p style="word-break: break-all;">{reset_link}</p>
                    <p>This link will expire in 24 hours.</p>
                    <p>If you didn't request this, please ignore this email.</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        © 2024 FashionBrand. All rights reserved.
                    </p>
                </body>
            </html>
            """
            
            # TODO: Integrate with actual email service
            logger.info(f"Password reset email prepared for: {user.email}")
            
            return {
                'success': True,
                'message': 'Password reset email sent',
                'email_to': user.email,
                'subject': 'Password Reset Request - FashionBrand'
            }
        
        except Exception as e:
            logger.error(f"Error sending password reset email: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def send_login_notification_email(self, user: User, login_record: LoginHistory) -> Dict[str, Any]:
        """
        Send login notification email to user.
        Helps detect unauthorized access.
        """
        try:
            email_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>New Login to Your Account</h2>
                    <p>Hello {user.first_name or user.username},</p>
                    <p>We detected a new login to your FashionBrand account:</p>
                    <ul>
                        <li><strong>Time:</strong> {login_record.login_at}</li>
                        <li><strong>IP Address:</strong> {login_record.ip_address}</li>
                        <li><strong>Device:</strong> {login_record.device_info}</li>
                    </ul>
                    <p>If this wasn't you, please change your password immediately.</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        © 2024 FashionBrand. All rights reserved.
                    </p>
                </body>
            </html>
            """
            
            logger.info(f"Login notification email prepared for: {user.email}")
            
            return {
                'success': True,
                'message': 'Login notification email sent',
                'email_to': user.email
            }
        
        except Exception as e:
            logger.error(f"Error sending login notification: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}
    
    def send_password_changed_email(self, user: User) -> Dict[str, Any]:
        """Send confirmation email after password change."""
        try:
            email_content = f"""
            <html>
                <body style="font-family: Arial, sans-serif;">
                    <h2>Password Changed Successfully</h2>
                    <p>Hello {user.first_name or user.username},</p>
                    <p>Your password has been changed successfully.</p>
                    <p>If you didn't make this change, please contact our support team immediately.</p>
                    <hr>
                    <p style="color: #666; font-size: 12px;">
                        © 2024 FashionBrand. All rights reserved.
                    </p>
                </body>
            </html>
            """
            
            logger.info(f"Password change confirmation email prepared for: {user.email}")
            
            return {
                'success': True,
                'message': 'Password change confirmation email sent',
                'email_to': user.email
            }
        
        except Exception as e:
            logger.error(f"Error sending password change email: {str(e)}")
            return {'success': False, 'message': f'Error: {str(e)}'}


def get_client_info(request) -> Dict[str, str]:
    """Extract client information from Flask request."""
    try:
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        if ',' in ip_address:
            ip_address = ip_address.split(',')[0].strip()
        
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Parse device info from user agent (simplified)
        device_info = 'Unknown Device'
        if 'Mobile' in user_agent:
            device_info = 'Mobile'
        elif 'Tablet' in user_agent:
            device_info = 'Tablet'
        elif 'Windows' in user_agent:
            device_info = 'Windows PC'
        elif 'Mac' in user_agent:
            device_info = 'Mac'
        elif 'Linux' in user_agent:
            device_info = 'Linux'
        
        return {
            'ip_address': ip_address,
            'user_agent': user_agent,
            'device_info': device_info
        }
    
    except Exception as e:
        logger.error(f"Error parsing client info: {str(e)}")
        return {
            'ip_address': 'Unknown',
            'user_agent': 'Unknown',
            'device_info': 'Unknown'
        }
