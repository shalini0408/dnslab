import { Component, OnInit, OnDestroy } from '@angular/core';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit, OnDestroy {
  // State
  dnssecEnabled = false;
  attackRunning = false;
  currentResolver: any = {};
  resolvedIp = '';
  isPoisoned = false;
  isCorrect = false;

  // Display data
  digOutput = '';
  tcpdumpOutput = '';
  logsOutput = '';
  plotData: any = null;

  // UI state
  activeTab: 'website' | 'tcpdump' | 'logs' | 'plots' = 'website';
  loading = false;
  error: string | null = null;

  // Auto-refresh
  private refreshInterval: any;
  private readonly REFRESH_INTERVAL = 2000; // 2 seconds

  constructor(private api: ApiService) { }

  ngOnInit(): void {
    this.loadInitialData();
    this.startAutoRefresh();
  }

  ngOnDestroy(): void {
    if (this.refreshInterval) {
      clearInterval(this.refreshInterval);
    }
  }

  loadInitialData(): void {
    this.loadResolverInfo();
    this.loadDnsResolution();
    this.loadAttackStatus();
  }

  startAutoRefresh(): void {
    this.refreshInterval = setInterval(() => {
      this.loadDnsResolution();
      this.loadAttackStatus();
    }, this.REFRESH_INTERVAL);
  }

  loadResolverInfo(): void {
    this.api.getCurrentResolver().subscribe({
      next: (data) => {
        this.currentResolver = data;
        this.dnssecEnabled = data.dnssec_enabled;
      },
      error: (err) => this.handleError(err)
    });
  }

  loadDnsResolution(): void {
    this.api.resolveDns().subscribe({
      next: (data) => {
        this.resolvedIp = data.resolved_ip;
        this.isPoisoned = data.is_poisoned;
        this.isCorrect = data.is_correct;
      },
      error: (err) => this.handleError(err)
    });
  }

  loadAttackStatus(): void {
    this.api.getAttackStatus().subscribe({
      next: (data) => {
        const resolverType = this.dnssecEnabled ? 'dnssec' : 'plain';
        this.attackRunning = data[resolverType] || false;
      },
      error: (err) => this.handleError(err)
    });
  }

  toggleDnssec(): void {
    this.loading = true;
    this.api.toggleDnssec(!this.dnssecEnabled).subscribe({
      next: (data) => {
        this.dnssecEnabled = data.dnssec_enabled;
        this.currentResolver.resolver_ip = data.resolver_ip;
        this.loadResolverInfo();
        this.loadDnsResolution();
        this.loading = false;
      },
      error: (err) => {
        this.handleError(err);
        this.loading = false;
      }
    });
  }

  startAttack(): void {
    this.loading = true;
    const mode = this.dnssecEnabled ? 'dnssec' : 'plain';
    this.api.startAttack(mode).subscribe({
      next: (data) => {
        this.attackRunning = true;
        this.loadAttackStatus();
        this.loading = false;
      },
      error: (err) => {
        this.handleError(err);
        this.loading = false;
      }
    });
  }

  stopAttack(): void {
    this.loading = true;
    this.api.stopAttack().subscribe({
      next: (data) => {
        this.attackRunning = false;
        this.loadAttackStatus();
        this.loading = false;
      },
      error: (err) => {
        this.handleError(err);
        this.loading = false;
      }
    });
  }

  clearCache(): void {
    this.loading = true;
    const resolver = this.dnssecEnabled ? 'dnssec' : 'plain';
    this.api.clearCache(resolver).subscribe({
      next: (data) => {
        this.loadDnsResolution();
        this.loading = false;
      },
      error: (err) => {
        this.handleError(err);
        this.loading = false;
      }
    });
  }

  loadDig(): void {
    const resolver = this.dnssecEnabled ? 'dnssec' : 'plain';
    this.api.getDig(resolver).subscribe({
      next: (data) => {
        this.digOutput = data.output;
      },
      error: (err) => this.handleError(err)
    });
  }

  loadTcpdump(): void {
    this.loading = true;
    const resolver = this.dnssecEnabled ? 'dnssec' : 'plain';
    this.api.getTcpdump(resolver).subscribe({
      next: (data) => {
        this.tcpdumpOutput = data.tcpdump;
        this.loading = false;
      },
      error: (err) => {
        this.handleError(err);
        this.loading = false;
      }
    });
  }

  loadLogs(): void {
    const resolver = this.dnssecEnabled ? 'dnssec' : 'plain';
    this.api.getLogs(resolver).subscribe({
      next: (data) => {
        this.logsOutput = data.logs;
      },
      error: (err) => this.handleError(err)
    });
  }

  loadPlotData(): void {
    this.api.getPlotData('attack').subscribe({
      next: (data) => {
        this.plotData = data;
      },
      error: (err) => this.handleError(err)
    });
  }

  setActiveTab(tab: 'website' | 'tcpdump' | 'logs' | 'plots'): void {
    this.activeTab = tab;
    if (tab === 'tcpdump') {
      this.loadTcpdump();
    } else if (tab === 'logs') {
      this.loadLogs();
    } else if (tab === 'plots') {
      this.loadPlotData();
    }
  }

  getWebsiteUrl(): string {
    return this.api.getWebsiteProxy();
  }

  handleError(error: any): void {
    this.error = error.message || 'An error occurred';
    console.error('Error:', error);
    setTimeout(() => {
      this.error = null;
    }, 5000);
  }
}

