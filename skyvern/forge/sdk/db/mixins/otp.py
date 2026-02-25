"""Mixin for OTP-related database operations.

Handles OTP/TOTP code creation and retrieval.
Accesses shared state via the AgentDB instance (self.Session(), self.debug_enabled).

Methods to be migrated here:
    - get_otp_codes
    - get_otp_codes_by_run
    - get_recent_otp_codes
    - create_otp_code
"""


class OTPMixin:
    """Mixin for OTP-related database operations.

    Handles OTP/TOTP code creation and retrieval.
    """
