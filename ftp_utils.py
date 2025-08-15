"""Module providing helper functions for FTP operations."""

import logging
from ftplib import FTP, error_perm, error_temp
from pathlib import Path

logger = logging.getLogger(__name__)


def is_mlsd_supported(ftp: FTP) -> bool:
    """
    Check if the FTP server supports the MLSD command.

    Args:
        ftp: FTP connection

    Returns:
        bool: True if MLSD is supported, False otherwise
    """
    try:
        # Try to execute MLSD on the current directory
        # We only need to see if it executes without error
        list(ftp.mlsd(".", facts=["type"]))
        return True
    except (error_perm, error_temp) as e:
        logger.debug("MLSD not supported: %s", e)
        return False
    except Exception as e:  # pylint: disable=broad-except
        logger.debug("Unexpected error when testing MLSD support: %s", e)
        return False


def is_remote_folder(ftp: FTP, name: str) -> bool:
    """
    Check if remote path is a folder.

    Args:
        ftp: FTP connection
        name: Remote path name

    Returns:
        bool: True if path is a folder, False if file
    """
    try:
        # Try using MLSD command first (RFC 3659)
        for item, facts in ftp.mlsd(path="", facts=["type"]):
            if item == name:
                return facts.get("type") == "dir"
    except (error_perm, error_temp) as e:
        logger.debug("MLSD not supported or failed for %s: %s", name, e)
        # Fallback to other methods
        try:
            # Try to change to the directory - if it works, it's a directory
            original_dir = ftp.pwd()
            ftp.cwd(name)
            ftp.cwd(original_dir)  # Change back to original directory
            return True
        except (error_perm, error_temp):
            # If we can't change to it, it's likely a file
            pass

        # Try using NLST to check if it's a directory
        try:
            # For a directory, NLST should list its contents
            # For a file, NLST would typically fail
            current_list = ftp.nlst()
            if name in current_list:
                # Try to list the contents of the item
                try:
                    ftp.nlst(name)
                    return True  # It's a directory if we can list its contents
                except (error_perm, error_temp):
                    return False  # It's a file if we can't list its contents
        except (error_perm, error_temp):
            pass

    return False


def get_ftp_folder_size(ftp: FTP, remote_path: str) -> int:
    """
    Recursively calculate total size of an FTP folder including subdirectories.

    This function first tries to use MLSD (RFC 3659) which provides size information directly.
    If MLSD is not supported, it falls back to using NLST and SIZE commands.

    Args:
        ftp: FTP connection
        remote_path: Remote folder path

    Returns:
        int: Total size in bytes
    """
    total_size = 0

    if is_mlsd_supported(ftp):
        # Use MLSD method (modern approach with size information)
        try:
            for item, facts in ftp.mlsd(remote_path, facts=["type", "size"]):
                if facts["type"] == "dir":
                    # Recursively get size of subdirectories
                    total_size += get_ftp_folder_size(
                        ftp, f"{remote_path}/{item}"
                    )
                elif "size" in facts:
                    total_size += int(facts["size"])
            return total_size
        except (error_perm, error_temp) as e:
            logger.debug(
                "MLSD failed for %s despite being supported: %s",
                remote_path,
                e,
            )
            # Fall through to fallback method

    # Fallback to using NLST and SIZE commands
    try:
        original_dir = ftp.pwd()

        # Change to the target directory
        ftp.cwd(remote_path)

        # List all items in the directory
        try:
            items = ftp.nlst()
        except (error_perm, error_temp):
            # If NLST fails, directory might be empty
            items = []

        # Process each item
        for item in items:
            try:
                # Try to change to the item (to check if it's a directory)
                ftp.cwd(item)
                # If successful, it's a directory, so change back and recurse
                ftp.cwd(original_dir)
                total_size += get_ftp_folder_size(ftp, f"{remote_path}/{item}")
            except (error_perm, error_temp):
                # If changing directory fails, it's likely a file
                # Try to get its size
                try:
                    size = ftp.size(item)
                    if size is not None:
                        total_size += size
                except (error_perm, error_temp):
                    # If we can't get the size, we skip this item
                    logger.debug("Could not get size for item: %s", item)

        # Return to the original directory
        ftp.cwd(original_dir)
    except (error_perm, error_temp) as fallback_error:
        logger.debug(
            "Fallback method failed for %s: %s", remote_path, fallback_error
        )
        raise

    return total_size


def download_ftp_file(
    ftp: FTP,
    remote_file: str,
    local_file: Path,
    progress_callback=None,
    total_size=0,
    current_size=0,
) -> int:
    """
    Download a single file from FTP server.

    Args:
        ftp: FTP connection
        remote_file: Remote file path
        local_file: Local file path
        progress_callback: Callback function for progress updates
        total_size: Total size of all files (for progress)
        current_size: Current downloaded size

    Returns:
        Updated current size after download
    """
    logger.info("Downloading file %s to %s", remote_file, local_file)

    # Open file in binary write mode using with statement
    with open(local_file, "wb") as f:

        def write_callback(data, file=f, total_size=total_size):
            nonlocal current_size
            current_size += len(data)
            file.write(data)
            if progress_callback:
                progress_callback(
                    current_size,
                    total_size,
                    message=f"Downloading file: {remote_file} to {local_file} - {current_size}/{total_size} bytes",
                )

        ftp.retrbinary(f"RETR {remote_file}", write_callback)
    return current_size


def download_ftp_folder(
    ftp: FTP,
    remote_path: str,
    local_base_path: str,
    progress_callback=None,
    total_size=0,
    current_size=0,
) -> int:
    """
    Recursively download a folder from FTP server.

    This function first checks if MLSD is supported. If so, it uses MLSD (RFC 3659)
    which provides type information directly. Otherwise, it falls back to using
    NLST and CWD commands to determine file and directory types.

    Args:
        ftp: FTP connection
        remote_path: Remote folder path
        local_base_path: Base path where to create the folder
        progress_callback: Callback function for progress updates
        total_size: Total size of all files (for progress)
        current_size: Current downloaded size

    Returns:
        Total size of downloaded files
    """
    # Extract folder name from remote path and create local path
    remote_folder_name = Path(remote_path).name
    local_path = Path(local_base_path) / remote_folder_name

    logger.info("Downloading folder %s to %s", remote_path, local_path)

    if not local_path.exists():
        local_path.mkdir(parents=True)

    if is_mlsd_supported(ftp):
        # Use MLSD method (modern approach with type information)
        try:
            for item in ftp.mlsd(remote_path):
                name, facts = item
                if facts["type"] == "dir":
                    # Recursively download subdirectories
                    new_remote = f"{remote_path}/{name}"
                    current_size = download_ftp_folder(
                        ftp,
                        new_remote,
                        str(
                            local_path
                        ),  # Convert Path to str for recursive calls
                        progress_callback,
                        total_size,
                        current_size,
                    )
                else:
                    # Download file
                    remote_file = f"{remote_path}/{name}"
                    local_file = local_path / name

                    current_size = download_ftp_file(
                        ftp,
                        remote_file,
                        local_file,
                        progress_callback,
                        total_size,
                        current_size,
                    )
        except (error_perm, error_temp) as e:
            logger.debug(
                "MLSD failed for %s despite being supported: %s",
                remote_path,
                e,
            )
            # Fall through to fallback method
    else:
        # Fallback to using NLST and CWD commands
        try:
            original_dir = ftp.pwd()

            # Change to the target directory
            ftp.cwd(remote_path)

            # List all items in the directory
            try:
                item_names = ftp.nlst()
            except (error_perm, error_temp):
                # If NLST fails, directory might be empty
                item_names = []

            # Process each item
            for name in item_names:
                try:
                    # Try to change to the item (to check if it's a directory)
                    ftp.cwd(name)
                    # If successful, it's a directory, so change back and recurse
                    ftp.cwd("..")  # Go back one level
                    new_remote = f"{remote_path}/{name}"
                    current_size = download_ftp_folder(
                        ftp,
                        new_remote,
                        str(
                            local_path
                        ),  # Convert Path to str for recursive calls
                        progress_callback,
                        total_size,
                        current_size,
                    )
                except (error_perm, error_temp):
                    # If changing directory fails, it's likely a file
                    # Download the file
                    remote_file = f"{remote_path}/{name}"
                    local_file = local_path / name

                    # Change back to the parent directory before downloading
                    # We need to go back to the original remote_path directory
                    ftp.cwd("..")

                    current_size = download_ftp_file(
                        ftp,
                        remote_file,
                        local_file,
                        progress_callback,
                        total_size,
                        current_size,
                    )

            # Return to the original directory
            ftp.cwd(original_dir)
        except (error_perm, error_temp) as fallback_error:
            logger.error(
                "Fallback method failed for %s: %s",
                remote_path,
                fallback_error,
            )
            raise

    return current_size


def download_ftp(
    ftp: FTP,
    remote_path: str,
    local_base_path: str,
    progress_callback=None,
) -> None:
    """
    Download a file or folder from FTP server automatically detecting the type.

    Args:
        ftp: FTP connection
        remote_path: Remote file or folder path
        local_base_path: Base path where to create the file or folder
        progress_callback: Callback function for progress updates

    Returns:
        None
    """
    try:
        # Check if it's a folder
        if is_remote_folder(ftp, remote_path):
            logger.info(
                "Starting folder download task for %s (%s)",
                remote_path,
                local_base_path,
            )

            # Calculate total size for progress tracking
            total_size = get_ftp_folder_size(ftp, remote_path)

            if total_size == 0:
                raise FileNotFoundError(
                    f"Folder {remote_path} is empty on FTP server "
                    f"{ftp.host}:{ftp.port}/{ftp.pwd()}"
                )

            # Call initial progress update
            if progress_callback:
                progress_callback(
                    0, total_size, message="Starting folder download"
                )

            download_ftp_folder(
                ftp,
                remote_path,
                local_base_path,
                progress_callback=progress_callback,
                total_size=total_size,
            )
        else:
            # It's a file, use download_ftp_file
            logger.info(
                "Starting file download task for %s (%s)",
                remote_path,
                local_base_path,
            )
            local_path = Path(local_base_path) / Path(remote_path).name

            total_size = ftp.size(remote_path)
            if total_size is None:
                raise FileNotFoundError(
                    f"File {remote_path} not found on FTP server "
                    f"{ftp.host}:{ftp.port}/{ftp.pwd()}"
                )

            # Call initial progress update
            if progress_callback:
                progress_callback(
                    0, total_size, message="Starting file download"
                )

            download_ftp_file(
                ftp,
                remote_path,
                local_path,
                progress_callback=progress_callback,
                total_size=total_size,
            )
    except Exception as e:
        logger.error(
            "Error downloading %s: %s",
            remote_path,
            e,
            exc_info=True,
        )
        raise e


def upload_ftp_file(
    ftp: FTP,
    local_file: Path,
    remote_file: str,
    progress_callback=None,
    total_size=0,
    current_size=0,
) -> int:
    """
    Upload a single file to FTP server.

    Args:
        ftp: FTP connection
        local_file: Local file path
        remote_file: Remote file path
        progress_callback: Callback function for progress updates
        total_size: Total size of all files (for progress)
        current_size: Current uploaded size

    Returns:
        Updated current size after upload
    """

    logger.info("Uploading file %s to %s", local_file, remote_file)

    def upload_callback(data, total_size=total_size):
        nonlocal current_size
        current_size += len(data)
        if progress_callback:
            progress_callback(
                current_size,
                total_size,
                message=f"Starting file upload: {local_file.name} to {remote_file} - {current_size}/{total_size} bytes",
            )

    with open(local_file, "rb") as f:
        ftp.storbinary(f"STOR {remote_file}", f, callback=upload_callback)
    return current_size


def upload_ftp_folder(
    ftp: FTP,
    local_path: str,
    remote_base_path: str,
    progress_callback=None,
    total_size=0,
    current_size=0,
) -> int:
    """
    Recursively upload a folder to FTP server.

    Args:
        ftp: FTP connection
        local_path: Local folder path to upload
        remote_base_path: Base path on remote server where to upload the folder
        progress_callback: Callback function for progress updates
        total_size: Total size of all files (for progress)
        current_size: Current uploaded size

    Returns:
        Total size of uploaded files
    """
    # Extract folder name from local path and create remote path
    local_folder_name = Path(local_path).name
    remote_path = (
        f"{remote_base_path}/{local_folder_name}"
        if remote_base_path
        else local_folder_name
    )

    logger.info("Uploading folder %s to %s", local_path, remote_path)

    try:
        # Try to create the remote directory
        ftp.mkd(remote_path)
    except error_perm:
        # Directory might already exist, that's fine
        pass

    # Save current directory and change to the remote directory
    original_cwd = ftp.pwd()
    ftp.cwd(remote_path)

    try:
        # Iterate through local directory contents
        for item in Path(local_path).iterdir():
            if item.is_dir():
                # Recursively upload subdirectories
                current_size = upload_ftp_folder(
                    ftp,
                    str(item),
                    "",  # Empty string as we've already changed to the remote directory
                    progress_callback,
                    total_size,
                    current_size,
                )
            else:
                # Upload file
                current_size = upload_ftp_file(
                    ftp,
                    item,
                    item.name,
                    progress_callback,
                    total_size,
                    current_size,
                )
    finally:
        # Always return to the original directory
        ftp.cwd(original_cwd)

    return current_size


def upload_ftp(
    ftp: FTP,
    local_path: str,
    remote_base_path: str,
    progress_callback=None,
) -> None:
    """
    Upload a file or folder to FTP server automatically detecting the type.

    Args:
        ftp: FTP connection
        local_path: Local file or folder path
        remote_base_path: Base path on remote server where to upload
        progress_callback: Callback function for progress updates (current, total)

    Returns:
        None
    """
    try:
        path = Path(local_path)

        # Check if it's a folder
        if path.is_dir():
            logger.info(
                "Starting folder upload task for %s",
                local_path,
            )

            # Calculate total size for progress tracking
            total_size = 0
            for file_path in path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size

            if total_size == 0:
                raise FileNotFoundError(
                    f"Folder {local_path} is empty on local server"
                )

            # Call initial progress update
            if progress_callback:
                progress_callback(
                    0, total_size, message="Starting folder upload"
                )

            upload_ftp_folder(
                ftp,
                local_path,
                remote_base_path,
                progress_callback=progress_callback,
                total_size=total_size,
            )
        else:
            # It's a file, use upload_ftp_file
            logger.info(
                "Starting file upload task for %s",
                local_path,
            )

            total_size = path.stat().st_size
            if total_size == 0:
                raise FileNotFoundError(
                    f"File {local_path} not found or is empty on local server"
                )

            # Call initial progress update
            if progress_callback:
                progress_callback(
                    0, total_size, message="Starting file upload"
                )

            upload_ftp_file(
                ftp,
                path,
                (
                    path.name
                    if not remote_base_path
                    else f"{remote_base_path}/{path.name}"
                ),
                progress_callback=progress_callback,
                total_size=total_size,
            )
    except Exception as e:
        logger.error(
            "Error uploading %s: %s",
            local_path,
            e,
            exc_info=True,
        )
        raise e
