import unittest
from unittest.mock import Mock
import sys
import ctypes
import parse_args
import helper_functions as main_funcs

# Test command: python.exe .\tests.py -b

class TestMethods(unittest.TestCase):

    def test_parse_args_inssuficient_args(self):
        with self.assertRaises(parse_args.InsufficientArgs):
            parse_args.parse_cmd_args(['.python_script'])

    def test_parse_args_help(self):
        config = parse_args.parse_cmd_args(['.python_script', 'help'])
        self.assertEqual( config.action, 'help')

    def test_parse_args_list(self):
        config = parse_args.parse_cmd_args(['.python_script', 'list'])
        self.assertEqual( config.action, 'list')

    def test_parse_args_fan_control(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '--name', 'RTX 4080'])
        self.assertEqual( config.action, 'fan-control')

    def test_parse_args_fan_policy(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-policy', '--name', 'RTX 4080', '--auto'])
        self.assertEqual( config.action, 'fan-policy')

    def test_parse_args_fan_policy_info(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-policy-info', '--name', 'RTX 4080'])
        self.assertEqual( config.action, 'fan-policy-info')

    def test_parse_args_fan_info(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-info', '--name', 'RTX 4080'])
        self.assertEqual( config.action, 'fan-info')

    def test_parse_args_get_power_limit_info(self):
        config = parse_args.parse_cmd_args(['.python_script', 'power-limit-info', '--name', 'RTX 4080'])
        self.assertEqual( config.action, 'get-power-limit-info')

    def test_parse_args_get_temp_thresholds_limit_info(self):
        config = parse_args.parse_cmd_args(['.python_script', 'thresholds-info', '--name', 'RTX 4080'])
        self.assertEqual( config.action, 'get-thresholds-info')

    def test_parse_args_action_power_control(self):
        config = parse_args.parse_cmd_args(['.python_script', 'power-control', '--name', 'RTX 4080', '-pl', '150'])
        self.assertEqual( config.action, 'power-control')

    def test_parse_args_action_temp_control(self):
        config = parse_args.parse_cmd_args(['.python_script', 'temp-control', '--name', 'RTX 4080', '-tl', '150'])
        self.assertEqual( config.action, 'temp-control')

    def test_parse_args_action_control_all(self):
        config = parse_args.parse_cmd_args(['.python_script', 'control-all', '--name', 'RTX 4080'])
        self.assertEqual( config.action, 'control-all')

    def test_parse_args_invalid_action(self):
        with self.assertRaises(parse_args.InvalidAction):
            parse_args.parse_cmd_args(['.python_script', 'invalid-action'])

    def test_parse_args_action_ignore_rest(self):
        config = parse_args.parse_cmd_args(['.python_script', 'help', '--name', 'RTX 4080'])
        self.assertEqual( config.action, 'help')
        self.assertEqual( config.target_gpu, '')

        config = parse_args.parse_cmd_args(['.python_script', 'list', '--name', 'RTX 4080'])
        self.assertEqual( config.action, 'list')
        self.assertEqual( config.target_gpu, '')

    def test_parse_args_option_gpu_name(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '--name', 'RTX 4080'])
        self.assertEqual( config.action, 'fan-control')
        self.assertEqual( config.gpu_name, 'RTX 4080')

        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '-n', 'RTX 3080'])
        self.assertEqual( config.action, 'fan-control')
        self.assertEqual( config.gpu_name, 'RTX 3080')

    def test_parse_args_option_gpu_uuid(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '--uuid', 'GPU-00000000-0000-0000-0000-000000000000'])
        self.assertEqual( config.action, 'fan-control')
        self.assertEqual( config.gpu_uuid, 'GPU-00000000-0000-0000-0000-000000000000')

    def test_parse_args_option_power_limit(self):
        config = parse_args.parse_cmd_args(['.python_script', 'power-control', '--name', 'RTX 4080', '--power-limit', '100'])
        self.assertEqual( config.power_limit, 100)

        config = parse_args.parse_cmd_args(['.python_script', 'power-control', '--name', 'RTX 4080', '-pl', '100'])
        self.assertEqual( config.power_limit, 100)

    def test_parse_args_option_acoustic_temp_limit(self):
        config = parse_args.parse_cmd_args(['.python_script', 'temp-control', '--name', 'RTX 4080', '--acoustic-temp-limit', '50'])
        self.assertEqual( config.acoustic_temp_limit, 50)

        config = parse_args.parse_cmd_args(['.python_script', 'temp-control', '--name', 'RTX 4080', '-tl', '50'])
        self.assertEqual( config.acoustic_temp_limit, 50)

    def test_parse_args_option_single_use(self):
        config = parse_args.parse_cmd_args(['.python_script', 'power-control', '--name', 'RTX 4080', '-pl', '50', '--single-use'])
        self.assertEqual( config.single_use, True)

        config = parse_args.parse_cmd_args(['.python_script', 'power-control', '--name', 'RTX 4080', '-pl', '50', '-su'])
        self.assertEqual( config.single_use, True)

        # Default should be False
        config = parse_args.parse_cmd_args(['.python_script', 'power-control', '--name', 'RTX 4080', '-pl', '50'])
        self.assertEqual( config.single_use, False)

    def test_parse_args_option_default_speed(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '--default-speed', '36', '-n', 'RTX 3080'])
        self.assertEqual( config.action, 'fan-control')
        self.assertEqual( config.default_speed, 36)

        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '-ds', '27', '-n', 'RTX 3080'])
        self.assertEqual( config.action, 'fan-control')
        self.assertEqual( config.default_speed, 27)
    
        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '-n', 'RTX 3080'])
        self.assertEqual( config.action, 'fan-control')
        self.assertTrue( config.default_speed >= 30) # Fan speed must never default for a value lower than 30%, except for when user explicitly wants to

    def test_parse_args_option_time_interval(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '--time-interval', '5', '-n', 'RTX 3080'])
        self.assertEqual( config.action, 'fan-control')
        self.assertEqual( config.time_interval, 5.0)

        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '-ti', '0.5', '-n', 'RTX 3080'])
        self.assertEqual( config.action, 'fan-control')
        self.assertEqual( config.time_interval, 0.5)

        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '-ti', '0', '-n', 'RTX 3080'])
        self.assertEqual( config.action, 'fan-control')
        self.assertEqual( config.time_interval, 0)

        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '-n', 'RTX 3080'])
        self.assertEqual( config.action, 'fan-control')
        self.assertTrue( config.time_interval <= 1) # Default should never be higher than 1s, unless the user states so

    def test_parse_args_option_time_interval_Error_negative_time(self):

        with self.assertRaises(parse_args.InvalidTimeParameter):
            parse_args.parse_cmd_args(['.python_script', 'fan-control', '--time-interval', '-5', '-n', 'RTX 3080'])

    def test_parse_args_option_retry_interval(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '--retry-interval', '5', '-n', 'RTX 3080'])
        self.assertEqual( config.action, 'fan-control')
        self.assertEqual( config.retry_interval_s, 5.0)

        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '-ri', '0.5', '-n', 'RTX 3080'])
        self.assertEqual( config.action, 'fan-control')
        self.assertEqual( config.retry_interval_s, 0.5)

        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '-ri', '0', '-n', 'RTX 3080'])
        self.assertEqual( config.action, 'fan-control')
        self.assertEqual( config.retry_interval_s, 0)

        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '-n', 'RTX 3080'])
        self.assertEqual( config.action, 'fan-control')
        self.assertTrue( config.retry_interval_s <= 2) # Default should never be higher than 2s, unless the user states so

    def test_parse_args_option_retry_interval_Error_negative_time(self):

        with self.assertRaises(parse_args.InvalidTimeParameter):
            parse_args.parse_cmd_args(['.python_script', 'fan-control', '--retry-interval', '-5', '-n', 'RTX 3080'])

    def test_parse_args_temp_speed_pair(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '--speed-pair', '0:0,10:30,20:50,35:75,40:100', '-n', 'RTX 3080'])

        expected_output = [
            parse_args.TempSpeedPair(40, 100),
            parse_args.TempSpeedPair(35, 75),
            parse_args.TempSpeedPair(20, 50),
            parse_args.TempSpeedPair(10, 30),
            parse_args.TempSpeedPair(0, 0),
        ]
        self.assertEqual(expected_output, config.temp_speed_pair)

        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '-sp', '0:0,10:30,20:50,35:75,40:100', '-n', 'RTX 3080'])
        self.assertEqual(expected_output, config.temp_speed_pair)

    def test_parse_args_temp_speed_pair_sort(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '--speed-pair', '40:100,20:50,10:30,35:75', '-n', 'RTX 3080'])

        expected_output = [
            parse_args.TempSpeedPair(40, 100),
            parse_args.TempSpeedPair(35, 75),
            parse_args.TempSpeedPair(20, 50),
            parse_args.TempSpeedPair(10, 30),
        ]
        self.assertEqual(expected_output, config.temp_speed_pair)

    def test_parse_args_temp_speed_pair_empty_list(self):

        with self.assertRaises(IndexError):
            parse_args.parse_cmd_args(['.python_script', 'fan-control', '--speed-pair'])

    def test_parse_args_temp_speed_pair_invalid_list(self):

        with self.assertRaises(parse_args.InvalidNumberSpeedPairParams):
            parse_args.parse_cmd_args(['.python_script', 'fan-control', '--speed-pair', ''])

        with self.assertRaises(parse_args.InvalidNumberSpeedPairParams):
            parse_args.parse_cmd_args(['.python_script', 'fan-control', '--speed-pair', '10-20'])

        with self.assertRaises(ValueError):
            parse_args.parse_cmd_args(['.python_script', 'fan-control', '--speed-pair', '10-20:10-20'])
        
        with self.assertRaises(ValueError):
            parse_args.parse_cmd_args(['.python_script', 'fan-control', '--speed-pair', '10-20:10-20,10-20:10-20'])

    def test_parse_args_temp_speed_pair_invalid_fan_speed(self):

        with self.assertRaises(parse_args.InvalidFanSpeed):
            parse_args.parse_cmd_args(['.python_script', 'fan-control', '--speed-pair', '10:120'])

        with self.assertRaises(parse_args.InvalidFanSpeed):
            parse_args.parse_cmd_args(['.python_script', 'fan-control', '--speed-pair', '10:-100'])

    def test_parse_args_dry_run(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '--dry-run', '-n', 'RTX 3080'])
        self.assertEqual(config.dry_run, True)

        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '-dr', '-n', 'RTX 3080'])
        self.assertEqual(config.dry_run, True)

        # Default value should always be False
        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '-n', 'RTX 3080'])
        self.assertEqual(config.dry_run, False)

    def test_parse_args_fan_policy_auto(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-policy', '--name', 'RTX 4080', '--auto'])
        self.assertEqual( config.fan_policy, 'automatic')

    def test_parse_args_fan_policy_manual(self):
        config = parse_args.parse_cmd_args(['.python_script', 'fan-policy', '--name', 'RTX 4080', '--manual'])
        self.assertEqual( config.fan_policy, 'manual')

    def test_parse_args_invalid_option(self):

        with self.assertRaises(parse_args.InvalidOption):
            parse_args.parse_cmd_args(['.python_script', 'fan-control', '--invalid-option', '10:120', '-n', 'RTX 3080'])

    def test_parse_args_real_cmd(self):

        config = parse_args.parse_cmd_args(['.python_script', 'fan-control', '--name', 'RTX 4080', '--speed-pair', '0:0,20:35,30:50,40:100', '--time-interval', '0.5'])

        self.assertEqual(config.action, 'fan-control')
        self.assertEqual(config.gpu_name, 'RTX 4080')
        self.assertEqual(config.time_interval, 0.5)
        expected_output = [
            parse_args.TempSpeedPair(40, 100),
            parse_args.TempSpeedPair(30, 50),
            parse_args.TempSpeedPair(20, 35),
            parse_args.TempSpeedPair(0, 0),
        ]
        self.assertEqual(config.temp_speed_pair, expected_output)

    def test_parse_args_sane_checks_no_fan_policy(self):

        # No fan policy
        with self.assertRaises(parse_args.InvalidConfig):
            parse_args.parse_cmd_args(['.python_script', 'fan-policy', '-n', 'RTX 3080'])

    def test_parse_args_sane_checks_no_gpu(self):

        # No target gpu
        with self.assertRaises(parse_args.InvalidConfig):
            parse_args.parse_cmd_args(['.python_script', 'fan-control'])

        # No target gpu
        with self.assertRaises(parse_args.InvalidConfig):
            parse_args.parse_cmd_args(['.python_script', 'power-control'])

        # No target gpu
        with self.assertRaises(parse_args.InvalidConfig):
            parse_args.parse_cmd_args(['.python_script', 'temp-control'])

        # No target gpu
        with self.assertRaises(parse_args.InvalidConfig):
            parse_args.parse_cmd_args(['.python_script', 'power-limit-info'])

        # No target gpu
        with self.assertRaises(parse_args.InvalidConfig):
            parse_args.parse_cmd_args(['.python_script', 'thresholds-info'])

    def test_parse_args_sane_checks_no_power_limit(self):

        # No fan policy
        with self.assertRaises(parse_args.InvalidConfig):
            parse_args.parse_cmd_args(['.python_script', 'power-control', '--name', 'RTX 4080'])

    def test_parse_args_sane_checks_no_temp_acoustic_limit(self):

        # No fan policy
        with self.assertRaises(parse_args.InvalidConfig):
            parse_args.parse_cmd_args(['.python_script', 'temp-control', '--name', 'RTX 4080'])


    def test_check_driver_version(self):

        # If the driver starts to return letters, a refactoring will be needed anyways
        # So I just want to verify that letters reaise erros
        with self.assertRaises(ValueError):
            main_funcs.check_driver_version('AAA')

        # Only cares for the major version
        with self.assertRaises(main_funcs.UnsupportedDriverVersion):
            main_funcs.check_driver_version('515')

        with self.assertRaises(main_funcs.UnsupportedDriverVersion):
            main_funcs.check_driver_version('515.20.20')

        with self.assertRaises(main_funcs.UnsupportedDriverVersion):
            main_funcs.check_driver_version('515.20.20.20')

        with self.assertRaises(main_funcs.UnsupportedDriverVersion):
            main_funcs.check_driver_version('515.20.20.20aaaaa')

    def test_fan_policy_info_msg(self):
        msg = main_funcs.fan_policy_info_msg(ctypes.c_uint(0).value)
        self.assertEqual('Current fan control policy is automatic', msg)

        msg = main_funcs.fan_policy_info_msg(ctypes.c_uint(1).value)
        self.assertEqual('Current fan control policy is manual', msg)

        msg = main_funcs.fan_policy_info_msg(ctypes.c_uint(100).value)
        self.assertEqual('Unknown fan control policy', msg)

#    # GPU Functions - I will need to improve the tests later
#
#    def test_gpu_something(self):
#        # Mocking
#        import pynvml
#
#        pynvml.nvmlDeviceGetCount = Mock(return_value=1)
#        pynvml.nvmlDeviceGetHandleByIndex = Mock(return_value=0)
#        pynvml.nvmlDeviceGetName = Mock(return_value='RTX 3080')
#
#        # Main function
#        main_funcs.list_gpus()
#
#        # Fail
#        self.assertTrue(True)



if __name__ == '__main__':
    unittest.main()