[CmdletBinding()]
param(
    [switch]$Quick,
    [int]$BatchTimeoutSec = 360,
    [int]$OverallTimeoutSec = 1800
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

$env:NODE_NO_WARNINGS = "1"
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

Write-Host "==> Checking Pi skills consistency (npm run check:pi)"
npm run check:pi
if ($LASTEXITCODE -ne 0) {
    throw "check:pi failed with exit code $LASTEXITCODE"
}

function Invoke-FreshBatch {
    param(
        [string]$BatchName,
        [string[]]$Files,
        [int]$TimeoutSeconds
    )

    Write-Host "==> [Batch: $BatchName] running $($Files.Count) file(s): $($Files -join ' ')"
    $sw = [System.Diagnostics.Stopwatch]::StartNew()

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "node"
    $argList = @("--test", "--test-concurrency=1") + $Files
    $psi.Arguments = ($argList | ForEach-Object { if ($_ -match '\s') { "`"$_`"" } else { $_ } }) -join " "
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $false
    $psi.RedirectStandardError = $false

    $proc = [System.Diagnostics.Process]::Start($psi)
    $completed = $proc.WaitForExit($TimeoutSeconds * 1000)
    $sw.Stop()
    $duration = [math]::Round($sw.Elapsed.TotalSeconds, 1)

    if (-not $completed) {
        try {
            $proc.Kill($true)
        } catch {}
        Write-Warning "[-] Batch [$BatchName] TIMED OUT after ${TimeoutSeconds}s (incomplete, duration: ${duration}s)"
        return [PSCustomObject]@{
            Name = $BatchName
            Files = $Files
            Status = "TIMEOUT"
            DurationSec = $duration
            ExitCode = -1
        }
    }

    if ($proc.ExitCode -ne 0) {
        Write-Warning "[-] Batch [$BatchName] FAILED with exit code $($proc.ExitCode) (duration: ${duration}s)"
        return [PSCustomObject]@{
            Name = $BatchName
            Files = $Files
            Status = "FAIL"
            DurationSec = $duration
            ExitCode = $proc.ExitCode
        }
    }

    Write-Host "[+] Batch [$BatchName] PASSED in ${duration}s"
    return [PSCustomObject]@{
        Name = $BatchName
        Files = $Files
        Status = "PASS"
        DurationSec = $duration
        ExitCode = 0
    }
}

if ($Quick) {
    Write-Host "==> Quick test pass (focused Windows and Pi packaging tests)"
    $quickRes = Invoke-FreshBatch -BatchName "Quick-Platform" -Files @("tests/windows.test.mjs", "tests/pi-packaging.test.mjs") -TimeoutSeconds $BatchTimeoutSec
    if ($quickRes.Status -ne "PASS") {
        throw "Quick test suite failed with status $($quickRes.Status) (exit code $($quickRes.ExitCode))"
    }
} else {
    Write-Host "==> Full test suite (fresh-process batches with per-batch timeout ${BatchTimeoutSec}s, overall cap ${OverallTimeoutSec}s)"
    $batches = @(
        [PSCustomObject]@{
            Name = "Platform-Packaging"
            Files = @("tests/windows.test.mjs", "tests/pi-packaging.test.mjs", "tests/upstream-checker.test.mjs")
        },
        [PSCustomObject]@{
            Name = "Companion-Core"
            Files = @("tests/dx.test.mjs", "tests/flags.test.mjs", "tests/policy.test.mjs", "tests/setup.test.mjs", "tests/state.test.mjs", "tests/state-lock.test.mjs", "tests/triage.test.mjs")
        },
        [PSCustomObject]@{
            Name = "Jobs-Observation"
            Files = @("tests/jobs.test.mjs", "tests/wait.test.mjs", "tests/observation.test.mjs", "tests/terminal-observation.test.mjs", "tests/streaming.test.mjs")
        },
        [PSCustomObject]@{
            Name = "Modes-Continuation"
            Files = @("tests/modes.test.mjs", "tests/continuation.test.mjs")
        },
        [PSCustomObject]@{
            Name = "Regressions-Recovery"
            Files = @("tests/recovery-regressions.test.mjs", "tests/issue-regressions.test.mjs")
        }
    )

    $overallSw = [System.Diagnostics.Stopwatch]::StartNew()
    $results = [System.Collections.Generic.Dictionary[string, object]]::new()

    foreach ($b in $batches) {
        if ($overallSw.Elapsed.TotalSeconds -gt $OverallTimeoutSec) {
            throw "Overall timeout cap (${OverallTimeoutSec}s) reached before batch [$($b.Name)]"
        }
        $res = Invoke-FreshBatch -BatchName $b.Name -Files $b.Files -TimeoutSeconds $BatchTimeoutSec
        $results[$b.Name] = $res
    }

    $incompleteOrFailed = @($results.Values | Where-Object { $_.Status -ne "PASS" })
    if ($incompleteOrFailed.Count -gt 0) {
        Write-Warning "==> Retrying $($incompleteOrFailed.Count) incomplete/failed batch(es)..."
        foreach ($target in $incompleteOrFailed) {
            if ($overallSw.Elapsed.TotalSeconds -gt $OverallTimeoutSec) {
                throw "Overall timeout cap (${OverallTimeoutSec}s) reached before retrying batch [$($target.Name)]"
            }
            Write-Host "==> Retrying batch [$($target.Name)]"
            $retryRes = Invoke-FreshBatch -BatchName $target.Name -Files $target.Files -TimeoutSeconds $BatchTimeoutSec
            $results[$target.Name] = $retryRes
        }
    }

    $overallSw.Stop()
    $totalSec = [math]::Round($overallSw.Elapsed.TotalSeconds, 1)

    Write-Host "`n================ Batch Summary (Total: ${totalSec}s) ================"
    foreach ($entry in $results.Values) {
        Write-Host ("[{0,-7}] {1,-24} {2,6}s" -f $entry.Status, $entry.Name, $entry.DurationSec)
    }
    Write-Host "================================================================`n"

    $finalFailures = @($results.Values | Where-Object { $_.Status -ne "PASS" })
    if ($finalFailures.Count -gt 0) {
        $failSummary = ($finalFailures | ForEach-Object { "$($_.Name): $($_.Status)" }) -join ", "
        throw "Test suite incomplete or failed in batches: $failSummary"
    }
}

Write-Host "==> Compiling Python tools"
python -m compileall -q tools
if ($LASTEXITCODE -ne 0) {
    throw "Python compile failed with exit code $LASTEXITCODE"
}

Write-Host "==> Checking fork document links"
python tools/check_links.py
if ($LASTEXITCODE -ne 0) {
    throw "Link check failed with exit code $LASTEXITCODE"
}

Write-Host "==> Checking upstream updates"
python tools/check_upstream_updates.py --strict
if ($LASTEXITCODE -ne 0) {
    throw "Upstream check failed with exit code $LASTEXITCODE"
}

Write-Host "WINDOWS DEV CHECK GREEN"
