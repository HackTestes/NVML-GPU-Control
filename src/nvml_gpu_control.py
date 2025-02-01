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
        # Starting nvml
        nvmlInit()

        # Verify driver version
        try:
            main_funcs.check_driver_version(nvmlSystemGetDriverVersion())

        except main_funcs.UnsupportedDriverVersion:
            print('WARNING: You are running an unsupported driver, you may have problems')

        while(True):
            try:
                match config.action:

                    # Information query
                    case 'list':
                        main_funcs.list_gpus()

                    case 'get-power-limit-info':
                        main_funcs.print_power_limit_info(config)

                    case 'get-thresholds-info':
                        main_funcs.print_thresholds_info(config)

                    # Fan control
                    case 'fan-control':
                        main_funcs.fan_control(config)

                    # Fan control
                    case 'fan-info':
                        main_funcs.print_fan_info(config)

                    case 'fan-policy':
                        main_funcs.fan_policy(config)

                    case 'fan-policy-info':
                        main_funcs.print_fan_policy_info(config)

                    # Power control
                    case 'power-control':
                        main_funcs.power_control(config)

                    # Temperature threshold control
                    case 'temp-control':
                        main_funcs.temp_control(config)

                    # Enable everything
                    case 'control-all':
                        main_funcs.control_all(config)
                    
                # If everything works fine, we don't need to retry
                break
                
            except Exception as error:
                print(f"Logging error: {error}")
                print(f"Retrying in {config.retry_interval_s} seconds\n")
                time.sleep(config.retry_interval_s)
                
    
    # One should call shutdown with or without erros, this is why I am using finally
    finally:
        print('Calling nvml shutdown and terminating the program')
        nvmlShutdown()

if __name__ == '__main__':
    main()