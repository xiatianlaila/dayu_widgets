"""A sidebar navigation widget."""

# Import third-party modules
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets

# Import local modules
from dayu_widgets import dayu_theme
from dayu_widgets.tool_button import MToolButton


class MSidebarNavigationItem(MToolButton):
    """MSidebarNavigationItem"""

    _text_spacing = 2

    def __init__(self, parent=None):
        super(MSidebarNavigationItem, self).__init__(parent=parent)
        self._dayu_text = ""
        self._collapsed = False
        self.setCheckable(True)
        self.setAutoRaise(False)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

    def set_dayu_text(self, value):
        """Set the navigation item text."""
        self._dayu_text = value or ""
        self.setText(self._dayu_text)

    def get_dayu_text(self):
        """Get the navigation item text."""
        return self._dayu_text

    def set_collapsed(self, value):
        """Set item display mode."""
        self._collapsed = value
        self.setProperty("dayu_collapsed", value)
        if value:
            self.setFixedWidth(self._dayu_size)
            self.setToolTip(self._dayu_text)
        else:
            self.setMinimumWidth(0)
            self.setMaximumWidth(16777215)
            self.setToolTip("")
        self.style().polish(self)
        self.update()

    def set_dayu_size(self, value):
        """
        Set the navigation item height.
        :param value: integer
        :return: None
        """
        self._dayu_size = value
        self.setFixedHeight(self._dayu_size)
        self.setIconSize(QtCore.QSize(self._dayu_size - 16, self._dayu_size - 16))
        if self._collapsed:
            self.setFixedWidth(self._dayu_size)
        self.style().polish(self)
        self.update()

    def paintEvent(self, event):
        """Paint icon at a fixed coordinate in all sidebar states."""
        option = QtWidgets.QStyleOption()
        option.initFrom(self)

        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, option, painter, self)

        icon_size = self.iconSize()
        icon_x = int((self._dayu_size - icon_size.width()) / 2.0)
        icon_y = int((self.height() - icon_size.height()) / 2.0)
        icon_rect = QtCore.QRect(icon_x, icon_y, icon_size.width(), icon_size.height())
        self.icon().paint(painter, icon_rect, QtCore.Qt.AlignCenter)

        if not self._collapsed and self._dayu_text:
            text_rect = QtCore.QRect(
                self._dayu_size + self._text_spacing,
                0,
                self.width() - self._dayu_size - self._text_spacing,
                self.height(),
            )
            painter.setPen(QtGui.QColor(dayu_theme.primary_text_color))
            painter.drawText(text_rect, QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft, self._dayu_text)
        painter.end()


class MSidebarNavigationToggle(MToolButton):
    """MSidebarNavigationToggle"""

    def __init__(self, parent=None):
        super(MSidebarNavigationToggle, self).__init__(parent=parent)
        self.setAutoRaise(False)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)

    def set_dayu_size(self, value):
        """
        Set the navigation toggle size.
        :param value: integer
        :return: None
        """
        self._dayu_size = value
        self.setFixedSize(QtCore.QSize(self._dayu_size, self._dayu_size))
        self.setIconSize(QtCore.QSize(self._dayu_size - 16, self._dayu_size - 16))
        self.style().polish(self)
        self.update()

    def paintEvent(self, event):
        """Paint icon at the same fixed coordinate as navigation items."""
        option = QtWidgets.QStyleOption()
        option.initFrom(self)

        painter = QtGui.QPainter(self)
        self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, option, painter, self)

        icon_size = self.iconSize()
        icon_x = int((self._dayu_size - icon_size.width()) / 2.0)
        icon_y = int((self.height() - icon_size.height()) / 2.0)
        icon_rect = QtCore.QRect(icon_x, icon_y, icon_size.width(), icon_size.height())
        self.icon().paint(painter, icon_rect, QtCore.Qt.AlignCenter)
        painter.end()


class MSidebarNavigation(QtWidgets.QWidget):
    """MSidebarNavigation"""

    sig_current_changed = QtCore.Signal(int)
    sig_collapsed_changed = QtCore.Signal(bool)

    def __init__(self, parent=None):
        super(MSidebarNavigation, self).__init__(parent=parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self._dayu_size = dayu_theme.large
        self._side_margin = 8
        self._expanded_width = 200
        self._collapsed_width = self._dayu_size + self._side_margin * 2
        self._custom_collapsed_width = False
        self._collapsed = False
        self._item_list = []
        self._bottom_item_list = []

        self._button_group = QtWidgets.QButtonGroup(self)
        self._button_group.setExclusive(True)
        self._button_group.idClicked.connect(self._slot_current_changed)

        self.toggle_button = MSidebarNavigationToggle(parent=self).icon_only().large().svg("left_line.svg")
        self.toggle_button.setObjectName("sidebar_toggle_button")
        self.toggle_button.clicked.connect(self.toggle_collapsed)

        self._main_layout = QtWidgets.QVBoxLayout()
        self._main_layout.setContentsMargins(self._side_margin, 8, self._side_margin, 8)
        self._main_layout.setSpacing(4)
        self._main_layout.addWidget(self.toggle_button, 0, QtCore.Qt.AlignLeft)
        self._main_layout.addSpacing(4)
        self._main_layout.addStretch()
        self.setLayout(self._main_layout)

        self.set_dayu_size(self._dayu_size)
        self.set_collapsed(self._collapsed)

    @QtCore.Slot()
    def toggle_collapsed(self):
        """Toggle collapsed state."""
        self.set_collapsed(not self.get_collapsed())

    @QtCore.Slot(int)
    def _slot_current_changed(self, value):
        self.sig_current_changed.emit(value)

    def add_item(self, data_dict, index=None):
        """Add a navigation item."""
        return self._add_item(data_dict, index=index)

    def add_bottom_item(self, data_dict, index=None):
        """Add a navigation item to the bottom."""
        return self._add_item(data_dict, index=index, bottom=True)

    def _add_item(self, data_dict, index=None, bottom=False):
        """Add a navigation item."""
        if isinstance(data_dict, str):
            data_dict = {"text": data_dict}
        elif isinstance(data_dict, QtGui.QIcon):
            data_dict = {"icon": data_dict}

        bottom = data_dict.get("bottom", bottom)
        button = MSidebarNavigationItem(parent=self)
        button.set_dayu_size(self._dayu_size)

        if data_dict.get("svg"):
            button.svg(data_dict.get("svg"))
        if data_dict.get("icon"):
            button.setIcon(data_dict.get("icon"))
        if data_dict.get("text"):
            button.set_dayu_text(data_dict.get("text"))
        if data_dict.get("data"):
            button.setProperty("data", data_dict.get("data"))
        if data_dict.get("tooltip"):
            button.setToolTip(data_dict.get("tooltip"))
        if data_dict.get("clicked"):
            button.clicked.connect(data_dict.get("clicked"))
        if data_dict.get("toggled"):
            button.toggled.connect(data_dict.get("toggled"))

        if index is None:
            index = len(self._item_list)
        self._button_group.addButton(button, index)
        self._item_list.append(button)
        if bottom:
            self._bottom_item_list.append(button)
            self._main_layout.addWidget(button)
        else:
            stretch_index = self._main_layout.count() - len(self._bottom_item_list) - 1
            self._main_layout.insertWidget(stretch_index, button)
        button.set_collapsed(self._collapsed)

        if data_dict.get("checked"):
            self.set_current_index(index)
        return button

    def add_item_list(self, item_list):
        """Add navigation items."""
        for index, data_dict in enumerate(item_list):
            self.add_item(data_dict, index)

    def items(self):
        """Return all navigation item widgets."""
        return self._item_list

    def set_current_index(self, value):
        """Set current checked item index."""
        button = self._button_group.button(value)
        if button:
            button.setChecked(True)
            self.sig_current_changed.emit(value)

    def get_current_index(self):
        """Get current checked item index."""
        return self._button_group.checkedId()

    def set_collapsed(self, value):
        """Set collapsed state."""
        value = bool(value)
        if value == self._collapsed and self.width() in (self._collapsed_width, self._expanded_width):
            return

        self._collapsed = value
        self.setProperty("dayu_collapsed", value)
        self.setFixedWidth(self._collapsed_width if value else self._expanded_width)
        self.toggle_button.svg("menu_line.svg" if value else "left_line.svg")

        for button in self._item_list:
            button.set_collapsed(value)
        self.toggle_button.setToolTip("Expand" if value else "Collapse")
        self.style().polish(self)
        self.sig_collapsed_changed.emit(value)

    def get_collapsed(self):
        """Get collapsed state."""
        return self._collapsed

    def set_dayu_size(self, value):
        """
        Set the navigation item size.
        :param value: integer
        :return: None
        """
        self._dayu_size = value
        if not self._custom_collapsed_width:
            self._collapsed_width = self._dayu_size + self._side_margin * 2
        self.toggle_button.set_dayu_size(value)
        for button in self._item_list:
            button.set_dayu_size(value)
            button.set_collapsed(self._collapsed)
        if self._collapsed:
            self.setFixedWidth(self._collapsed_width)
        self.style().polish(self)

    def get_dayu_size(self):
        """Get the navigation item size."""
        return self._dayu_size

    def set_expanded_width(self, value):
        """Set expanded width."""
        self._expanded_width = value
        if not self._collapsed:
            self.setFixedWidth(value)

    def get_expanded_width(self):
        """Get expanded width."""
        return self._expanded_width

    def set_collapsed_width(self, value):
        """Set collapsed width."""
        self._custom_collapsed_width = True
        self._collapsed_width = value
        if self._collapsed:
            self.setFixedWidth(value)

    def get_collapsed_width(self):
        """Get collapsed width."""
        return self._collapsed_width

    current_index = QtCore.Property(
        int,
        get_current_index,
        set_current_index,
        notify=sig_current_changed
    )
    collapsed = QtCore.Property(
        bool,
        get_collapsed,
        set_collapsed,
        notify=sig_collapsed_changed
    )
    dayu_size = QtCore.Property(int, get_dayu_size, set_dayu_size)
    expanded_width = QtCore.Property(int, get_expanded_width, set_expanded_width)
    collapsed_width = QtCore.Property(int, get_collapsed_width, set_collapsed_width)
