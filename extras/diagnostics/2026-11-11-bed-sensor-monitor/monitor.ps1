$ErrorActionPreference = 'Stop'
$baseUrl = 'http://192.168.1.43:7125'
$samplePath = Join-Path $PSScriptRoot 'samples.csv'
$samples = [System.Collections.Generic.List[object]]::new()
$lastTemperature = $null
$lastSampleTime = $null
$reachedAt = $null
$startedAt = [DateTime]::UtcNow
$nextReport = $startedAt
$failure = $null

function Get-PrinterStatus {
    return (Invoke-RestMethod -Uri "$baseUrl/printer/objects/query?print_stats&heater_bed&configfile" -TimeoutSec 8).result.status
}

try {
    $info = (Invoke-RestMethod -Uri "$baseUrl/printer/info" -TimeoutSec 8).result
    $status = Get-PrinterStatus
    if ($info.state -ne 'ready' -or $status.print_stats.state -ne 'standby') { throw 'Printer is not ready and standby.' }
    if ($status.configfile.settings.heater_bed.heater_pin -ne 'PA5') { throw 'Unexpected bed SSR pin.' }
    if ($status.configfile.settings.heater_bed.sensor_pin -ne 'PB0') { throw 'Unexpected bed sensor pin.' }

    if ($status.heater_bed.target -ne 100) { throw 'Bed is not already at target 100 C.' }
    Write-Output "ATTACHED $([DateTime]::UtcNow.ToString('o')) target=100"

    while ($true) {
        $now = [DateTime]::UtcNow
        if (($now - $startedAt).TotalMinutes -gt 25) { throw 'Test timed out.' }
        $info = (Invoke-RestMethod -Uri "$baseUrl/printer/info" -TimeoutSec 8).result
        $status = Get-PrinterStatus
        $bed = $status.heater_bed
        $temp = [double]$bed.temperature
        $samples.Add([pscustomobject]@{
            utc_time = $now.ToString('o')
            temperature = $temp
            target = [double]$bed.target
            power = [double]$bed.power
            print_state = $status.print_stats.state
            klippy_state = $info.state
        })
        if ($info.state -ne 'ready' -or $status.print_stats.state -ne 'standby') { throw 'Printer state changed during test.' }
        if ([double]$bed.target -eq 0 -and [double]$bed.power -eq 0) {
            Write-Output "OPERATOR_STOP $($now.ToString('o')) samples=$($samples.Count)"
            break
        }
        if ([double]$bed.target -ne 100) { throw 'Bed target changed to an unexpected value.' }
        if ($temp -gt 110 -or $temp -lt 0) { throw "Bed reading outside safe test range: $temp C." }
        if ($null -ne $lastTemperature -and $null -ne $lastSampleTime) {
            $dt = ($now - $lastSampleTime).TotalSeconds
            if ($dt -le 4 -and [math]::Abs($temp - $lastTemperature) -ge 5) {
                throw "Implausible bed step: $lastTemperature to $temp C in $([math]::Round($dt, 1)) s."
            }
        }
        if ($null -eq $reachedAt -and $temp -ge 99) {
            $reachedAt = $now
            Write-Output "REACHED $($now.ToString('o')) temperature=$temp"
        }
        if ($null -ne $reachedAt -and ($now - $reachedAt).TotalMinutes -ge 10) { break }
        if ($now -ge $nextReport) {
            Write-Output "PROGRESS $($now.ToString('o')) temperature=$temp target=$($bed.target) power=$($bed.power) samples=$($samples.Count)"
            $nextReport = $now.AddSeconds(30)
        }
        $lastTemperature = $temp
        $lastSampleTime = $now
        Start-Sleep -Seconds 1
    }
    Write-Output "COMPLETE $([DateTime]::UtcNow.ToString('o')) samples=$($samples.Count)"
} catch {
    $failure = $_.Exception.Message
    Write-Output "ABORT $([DateTime]::UtcNow.ToString('o')) reason=$failure"
} finally {
    $samples | Export-Csv -LiteralPath $samplePath -NoTypeInformation -Encoding utf8
    try {
        $status = Get-PrinterStatus
        Write-Output "FINAL target=$($status.heater_bed.target) power=$($status.heater_bed.power) temperature=$($status.heater_bed.temperature)"
    } catch {
        Write-Output "FINAL_STATUS_FAILED $($_.Exception.Message)"
    }
}
if ($null -ne $failure) { exit 1 }
