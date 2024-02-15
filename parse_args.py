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

class InvalidConfig(Exception):
    pass


class Configuration:

    def __init__(self):
        # This only supports one target gpu, use a process for each GPU (erros become isolated to each other) 
        self.target_gpu = ""
        self.action = ""
        self.temp_speed_pair = []
        self.curve_type = "fixed" # Currently for internal usage only (I want to later add calculation for lines and curves fuctions)
        self.default_speed = 50 # Percentage
        self.time_interval = 1.0 # In seconds
        self.dry_run = False

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

    if config.target_gpu == '':
        print("You did not select a target GPU")
        raise InvalidConfig("No GPU was selected")

    # A user will always have a default speed set, so I don't think this check is necessary
    #if len(config.temp_speed_pair) == 0:
    #    print("You did not create fan points (see --speed-pairs)")
    #    raise InvalidConfig("Has no fan curve")


def parse_cmd_args(args):
    
    configuration = Configuration()

    if len(args) == 1:
        print(f'You must pass more argument')
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

    else:
        print(f'Invalid action: {action}')
        raise InvalidAction("The action passed as argument is incorrect")


    # You can safely ignore the actions here
    i = 2
    while(i < len(args)):

        arg = args[i]

        if (arg == '--target' or arg == '-t'):
            configuration.target_gpu = args[i+1]
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

        elif (arg == '--dry-run' or arg == '-dr'):
            configuration.dry_run = True

        else:
            print(f'Invalid option: {arg}')
            raise InvalidOption('The option given was invalid')

        # Change iteration
        i += 1

    # Organizing the array before sending the configuration
    configuration.temp_speed_pair.sort(reverse=True)

    validate_config(configuration)

    return configuration