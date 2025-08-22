import msal
from django.conf import settings

def _authority():
    return f"https://login.microsoftonline.com/{settings.AZURE_TENANT_ID}"

def build_msal_app():
    return msal.ConfidentialClientApplication(
        client_id=settings.AZURE_CLIENT_ID,
        client_credential=settings.AZURE_CLIENT_SECRET,
        authority=_authority(),
    )

def auth_url(state: str):
    app = build_msal_app()
    return app.get_authorization_request_url(
        scopes=settings.AZURE_SCOPES,
        redirect_uri=settings.AZURE_REDIRECT_URI,
        state=state,
        prompt="select_account",
        response_mode="form_post",
    )

def acquire_token_by_auth_code(code: str):
    app = build_msal_app()
    return app.acquire_token_by_authorization_code(
        code=code,
        scopes=settings.AZURE_SCOPES,
        redirect_uri=settings.AZURE_REDIRECT_URI,
    )
