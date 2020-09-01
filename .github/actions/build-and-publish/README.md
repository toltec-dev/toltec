# Build and publish action

This action spawns a Docker container with the `matteodelabre/toltec` image, builds the whole repository, and uploads it to a remote server through rsync.

## Environment

Variable name       | Description
--------------------|---------------------------
`REMOTE_PATH`       | Path to the remote server to which the artifacts will be uploaded. Should be in the `user@host:/path` format.
`SSH_PRIVATE_KEY`   | Private key used for authenticating to the remote server.
`SSH_KNOWN_HOSTS`   | Known public key of the remote server.
