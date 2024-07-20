class Patients:
    def __init__(self,
                 name="小明",
                 age=18,
                 gender=1,
                 ethnic="汉族",
                 address="翻斗大街翻斗花园2号楼1001室",
                 id_number="123456789987654"
                 ):
        self.name = name
        self.age = age
        self.gender = gender
        self.ethnic = ethnic
        self.address = address
        self.id_number = id_number

        self.ecg_heatRate = 0
        self.ecg_HRV = 0
        self.ecg_prInterval = 0

        self.bodyTemperature = 0
        self.bloodOxygenSaturation = 0

        self.bloodPressure_high = 0
        self.bloodPressure_low = 0

        self.evaluate = 100








