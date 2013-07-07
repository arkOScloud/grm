# Genesis Repository Manager

A server for managing the Genesis plugin repository. Clients can download the repo list from the server with the latest versions of all plugins, then request and download the plugin as needed.

To run, your `settings.py` must have the following settings:

* `HOSTNAME`: the base address of your Django server
* `MEDIA_ROOT`
* `PLUGIN_ROOT` to store plugins
* `TEMP_FOLDER` to store extracted files as they are read
