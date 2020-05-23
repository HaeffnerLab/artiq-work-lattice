import pytest
import yaml

from parse_yaml import *

class TestParseYaml:

    def test_empty(self):
        yaml_contents = ''
        config_yaml = yaml.safe_load(yaml_contents)
        with pytest.raises(Exception):
            validate_yaml(config_yaml)

    def test_simple_invalid(self):
        yaml_contents = '''
            jobs:
                MyJobName:
                    fake_attribute: 0
        '''
        config_yaml = yaml.safe_load(yaml_contents)
        with pytest.raises(Exception):
            validate_yaml(config_yaml)

    def test_simple_valid(self):
        yaml_contents = '''
            fits:
                MyFitName:
                    parameters:
                        - param_name_1
                    python: >
                        param_name_1 * x
            jobs:
                MyJobName:
                    description: Something.
        '''
        config_yaml = yaml.safe_load(yaml_contents)
        validate_yaml(config_yaml)

    def test_invalid_fit_python(self):
        yaml_contents = '''
            fits:
                MyFitName:
                    parameters:
                        - param_name_1
                    python: >
                        bad_param_name * x
            jobs:
                MyJobName:
                    description: Something.
        '''
        config_yaml = yaml.safe_load(yaml_contents)
        with pytest.raises(InvalidFitPythonCode):
            validate_yaml(config_yaml)

    def test_self_inheritance(self):
        yaml_contents = '''
            fits:
                MyFitName:
                    parameters:
                        - param_name_1
                    python: >
                        param_name_1 * x
            jobs:
                MyJobName:
                    description: Something.
                    inherits-from: MyJobName
        '''
        config_yaml = yaml.safe_load(yaml_contents)
        with pytest.raises(CircularJobInheritanceError):
            validate_yaml(config_yaml)

    def test_circular_inheritance(self):
        yaml_contents = '''
            fits:
                MyFitName:
                    parameters:
                        - param_name_1
                    python: >
                        param_name_1 * x
            jobs:
                MyJobName:
                    description: Something.
                    inherits-from: MyOtherJobName
                MyOtherJobName:
                    description: Something else.
                    inherits-from: MyJobName
        '''
        config_yaml = yaml.safe_load(yaml_contents)
        with pytest.raises(CircularJobInheritanceError):
            validate_yaml(config_yaml)

    def test_self_prerequisite(self):
        yaml_contents = '''
            fits:
                MyFitName:
                    parameters:
                        - param_name_1
                    python: >
                        param_name_1 * x
            jobs:
                MyJobName:
                    description: Something.
                    prerequisites:
                        - MyJobName
        '''
        config_yaml = yaml.safe_load(yaml_contents)
        with pytest.raises(CircularJobPrerequisiteError):
            validate_yaml(config_yaml)

    def test_circular_prerequisite_two(self):
        yaml_contents = '''
            fits:
                MyFitName:
                    parameters:
                        - param_name_1
                    python: >
                        param_name_1 * x
            jobs:
                MyJobName:
                    description: Something.
                    prerequisites:
                        - MyOtherJobName
                MyOtherJobName:
                    description: Something.
                    prerequisites:
                        - MyJobName
        '''
        config_yaml = yaml.safe_load(yaml_contents)
        with pytest.raises(CircularJobPrerequisiteError):
            validate_yaml(config_yaml)

    def test_circular_prerequisite_three(self):
        yaml_contents = '''
            fits:
                MyFitName:
                    parameters:
                        - param_name_1
                    python: >
                        param_name_1 * x
            jobs:
                MyJobName:
                    description: Something.
                    prerequisites:
                        - MyOtherJobName
                MyOtherJobName:
                    description: Something.
                    prerequisites:
                        - YetAnotherJobName
                YetAnotherJobName:
                    description: Something.
                    prerequisites:
                        - MyJobName
        '''
        config_yaml = yaml.safe_load(yaml_contents)
        with pytest.raises(CircularJobPrerequisiteError):
            validate_yaml(config_yaml)

    def test_incomplete_job_fit(self):
        yaml_contents = '''
            fits:
                MyFitName:
                    parameters:
                        - param_name_1
                    python: >
                        param_name_1 * x
            jobs:
                MyJobName:
                    description: Something.
                    fit:
                        name: MyFitName
        '''
        config_yaml = yaml.safe_load(yaml_contents)
        with pytest.raises(Exception):
            validate_yaml(config_yaml)

    def test_valid_job_fit(self):
        yaml_contents = '''
            fits:
                MyFitName:
                    parameters:
                        - param_name_1
                    python: >
                        param_name_1 * x
            jobs:
                MyJobName:
                    description: Something.
                    fit:
                        name: MyFitName
                        parameter-source: ParameterVault
                        parameter-name: Category.name
                        parameter-value: param_name_1
        '''
        config_yaml = yaml.safe_load(yaml_contents)
        validate_yaml(config_yaml)

    def test_invalid_job_fit_name(self):
        yaml_contents = '''
            fits:
                MyFitName:
                    parameters:
                        - param_name_1
                    python: >
                        param_name_1 * x
            jobs:
                MyJobName:
                    description: Something.
                    fit:
                        name: SomeOtherFitName
                        parameter-source: ParameterVault
                        parameter-name: Category.name
                        parameter-value: param_name_1
        '''
        config_yaml = yaml.safe_load(yaml_contents)
        with pytest.raises(Exception):
            validate_yaml(config_yaml)

    def test_invalid_job_fit_parameter(self):
        yaml_contents = '''
            fits:
                MyFitName:
                    parameters:
                        - param_name_1
                    python: >
                        param_name_1 * x
            jobs:
                MyJobName:
                    description: Something.
                    fit:
                        name: MyFitName
                        parameter-source: ParameterVault
                        parameter-name: Category.name
                        parameter-value: some_other_param_name
        '''
        config_yaml = yaml.safe_load(yaml_contents)
        with pytest.raises(Exception):
            validate_yaml(config_yaml)

    def test_auto_calibration_yaml(self):
        yaml_filename = "auto_calibration.yml"
        with open(yaml_filename, "r") as yaml_file:
            config_yaml = yaml.load(yaml_file)
        validate_yaml(config_yaml)
