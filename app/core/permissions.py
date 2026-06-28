from core.models import User


class DatasetFilter:
    """
    Filtra registros del dataset histórico según permisos de perfil.

    Regla: Perfil "Usuario" NO puede acceder a comunicaciones dirigidas a:
    - macro (case-insensitive)
    - macroestructura (case-insensitive)
    - líderes / lideres (case-insensitive)
    """

    RESTRICTED_SUBSTRINGS = ['macro', 'macroestructura', 'líderes', 'lideres']

    @classmethod
    def filter_by_profile(cls, user, dataset_records: list) -> list:
        """
        Filtra registros según perfil del usuario.

        Args:
            user: Instancia de User model
            dataset_records: Lista de diccionarios del dataset

        Returns:
            Lista filtrada de registros (excluye contenido restringido)

        Raises:
            ValueError: Si user no tiene perfil válido
        """
        if not user or not user.perfil:
            raise ValueError("Usuario sin perfil definido")

        if user.can_access_restricted_content():
            return dataset_records

        filtered = []
        for record in dataset_records:
            destinatario = (record.get('destinatario') or '').lower()
            is_restricted = any(
                substring in destinatario
                for substring in cls.RESTRICTED_SUBSTRINGS
            )
            if not is_restricted:
                filtered.append(record)

        return filtered

    @classmethod
    def is_record_restricted(cls, record: dict, user) -> bool:
        """
        Verifica si un registro específico está restringido para el usuario.

        Args:
            record: Diccionario con campo 'destinatario'
            user: Instancia de User model

        Returns:
            True si el registro está restringido para este usuario
        """
        if user.can_access_restricted_content():
            return False

        destinatario = (record.get('destinatario') or '').lower()
        return any(
            substring in destinatario
            for substring in cls.RESTRICTED_SUBSTRINGS
        )
