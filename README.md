# Self-updating Application

This is a simple sample application to demonstrate a workflow where small tools can automatically update themselves to the latest version on startup.

The update mechanism is based on Git tags. When the application starts, it checks for a new version by looking at the latest Git tag in the repository. If a newer version is available, it will be downloaded and the application will restart.
