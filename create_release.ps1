# create_release.ps1
# Jalankan dari folder proyek yang berisi folder dist/

# Masukkan token (akan disimpan di ENV untuk session ini)
$env:GITHUB_TOKEN = Read-Host -Prompt 'Paste your GitHub Personal Access Token (scope: repo)'

# Konfigurasi release
$owner = 'RafifFarandHariri'
$repo  = 'Universal-Converter'
$tag   = Read-Host -Prompt 'Tag name (e.g. v1.0.0) [default v1.0.0]'
if ([string]::IsNullOrWhiteSpace($tag)) { $tag = 'v1.0.0' }
$name  = Read-Host -Prompt 'Release name [default same as tag]'
if ([string]::IsNullOrWhiteSpace($name)) { $name = $tag }
$body  = Read-Host -Prompt 'Release notes/body [optional]'

# Create release
$payload = @{
  tag_name = $tag
  name = $name
  body = $body
  draft = $false
  prerelease = $false
} | ConvertTo-Json

$headers = @{ Authorization = "token $env:GITHUB_TOKEN"; 'User-Agent' = 'PowerShell' }

$release = Invoke-RestMethod -Method Post -Uri "https://api.github.com/repos/$owner/$repo/releases" -Headers $headers -Body $payload -ContentType 'application/json'
$releaseId = $release.id
Write-Host "Created release: $($release.html_url)"

# Upload assets from dist/
Get-ChildItem -Path .\dist\* -File | ForEach-Object {
  $file = $_.FullName
  $filename = $_.Name
  Write-Host "Uploading $filename ..."
  $uploadUrl = "https://uploads.github.com/repos/$owner/$repo/releases/$releaseId/assets?name=$([System.Uri]::EscapeDataString($filename))"
  Invoke-RestMethod -Method Post -Uri $uploadUrl -Headers $headers -InFile $file -ContentType 'application/octet-stream'
  Write-Host "Uploaded $filename"
}

# Clean token from env for safety
Remove-Item Env:\GITHUB_TOKEN
Write-Host "Done."