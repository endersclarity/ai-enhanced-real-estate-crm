# Property Management Guide

## Overview
The Property Management module allows you to list, track, and manage all property listings in your portfolio. This guide covers creating listings, managing property details, and tracking property status through the sales cycle.

## Accessing Property Management

### Navigation:
1. Click **"Properties"** in the left sidebar
2. Direct URL: `/properties`
3. Keyboard shortcut: `Ctrl + 2`

### Initial View Components:
- Property grid/list view toggle
- Search and filter options
- Sort controls
- Add Property button

## Property List View

### View Options:

#### Grid View (Default):
- Property cards with photos
- 3 columns on desktop, 1 on mobile
- Key details visible at glance
- Hover effects for actions

#### List View:
- Detailed table format
- More information visible
- Easier for bulk operations
- Better for data export

### Property Card Information:
Each property card displays:
- **Primary Photo** (or placeholder)
- **Address** (street, city, state)
- **Price** (formatted with commas)
- **Key Stats**: Beds, Baths, Sq Ft
- **Status Badge**: Active/Pending/Sold
- **MLS Number**
- **Days on Market**
- **Quick Actions**: View, Edit, Share

### Search and Filters:

#### Search Box Features:
- Search by address
- Search by MLS number
- Search by city or ZIP
- Partial matching supported
- Results update live

#### Filter Options:

**Property Type**:
- Single Family
- Condo
- Townhouse
- Multi-Family
- Land
- Commercial

**Status Filter**:
- Active (on market)
- Pending (under contract)
- Sold (closed)
- Coming Soon
- Withdrawn
- Expired

**Price Range**:
- Minimum price slider
- Maximum price slider
- Quick ranges: Under $500k, $500k-$1M, Over $1M

**Location Filter**:
- City dropdown
- ZIP code
- Neighborhood
- School district

**Features Filter**:
- Bedrooms (1-5+)
- Bathrooms (1-4+)
- Garage (0-3+)
- Pool (Yes/No)
- View (Yes/No)

## Adding a New Property

### Step 1: Access Property Form
Click **"Add Property"** button or navigate to `/properties/new`

### Step 2: Complete Property Information

#### Basic Information Tab:

**Address Section**:
1. **Street Address*** - Full street address
2. **Unit/Apt** - For condos/apartments
3. **City*** - Required field
4. **State*** - Dropdown selection
5. **ZIP Code*** - 5 or 9 digits
6. **County** - Auto-populated usually
7. **Neighborhood** - Optional

**Listing Details**:
1. **MLS Number*** - Unique identifier
2. **Listing Price*** - Current asking price
3. **Original Price** - If price reduced
4. **Property Type*** - Dropdown selection
5. **Status*** - Active by default
6. **Listing Date** - Defaults to today
7. **Expiration Date** - Listing agreement end

#### Property Details Tab:

**Structure Information**:
1. **Year Built** - 4-digit year
2. **Square Footage** - Total living area
3. **Lot Size** - In sq ft or acres
4. **Stories** - Number of levels
5. **Construction Type** - Frame, Brick, etc.
6. **Foundation** - Slab, Crawl, Basement
7. **Roof Type** - Shingle, Tile, Metal

**Room Information**:
1. **Bedrooms** - Total count
2. **Bathrooms** - Full + Half
3. **Kitchen** - Updated/Original
4. **Living Areas** - Count
5. **Dining Room** - Formal/Informal
6. **Office/Den** - Yes/No
7. **Bonus Room** - Yes/No

**Features**:
- **Garage**: Spaces and type
- **Pool**: Yes/No, Type
- **Fireplace**: Count
- **HVAC**: Type and age
- **Flooring**: Types
- **Appliances**: Included items

#### Marketing Tab:

**Listing Description**:
- Headline (100 characters)
- Full description (5000 characters)
- Features bullet points
- Neighborhood highlights
- School information

**Virtual Tour**:
- Video URL
- 3D tour link
- Virtual staging links

**Open House**:
- Schedule multiple dates
- Time slots
- Special instructions
- RSVP tracking

#### Photos Tab:

**Photo Upload**:
1. Drag and drop interface
2. Multiple file selection
3. Automatic optimization
4. Order management
5. Caption addition

**Photo Requirements**:
- Minimum 1 photo required
- Maximum 50 photos
- Preferred size: 1920x1080
- Accepted formats: JPG, PNG
- Max file size: 10MB each

**Photo Categories**:
- Exterior (front, back, sides)
- Interior (rooms)
- Features (pool, view)
- Neighborhood
- Floorplans

#### Financial Tab:

**Pricing Information**:
1. **List Price** - Current asking
2. **Price per Sq Ft** - Auto-calculated
3. **Original List Price**
4. **Previous Sale Price**
5. **Previous Sale Date**
6. **Tax Assessed Value**
7. **Annual Property Tax**

**HOA Information**:
1. **HOA Fee** - Monthly amount
2. **HOA Frequency** - Monthly/Quarterly/Annual
3. **HOA Includes** - Amenities covered
4. **Special Assessments**

**Commission**:
1. **Listing Side** - Percentage
2. **Buying Side** - Percentage
3. **Total Commission** - Auto-calculated
4. **Bonus Commission** - If applicable

### Step 3: Save and Publish
1. Click **"Save as Draft"** to save without publishing
2. Click **"Save and Publish"** to make active
3. System validates all required fields
4. Success message and redirect to property detail

## Property Detail View

### Accessing Property Details:
1. Click property card in grid
2. Click address in list view
3. Direct URL: `/properties/{id}`

### Detail Page Layout:

#### Header Section:
- Full address as title
- Status badge (color-coded)
- Price (large, prominent)
- Days on market counter
- Action buttons: Edit, Share, Print

#### Photo Gallery:
- Large primary photo
- Thumbnail navigation
- Fullscreen option
- Slideshow mode
- Download options

#### Key Information Cards:

**Property Overview**:
- Type and style
- Year built
- Square footage
- Lot size
- Beds/Baths count
- Garage info

**Listing Information**:
- MLS number
- Listed date
- Price history
- Status changes
- Listing agent
- Office information

**Financial Details**:
- Current price
- Price per sq ft
- Property taxes
- HOA fees
- Estimated payment
- Commission breakdown

#### Tabbed Content:

**Description Tab**:
- Full marketing description
- Features list
- Neighborhood info
- School details
- Walk scores

**Details Tab**:
- Room-by-room breakdown
- Appliances included
- Recent updates
- Systems and ages
- Additional features

**Map Tab**:
- Interactive map
- Property boundaries
- Nearby amenities
- School zones
- Commute times

**History Tab**:
- Price changes
- Status changes
- Showing activity
- Offer history
- View statistics

**Documents Tab**:
- Listing agreement
- Disclosures
- Floor plans
- Survey
- HOA documents

## Managing Property Status

### Status Workflow:

1. **Coming Soon** → **Active**
   - Pre-marketing phase
   - Generate interest
   - No showings yet

2. **Active** → **Pending**
   - Accepting offers
   - Showings active
   - Full marketing

3. **Pending** → **Sold**
   - Under contract
   - Contingencies active
   - Limited showings

4. **Special Statuses**:
   - **Withdrawn**: Temporarily off market
   - **Expired**: Listing period ended
   - **Cancelled**: Listing terminated

### Changing Status:
1. Open property edit form
2. Select new status from dropdown
3. Add status change note
4. System logs change with timestamp
5. Notifications sent as configured

## Property Marketing Tools

### Listing Syndication:
- Automatic MLS upload
- Zillow/Trulia/Realtor.com
- Social media scheduling
- Email campaigns
- Website integration

### Marketing Materials:
1. **Flyer Generation**:
   - Professional templates
   - Auto-populate from listing
   - PDF download
   - Print-ready format

2. **Social Media Posts**:
   - Pre-written captions
   - Optimized images
   - Platform-specific formats
   - Schedule posting

3. **Email Campaigns**:
   - New listing announcement
   - Price reduction alerts
   - Open house invitations
   - Just sold notices

### Virtual Marketing:
- 3D tour integration
- Video walkthrough
- Virtual staging
- Drone footage
- Interactive floor plans

## Property Analytics

### Performance Metrics:
- **Views**: Online and in-person
- **Saves**: Favorited count
- **Inquiries**: Leads generated
- **Showings**: Scheduled and completed
- **Offers**: Received count

### Analytics Dashboard:
- Daily/weekly view trends
- Source tracking
- Demographic insights
- Competitive analysis
- Price positioning

## Bulk Property Operations

### Bulk Actions:
1. **Select Properties**:
   - Checkbox selection
   - Select all option
   - Filter then select

2. **Available Actions**:
   - Export to CSV
   - Bulk status change
   - Assign to agent
   - Update pricing
   - Generate reports

### Import Properties:
1. Download template CSV
2. Fill property information
3. Upload completed file
4. System validates data
5. Review and confirm import

## Integration Features

### MLS Integration:
- Automatic updates
- Two-way sync
- Compliance checking
- Auto-population
- Error reporting

### Calendar Integration:
- Showing schedule
- Open house events
- Task reminders
- Team coordination
- Client appointments

### Transaction Integration:
- Create transaction from listing
- Link offers to property
- Track through closing
- Commission calculation
- Document management

## Best Practices

### Listing Optimization:
1. **Complete all fields** - Better search ranking
2. **High-quality photos** - Minimum 15-20
3. **Compelling description** - Highlight unique features
4. **Accurate pricing** - Use comparative analysis
5. **Regular updates** - Keep information current

### Photo Guidelines:
1. **Bright, natural lighting**
2. **Wide-angle shots**
3. **Decluttered spaces**
4. **Highlight best features**
5. **Professional quality**

### Description Writing:
1. **Start with highlights**
2. **Use descriptive language**
3. **Include neighborhood benefits**
4. **Mention recent updates**
5. **Call to action**

## Troubleshooting

### Common Issues:

**Photos Not Uploading**:
- Check file size (< 10MB)
- Verify format (JPG/PNG)
- Clear browser cache
- Try different browser

**MLS Sync Errors**:
- Verify required fields
- Check MLS credentials
- Review compliance rules
- Contact MLS support

**Search Not Finding Property**:
- Check status filter
- Verify address spelling
- Clear all filters
- Try MLS number

**Map Not Displaying**:
- Verify address accuracy
- Check internet connection
- Enable location services
- Refresh page

## Performance Expectations

### Load Times:
- Property grid: < 3 seconds
- Individual property: < 2 seconds
- Photo gallery: < 4 seconds
- Search results: < 1 second

### Data Limits:
- 1000 active listings
- 50 photos per property
- 10MB per photo
- 5000 character descriptions

This comprehensive property management system ensures your listings are professionally presented and efficiently managed throughout the sales cycle.