# Dashboard Overview and Navigation Guide

## Introduction
The Narissa Realty CRM Dashboard is your central hub for managing all real estate operations. This guide explains how to navigate and use the dashboard effectively.

## Accessing the Dashboard

### Expected Behavior:
1. Navigate to: https://real-estate-crm-rfzvf.ondigitalocean.app
2. After logging in, you'll be automatically directed to the dashboard
3. The dashboard should load within 2-3 seconds

### Dashboard Layout

The dashboard consists of several key sections:

## 1. Navigation Bar (Top)
- **Logo/Brand**: "Narissa Realty CRM" - clicking returns you to dashboard
- **Search Bar**: Global search for clients, properties, and transactions
- **Notifications**: Bell icon showing recent activities
- **User Menu**: Profile dropdown with settings and logout options

## 2. Sidebar Navigation (Left)
Primary navigation menu with:
- **Dashboard** (Home icon) - Current page
- **Clients** - Manage all client records
- **Properties** - View and manage property listings
- **Transactions** - Track all deals and transactions
- **Calendar** - Schedule appointments and tasks
- **Reports** - Generate business reports
- **AI Assistant** - Chat with AI for help

## 3. Main Content Area

### A. Statistics Cards (Top Row)
Four key metric cards showing:

1. **Total Clients Card**
   - Shows total number of clients in database
   - Click to view all clients
   - Color: Blue gradient
   - Updates in real-time

2. **Active Properties Card**
   - Displays current active listings
   - Click to view property list
   - Color: Green gradient
   - Shows percentage change from last month

3. **Pending Transactions Card**
   - Number of deals in progress
   - Click to view transaction pipeline
   - Color: Orange gradient
   - Critical metric for business flow

4. **Monthly Revenue Card**
   - Total revenue for current month
   - Click for detailed revenue report
   - Color: Purple gradient
   - Shows commission totals

### B. Recent Activities Section (Left Column)
- Shows last 10 system activities
- Each entry includes:
  - Activity type icon
  - Description of action
  - User who performed action
  - Timestamp (relative time)
- Auto-refreshes every 30 seconds

### C. Upcoming Appointments (Right Column)
- Next 7 days of scheduled appointments
- Each appointment shows:
  - Time and date
  - Client name
  - Property address (if applicable)
  - Appointment type
- Click any appointment to view details

### D. Quick Actions Panel
Buttons for common tasks:
- **Add New Client** - Opens client creation form
- **List Property** - Create new property listing
- **Create Transaction** - Start new deal
- **Schedule Showing** - Book property viewing

## 4. AI Assistant Chat Widget (Bottom Right)
- Floating chat bubble
- Click to open AI assistant
- Can help with:
  - Finding information
  - Creating records
  - Answering questions
  - Generating reports

## Navigation Tips

### Keyboard Shortcuts:
- `Ctrl + /` - Focus search bar
- `Ctrl + K` - Open command palette
- `Esc` - Close any open modal
- `?` - Show keyboard shortcuts

### Mobile Navigation:
- Hamburger menu icon appears on mobile
- Swipe right to open sidebar
- Swipe left to close sidebar
- All features accessible on mobile

## Common Tasks from Dashboard

### 1. Quick Search
- Type in search bar at top
- Results appear instantly
- Categories: Clients, Properties, Transactions
- Press Enter to see all results

### 2. View Notifications
- Click bell icon
- Red badge shows unread count
- Mark all as read option
- Settings to customize notifications

### 3. Access Recent Items
- Recent activities are clickable
- Opens relevant record directly
- Can filter by type
- Export activity log option

## Dashboard Refresh Behavior

### Automatic Updates:
- Statistics refresh every 60 seconds
- Activities update every 30 seconds
- No page reload required
- Visual shimmer effect during update

### Manual Refresh:
- Pull down on mobile to refresh
- F5 or Ctrl+R on desktop
- "Refresh" button in top right

## Troubleshooting Dashboard Issues

### Dashboard Not Loading:
1. Check internet connection
2. Clear browser cache
3. Try different browser
4. Contact support if issue persists

### Statistics Not Updating:
1. Check for JavaScript errors (F12)
2. Verify you're logged in
3. Manual refresh may be needed
4. Check system status page

### Missing Features:
1. Verify your user role permissions
2. Some features may be role-restricted
3. Contact administrator for access
4. Check if feature is enabled

## Performance Expectations

### Load Times:
- Initial load: 2-3 seconds
- Subsequent navigation: < 1 second
- Search results: < 500ms
- Report generation: 2-5 seconds

### Browser Requirements:
- Chrome 90+ (recommended)
- Firefox 88+
- Safari 14+
- Edge 90+
- JavaScript must be enabled

## Best Practices

1. **Check Dashboard Daily**
   - Review new activities
   - Check upcoming appointments
   - Monitor key metrics

2. **Use Quick Actions**
   - Faster than navigating menus
   - Reduces clicks needed
   - Improves efficiency

3. **Customize Your View**
   - Arrange widgets as needed
   - Set notification preferences
   - Save frequent searches

4. **Leverage AI Assistant**
   - Ask questions naturally
   - Request help with tasks
   - Get insights from data

## Debug Reference

When debugging dashboard issues, check:

1. **Network Tab (F12)**
   - API calls should return 200 status
   - Check response times
   - Look for failed requests

2. **Console Errors**
   - No red errors should appear
   - Warnings are generally okay
   - Note any repeated errors

3. **Expected API Endpoints**
   - `/api/dashboard/stats` - Statistics
   - `/api/activities/recent` - Activities
   - `/api/appointments/upcoming` - Calendar
   - `/api/search` - Search functionality

This dashboard is designed to give you a complete overview of your real estate business at a glance. Regular use helps you stay on top of all activities and opportunities.