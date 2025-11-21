import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = 'http://localhost:5000';

  constructor(private http: HttpClient) { }

  // Health check
  health(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`);
  }

  // Resolver management
  getCurrentResolver(): Observable<any> {
    return this.http.get(`${this.apiUrl}/resolver/current`);
  }

  toggleDnssec(enabled: boolean): Observable<any> {
    return this.http.post(`${this.apiUrl}/dnssec/toggle`, { enabled });
  }

  // DNS resolution
  resolveDns(hostname: string = 'www.victim.local'): Observable<any> {
    return this.http.get(`${this.apiUrl}/dns/resolve`, {
      params: new HttpParams().set('hostname', hostname)
    });
  }

  // Attack control
  getAttackStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/attack/status`);
  }

  startAttack(mode?: string): Observable<any> {
    const params = mode ? new HttpParams().set('mode', mode) : undefined;
    return this.http.post(`${this.apiUrl}/attack/start`, {}, { params });
  }

  stopAttack(): Observable<any> {
    return this.http.post(`${this.apiUrl}/attack/stop`, {});
  }

  // Monitoring
  getDig(resolver: string = 'plain'): Observable<any> {
    return this.http.get(`${this.apiUrl}/dig`, {
      params: new HttpParams().set('resolver', resolver)
    });
  }

  getTcpdump(resolver: string = 'plain'): Observable<any> {
    return this.http.get(`${this.apiUrl}/tcpdump`, {
      params: new HttpParams().set('resolver', resolver)
    });
  }

  getLogs(resolver: string = 'plain'): Observable<any> {
    return this.http.get(`${this.apiUrl}/logs`, {
      params: new HttpParams().set('resolver', resolver)
    });
  }

  // Cache management
  clearCache(resolver: string = 'plain'): Observable<any> {
    return this.http.post(`${this.apiUrl}/cache/clear`, {}, {
      params: new HttpParams().set('resolver', resolver)
    });
  }

  // Website proxy
  getWebsiteProxy(hostname: string = 'www.victim.local'): string {
    return `${this.apiUrl}/proxy/website?hostname=${hostname}`;
  }

  // Plot data
  getPlotData(type: string = 'attack'): Observable<any> {
    return this.http.get(`${this.apiUrl}/plot/data`, {
      params: new HttpParams().set('type', type)
    });
  }

  // DNSSEC status
  getDnssecStatus(): Observable<any> {
    return this.http.get(`${this.apiUrl}/dnssec/status`);
  }
}

