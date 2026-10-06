
# Printer Troubleshooting Runbook
## Issue: Queue Stuck
1. Check device status via `check_device_status`
2. If status contains 'queue stuck', run `clear_print_queue`
3. Verify status again
4. If fixed, close ticket with note
