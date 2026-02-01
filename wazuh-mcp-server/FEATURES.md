# Wazuh AI Security Agent 功能列表

本项目已验证并集成了以下 Wazuh 安全运营功能：

## 1. Agent 管理 (Agent Management)

*   **列出在线 Agent (get_agents)**
    *   **功能**: 获取当前 Wazuh 环境中所有处于 "active" (在线) 状态的 Agent 列表。
    *   **返回数据**: Agent ID、名称、IP 地址、操作系统版本、注册时间、最后活跃时间。
    *   **验证状态**: ✅ 通过

*   **查询 Agent 详情 (get_agent_info)**
    *   **功能**: 查询指定 Agent ID 的详细配置和状态信息。
    *   **返回数据**: 包含所属组、配置同步状态、系统内核版本等深层信息。
    *   **验证状态**: ✅ 通过

## 2. 漏洞管理 (Vulnerability Management)

*   **查询 Agent 漏洞 (get_vulnerabilities)**
    *   **功能**: 扫描并列出指定 Agent 上存在的已知漏洞 (CVE)。
    *   **依赖**: 需要连接 Wazuh Indexer (端口 9201)。
    *   **返回数据**: 漏洞 CVE ID、严重程度 (Critical/High/Medium/Low)、受影响的软件包名及版本、漏洞描述、发布时间。
    *   **验证状态**: ✅ 通过

## 3. 告警管理 (Alert Management)

*   **查询最近告警 (get_alerts)**
    *   **功能**: 获取最近触发的安全告警，支持按严重等级过滤。
    *   **依赖**: 需要连接 Wazuh Indexer (端口 9201)。
    *   **返回数据**: 告警时间、规则 ID、告警等级、描述、源 IP、Agent 信息。
    *   **验证状态**: ✅ 通过 (已修复)

## 4. 系统监控 (System Monitoring)

*   **获取 Manager 信息 (get_manager_info)**
    *   **功能**: 获取 Wazuh Manager 的基本状态信息。
    *   **返回数据**: Wazuh 版本、编译信息、运行状态。
    *   **验证状态**: ✅ 通过

## 已知限制

*   **安全事件搜索 (search_security_events)**: 当前版本暂不支持通过 `/security/events` 路径搜索，建议使用 `get_alerts` 进行替代查询。

---

**使用提示**:
在 Web UI 中，您可以直接使用自然语言调用这些功能，例如：
*   “帮我看看 Agent 001 有没有高危漏洞”
*   “列出所有在线的主机”
*   “最近有什么等级大于 10 的告警？”
