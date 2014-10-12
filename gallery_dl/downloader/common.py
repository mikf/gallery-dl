import os

class BasicDownloader():

    max_tries = 5

    def download(self, url, path):
        with open(path, "wb") as file:
            try:
                return self.download_impl(url, file)
                file.close()
            except:
                # make sure to remove file if download failed
                os.unlink(path)
                raise

    @staticmethod
    def print_error(file, error, tries, max_tries=5):
        if tries == 1 and hasattr(file, "name"):
            print("\r\033[1;31m", file.name, sep="")
        print("\033[0;31m[Error]\033[0m ", error, " (", tries, "/", max_tries, ")", sep="")
