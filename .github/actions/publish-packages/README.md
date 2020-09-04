# Action: Publish packages

This action spawns a Docker container with the `matteodelabre/toltec` image, builds the whole repository, and uploads it to a remote server through rsync.

## Environment

Variable name       | Description
--------------------|---------------------------
`REMOTE`            | Remote server to which the artifacts will be uploaded. Should be in the `user@host` format.
`REMOTE_PATH`       | Path to the folder in the remote server to which the artifacts will be uploaded.
`SSH_PRIVATE_KEY`   | Private key used for authenticating to the remote server.
`SSH_KNOWN_HOSTS`   | Known public key of the remote server.
