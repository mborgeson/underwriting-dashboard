"""
Error Monitoring Module

This module provides utilities for monitoring and reporting application errors.
It works with the error_handler module to provide a comprehensive error
management system.
"""

import logging
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from src.utils.error_handler import (
    error_registry, 
    ApplicationError, 
    ErrorSeverity,
    capture_errors,
    DatabaseError, 
    FileError
)
from src.config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)

class ErrorReport:
    """Class for generating error reports."""
    
    @staticmethod
    def generate_summary(
        since: Optional[datetime] = None,
        severity: Optional[ErrorSeverity] = None
    ) -> Dict[str, Any]:
        """
        Generate an error summary report.
        
        Args:
            since: Only include errors since this timestamp
            severity: Filter by error severity
            
        Returns:
            Dictionary with error summary
        """
        errors = error_registry.get_errors(severity=severity)
        
        if since:
            errors = [e for e in errors if e.timestamp >= since]
        
        if not errors:
            return {
                "total_errors": 0,
                "by_severity": {},
                "by_type": {},
                "recent_errors": []
            }
        
        # Count errors by severity
        by_severity = {}
        for severity_level in ErrorSeverity:
            count = len([e for e in errors if e.severity == severity_level])
            if count > 0:
                by_severity[severity_level.value] = count
        
        # Count errors by type
        by_type = {}
        for error in errors:
            error_type = type(error).__name__
            by_type[error_type] = by_type.get(error_type, 0) + 1
        
        # Get the most recent errors
        recent_errors = [e.to_dict() for e in errors[-10:]]
        
        return {
            "total_errors": len(errors),
            "by_severity": by_severity,
            "by_type": by_type,
            "recent_errors": recent_errors
        }
    
    @staticmethod
    def generate_html_report(
        since: Optional[datetime] = None,
        severity: Optional[ErrorSeverity] = None
    ) -> str:
        """
        Generate an HTML error report.
        
        Args:
            since: Only include errors since this timestamp
            severity: Filter by error severity
            
        Returns:
            HTML string with the error report
        """
        summary = ErrorReport.generate_summary(since, severity)
        
        # Start building HTML with timestamp
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #333; }}
                .error-count {{ font-size: 24px; font-weight: bold; }}
                .error-item {{ border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; }}
                .error-critical {{ border-left: 5px solid #ff0000; }}
                .error-error {{ border-left: 5px solid #ff6600; }}
                .error-warning {{ border-left: 5px solid #ffcc00; }}
                .error-info {{ border-left: 5px solid #66cc00; }}
                .summary-table {{ border-collapse: collapse; width: 100%; }}
                .summary-table th, .summary-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .summary-table th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>Underwriting Dashboard Error Report</h1>
            <p>Generated at: {timestamp_str}</p>
        """
        
        # Add summary section
        html += """
            <h2>Error Summary</h2>
            <p class="error-count">Total Errors: {total_errors}</p>
        """.format(total_errors=summary["total_errors"])
        
        # Add severity breakdown
        if summary["by_severity"]:
            html += """
            <h3>By Severity</h3>
            <table class="summary-table">
                <tr>
                    <th>Severity</th>
                    <th>Count</th>
                </tr>
            """
            
            for severity, count in summary["by_severity"].items():
                html += f"""
                <tr>
                    <td>{severity}</td>
                    <td>{count}</td>
                </tr>
                """
            
            html += "</table>"
        
        # Add type breakdown
        if summary["by_type"]:
            html += """
            <h3>By Error Type</h3>
            <table class="summary-table">
                <tr>
                    <th>Error Type</th>
                    <th>Count</th>
                </tr>
            """
            
            for error_type, count in summary["by_type"].items():
                html += f"""
                <tr>
                    <td>{error_type}</td>
                    <td>{count}</td>
                </tr>
                """
            
            html += "</table>"
        
        # Add recent errors
        if summary["recent_errors"]:
            html += "<h2>Recent Errors</h2>"
            
            for error in summary["recent_errors"]:
                severity_class = f"error-{error['severity'].lower()}"
                
                html += f"""
                <div class="error-item {severity_class}">
                    <h3>{error['severity']}: {error['message']}</h3>
                    <p><strong>Time:</strong> {error['timestamp']}</p>
                """
                
                if error['cause_type']:
                    html += f"<p><strong>Cause:</strong> {error['cause_type']}: {error['cause']}</p>"
                
                if error['details']:
                    html += "<p><strong>Details:</strong></p>"
                    html += "<pre>" + json.dumps(error['details'], indent=2) + "</pre>"
                
                if error['traceback']:
                    html += "<p><strong>Traceback:</strong></p>"
                    html += f"<pre>{error['traceback']}</pre>"
                
                html += "</div>"
        
        # Close HTML
        html += """
        </body>
        </html>
        """
        
        return html
    
    @staticmethod
    @capture_errors(error_type=FileError)
    def save_report_to_file(report_path: Path) -> bool:
        """
        Save an error report to a file.
        
        Args:
            report_path: Path to save the report
            
        Returns:
            True if successful, False otherwise
        """
        # Create directory if it doesn't exist
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate report for the last 24 hours
        since = datetime.now() - timedelta(days=1)
        html_report = ErrorReport.generate_html_report(since=since)
        
        # Save to file
        with open(report_path, 'w') as f:
            f.write(html_report)
        
        logger.info(f"Error report saved to {report_path}")
        return True

class EmailReporter:
    """Class for sending error reports via email."""
    
    @staticmethod
    @capture_errors()
    def send_error_report(
        recipients: List[str],
        subject: str = "Underwriting Dashboard Error Report",
        since: Optional[datetime] = None,
        severity_threshold: ErrorSeverity = ErrorSeverity.ERROR,
        smtp_server: Optional[str] = None,
        smtp_port: int = 587,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_address: Optional[str] = None
    ) -> bool:
        """
        Send an error report via email.
        
        Args:
            recipients: List of email addresses to send the report to
            subject: Email subject
            since: Only include errors since this timestamp
            severity_threshold: Only include errors with this severity or higher
            smtp_server: SMTP server address
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_address: Sender email address
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        if not recipients:
            logger.warning("No recipients specified for error report email")
            return False
        
        # Get email settings from config or parameters
        smtp_server = smtp_server or getattr(settings, 'smtp_server', None)
        smtp_port = smtp_port or getattr(settings, 'smtp_port', 587)
        smtp_user = smtp_user or getattr(settings, 'smtp_user', None)
        smtp_password = smtp_password or getattr(settings, 'smtp_password', None)
        from_address = from_address or getattr(settings, 'error_report_from', smtp_user)
        
        if not smtp_server or not from_address:
            logger.error("SMTP server or sender address not configured")
            return False
        
        # Generate the HTML report
        html_report = ErrorReport.generate_html_report(since, severity_threshold)
        
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = from_address
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        
        # Attach the HTML report
        msg.attach(MIMEText(html_report, 'html'))
        
        try:
            # Connect to the SMTP server
            smtp = smtplib.SMTP(smtp_server, smtp_port)
            smtp.ehlo()
            smtp.starttls()
            
            # Log in if credentials are provided
            if smtp_user and smtp_password:
                smtp.login(smtp_user, smtp_password)
            
            # Send the email
            smtp.sendmail(from_address, recipients, msg.as_string())
            smtp.quit()
            
            logger.info(f"Error report email sent to {', '.join(recipients)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send error report email: {str(e)}")
            return False

class ErrorMonitor:
    """Class for monitoring and managing application errors."""
    
    def __init__(self, notification_threshold: int = 5):
        """
        Initialize the error monitor.
        
        Args:
            notification_threshold: Number of errors required to trigger notification
        """
        self.notification_threshold = notification_threshold
        self.last_notification_time = None
        self.notification_cooldown = timedelta(hours=1)
    
    @capture_errors()
    def check_and_notify(
        self, 
        notification_callback: Optional[Callable] = None,
        check_period: timedelta = timedelta(hours=1),
        severity_threshold: ErrorSeverity = ErrorSeverity.ERROR
    ) -> bool:
        """
        Check for errors and notify if threshold is exceeded.
        
        Args:
            notification_callback: Function to call for notification
            check_period: Time period to check for errors
            severity_threshold: Minimum severity level to count
            
        Returns:
            True if notification was sent, False otherwise
        """
        # Get errors from the specified period
        since = datetime.now() - check_period
        errors = [e for e in error_registry.get_errors(severity=severity_threshold) 
                 if e.timestamp >= since]
        
        if len(errors) >= self.notification_threshold:
            # Check if we're within the cooldown period
            if (self.last_notification_time and 
                (datetime.now() - self.last_notification_time) < self.notification_cooldown):
                logger.info("Skipping notification due to cooldown period")
                return False
            
            # If no callback is provided, use the default email reporter
            if not notification_callback:
                recipients = getattr(settings, 'error_report_recipients', [])
                if recipients:
                    subject = f"ALERT: {len(errors)} errors detected in Underwriting Dashboard"
                    EmailReporter.send_error_report(
                        recipients=recipients,
                        subject=subject,
                        since=since,
                        severity_threshold=severity_threshold
                    )
            else:
                # Call the provided callback
                notification_callback(errors)
            
            self.last_notification_time = datetime.now()
            return True
            
        return False
    
    @staticmethod
    @capture_errors(error_type=DatabaseError)
    def analyze_database_errors() -> Dict[str, Any]:
        """
        Analyze database-related errors.
        
        Returns:
            Dictionary with analysis results
        """
        db_errors = [e for e in error_registry.get_errors() if isinstance(e, DatabaseError)]
        
        if not db_errors:
            return {"database_errors": 0}
        
        # Group errors by details or messages to find patterns
        error_patterns = {}
        for error in db_errors:
            key = error.message.split(":")[0]  # Use first part of message as key
            if key not in error_patterns:
                error_patterns[key] = 0
            error_patterns[key] += 1
        
        # Find the most common error patterns
        common_patterns = sorted(error_patterns.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "database_errors": len(db_errors),
            "common_patterns": common_patterns[:5],  # Top 5 patterns
            "recent_errors": [e.to_dict() for e in db_errors[-5:]]  # 5 most recent errors
        }
    
    @staticmethod
    @capture_errors(error_type=FileError)
    def analyze_file_errors() -> Dict[str, Any]:
        """
        Analyze file-related errors.
        
        Returns:
            Dictionary with analysis results
        """
        file_errors = [e for e in error_registry.get_errors() if isinstance(e, FileError)]
        
        if not file_errors:
            return {"file_errors": 0}
        
        # Group errors by file extension
        extension_counts = {}
        for error in file_errors:
            if 'file_path' in error.details:
                ext = Path(error.details['file_path']).suffix
                if ext not in extension_counts:
                    extension_counts[ext] = 0
                extension_counts[ext] += 1
        
        return {
            "file_errors": len(file_errors),
            "by_extension": extension_counts,
            "recent_errors": [e.to_dict() for e in file_errors[-5:]]
        }
    
    @staticmethod
    def generate_daily_report() -> bool:
        """
        Generate and save a daily error report.
        
        Returns:
            True if report was generated successfully, False otherwise
        """
        # Create report directory if it doesn't exist
        reports_dir = Path(settings.logs_dir) / "error_reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with date
        today = datetime.now().strftime("%Y-%m-%d")
        report_path = reports_dir / f"error_report_{today}.html"
        
        # Save report
        return ErrorReport.save_report_to_file(report_path)

# Global error monitor instance
error_monitor = ErrorMonitor()