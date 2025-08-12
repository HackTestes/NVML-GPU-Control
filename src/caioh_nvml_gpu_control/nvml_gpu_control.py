from pynvml import *
import sys
import helper_functions as main_funcs
import parse_args
import time
import multiprocessing

# This is working in a separate process
def worker_task(config):

    # So we need to reinitialize nvml
    nvmlInit()
    main_funcs.control_all(config)
    nvmlShutdown()

def control_worker(config):

    while(True):
        # Execute the GPU queries in a separate process, so it can be restarted on errors
        process = multiprocessing.Process(target=worker_task, args=(config,), daemon=True)
        process.start()
        process.join()

        if process.exitcode != 0:
            print(f"Worker failed. Exit code: {process.exitcode}")
            process.close()

            if config.retry == True:
                print(f"Retrying in {config.retry_interval_s} seconds\n")
                time.sleep(config.retry_interval_s) 
                continue               

        # If everything works fine, we don't need to retry
        process.close()
        break

def main():
    
    # Getting a configuration obj
    config = parse_args.parse_cmd_args(sys.argv)

    if config.action == 'help':
        main_funcs.print_help()
        return

    nvmlInit()

    # Verify driver version
    try:
        main_funcs.check_driver_version(nvmlSystemGetDriverVersion())

    except main_funcs.UnsupportedDriverVersion:
        print('WARNING: You are running an unsupported driver, you may have problems')
    
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
            control_worker(config)

    nvmlShutdown()

if __name__ == '__main__':
    main()