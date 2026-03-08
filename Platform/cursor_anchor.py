from AppKit import NSWorkspace
from Quartz import (
    AXUIElementCreateSystemWide,
    AXUIElementCopyAttributeValue,
    kAXFocusedUIElementAttribute,
    kAXSelectedTextRangeAttribute,
)

class MacOSCursor:

    def get_position(self):

        system = AXUIElementCreateSystemWide()

        element = AXUIElementCopyAttributeValue(
            system,
            kAXFocusedUIElementAttribute,
            None
        )

        if element:

            pos = AXUIElementCopyAttributeValue(
                element,
                "AXPosition",
                None
            )

            if pos:
                return pos

        return (0, 0)