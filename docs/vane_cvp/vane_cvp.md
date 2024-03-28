# Vane CVP Application

This application can be installed on your cvp instance in order to conduct network testing. You can run NRFU tests as well as any other kind of tests that have been automated within your test plan.

## I. Running NRFU Tests on your CVP instance

To execute the predefined NRFU tests that are available as a part of this application on your cvp instance refer to this [section](../nrfu_setup/nrfu_setup.md#ii-running-vane-as-a-cvp-application)

## II. Running non NRFU Tests on your CVP instance

To execute non-NRFU tests, including customized test cases, and network certification test cases, abide by the following instructions:

### Step 1

Follow the instructions, specifically the steps from [Step 1](../nrfu_setup/nrfu_setup.md#step-1-download-the-vane-cvp-rpm-from-the-vane-repo) to [Step 8](../nrfu_setup/nrfu_setup.md#step-8-activate-vane-shell) laid out in this [section](../nrfu_setup/nrfu_setup.md#ii-running-vane-as-a-cvp-application) of NRFU Testing. Those steps should guide you towards downloading and installing the application on your cvp instance.

By the end of Step 8, you should be able to see the following prompt:

![Screenshot](../images/vane-cvp-prompt.png)

### Step 2

Now you are good to execute non Nrfu tests using Vane. There are 2 paths you could follow at this point:

A. Run Vane the default way

B. Run Vane using the CVP option (*recommended for new users*)

Before we dive into either of these, let us briefly cover how you can import your customized test cases into this working environment. This is essential as by default the application comes pre-installed only with nrfu tests and sample network tests which test basic aspects of your network. These pre-defined tests can be found within the vane-data directory.

#### Importing local customized test directories

!!! important

    Ensure that your test case folder has a conftest.py file for initializing the basic pytest configs for a valid test run. You can find a sample conftest.py file [here](https://github.com/aristanetworks/vane/blob/develop/nrfu_tests/conftest.py).

<!-- # Gary to fill in these steps and test functionality of vane --cvp using imported tests on 10.88.160.92

Now that we have access to our customised test cases in this environment, we are ready to run Vane! -->

#### A. Run Vane the default way

This is basically the conventional way of running Vane where you set up your definitions.yaml file and duts.yaml file with the necessary information. [Executing Vane section](../executing_vane/executing_vane.md) covers these steps in detail. Keep in mind to give path to your imported customized test case folder in the test_dirs field within your definitions.yaml file.

We recommend using Option B if this is your first time running Vane, since it will initialize the defaults and use your CVP instance to gather duts data for running vane.

#### B. Run Vane using the CVP option (*recommended for new users*)

Here you will be making use of the vane -- cvp option provided within the vane cli.

``` text
vane --cvp
```

Executing the above command will lead to a prompt asking you to enter your credentials for the cvp monitored devices.

After successfully authorizing, it will display the following

``` text
Using CVP to gather duts data
```

After which it will ask you if you want to provide custom test cases (it will default to in built nrfu test cases if you say No)

If you say Yes to the above prompt, it will further ask you for the path to the imported test cases.

!!! success

    Once you provide a valid path, you are all set and Vane will execute your customized test cases on your devices and generate corresponding reports.
