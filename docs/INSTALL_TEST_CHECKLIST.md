# ClearWork Install Test Checklist

Use this checklist for external Windows installer testing of `ClearWork-Setup-0.1.0.exe`.

1. Install `ClearWork-Setup-0.1.0.exe`.
2. Launch ClearWork from the Start Menu.
3. Verify the application icon in the shortcut and running window.
4. Verify the login / first-run security screen opens correctly.
5. Create or open the local database.
6. Create a test employee.
7. Restart the program.
8. Verify that the data is still available after restart.
9. Create a backup.
10. Close the program.
11. Reboot the PC.
12. Launch ClearWork again.
13. Verify that the data is still available after reboot.
14. Uninstall the program using the uninstaller.
15. Verify that Start Menu and desktop shortcuts are removed.
16. Verify that user-created `data/` and `logs/` folders remain.
17. Install ClearWork again.
18. Verify that the previous local database is picked up.
19. Verify report generation.
20. Verify the basic settings flow.
