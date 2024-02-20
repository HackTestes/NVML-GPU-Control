from pynvml import *
import sys
import helper_functions as main_funcs
import parse_args

def main():
    
    # Getting a configuration obj
    config = parse_args.parse_cmd_args(sys.argv)

    try:
        # Starting nvml
        nvmlInit()

        # Verify driver version
        try:
            main_funcs.check_driver_version(nvmlSystemGetDriverVersion())

        except main_funcs.UnsupportedDriverVersion:
            print('WARNING: You are running an unsupported driver, you may have problems')

        match config.action:

            # Help doesn't require nvml (TODO change code paths)
            case 'help':
                main_funcs.print_help()

            case 'list':
                main_funcs.list_gpus()

            case 'fan-control':
                main_funcs.fan_control(config)
    
    # One should call shutdown with or without erros, this is why I am using finally
    finally:
        print('Calling nvml shutdown and teminating the program')
        nvmlShutdown()

if __name__ == '__main__':
    main()