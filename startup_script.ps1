# Specify directory
$path = 'F:\school\jaar4\the lighthouse internship\AVInsight'

# Change to directory
Set-Location $path

# Create a firewall rule for the app's port
Start-Process -FilePath "powershell.exe" -ArgumentList "-Command", 'New-NetFirewallRule -DisplayName "MyAppRule" -Direction Inbound -LocalPort 5000 -Protocol UDP -Action Allow'

# Open the web page
# Start-Process 'http://127.0.0.1:5000'

# Minimize current PowerShell window
Add-Type -TypeDefinition @"
    using System;
    using System.Runtime.InteropServices;

    public class Window {
        [DllImport("user32.dll")]
        public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    }
"@
$consolePtr = (Get-Process -Id $pid).MainWindowHandle
[void] [Window]::ShowWindow($consolePtr, 2)

# Start the app
.\app.exe $path
