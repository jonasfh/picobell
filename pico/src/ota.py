# ota.py
import config

class OTAUpdater:
    def __init__(self, hal, current_version, on_progress=None):
        self.hal = hal
        self.current_version = current_version
        self.new_version = None
        self.files_to_update = []
        self.on_progress = on_progress

    def check_for_updates(self):
        """Checks server for a newer version. Returns True if update available."""
        print(f"[OTA] Checking for updates... (Current: {self.current_version})")
        response = self.hal.http_get(config.URL_OTA_VERSION)
        if not response:
            print("[OTA] Failed to fetch version info")
            return False

        try:

            data = response.json()
            response.close()

            latest_version = data.get("fw_version")
            if not latest_version:
                return False

            print(f"[OTA] Latest version: {latest_version}")

            # Simple string comparison or integer comparison if version is strictly int
            # Assuming semantic versioning or integer build number.
            # For robustness, simply check inequality or implement semver parsing if needed.
            # Here: string inequality check is simple but risky for "1.10" vs "1.2".
            # Better to assume user manages versioning strictly increasing.
            if latest_version != self.current_version:
                self.new_version = latest_version

                # Fetch file list from separate endpoint
                print(f"[OTA] Fetching file list for version {latest_version}...")
                response_files = self.hal.http_get(config.URL_OTA_FILES) # Need to add this to config
                if response_files:
                     try:
                         self.files_to_update = response_files.json()
                         response_files.close()
                         return True
                     except Exception as e:
                         print(f"[OTA] Error parsing file list: {e}")
                         response_files.close()
                else:
                    print("[OTA] Failed to fetch file list")

                return False

        except Exception as e:
            print(f"[OTA] Error parsing version info: {e}")

        return False

    def update_firmware(self):
        """Downloads files and overwrites them."""
        if not self.new_version or not self.files_to_update:
            print("[OTA] No update to apply")
            return False

        print(f"[OTA] Starting update to {self.new_version}")

        success = True
        total = len(self.files_to_update)
        for i, file_info in enumerate(self.files_to_update):
            filename = file_info.get("name")
            url = file_info.get("url")

            if not filename or not url:
                continue

            # Handle relative URLs (default behavior now)
            if not url.startswith("http"):
                 url = config.BASE_URL + url

            print(f"[OTA] Downloading {filename}...")
            if self.on_progress:
                self.on_progress(i + 1, total, False)

            if not self._download_and_save(url, filename):
                print(f"[OTA] Failed to download {filename}")
                success = False
                break

        if success:
            print("[OTA] Update complete. Rebooting...")
            if self.on_progress:
                self.on_progress(total, total, True)
            return True
        else:
            print("[OTA] Update failed.")
            return False

    def _download_and_save(self, url, filename):
        response = self.hal.http_get(url)
        if not response:
            return False

        # Write to file
        try:
            # We can't use hal.save_json here as it might be raw code
            # We need raw file writing in HAL? Or just use open() if we assume HAL environment supports it?
            # HAL wraps 'open', but let's stick to standard python open which works on Pico and Host (if path valid)
            # But HAL should ideally handle paths.
            # For simplicity, we write to root.

            # Note: response.text or response.content depends on implementation.
            # urequests response object has .text and .content
            content = response.text

            with open(filename, "w") as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"[OTA] Write error: {e}")
            return False
        finally:
            response.close()
