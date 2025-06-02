# --- Version ---
__major__ = 0
__minor__ = 5 # Incremented version due to architecture change
__patch__ = 0
__version__ = f"{__major__}.{__minor__}.{__patch__}"


def get_version() -> str:
    """
    Gibt die aktuelle Version des Moduls zurück.
    
    Returns:
        str: Die aktuelle Version im Format 'major.minor.patch'.
    """
    return __version__