from PySide6.QtCore import QEvent, QObject, QTimer
from PySide6.QtWidgets import QSplitter, QWidget


class _DetailSplitterConfigurator(QObject):
    """Конфігуратор стартової ширини detail-pane після реального показу splitter.
    Configures initial detail-pane width after the splitter is actually shown.
    """

    def __init__(
        self,
        splitter: QSplitter,
        detail_widget: QWidget,
        *,
        detail_fraction: float,
        detail_min_width: int,
        detail_max_width: int,
    ) -> None:
        super().__init__(splitter)
        self._splitter = splitter
        self._detail_widget = detail_widget
        self._detail_fraction = detail_fraction
        self._detail_min_width = detail_min_width
        self._detail_max_width = detail_max_width
        self._applied = False

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:  # type: ignore[override]
        if watched is self._splitter and event.type() in {QEvent.Type.Show, QEvent.Type.Resize} and not self._applied:
            QTimer.singleShot(0, self._apply_sizes)
        return super().eventFilter(watched, event)

    def _apply_sizes(self) -> None:
        if self._applied:
            return
        total_width = self._splitter.width()
        if total_width <= 0:
            return

        content_widget = getattr(self._detail_widget, "widget", lambda: None)()
        content_hint_width = content_widget.sizeHint().width() if content_widget is not None else self._detail_widget.sizeHint().width()
        preferred_width = max(int(total_width * self._detail_fraction), content_hint_width + 24)
        detail_width = min(self._detail_max_width, max(self._detail_min_width, preferred_width))
        self._splitter.setSizes([max(1, total_width - detail_width), detail_width])
        self._applied = True


def configure_detail_splitter(
    splitter: QSplitter,
    detail_widget: QWidget,
    *,
    detail_fraction: float = 0.33,
    detail_min_width: int = 360,
    detail_max_width: int = 560,
) -> None:
    """Налаштовує стартову ширину правої панелі деталей без ручного перетягування.
    Configures the initial width of the right details pane without manual dragging.
    """

    detail_widget.setMinimumWidth(detail_min_width)
    detail_widget.setMaximumWidth(detail_max_width)
    configurator = _DetailSplitterConfigurator(
        splitter,
        detail_widget,
        detail_fraction=detail_fraction,
        detail_min_width=detail_min_width,
        detail_max_width=detail_max_width,
    )
    splitter.installEventFilter(configurator)
    splitter.setProperty("_detail_splitter_configurator", configurator)
