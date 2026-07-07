# Import third-party modules
from qtpy import QtWidgets

# Import local modules
from dayu_widgets.label import MLabel
from dayu_widgets.sidebar_navigation import MSidebarNavigation


class SidebarNavigationExample(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(SidebarNavigationExample, self).__init__(parent)
        self.setWindowTitle("Examples for MSidebarNavigation")
        self._init_ui()

    def _init_ui(self):
        self.stacked_widget = QtWidgets.QStackedWidget()
        self.stacked_widget.addWidget(MLabel("Application").h2())
        self.stacked_widget.addWidget(MLabel("Projects").h2())
        self.stacked_widget.addWidget(MLabel("Assets").h2())
        self.stacked_widget.addWidget(MLabel("Settings").h2())

        side_bar = MSidebarNavigation()
        side_bar.add_item_list(
            [
                {"text": "Application", "svg": "application_line.svg", "checked": True},
                {"text": "Projects", "svg": "folder_line.svg"},
                {"text": "Assets", "svg": "media_line.svg"},
                {"text": "Settings", "svg": "setting_line.svg", "bottom": True},
            ]
        )
        side_bar.sig_current_changed.connect(self.stacked_widget.setCurrentIndex)

        main_lay = QtWidgets.QHBoxLayout()
        main_lay.setContentsMargins(0, 0, 0, 0)
        main_lay.setSpacing(0)
        main_lay.addWidget(side_bar)
        main_lay.addWidget(self.stacked_widget)
        self.setLayout(main_lay)
        self.resize(640, 360)


if __name__ == "__main__":
    # Import local modules
    from dayu_widgets import dayu_theme
    from dayu_widgets.qt import application

    with application() as app:
        test = SidebarNavigationExample()
        dayu_theme.apply(test)
        test.show()
