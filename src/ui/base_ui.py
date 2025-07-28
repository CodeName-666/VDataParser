
from PySide6.QtWidgets import QStackedWidget, QWidget, QVBoxLayout


class BaseUi(QWidget):
    """Common base class for all custom Qt widgets.

    Parameters
    ----------
    parent:
        Optional widget used as this widget's parent. Defaults to ``None``.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialise the base widget.

        Parameters
        ----------
        parent:
            Optional parent widget for correct Qt ownership handling.
        """
        super().__init__(parent)

    def setup_ui(self) -> None:
        """Create child widgets and layouts.

        Subclasses are expected to reimplement this method and
        populate themselves with the necessary child widgets.
        """
        pass

    def setup_signals(self) -> None:
        """Connect Qt signals to their slots.

        This method is a stub that can be overridden to connect the
        created widgets with their corresponding signal handlers.
        """
        pass

    def add_widget(self, parent_widget: QWidget, widgetClass):
        """Add ``widgetClass`` as a child of ``parent_widget``.

        Parameters
        ----------
        parent_widget:
            The widget that will act as the parent for the newly created widget.
        widgetClass:
            A class reference used to instantiate the widget.

        Returns
        -------
        QWidget
            The created child widget instance.
        """
        layout = parent_widget.layout()
        if layout is None:
            layout = QVBoxLayout(parent_widget)
            widget_to_add = widgetClass(self)
            layout.addWidget(widget_to_add)
            parent_widget.setLayout(layout)

        return widget_to_add
