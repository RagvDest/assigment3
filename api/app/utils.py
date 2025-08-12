import hashlib
import os


def allowed_file(filename):
    """
    Checks if the format for the file received is acceptable. For this
    particular case, we must accept only image files. This is, files with
    extension ".png", ".jpg", ".jpeg" or ".gif".

    Parameters
    ----------
    filename : str
        Filename from werkzeug.datastructures.FileStorage file.

    Returns
    -------
    bool
        True if the file is an image, False otherwise.
    """
    # TODO: Implement the allowed_file function
    # Current implementation will return True for any file
    # Check if the file extension of the filename received is in the set of allowed extensions (".png", ".jpg", ".jpeg", ".gif")
    allowed_extensions = {".png", ".jpg", ".jpeg", ".gif"}
    _, ext = os.path.splitext(filename)
    if ext.lower() in allowed_extensions:
        return True
    else:
        return False


async def get_file_hash(file):
    """
    Returns a new filename based on the file content using MD5 hashing.
    It uses hashlib.md5() function from Python standard library to get
    the hash.

    Parameters
    ----------
    file : werkzeug.datastructures.FileStorage
        File sent by user.

    Returns
    -------
    str
        New filename based in md5 file hash.
    """
    # TODO: Implement the get_file_hash function
    # Current implementation will return the original file name.

    # Read file content and generate md5 hash (Check: https://docs.python.org/3/library/hashlib.html#hashlib.md5)
    await file.seek(0)  # Ensure we read from the beginning of the file
    file_content = await file.read()
    print(f"Type of file_content: {type(file_content)}")
    file_hash = hashlib.md5(file_content).hexdigest()
    # Return file pointer to the beginning
    await file.seek(0)
    # Add original file extension
    _, ext = os.path.splitext(file.filename)
    file_hash = f"{file_hash}{ext}"

    return file_hash
