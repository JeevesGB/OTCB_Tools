import weakref
from PyQt6.QtGui import QColor
from PyQt6.QtCore import (
    QPropertyAnimation,
    QEasingCurve,
    QPoint,
    QParallelAnimationGroup,
    QObject,
)
from PyQt6.QtWidgets import (
    QGraphicsOpacityEffect,
    QGraphicsDropShadowEffect,
    QWidget,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QTextEdit,
    QPlainTextEdit,
)


class UIAnimator(QObject):
    """
    Attach this to your MainWindow after creation:
        self.animator = UIAnimator(self)
    """

    def __init__(self, main_window):
        super().__init__()
        self.main = weakref.ref(main_window)

        # Store animations to prevent garbage collection
        self._animations = []

        self._setup_tab_animation()
        self._setup_tree_fade()
        self._setup_focus_glow_recursive(main_window)

    # -------------------------------------------------
    # Utility: keep animation alive
    # -------------------------------------------------
    def _keep(self, animation):
        self._animations.append(animation)
        animation.finished.connect(lambda: self._animations.remove(animation))

    # -------------------------------------------------
    # TAB SLIDE + FADE
    # -------------------------------------------------
    def _setup_tab_animation(self):
        window = self.main()
        if not hasattr(window, "tabs"):
            return

        window.tabs.currentChanged.connect(self._animate_tab_change)

    def _animate_tab_change(self, index):
        window = self.main()
        tabs = window.tabs
        widget = tabs.widget(index)

        if not widget:
            return

        width = tabs.width()

        widget.move(width, 0)

        slide = QPropertyAnimation(widget, b"pos")
        slide.setDuration(220)
        slide.setStartValue(QPoint(width, 0))
        slide.setEndValue(QPoint(0, 0))
        slide.setEasingCurve(QEasingCurve.Type.OutCubic)

        fade_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(fade_effect)

        fade = QPropertyAnimation(fade_effect, b"opacity")
        fade.setDuration(220)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)

        group = QParallelAnimationGroup()
        group.addAnimation(slide)
        group.addAnimation(fade)

        group.start()
        self._keep(group)

    # -------------------------------------------------
    # TREE CLICK FADE
    # -------------------------------------------------
    def _setup_tree_fade(self):
        window = self.main()
        if hasattr(window, "tree"):
            window.tree.clicked.connect(self._animate_tree_click)

    def _animate_tree_click(self):
        window = self.main()
        tree = window.tree

        effect = QGraphicsOpacityEffect(tree)
        tree.setGraphicsEffect(effect)

        fade = QPropertyAnimation(effect, b"opacity")
        fade.setDuration(150)
        fade.setStartValue(0.7)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutQuad)

        fade.start()
        self._keep(fade)

    # -------------------------------------------------
    # FOCUS GLOW (only on input widgets)
    # -------------------------------------------------
    def _setup_focus_glow_recursive(self, root_widget):
        input_types = (
            QLineEdit,
            QSpinBox,
            QDoubleSpinBox,
            QComboBox,
            QTextEdit,
            QPlainTextEdit,
        )

        for child in root_widget.findChildren(input_types):
            self._install_focus_glow(child)

    def _install_focus_glow(self, widget):
        effect = QGraphicsDropShadowEffect(widget)
        effect.setBlurRadius(0)
        effect.setOffset(0)
        effect.setColor(QColor("#2f6feb"))

        widget.setGraphicsEffect(effect)

        glow = QPropertyAnimation(effect, b"blurRadius")
        glow.setDuration(180)
        glow.setEasingCurve(QEasingCurve.Type.OutCubic)

        original_focus_in = widget.focusInEvent
        original_focus_out = widget.focusOutEvent

        def focus_in(event):
            glow.setStartValue(effect.blurRadius())
            glow.setEndValue(18)
            glow.start()
            self._keep(glow)
            if original_focus_in:
                original_focus_in(event)

        def focus_out(event):
            glow.setStartValue(effect.blurRadius())
            glow.setEndValue(0)
            glow.start()
            self._keep(glow)
            if original_focus_out:
                original_focus_out(event)

        widget.focusInEvent = focus_in
        widget.focusOutEvent = focus_out

    # -------------------------------------------------
    # Public: Fade any widget
    # -------------------------------------------------
    def animate_content_fade(self, widget):
        effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(effect)

        fade = QPropertyAnimation(effect, b"opacity")
        fade.setDuration(250)
        fade.setStartValue(0.0)
        fade.setEndValue(1.0)
        fade.setEasingCurve(QEasingCurve.Type.OutCubic)

        fade.start()
        self._keep(fade)