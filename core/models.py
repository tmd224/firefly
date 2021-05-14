import logging
import os
# import numpy as np
from util import init_logger, validate_arg


class StatParam():
    """
    class to model parameter statistics.  Modeling parameters in this way allows us to run Monte Carlo analysis
    """
    def __init__(self, name:str, units:str, nom_value:[int, float], param_type:str=None, param_dist:str=None, low_val:[int,float]=None, high_val:[int,float]=None):
        """
        Args:
            name (str): Name of the parameter
            units (str): Units of the parameter
            nom_value (int, float): Nominal value of the parameter
            param_type (str): Type of statistical parameter ['value', 'percent']
            param_dist (str): Type of statistical distribution to use ['uniform', 'normal']
            low_val (int, float): Lower value as represented by param_type
            high_val (int, float): Upper value as represented by param_type
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        # required arguments
        self.name = validate_arg(name, str)
        self.units = validate_arg(units, str)
        self.nom_value = validate_arg(nom_value, [int, float])
        # optional arguments
        self.param_type = validate_arg(param_type, str, valid_values=['value', 'percent'], optional=True)
        self.param_dist = validate_arg(param_dist, str, valid_values=['uniform','normal'], optional=True)
        self.low_val = validate_arg(low_val, [int,float], optional=True)
        self.high_val = validate_arg(high_val, [int,float], optional=True)

        self.logger.debug("Creating new StatParam ({})".format(self.name))

        def __repr__(self):
            return "{}-{}".format(self.name, self.nom_value)

        def get_value(self, nom=True):
            """
            Get the value of the parameter.

            Args:
                nom (bool): Returns nominal value if True, otherwise returns random value with distribution

            Returns:
                val (int, float): value
            """
            # just always return nominal value for now
            return self.nom_value

class BaseModel():
    """
    Base model class template.  All models should inherit from here
    """
    def __init__(self, id:int, name:str, tags:dict=None, sub_system_id:int=None):
        """
        Args:
            id (int): id number for internal use only
            name (str): display name for the load
            tags (dict): Dictionary of tags which determine what states the load should be enabled or disabled.  The format of the dictionary
                is 2 keys: 'enabled' and 'disabled'.  The values for both keys are lists of 'tag' strings.             
            sub_system_id (int): Sub-system id that the model belongs to
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.id = validate_arg(id, int)
        self.name = validate_arg(name, str)
        self.sub_system_id = validate_arg(sub_system_id, int, optional=True)
        self.tags = validate_arg(tags, dict, optional=True)          

        self.logger.debug("Creating new model object: {}".format(self.name))

class BaseLoad(BaseModel):
    """
    Base load class
    """

    def __init__(self, id:int, name:str, load_value:StatParam, input_resistance:StatParam=None, tags:dict=None, sub_system_id:str=None, ):
        """
        Args:
            id (int): id number for internal use only
            name (str): display name for the load
            sub_system (str): Sub-system name that the load belongs to
            tags (dict): Dictionary of tags which determine what states the load should be enabled or disabled.  The format of the dictionary
                is 2 keys: 'enabled' and 'disabled'.  The values for both keys are lists of 'tag' strings.
            input_resistance (StatParam): input resistance of the load (i.e a series component prior to the Vcc pin)
            load_value (StatParam): load value, typically current, but units based on child class implementation
        """
        super().__init__(id, name, tags, sub_system_id)
        self.load_value = validate_arg(load_value, StatParam)      
        self.input_resistance = validate_arg(input_resistance, StatParam, optional=True, default=StatParam('input_resistance', 'Ohm', 0.0))
        


class ResistiveLoad(BaseLoad):
    """
    This class models a typical resistive load.  The current through the load is a function of the load resistance and the input voltage.
    The ResistiveLoad model can be defined as having a specified current load or more directly the load resistance.
    """
    def __init__(self, *args):
        """
        * see base class for argument list *
        """
        super().__init__(*args)

class ConstantCurrentLoad(BaseLoad):
    """
    This class models a typical constant current load.  The current consumption by the load is independent from the input voltage
    """
    def __init__(self, *args):
        """
        * see base class for argument list *
        """
        super().__init__(*args)

class ConstantPowerLoad(BaseLoad):
    """
    This class models a typical constant power load.  The current consumed by the load is a function of the input voltage such that the power dissipated by the load is constant.
    """
    def __init__(self, *args):
        """
        * see base class for argument list *
        """
        super().__init__(*args)

class LoadSwitch(BaseModel):
    """
    This class models a load switch.  It can contain a collection of underlying load models
    """
    def __init__(self, id:int, name:str, switch_resistance:StatParam, input_resistance:StatParam=None, output_resistance:StatParam=None, tags=None, sub_system_id=None, child_loads:dict=None):
        """
        Args:
            id (int): model id
            name (str): model name
            switch_resistance (StatParam): The internal load switch DC resistance in Ohms
            input_resistance (StatParam): Additional input resistance prior to the load switch (ferrites, etc)
            output_resistance (Statparam): Additional output resistance at output of load switch (ferrites, etc)
            child_loads (dict): Initial dictionary of child load objects.  Child loads can be added after __init__
            *args: See BaseModel documentation for additional arguments
        """
        super().__init__(id, name, tags, sub_system_id)
        self.switch_resistance = validate_arg(switch_resistance, StatParam)
        self.input_resistance = validate_arg(input_resistance, StatParam, optional=True, default=StatParam('input_resistance', 'Ohm', 0))
        self.output_resistance = validate_arg(output_resistance, StatParam, optional=True, default=StatParam('output_resistance', 'Ohm', 0))
        self.child_loads = validate_arg(child_loads, dict, optional=True, default=dict())

    def add_load(self, load_obj):
        """
        Method to add a child load to the load switch model.  The 'child_loads' dictionary hosts all child load objects and 
        this method will add a new key/val pair.  The child loads are stored by the 'id' of the load object and the value is the object itself.

        Args:
            load_obj (obj): Load object that inherits from BaseLoad or is another loadSwitch object
        """
        self.child_loads[load_obj.id] = load_obj
        self.logger.debug("Adding load [{}-{}] to LoadSwitch [{}-{}]".format(load_obj.id, load_obj.name, self.id, self.name))


if __name__=="__main__":
    init_logger("log.log")
    load_param = StatParam("load_current", "A", 0.15)
    # input_resistance = StatParam("Input Resistance", "Ohm", 0.1)
    load = BaseLoad(1, 'Load1', load_param)
    load2 = ResistiveLoad(2, 'ResitiveLoad1', load_param)

    switch_resistance = StatParam('SwitchResistance', 'Ohm', 0.05)
    load_switch = LoadSwitch(3, 'LoadSwitch1', switch_resistance, child_loads={1:load})
    load_switch.add_load(load2)
