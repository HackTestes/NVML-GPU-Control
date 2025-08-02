from pynvml import *
import sys
import helper_functions as main_funcs
import parse_args
import time


def main():
    
    # Getting a configuration obj
    config = parse_args.parse_cmd_args(sys.argv)

    if config.action == 'help':
        main_funcs.print_help()
        return

    try:

        # Verify driver version
        try:
            # Call nvml init and shutdown as an exception (special case), because I need it to restart in a loop later 
            nvmlInit()
            main_funcs.check_driver_version(nvmlSystemGetDriverVersion())
            nvmlShutdown()

        except main_funcs.UnsupportedDriverVersion:
            print('WARNING: You are running an unsupported driver, you may have problems')

        while(True):
            try:
                # Start nvml (or again in case of errors)
                # Useful to keep the process running during driver updates
                nvmlInit()
                
                match config.action:

                    # Information query
                    case 'list':
                        main_funcs.list_gpus()

                    case 'get-power-limit-info':
                        main_funcs.print_power_limit_info(config)

                    case 'get-thresholds-info':
                        main_funcs.print_thresholds_info(config)

                    case 'fan-info':
                        main_funcs.print_fan_info(config)

                    case 'fan-policy':
                        main_funcs.fan_policy(config)

                    case 'fan-policy-info':
                        main_funcs.print_fan_policy_info(config)

                    # Enable everything
                    case 'control':
                        main_funcs.control_all(config)
                    
                # If everything works fine, we don't need to retry
                break
                
            except Exception as error:
                print(f"Logging error: {error}")

                if config.retry == True:
                    # Clear all handles that nvml is holding, so errors won't persist across runs
                    nvmlShutdown()
                    print(f"Retrying in {config.retry_interval_s} seconds\n")
                    time.sleep(config.retry_interval_s)                

                else:
                    raise error
    
    # One should call shutdown with or without erros, this is why I am using finally
    finally:
        print('Calling nvml shutdown and terminating the program')
        nvmlShutdown()

if __name__ == '__main__':
    main()