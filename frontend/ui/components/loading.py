from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QTimer


class LoadingOverlay(QWidget):
    """
    Полупрозрачный оверлей поверх контейнера с простой текстовой
    «анимацией» Загрузка..., чтобы показывать фоновые операции.
    """

    def __init__(self, parent: QWidget | None = None, text: str = "Загрузка"):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setObjectName("LoadingOverlay")
        self._base_text = text
        self._dots = 0

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(self._base_text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("LoadingLabel")
        layout.addWidget(self.label)

        self.timer = QTimer(self)
        self.timer.setInterval(400)
        self.timer.timeout.connect(self._update_text)

        self.hide()

    def _update_text(self) -> None:
        self._dots = (self._dots + 1) % 4
        self.label.setText(self._base_text + "." * self._dots)

    def resizeEvent(self, event):  # noqa: N802
        # Растягиваем оверлей на весь родительский виджет
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().resizeEvent(event)

    def showEvent(self, event):  # noqa: N802
        self.timer.start()
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().showEvent(event)

    def hideEvent(self, event):  # noqa: N802
        self.timer.stop()
        super().hideEvent(event)


