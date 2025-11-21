# Angular Dashboard Setup

This repo only includes instructions for the dashboard. Create the Angular app yourself using the Angular CLI.

## 1. Create Angular App

From `C:\dnslab\frontend`:

```powershell
cd C:\dnslab\frontend
ng new dns-dashboard --routing=false --style=css
cd dns-dashboard
```

Run:

```powershell
ng serve
```

Visit: http://localhost:4200

## 2. Enable HttpClientModule + FormsModule

Edit `src/app/app.module.ts` to import:

```typescript
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
```

Add them in the `imports` array.

## 3. Generate Dashboard + Service

```powershell
ng g component dashboard
ng g service services/api
```

## 4. Copy the Dashboard Files

The dashboard files are already created in this repo. Copy them to your Angular app:

**Files to copy:**
- `src/app/services/api.service.ts` - API service (already created)
- `src/app/dashboard/dashboard.component.ts` - Dashboard component (already created)
- `src/app/dashboard/dashboard.component.html` - Dashboard template (already created)
- `src/app/dashboard/dashboard.component.css` - Dashboard styles (already created)
- `src/app/app.component.html` - App template (already created)

**Or if files are in the repo, just ensure they're in the correct locations.**

## 5. Update app.module.ts

Make sure `app.module.ts` includes:

```typescript
import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';

import { AppComponent } from './app.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { ApiService } from './services/api.service';

@NgModule({
  declarations: [
    AppComponent,
    DashboardComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule
  ],
  providers: [ApiService],
  bootstrap: [AppComponent]
})
export class AppModule { }
```

## 6. Run the Dashboard

```powershell
ng serve
```

Visit: http://localhost:4200

## Features

The dashboard provides:

- ✅ DNSSEC toggle (enable/disable protection)
- ✅ Attack controls (start/stop attack)
- ✅ Real-time DNS resolution status
- ✅ Website iframe (shows real or fake site based on poisoning)
- ✅ Network traffic capture (TCPDUMP)
- ✅ Resolver logs viewer
- ✅ Attack statistics plots
- ✅ Auto-refresh every 2 seconds

