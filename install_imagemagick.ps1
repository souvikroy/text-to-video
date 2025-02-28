# Download ImageMagick installer
$url = "https://imagemagick.org/archive/binaries/ImageMagick-7.1.1-27-Q16-HDRI-x64-dll.exe"
$output = "ImageMagick-installer.exe"
Write-Host "Downloading ImageMagick..."
Invoke-WebRequest -Uri $url -OutFile $output

# Install ImageMagick
Write-Host "Installing ImageMagick..."
Start-Process -FilePath .\$output -ArgumentList "/SILENT /SP-" -Wait

# Clean up
Remove-Item $output
Write-Host "ImageMagick installation completed!"
