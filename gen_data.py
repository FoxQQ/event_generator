
"""
    VARs needed:

    GENERAL
    - model : CSH7581-80Y
    - serial : comp00001
    - status : ready
    - running : 0 / 1
    - firmware version : 0.70.x

    PHYSICAL
    - evaporating temp (SST): -4,7 °C       [ -15, 15 ]
    - condensing temp(SDT): 54 °C           [  20, 60 ]
    - oil pressure : UNK                                    Öldruck
    - discharge gas/oil temp : 52.2 °C                      Druckgas
    - auxiliary temp sensor : 25,4 °C
    - suction pressure 1,5 Bar                              Ansaugddruck
    - discharge pressure 13,5 Bar                           Enddruck
    - power supply freq 50/60 Hz
    - volumetric displacement : 295/356  m³/h               Fördervolumen
    - oil charge : 15 dm³                                   Ölfüllung
    - max operating current : 144 A
    - max power consumption : 88 kW

    - coolant
    - coolant_leakage   100g / a, -5-10% avg, in supermarket up to -15% normal

    - times active -> how often did it run in the timeframe to cool down?
    TIME
    operation time: x h
    log DT : daily 2 years?
"""

import time, datetime, pickle
import numpy as np
#GLOBALS
OUTFILE = "100devices.csv"
NUMBER_OF_DEVICES = 100
START_DATE = "2016-01-01"
END_DATE = "2016-12-31"
#END_DATE = "2016-01-10"
TIMESTEP = 3600 #*24 #3600=1h #
with open("cond-evap-temp-model", "rb") as fh:
    MODEL = (pickle.load(fh))[0][0]

#OTHER GLOBALS
MAXLEN = NUMBER_OF_DEVICES
START_UNIX = int(time.mktime(datetime.datetime.strptime(START_DATE, "%Y-%m-%d").timetuple()))
END_UNIX = int(time.mktime(datetime.datetime.strptime(END_DATE, "%Y-%m-%d").timetuple()))

HEADER = "sn,entry,mode,timestamp,model,eva_temp,con_temp,\
oil_temp,aux_temp_sens,suc_pres,dis_pres,freq,vol_disp,\
pow_cons,oil_charge,coolant_charge,ops_time,times_active,running,site_id"


class GenDevice:
    ops_time = 0
    eva_temp = np.random.randint(-15, 0)   #-4.7
    con_temp = np.random.randint(30, 55)   #54.0
    oil_temp = 52.2
    aux_temp_sens = 20.0
    suc_pres = 1.5
    dis_pres = 13.5
    freq = 50
    vol_disp = 295
    oil_char = 15
    pow_cons = 0  # calculate from eva vs con temp
    model = "CSH7581-80Y"
    sn, et, ct = None, None, None
    running = 1
    mode = "normal"
    coolant_charge = 100 #%
    coolant_decr = 0.04 / 24
    times_active = 1
    site_id = 0

    def __init__(self, sn, mode):
        self.sn = sn
        self.site_id = np.random.randint(1,46)
        self.eva_temp = np.random.randint(-15, 0)  # -4.7
        self.con_temp = np.random.randint(30, 55)  # 54.0
        if(mode == "leakage"):
            self.mode = mode
            self.gen_datarow = self.leakage
        elif(mode == "highconsumption"):
            self.mode = mode
            self.gen_datarow = self.highconsumption
        elif(mode == "nooil"):
            self.mode = "nooil"
            self.gen_datarow = self.nooil
        else:
            self.gen_datarow = self.normal

    def gen_datarow(self):
        pass

    def leakage(self, i, d, TIMESTEP):
        self.coolant_decr = 0.1
        self.dis_pres -= 0.001
        self.oil_temp += 0.01
        self.con_temp += 0.05
        if self.coolant_charge < 90 and self.coolant_charge >= 80: self.times_active = 1.2
        elif self.coolant_charge < 80 and self.coolant_charge >= 70: self.times_active = 1.4
        elif self.coolant_charge < 70: self.coolant_charge = 2
        return self.normal(i, d, TIMESTEP)

    def highconsumption(self, i, d, TIMESTEP):
        return self.normal(i, d, TIMESTEP)

    def nooil(self, i, d, TIMESTEP):
        self.oil_char -= i/10000
        return self.normal(i, d, TIMESTEP)

    def normal(self, i, d, TIMESTEP):
        self.ops_time += TIMESTEP / 3600
        self.et = self.make_random(self.eva_temp)
        self.ct = self.make_random(self.con_temp)
        datarow = self.sn + "," + str(i + 1) + "," + self.mode + "," \
                  + datetime.datetime.strftime(datetime.datetime.fromtimestamp(d), "%Y-%m-%d_%H:%M:%S")
        datarow += "," + self.model  # model
        if not self.running:
            return datarow + ",,,,,,,,,,,,,,0"
        datarow += "," + str(self.et)  # evaporation temp
        datarow += "," + str(self.ct)  # condensation temp
        datarow += "," + str(self.make_random(self.oil_temp))  # oil temp
        datarow += "," + str(self.make_random(self.aux_temp_sens))
        datarow += "," + str(self.make_random(self.suc_pres))  # suction pressure
        datarow += "," + str(self.make_random(self.dis_pres))  # discharge pressure
        datarow += "," + str(self.make_random(self.freq / 2))  # power supply freq
        datarow += "," + str(self.vol_disp)  # displacement
        self.pow_cons = np.asscalar(self.times_active * np.round(MODEL.predict([[self.ct, self.et]]), decimals=3))
        datarow += "," + str(self.pow_cons)  # power consumption  [[contT, evapT],[1.10207728 0.04840579]]
        self.oil_char = np.round(self.oil_char - 0.001, decimals=4)
        if (self.oil_char <= .1 and self.mode == "normal"):
            self.oil_char = 15
        datarow += "," + str(self.oil_char)  # oil charge
        self.coolant_charge = np.round(self.coolant_charge - self.coolant_decr, decimals=4)
        if(self.coolant_charge <= 1 and self.mode == "normal"):
            self.coolant_charge = 100
        datarow += "," + str(self.coolant_charge)  # coolant charge
        datarow += "," + str(self.ops_time)  # operation time
        datarow += "," + str(self.times_active) #how often did it run to keep the defined temerature?
        if (self.pow_cons > 88 or self.oil_char <= 0):
            self.running = 0
        datarow += "," + str(self.running)
        datarow += "," + str(self.site_id)
        return datarow

    def make_random(self, mu):
        return np.round((mu * 0.05 / 3) ** 2 * np.random.randn() + mu, decimals=5)


def dyn_range(start, stop, step):
    i = start
    while i <= stop:
        yield i
        i *= step


def get_serial(i, maxlen):
    zeros = str(len(str(maxlen)) - len(str(i)))
    return "SN" + int(zeros) * "0" + str(i)


devices_defect_nooil_perc = 3 #%
devices_defect_leakage_perc = 2 #%
devices_defect_nooil_num = devices_defect_nooil_perc * NUMBER_OF_DEVICES // 100
devices_defect_leakage_num = devices_defect_leakage_perc * NUMBER_OF_DEVICES // 100
random_selection = np.random.choice(NUMBER_OF_DEVICES, size=devices_defect_leakage_num + devices_defect_nooil_num,
                                    replace=False)
devices_nooil = random_selection[:devices_defect_leakage_num]
devices_leakage = random_selection[-devices_defect_nooil_num:]

print("no oil defects", devices_nooil)
print("leakage defects", devices_leakage)

with open(OUTFILE, "w") as fh:
    fh.write(HEADER + "\n")

    for devicenum in range(1, NUMBER_OF_DEVICES+1):
        print("devices left:", NUMBER_OF_DEVICES-devicenum)
        serial = get_serial(devicenum, MAXLEN)
        gendevice = GenDevice(serial, "normal")

        #Adding randomness to when a device will get a defect
        break_in_iter = np.random.randint(2000,7000)
        switch_nooil, switch_leakage = False, False
        if devicenum in devices_nooil:
            switch_nooil = True
        if devicenum in devices_leakage:
            switch_leakage = True

        content = ""
        #Creating events for the timeframe set in variables in the upper script part
        for i, d in enumerate(range(START_UNIX, END_UNIX, TIMESTEP)):
            datarow = gendevice.gen_datarow(i, d, TIMESTEP)
            # writing the event to the output file
            content+=datarow + "\n"

            # check if the current devices is part of those who have defect and check in which itereation the defect will start
            if  switch_nooil and i == break_in_iter:
                print(devicenum, "is defect no oil")
                current_oil_charge, c_eva_temp, c_cond_temp, c_coolant_charge, c_site_id= gendevice.oil_char, gendevice.eva_temp, gendevice.con_temp, gendevice.coolant_charge, gendevice.site_id
                gendevice = GenDevice(serial, "nooil")
                gendevice.oil_char, gendevice.eva_temp, gendevice.con_temp, gendevice.coolant_charge, gendevice.site_id = current_oil_charge, c_eva_temp, c_cond_temp, c_coolant_charge, c_site_id
            elif switch_leakage and i == break_in_iter:
                print(devicenum, "is defect leakage")
                current_oil_charge, c_eva_temp, c_cond_temp, c_coolant_charge, c_site_id = gendevice.oil_char, gendevice.eva_temp, gendevice.con_temp, gendevice.coolant_charge, gendevice.site_id
                gendevice = GenDevice(serial, "leakage")
                gendevice.oil_char, gendevice.eva_temp, gendevice.con_temp, gendevice.coolant_charge, gendevice.site_id = current_oil_charge, c_eva_temp, c_cond_temp, c_coolant_charge, c_site_id
        fh.write(content)


