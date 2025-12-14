from marsclock.view.absview import AbsView
from marsclock.hardware.wifi import settings



class SettingsView(AbsView):
    def __init__(self, hardware):
        super().__init__(hardware)
        self.ap_server = settings.SettingsApServer()
    
    def action(self):
        self.ap_server.listen()


    def _draw_full(self):
        msgs = [
            "Ready to recieve updated settings.",
            f"Connect to the clock using the following wifi settings:",
            f"    SSID: {self.ap_server.ssid}",
            f"    Pwd : {self.ap_server.pwd}",
            "",
            "Once connected, in your browser go to:",
            f"    Pwd : {self.ap_server.pwd}",
        ]
        for i, s in msgs:
            x, y = 20, 20+(i*15)
            self.display.text(s, x, y, self.display.palette.BLACK, )
