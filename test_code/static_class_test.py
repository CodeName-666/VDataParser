class Base:
    base_param: str = "base_param"          # Klassenattribut

    def __init__(self, param: str | None = None):
        if param is not None:
            Base.base_param = param         # <-- auf die Klasse schreiben
            # alternativ: type(self).base_param = param
            # so gilt es auch in späteren Subklassen


class Derived(Base):
    def __init__(self, param: str | None = None):
        super().__init__(param)             # übergebenen Wert ggf. weiterreichen
        print(self.base_param)              # liest Klassenattribut


if __name__ == "__main__":
    b = Base("base_param_value")            # setzt Klassenattribut
    derived_instance = Derived()            # liest denselben Wert
    print(derived_instance.base_param)      # -> base_param_value