# NRFU Testing

We also provide specific NRFU functionality which allows users to run NRFU tests
against their network by using Vane. This functionality can be utilized by
connecting Vane to the network in 3 different ways as follows:

- Running Vane locally

    1. Connecting to devices locally (via a device ip text file)
    2. Connecting to devices via a CVP instance (by providing the CVP ip)
  
- Running Vane as a CVP Application
  
    1. Connecting to devices by running Vane as a CVP container

## NRFU Test cases supported in Vane

!!! eos-config "Note"

    The list of supported NRFU test cases can be found [here](https://github.com/aristanetworks/vane/tree/develop/nrfu_tests)

## I. Running Vane locally

Executing the below command will prompt for EOS device/CVP
credentials (which should be the same)

``` text
vane --nrfu
```

After entering those, you will be prompted as follows:

``` text
Do you wish to use CVP for DUTs?
```

### a. Local Execution without CVP

If you answer No, it will prompt you as follows:

``` text
Please input Name/Path of device list file (.txt) (Use tab for autocompletion):
```

Once you enter the path to a file with device ip’s,
it will prompt you for a test directory as follows:

``` text
Do you want to specify a test case directory [y|n]: 
```

If you answer n/no, it will default to the
[nrfu_tests folder](https://github.com/aristanetworks/vane/tree/develop/nrfu_tests)
in vane, if yes it will further prompt you as follows:

``` text
Please specify test case directory <path/to/test case dir> (Use tab for autocompletion):
```

!!! Success

    Following which Vane will start executing the nrfu test cases
    on the devices whose ip’s were provided in the device file.

### b. Local Execution with CVP

If you answer Yes, it will prompt you as follows:

``` text
Please input CVP IP address
```

Given you authenticate in successfully after providing the address,
it will prompt you for the test directory as earlier.

!!! Success

    After which Vane will start executing the test cases
    on your devices managed through CVP.

## II.  Running Vane as a CVP Application

!!! info

    If you have the initialized vane-cvp setup, then skip to
    the second part of Step 8, if not then follow from Step 1

### Step 1: Download the vane-cvp-rpm from the vane repo

Location: <https://github.com/aristanetworks/vane/actions/workflows/cvp-extension-builder.yml>

Select the most recent successful build,
which would be the one at the top with a green checkmark.

Then download the rpm from the artifacts section
(You need to be signed into your github account to be able to download this)

The package is downloaded as a zip archive.
Unzip the archive to extract the rpm file.

### Step 2: scp the rpm file from your local device to your cvp instance

The file should be copied into the cvp user’s home directory on the cvp instance.

``` text
scp <path_to_rpm_on_local_device> <cvp_user>@<cvp_ip>:/home/cvp
```

!!! example

    scp /Users/rewati/Downloads/vane-cvp-0.91-1.noarch.rpm root@10.255.67.157:/home/cvp

### Step 3: Ssh into cvp instance and change to the cvp user

Log into the cvp instance as the root user initially.
Then use the shown command to change to the cvp user’s account.

``` text
ssh root@<cvp_ip>
su - cvp
```

### Step 4: Install the rpm to add the vane-cvp extension to CVP

!!! warning
    If upgrading a previously installed vane-cvp extension,
    skip to section 4b below regarding upgrades.

``` text
cvpi install -f <rpm_package>
```

!!! example
    cvpi install -f vane-cvp-0.91-1.noarch.rpm

#### Step 4b: Upgrade installation

!!! warning
    If not doing an upgrade to an existing vane-cvp extension, skip to Step 5.

To upgrade an existing vane-cvp installation, before installing the new
rpm package, the old rpm package must first be uninstalled and the vane-cvp
container must be removed from the container library. If the old container
is not removed, the newer container will not be installed correctly and when
the vane-cvp extension is run, the old container will be used instead.

**First uninstall the vane-cvp extension from the CVP host.**

``` text
cvpi uninstall -f vane-cvp
```

The next operation is optional. If desired, remove the vane-data
directory from the CVP host system. This will essentially create a
“fresh install” state for the updated vane-cvp extension.

!!! warning

    If there is data in the shared directory that is going to be
    needed in the updated environment, do not do this next command,
    leave the existing data, which will be shared with the new container
    when it is started.

``` text
rm -rf /cvpi/apps/vane-cvp/vane-data
```

**Remove the previous container image from the image registry on the CVP host.**

 This is done using the nerdctl utility run as the root user.
 Running nerdctl with sudo does not seem to produce the desired
 results, so we need to switch from the cvp user to the root user,
 then run the nerdctl command, then switch back to the cvp user
 to continue our regular operations.

!!! info
    The commands shown below should produce a block of output
    that indicates images have been removed, which
    usually begins with a line that states

     * Untagged: docker.io/library/vane-cvp:latest@sha256:<some-hash>
       followed by a block of lines that begin with Deleted: sha256:<hash>. 

``` text
sudo -i     (to change to the root user for the next command)
nerdctl rmi -f `nerdctl images | grep vane-cvp | awk '{print $3}'
exit        (to switch back to the cvp user again)
```

**Finally, install the updated vane-cvp extension as before.**

``` text
cvpi install -f <rpm_package>
```

From this point on, the upgrade of the vane-cvp extension is complete.
The extension will need to be enabled and started as before, and can
be exec’ed into after that. Continue with Step 5.

### Step 5: Enable the vane-cvp extension

``` text
cvpi enable -f vane-cvp
```

### Step 6: Start the vane-cvp extension

``` text
cvpi start -f vane-cvp
```

Check the status of the package by running : ```cvpi status -f vane-cvp```

### Step 7: Get a command shell in the vane-cvp extension container

To run Vane, we need to be in the container that is running the
vane-cvp extension. To enter the vane-cvp container, exec into the
container using kubectl.

``` text
kubectl exec -it <vane-cvp-container-id> -- /bin/bash
```

To get the *vane-cvp-container-id* start typing ‘vane’
and hit tab to trigger the tab-completion which should
fill in the name of the vane-cvp container. The container
id should be something like vane-cvp-667699998-m42gh.
If returning to a previously initialized vane-cvp setup,
you will need to first log into the CVP host, then change
to the cvp user before exec’ing into the vane-cvp container.

``` text
ssh root@<cvp_ip>
su - cvp
kubectl exec -it <vane-cvp-container-id> -- /bin/bash
```

### Step 8: Activate Vane shell

After the above command, if everything is successful
you will be greeted with the prompt, after which if you
type **activate**, you will enter the vane virtual environment

### Step 9: Executing Vane

Now you are good to run Vane on the Nrfu tests

``` text
vane --nrfu
```

Executing the above command will prompt for EOS device/CVP
credentials (which should be the same)

After entering those, it will identify that you are running
Vane as a CVP application and show the following prompt

``` text
Using CVP to gather duts data
```

Given CVP authentication is successful, it will prompt you the following:

``` text
Do you want to specify a test case directory [y|n]: 
```

If you answer n/no, it will default to the nrfu_tests folder
in vane, if yes it will further prompt you

``` text
    Please specify test case directory <path/to/test case dir> (Use tab for autocompletion):
```

!!! success

    After which Vane will start executing the test cases on
    your devices managed through CVP
