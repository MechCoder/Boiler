import shelve
from state import State
specific_volume = 0.01602
cpair = 1.0
cpwater = 4.1855

class Boiler(object):
    r"""
    Simulation of Boiler.
    A typical Boiler consists of the following components.
    1] Feed Pump
    2] Economiser
    3] Air Preheater
    4] Superheater
    """

    def _check_eff(eff):
        if eff > 1 or eff < 0:
            raise ValueError("Efficiency should be in between zero "
                             "and one.")
        return eff


    def __init__(self, P1):
        r"""
        Initialising several attributes which are useful in simulating
        the boiler.
        """
        self.input_pressure = P1
        self.pump_work = 0
        self.economiser_heat = 0
        self.air_heat = 0
        self.superheater_heat = 0


    def feed_pump(self, P2, eff=1):
        r"""
        The feed pump is used to deliver feed water to the boiler.
        Assumptions made:
        1] Input pressure is provided
        2] The output pressure is saturated liquid.
        """
        eff = self._check_eff(eff)
        self.pump_present = True
        self.output_pressure_pump = P2
        self.pump_work = specific_volume*(P2 - self.input_pressure)
        if eff != 1:
            self.pump_work *= (1/eff)


    def economiser(self, f1, f2):
        r"""
        An economiser is a device in which the waste heat of the flue gases
        is utilised for heating the feed water, before entering the boiler.
        Assumptions made:
        1] The input to the economiser is saturated liquid.
        """
        self.economiser_present = True
        if hasattr(self, 'pump_present'):
            # Feed pump has been fit.
            P1 = self.output_pressure_pump

        else:
            # Feed pump has not been fit. Assume input water to the economiser
            # is in saturated state.
            P1 = self.input_pressure

        self.econ_T1 = State(P=P1, x=0).getTemp()

        # ft1 and ft2 are the flue gas temperatures.
        if f2 > f1:
            f2, f1 = f1, f2

        self.flue_T1 = f1
        self.flue_T2 = f2
        self.econ_T2 = self.econ_T1 + cpair*(self.flue_T1 - self.flue_T2)/cpwater


    def effectiveness(self):
        r"""
        Returns effectiveness of the economiser.
        """
        if not hasattr(self, "economiser_present"):
            raise ValueError("No economiser present")
        return (self.econ_T2 - self.econ_T1)/(self.flue_T1 - self.econ_T1)


    def air_preheater(self, Tp1, Tp2=None, eff=1):
        r"""
        The function of the air preheater is to increase the temperature
        of the air before it enters the furnace.
        Assumptions made:
        1] If the economiser is fit, input temperature of the economiser
           is the output of the air preheater.
        """
        eff = self._check_eff(eff)
        if hasattr(self, "economiser_present"):
            Tp2 = self.flue_T2
        elif not Tp2:
            raise ValueError("If economiser is not fit both input temperature "
                             "and output temperature should be provided.")
        self.air_heat = cpair*(Tp2 - Tp1)

        if eff != 1:
            self.air_heat *= 1/eff


    def boiler(self, eff=1):
        r"""
        The actual boiler
        Assumptions made
        1] Input of the boiler is saturated liquid.
        2] Output of the boiler is saturated vapour.
        So the heat is the difference in enthalpy at constant pressure.
        """
        eff = self._check_eff(eff)
        if hasattr(self, "economiser_present"):
            Tb = self.econ_T2
            self.h1 = State(T=Tb, x=0).getEnthalpy()
            self.h2 = State(T=Tb, x=1).getEnthalpy()
        elif hasattr(self, "pump_present"):
            Pb = self.output_pressure_pump
            self.h1 = State(P=Pb, x=0).getEnthalpy()
            self.h2 = State(P=Pb, x=1).getEnthalpy()
            Tb = State(P=Pb, x=1).getTemp()
        else:
            Pb = self.input_pressure
            self.h1 = State(P=Pb, x=0).getEnthalpy()
            self.h2 = State(P=Pb, x=1).getEnthalpy()
            Tb = State(P=Pb, x=1).getTemp()
        self.final_temp = Tb
        self.boiler_heat = self.h2 - self.h1
        if eff != 1:
            self.boiler_heat *= eff


    def superheater(self, final_temp, eff=1):
        r"""
        The function of the superheater is to increase the temperature
        above its saturation point.
        """
        eff = self._check_eff(eff)
        if not hasattr(self, "boiler_heat"):
            raise ValueError("Please fit boiler as accessories alone cannot"
                             "do anything.")
        if final_temp < self.final_temp:
            self.superheater_heat = 0
        else:
            self.superheater_heat = cpwater*(final_temp - self.final_temp)
        self.final_temp = final_temp
        if eff != 1:
            self.superheater_heat *= 1/eff

    def efficiency(self, heat_supplied):
        r"""
        Efficiency = (Actual heat)/(Heat supplied)
        """
        if not hasattr(self, "boiler_heat"):
            raise ValueError("Please fit boiler as accessories alone cannot"
                             "do anything.")
        heat = self.boiler_heat - (self.economiser_heat + self.air_heat +
                                   self.pump_work + self.superheater_heat)
        return (heat/heat_supplied)


    def actual_heat(self):
        return self.boiler_heat - (self.economiser_heat + self.air_heat +
                                   self.pump_work + self.superheater_heat)
