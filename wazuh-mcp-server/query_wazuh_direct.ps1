$user = "wazuh"
$pass = "fsLvTt05YQZ.4b32hJYTybmEG9.IKWhO"
$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("{0}:{1}" -f $user, $pass)))

# Trust all certificates (for self-signed certs)
add-type @"
    using System.Net;
    using System.Security.Cryptography.X509Certificates;
    public class TrustAllCertsPolicy : ICertificatePolicy {
        public bool CheckValidationResult(
            ServicePoint srvPoint, X509Certificate certificate,
            WebRequest request, int certificateProblem) {
            return true;
        }
    }
"@
[System.Net.ServicePointManager]::CertificatePolicy = New-Object TrustAllCertsPolicy
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.SecurityProtocolType]::Tls12

# 1. Get Token
$tokenUrl = "https://192.168.88.129:55000/security/user/authenticate"
$headers = @{
    Authorization = ("Basic {0}" -f $base64AuthInfo)
}

try {
    $response = Invoke-RestMethod -Uri $tokenUrl -Headers $headers -Method Get
    $token = $response.data.token
    Write-Host "Token obtained successfully."
} catch {
    Write-Host "Error getting token: $_"
    # Print more details if available
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.ReadToEnd()
    }
    exit
}

# 2. Get Online Agents
$agentsUrl = "https://192.168.88.129:55000/agents?status=active"
$headers = @{
    Authorization = ("Bearer {0}" -f $token)
}

Write-Host "`n=== Online Agents ==="
try {
    $agents = Invoke-RestMethod -Uri $agentsUrl -Headers $headers -Method Get
    $agents.data.affected_items | ConvertTo-Json -Depth 5
} catch {
    Write-Host "Error getting agents: $_"
}

# 3. Get Agent 001 Details
$agent001Url = "https://192.168.88.129:55000/agents?agents_list=001"
Write-Host "`n=== Agent 001 Details ==="
try {
    $agent001 = Invoke-RestMethod -Uri $agent001Url -Headers $headers -Method Get
    $agent001.data.affected_items | ConvertTo-Json -Depth 5
} catch {
    Write-Host "Error getting agent 001: $_"
}
