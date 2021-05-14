import logging

# Logger levels
LOG_LEVEL = logging.DEBUG
CONSOLE_LEVEL = logging.INFO

def init_logger(fullpath):
    """
    Setup the logger object

    Args:
        fullpath (str): full path to the log file
    """
    logging.basicConfig(level=LOG_LEVEL,
                        format='%(asctime)s %(threadName)-10s %(name)-20s %(levelname)-8s %(message)s',
                        datefmt='%m-%d-%y %H:%M:%S',
                        filename=fullpath,
                        filemode='w')

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(CONSOLE_LEVEL)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    logging.debug("Creating log file")

def validate_string(arg, values:[str,list], strict=True):
    """
    Helper function to validate an argument against an acceptable string or list of strings. This function
    is meant to be passed into validate_arg() as a callback function
    
    Args:
        arg (str): argument to validate
        values (str, list): string or list of valid strings
        strict (bool): If True, direct compare is made, otherwise lowercase compare is made

    Returns:
        None

    Raises:
        ValueError
    """
    if type(values) is str:
        values = [values]   # cast to list for comparison
    
    if strict is False:
        # do a lowercase compare on each element in the list
        values = [s.lower() for s in values]
        arg = arg.lower()

    if arg not in values:
        raise ValueError("{} is invalid value. Acceptable values are {}".format(arg, values))


def validate_number(arg:[int,float], range:list):
    """
    Helper function to validate a number between a valid range of values.  This function is meant to be
    passed into validate_arg as a callback function

    Args:
        arg (int, float): number to validate
        range (list): inclusive bounds on valid range [lower, upper]

    Returns:
        None

    Raises:
        ValueError
    """
    print(range)
    if arg < range[0] or arg > range[1]:
        raise ValueError("Value ({}) must be in the range [{}, {}]".format(arg, range[0],range[1]))

def validate_arg(arg, expected_type, valid_values=None, optional=False, default=None, strict=False):
    """
    Utility function to validate a function argument.

    Args:
        arg (obj): argument to be validated.  Can be any object type
        expected_type (obj): Object type to check against
        optional (bool): If True, raise exception if arg is None Type.
        valid_values (str, list): values used to validate the argument
        default (obj): Default value to use if arg is None Type.  default type must match expected_type or exception will be thrown
        strict (bool): use strict enforcement of string validation (if applicable)

    Returns:
        arg (obj): Returns arg input if check passes.

    Raises: 
        TypeError: Raised if arg type does not match expected_type
        ValueError: If arg value is not in expected range
    """
    logger = logging.getLogger(validate_arg.__qualname__)
    # if argument is optional and it's None, check if default type was specified
    if optional is True and arg is None:
        if default is None:
            logger.debug("Ignoring NoneType optional argument")
            return None
        else:
            logger.debug("Using default argument")
            arg = default 

    # check argument type against expected type
    if type(expected_type) is not list:
        expected_type = [expected_type]     # format expected type into a list for checking

    if type(arg) not in expected_type:
        raise TypeError("Invalid argument type ({}) must be ({})".format(type(arg), expected_type))
    
    # now, validate the argument value using the appropriate function if valid values were supplied
    if valid_values is not None:
        if type(arg) is str:
            validate_string(arg, valid_values, strict)
        elif type(arg) is int or float:
            validate_number(arg, valid_values)

    logger.debug("Validated arg: {}".format(arg))
    return arg

if __name__=="__main__":
    validate_arg("hi", [str], "Hi", strict=False)
    validate_arg("hi", str, ["hi", "bye"], strict=False)
    validate_arg(5.0, [int, float], strict=False)

