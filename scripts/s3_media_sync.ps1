param(
  [Parameter(Mandatory=$true)][string]$BucketName,
  [string]$MediaPath = "media",
  [switch]$DryRun
)

if (!(Test-Path $MediaPath)) {
  Write-Error "No se encontró la carpeta media en: $MediaPath"
  exit 1
}

$dest = "s3://$BucketName/media/"
$cmd = @("s3", "sync", $MediaPath, $dest, "--exclude", "*.tmp")
if ($DryRun) { $cmd += "--dryrun" }

Write-Host "Ejecutando: aws $($cmd -join ' ')"
aws @cmd
if ($LASTEXITCODE -ne 0) {
  Write-Error "Falló sync a S3"
  exit $LASTEXITCODE
}

Write-Host "Sync completado correctamente."
