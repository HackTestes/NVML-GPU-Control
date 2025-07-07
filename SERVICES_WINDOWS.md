# Windows startup services

## Setting up startup tasks

> [!CAUTION]
> You should secure the files under an admin only folder, so only authorized programs can modify the scripts

This section will present some simple commands to setup services or tasks that start as admin and run the configured program with the configured settings. 

But first, please check Microsoft's documentation:

* [Task scheduler](https://learn.microsoft.com/en-us/windows/win32/taskschd/task-scheduler-start-page)
* [Task scheduler command line](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/schtasks)

Since this program does not implement the service API, it will be using scheduled tasks to run at startup. There will be presented a GUI and a command line method.

### Import and edit the task

Take a look at the [xml task file](windows_config/User%20NVIDIA%20GPU%20Control%20Task.xml) and make the necessary changes in the [Arguments](windows_config/User%20NVIDIA%20GPU%20Control%20Task.xml#L44)

In an administrator prompt, run the following command

```cmd
schtasks /create /xml "C:\path\to\task\file\User NVIDIA GPU Control Task.xml" /tn "CaioH NVIDIA GPU Control"
```

Or you can use the GUI interface and import the xml (also needs to be running as admin): Click on "import task" -> select the xml file

### Removing the task

In an administrator prompt, run the following command

```cmd
schtasks /delete /tn "CaioH NVIDIA GPU Control"
```

Or use the GUI (needs admin): navigate the tasks in the bottom of the window -> update tasks -> look for "CaioH NVIDIA GPU Control" -> click on it and then on "delete"