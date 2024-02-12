class Status:
    def __init__(self, name, proc, ship, stor):
        self.name = name
        self.proc = proc
        self.ship = ship
        self.stor = stor

    def update_proc(self, new_status):
        self.proc = new_status

    def update_ship(self, new_status):
        self.ship = new_status

    def update_stor(self, new_status):
        self.stor = new_status

    def __str__(self):  # Customize output representation
        return f"{self.name}: proc={self.proc}, ship={self.ship}, stor={self.stor}"


STATUS = {
    "ADS": Status("ADS", "N/A", "No!", "No!"),
    "LRT": Status("LRT", "No!", "No!", "No!"),
    "KML": Status("KML", "No!", "No!", "No!"),
    "HRT": Status("HRT", "No!", "No!", "No!"),
    "SRT": Status("SRT", "No!", "No!", "No!"),
    "ICARTT": Status("ICARTT", "No!", "No!", "No!"),
    "IWG1": Status("IWG1", "No!", "No!", "No!"),
    "PMS2D": Status("PMS2D", "No!", "No!", "No!"),
    "threeVCPI": Status("threeVCPI", "No!", "No!", "No!"),
    "QCplots": Status("QCplots", "No!", "No!", "No!"),
}