# 🚀 UPTAX Monitoring Dashboard

## Overview

The UPTAX Monitoring Dashboard is a comprehensive web-based monitoring solution for the multi-agent UPTAX system. It provides real-time insights into system health, agent status, N8N integrations, and infrastructure metrics.

## 🎯 Key Features

### 📊 System Monitoring
- **Real-time Metrics**: CPU, Memory, Disk usage monitoring
- **Docker Status**: Container health and responsiveness
- **Process Monitoring**: System process count and health
- **Resource Alerts**: Automated threshold-based alerting

### 🤖 Agent Management
- **7 MCP Agents**: Complete status overview of all agents
- **Capability Tracking**: Monitor agent capabilities and features
- **Health Checks**: Individual agent health monitoring
- **Context7 Integration**: SSE transport status

### 🔗 Integration Status
- **N8N Platform**: Workflow integration monitoring
- **API Connectivity**: External service health checks
- **Webhook Support**: Real-time webhook monitoring
- **Company APIs**: Omie and Nibo API status

### 📈 Analytics Database
- **Neo4j Analytics**: JSON-based graph database monitoring
- **Relationship Tracking**: Node and relationship metrics
- **Data Freshness**: Real-time data validation

## 🚀 Quick Start

### Option 1: Simple Launcher (Recommended)
```bash
./launch_monitoring.sh
```

### Option 2: Full Startup Check
```bash
python start_monitoring_dashboard.py
```

### Option 3: Direct Server Start
```bash
source venv/bin/activate
python monitoring_dashboard_server.py
```

## 📱 Dashboard Access

Once started, access the dashboard at:
- **Main Dashboard**: http://localhost:8080
- **Health Check**: http://localhost:8080/api/health
- **Data API**: http://localhost:8080/api/data
- **System Actions**: http://localhost:8080/api/actions (POST)

## 📋 System Requirements

### Dependencies
- Python 3.12+
- Virtual environment (venv)
- Required packages: `aiohttp`, `aiofiles`, `psutil`

### Data Files
The dashboard requires these data files to be present:
- `monitoring_data.json` - System metrics
- `graph_analytics.json` - Neo4j analytics data
- `n8n_mcp_discovery.json` - N8N integration data
- `monitoring_config.json` - Configuration settings

### System Resources
- **Memory**: < 90% usage recommended
- **CPU**: < 80% usage recommended
- **Port 8080**: Must be available
- **N8N Service**: Optional but recommended for full functionality

## 🎛️ Dashboard Components

### System Health Card
- Overall system status indicator
- CPU, Memory, Disk usage with progress bars
- Docker connectivity status
- Real-time resource monitoring

### MCP Agents Status
- 7 agents overview (6 active, 1 inactive)
- Individual agent cards with capabilities
- Agent type classification
- Context7 integration status

### N8N Integration
- Connection status to localhost:5678
- API accessibility check
- Workflow count monitoring
- Webhook support verification

### Company APIs
- Omie API status (8 APIs available)
- Nibo API status (needs configuration)
- Company data overview

### Neo4j Analytics
- JSON Graph database status
- Node and relationship counts
- Data population success status

### Performance Metrics
- Process count monitoring
- Network traffic statistics
- Available memory tracking

## 🚨 Alert System

### Alert Levels
- **Critical**: Docker unresponsive, port conflicts
- **Warning**: High memory usage, stale data
- **Info**: Service notifications, recommendations

### Current System Alerts
- ❌ **Critical**: Docker daemon unresponsive
- ⚠️ **Warning**: Memory usage at 84.1%
- ⚠️ **Warning**: N8N credentials endpoint error (405)
- ℹ️ **Info**: Context7-SSE agent inactive

## 🔧 Priority Actions

The dashboard provides actionable buttons for common tasks:

1. **Fix Docker Connectivity** - Resolve Docker timeout issues
2. **Optimize Memory Usage** - Free up system memory
3. **Fix N8N Credentials** - Resolve credentials endpoint
4. **Activate Context7-SSE** - Enable specialized agent
5. **Configure Nibo APIs** - Set up Nibo integrations
6. **Setup Auto-monitoring** - Enable automated monitoring

## 📊 Data Sources

### Real-time Data Integration
- **monitoring_data.json**: System metrics, Docker status, resource usage
- **graph_analytics.json**: Agent relationships, Neo4j data, company info
- **n8n_mcp_discovery.json**: N8N connectivity, agent discovery, templates

### Data Freshness
The dashboard checks data freshness and warns if files are older than 30 minutes:
- Green: Fresh data (< 30 min)
- Yellow: Stale data (30+ min)
- Red: Missing or invalid data

## 🔄 Auto-refresh

- **Dashboard**: Updates every 30 seconds
- **Metrics**: Real-time progress bar animations
- **Timestamp**: Continuous time updates
- **API Polling**: Efficient data retrieval

## 📁 File Structure

```
uptaxdev/
├── monitoring_dashboard.html          # Main dashboard UI
├── monitoring_dashboard_server.py     # Python web server
├── start_monitoring_dashboard.py      # Full startup script
├── launch_monitoring.sh              # Simple launcher
├── monitoring_config.json            # Configuration file
├── monitoring_data.json              # System metrics data
├── graph_analytics.json              # Analytics database
├── n8n_mcp_discovery.json           # N8N integration data
└── logs/
    ├── monitoring_startup.log        # Startup logs
    ├── dashboard.log                 # Server logs
    └── alerts.log                    # Alert logs
```

## 🛠️ Configuration

### monitoring_config.json
Comprehensive configuration file with:
- System thresholds (CPU, Memory, Disk)
- Alert levels and notification channels
- Agent configurations and resource limits
- Monitoring intervals and data retention
- Auto-action settings

### Environment Variables
- `MONITORING_PORT`: Dashboard port (default: 8080)
- `DATA_DIR`: Data directory path
- `LOG_LEVEL`: Logging level (INFO, DEBUG, ERROR)

## 🔒 Security

- **CORS**: Configured for localhost access
- **API Keys**: Optional authentication
- **Rate Limiting**: Configurable request limits
- **SSL**: Optional HTTPS support

## 🐛 Troubleshooting

### Common Issues

1. **Port 8080 in use**
   ```bash
   lsof -ti:8080 | xargs kill -9
   ```

2. **Virtual environment missing**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install aiohttp aiofiles psutil
   ```

3. **Missing data files**
   - Run system monitoring scripts to generate data
   - Check file permissions and paths

4. **Docker connectivity issues**
   ```bash
   docker system prune -f
   sudo systemctl restart docker
   ```

### Log Files
- **Startup logs**: `logs/monitoring_startup.log`
- **Server logs**: `dashboard.log`
- **System logs**: Check system monitoring scripts

## 📈 Performance Optimization

### Cost-Efficient Monitoring
- Uses existing JSON data files (no database required)
- Lightweight web server (minimal resource usage)
- Client-side rendering (reduced server load)
- Efficient data caching

### Resource Management
- Memory usage monitoring
- CPU threshold alerts
- Docker container optimization
- Process count tracking

## 🔮 Future Enhancements

- Historical data charts
- Advanced alerting (email, Slack)
- Mobile-responsive design
- Multi-tenant support
- Integration with external monitoring tools

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review log files in `logs/` directory
3. Verify all required files are present
4. Ensure system resources are adequate

---

**Last Updated**: July 24, 2025  
**Version**: 1.0  
**Compatible with**: UPTAX Multi-Agent Platform v2.0