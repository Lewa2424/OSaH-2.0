from pathlib import Path

from osah.domain.entities.service_reset_request import ServiceResetRequest

from osah.application.services.security.load_security_profile import load_security_profile


# ###### ПОБУДОВА ДАНИХ СЕРВІСНОГО СКИДАННЯ / ПОСТРОЕНИЕ ДАННЫХ СЕРВИСНОГО СБРОСА ######
def build_service_reset_request(database_path: Path) -> ServiceResetRequest:
    """Повертає installation ID і поточний номер сервісного запиту.
    Возвращает installation ID и текущий номер сервисного запроса.
    """

    security_profile = load_security_profile(database_path)
    return ServiceResetRequest(
        installation_id=security_profile.installation_id,
        request_counter=security_profile.service_request_counter,
    )
