from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QWidget

from osah.ui.qt.design.tokens import COLOR, RADIUS, SPACING


class SummaryStrip(QFrame):
    """Рядкова смуга з ключовими показниками для службових екранів.
    Single-line key metrics strip for operational screens.
    """

    def __init__(self, metrics: tuple[tuple[str, int, str], ...]) -> None:
        super().__init__()
        self.setObjectName("summaryStrip")
        self.setStyleSheet(
            f"""
            QFrame#summaryStrip {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 255, 255, 0.97),
                    stop:0.55 rgba(246, 249, 252, 0.98),
                    stop:1 rgba(239, 244, 249, 0.98));
                border: 1px solid #D9E2EC;
                border-radius: {RADIUS['xxl']}px;
            }}
            """
        )
        self._metric_labels: list[QLabel] = []
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(SPACING["lg"], SPACING["md"], SPACING["lg"], SPACING["md"])
        self._layout.setSpacing(SPACING["md"])
        self.set_metrics(metrics)

    # ###### СЕГМЕНТИ СМУГИ / STRIP SEGMENTS ######
    def set_metrics(self, metrics: tuple[tuple[str, int, str], ...]) -> None:
        """Перебудовує сегменти summary-strip.
        Rebuilds the summary-strip segments.
        """

        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._metric_labels.clear()

        for index, (title, value, color) in enumerate(metrics):
            segment, value_label = _build_metric_segment(title, value, color)
            self._layout.addWidget(segment, stretch=1)
            self._metric_labels.append(value_label)
            if index < len(metrics) - 1:
                self._layout.addWidget(_build_separator())

    # ###### ЗНАЧЕННЯ СМУГИ / STRIP VALUES ######
    def set_values(self, values: tuple[int, ...]) -> None:
        """Оновлює числові значення існуючих сегментів з анімацією count-up.
        Updates numeric values of existing segments with count-up animation.
        """
        from osah.ui.qt.components.animations.count_up import apply_count_up

        for label, new_value in zip(self._metric_labels, values):
            try:
                current_value = int(label.text())
            except (ValueError, AttributeError):
                current_value = 0
            if current_value != new_value:
                apply_count_up(label, current_value, new_value)
            else:
                label.setText(str(new_value))


def _build_metric_segment(title: str, value: int, color: str) -> tuple[QWidget, QLabel]:
    """Створює один сегмент рядкової смуги.
    Creates one row-strip segment.
    """

    container = QWidget()
    container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    layout = QHBoxLayout(container)
    layout.setContentsMargins(SPACING["sm"], 0, SPACING["sm"], 0)
    layout.setSpacing(SPACING["xs"])

    title_label = QLabel(title)
    title_label.setStyleSheet(
        f"color: {COLOR['text_secondary']}; font-size: 16px; font-weight: 800;"
    )
    dash_label = QLabel(" - ")
    dash_label.setStyleSheet(
        f"color: {COLOR['text_muted']}; font-size: 16px; font-weight: 700;"
    )
    value_label = QLabel(str(value))
    value_label.setStyleSheet(
        f"color: {color}; font-size: 22px; font-weight: 900;"
    )

    layout.addWidget(title_label)
    layout.addWidget(dash_label)
    layout.addWidget(value_label)
    return container, value_label


def _build_separator() -> QFrame:
    """Створює компактний вертикальний роздільник між сегментами.
    Creates a compact vertical separator between segments.
    """

    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.VLine)
    separator.setStyleSheet(f"color: {COLOR['divider']};")
    return separator
