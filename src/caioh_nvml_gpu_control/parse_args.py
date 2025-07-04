import helper_functions

class InvalidAction(Exception):
    pass

class InvalidOption(Exception):
    pass

class InvalidNumberSpeedPairParams(Exception):
    pass

class InvalidFanSpeed(Exception):
    pass

class InsufficientArgs(Exception):
    pass

class InvalidTimeParameter(Exception):
    pass

class InvalidConfig(Exception):
    pass


class Configuration:

    def __init__(self):
        # This only supports one target gpu, use a process for each GPU (erros become isolated to each other) 
        self.target_gpu = ""
        self.gpu_name = ""
        self.gpu_uuid = ""
        self.action = ""
        self.temp_speed_pair = []
        self.curve_type = "fixed" # Currently for internal usage only (I want to later add calculation for lines and curves fuctions)
        self.default_speed = 50 # Percentage
        self.time_interval = 1.0 # In seconds
        self.retry_interval_s = 2.0 # In seconds
        self.dry_run = False
        self.fan_policy = ''
        self.single_use = False
        self.acoustic_temp_limit = 0 # The user must set the value
        self.power_limit = 0 # The user must set the value

class TempSpeedPair:

    def __init__(self, temperature, speed):

        self.temperature = temperature
        self.speed = speed # Percentage!

    # The sorting is based on the temperature
    def __lt__(self, other):
        if (self.temperature <= other.temperature):
            return True

        else:
            return False

    # Important for testing
    def __eq__(self, other):
        if (self.temperature == other.temperature and self.speed == other.speed):
            return True

        else:
            return False

# Some sane checks (in case the user makes a bad config by accident)
def validate_config(config):

    # At least one of the target setting must be configured
    if config.gpu_name == '' and config.gpu_uuid == '':
        print("You did not select a target GPU")
        raise InvalidConfig("No GPU was selected")

    # fan-policy needs a mode
    if config.action == 'fan-policy':
        if config.fan_policy == '':
            print("You did not select a fan policy: autmatic or manual")
            raise InvalidConfig("No fan policy was selected")

    # power-control needs a power limit configuration
    if config.action == 'power-control':
        if config.power_limit == 0:
            print("You did not select a power limit")
            raise InvalidConfig("No power limit was selected")

    # temp-control needs a power limit configuration
    if config.action == 'temp-control':
        if config.acoustic_temp_limit == 0:
            print("You did not select a temperature limit")
            raise InvalidConfig("No temperature limit was selected")


def parse_cmd_args(args):

    configuration = Configuration()

    if len(args) == 1:
        print(f'You must pass more arguments')
        raise InsufficientArgs("No action was supplied")

    # You can always ignore the first argument, since it is the program itself
    # Get the second arg, which is the action
    action = args[1]

    # The action names are decoupled from the cmd interface, allowing for flexibility
    if (action == 'help'):
        configuration.action = 'help'
        return configuration # It should stop here, ignore all other args

    elif (action == 'list'):
        configuration.action = 'list'
        return configuration # It should stop here, ignore all other args

    elif (action == 'fan-control'):
        configuration.action = 'fan-control'

    elif (action == 'fan-info'):
        configuration.action = 'fan-info'

    elif (action == 'fan-policy'):
        configuration.action = 'fan-policy'

    elif (action == 'fan-policy-info'):
        configuration.action = 'fan-policy-info'

    elif (action == 'power-limit-info'):
        configuration.action = 'get-power-limit-info'

    elif (action == 'thresholds-info'):
        configuration.action = 'get-thresholds-info'

    elif (action == 'power-control'):
        configuration.action = 'power-control'

    elif (action == 'temp-control'):
        configuration.action = 'temp-control'

    elif (action == 'control-all'):
        configuration.action = 'control-all'

    else:
        helper_functions.print_help()
        print(f'Invalid action: {action}\n\n')
        raise InvalidAction("The action passed as argument is incorrect")


    # You can safely ignore the action here
    i = 2
    while(i < len(args)):

        arg = args[i]

        if (arg == '--name' or arg == '-n'):
            configuration.gpu_name = args[i+1]
            i += 1 # Skip the next iteration

        elif (arg == '--uuid' or arg == '-id'):
            configuration.gpu_uuid = args[i+1]
            i += 1 # Skip the next iteration

        elif (arg == '--speed-pair' or arg == '-sp'):

            # Think of as points in a graph (speed % x temp °C)
            speed_points = args[i+1].split(',')

            for speed_pair_str in speed_points:
    
                speed_pair = speed_pair_str.split(':')

                if (len(speed_pair) != 2):
                    print('Invalid number of speed pair parameters')
                    raise InvalidNumberSpeedPairParams("You can only set temperature and target speed at a time")

                temp = int(speed_pair[0])
                speed = int(speed_pair[1])

                if (speed > 100):
                    print(f'The fan speed only goes up to 100%. You choose {speed}')
                    raise InvalidFanSpeed(f'The fan speed only goes up to 100%. You choose {speed}')

                if (speed < 0):
                    print(f'The fan speed cannot be lower than 0%. You choose {speed}')
                    raise InvalidFanSpeed(f'The fan speed cannot be lower than 0%. You choose {speed}')

                configuration.temp_speed_pair.append( TempSpeedPair(temp, speed) )

            i += 1 # Skip the next iteration

        elif (arg == '--default-speed' or arg == '-ds'):
            configuration.default_speed = int(args[i+1])
            i += 1 # Skip the next iteration

        elif (arg == '--time-interval' or arg == '-ti'):
            configuration.time_interval = float(args[i+1])
            i += 1 # Skip the next iteration

            # Refuse to continue with negative time values
            if configuration.time_interval < 0:
                print("You cannot use negative time values for intervals")
                raise InvalidTimeParameter("Invalid time parameter")

        elif (arg == '--retry-interval' or arg == '-ri'):
            configuration.retry_interval_s = float(args[i+1])
            i += 1 # Skip the next iteration

            # Refuse to continue with negative time values
            if configuration.retry_interval_s < 0:
                print("You cannot use negative time values for intervals")
                raise InvalidTimeParameter("Invalid time parameter")

        elif (arg == '--dry-run' or arg == '-dr'):
            configuration.dry_run = True

        # For the fan-policy action
        elif (arg == '--auto'):
            configuration.fan_policy = 'automatic'

        elif (arg == '--manual'):
            configuration.fan_policy = 'manual'

        elif (arg == '--single-use' or arg == '-su'):
            configuration.single_use = True

        elif (arg == '--acoustic-temp-limit' or arg == '-tl'):
            configuration.acoustic_temp_limit = int(args[i+1])
            i += 1 # Skip the next iteration

        elif (arg == '--power-limit' or arg == '-pl'):
            configuration.power_limit = int(args[i+1])
            i += 1 # Skip the next iteration

        else:
            helper_functions.print_help()
            print(f'Invalid option: {arg}\n\n')
            raise InvalidOption('The option given was invalid')

        # Change iteration
        i += 1

    # Organizing the array before sending the configuration
    configuration.temp_speed_pair.sort(reverse=True)

    validate_config(configuration)

    return configuration