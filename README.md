# national-park-service-mcp-server

# Complete Guide to All 29 National Park Service MCP Tools

This comprehensive reference shows all available tools for accessing National Park Service data, with sample calls and descriptions.

## Basic Park Information Tools

### 1. get_park_tool
**Purpose**: Retrieve basic park information including descriptions, contact info, entrance fees, operating hours, and addresses.

**Sample Call**:
```json
{
  "park_code": "yose",
  "state_code": "CA", 
  "search_term": "Yosemite"
}
```

**Returns**: Complete park details including descriptions, fees, operating hours, contact information, and images.

### 2. get_alerts_tool
**Purpose**: Retrieve current alerts for parks (danger, closure, caution, and information alerts).

**Sample Call**:
```json
{
  "park_code": "yose",
  "state_code": "CA",
  "search_term": "closure"
}
```

**Returns**: Active park alerts with descriptions, categories, and effective dates.

### 3. get_news_releases_tool
**Purpose**: Get press releases and announcements from national parks.

**Sample Call**:
```json
{
  "park_code": "grca",
  "state_code": "AZ",
  "search_term": "wildlife"
}
```

**Returns**: News releases with titles, abstracts, and publication dates.

## Activities and Topics Tools

### 4. get_all_activity_list_tool
**Purpose**: Retrieve all available activity categories (astronomy, hiking, wildlife watching, etc.) across all parks.

**Sample Call**:
```json
{
  "id": null,
  "search_term": "hiking"
}
```

**Returns**: List of all activity types with unique IDs and names.

### 5. get_park_specific_activity_list_tool
**Purpose**: Get activities available at a specific park.

**Sample Call**:
```json
{
  "park_code": "yell",
  "state_code": "WY",
  "search_term": "fishing"
}
```

**Returns**: Activities offered at the specified park.

### 6. get_topics_tool
**Purpose**: Retrieve topic categories (American revolution, music, women's history, etc.) for all parks.

**Sample Call**:
```json
{
  "id": null,
  "search_term": "history"
}
```

**Returns**: All available topic categories with IDs and descriptions.

### 7. get_park_specific_topics_tool
**Purpose**: Get topics relating to a specific national park.

**Sample Call**:
```json
{
  "park_code": "gett",
  "state_code": "PA",
  "search_term": "civil war"
}
```

**Returns**: Topics specific to the requested park.

## Facilities and Amenities Tools

### 8. get_all_amenities_list_tool
**Purpose**: Retrieve all amenity types (restrooms, fire pits, picnic areas, etc.) available across parks.

**Sample Call**:
```json
{
  "id": null,
  "search_term": "restroom"
}
```

**Returns**: Complete list of amenity types with IDs.

### 9. get_amenities_parkplaces_tool
**Purpose**: Get "places" within parks that have different amenities.

**Sample Call**:
```json
{
  "park_code": "yose",
  "state_code": "CA",
  "search_term": "picnic"
}
```

**Returns**: Locations within parks that offer specific amenities.

### 10. get_campgrounds_tool
**Purpose**: Retrieve campground information including addresses, contacts, descriptions, and hours.

**Sample Call**:
```json
{
  "park_code": "yell",
  "state_code": "WY",
  "search_term": "reservation"
}
```

**Returns**: Detailed campground information with facilities and booking details.

### 11. get_visitor_centers_tool
**Purpose**: Get information about visitor centers including descriptions, directions, and operating hours.

**Sample Call**:
```json
{
  "park_code": "grca",
  "state_code": "AZ",
  "search_term": "museum"
}
```

**Returns**: Visitor center details with services and hours.

### 12. get_park_specific_visitorcenter_with_amenities_tool
**Purpose**: Retrieve visitor centers within specific parks that have different amenities.

**Sample Call**:
```json
{
  "park_code": "yell",
  "state_code": "WY",
  "search_term": "accessibility"
}
```

**Returns**: Visitor centers with detailed amenity information.

### 13. get_places_tool
**Purpose**: Get information about places within parks (visitor centers, museums, facilities).

**Sample Call**:
```json
{
  "park_code": "yose",
  "state_code": "CA",
  "search_term": "museum"
}
```

**Returns**: Various places and facilities within parks.

### 14. get_parkinglots_tool
**Purpose**: Retrieve parking lot information created by parks and NPS entities.

**Sample Call**:
```json
{
  "park_code": "grca",
  "state_code": "AZ",
  "search_term": "shuttle"
}
```

**Returns**: Parking facility details and availability.

## Educational and Event Tools

### 15. get_events_tool
**Purpose**: Retrieve park events including dates, descriptions, and times.

**Sample Call**:
```json
{
  "park_code": "yell",
  "state_code": "WY",
  "search_term": "ranger program"
}
```

**Returns**: Scheduled events with dates, times, and descriptions.

### 16. get_lesson_plans_tool
**Purpose**: Get educational lesson plans created by parks and NPS entities.

**Sample Call**:
```json
{
  "park_code": "yose",
  "state_code": "CA",
  "search_term": "geology"
}
```

**Returns**: Educational materials and lesson plans.

### 17. get_articles_tool
**Purpose**: Retrieve articles created by national parks and other NPS entities.

**Sample Call**:
```json
{
  "park_code": "yell",
  "state_code": "WY",
  "search_term": "wildlife"
}
```

**Returns**: Informational articles and content.

### 18. get_people_tool
**Purpose**: Get information about people associated with parks (rangers, scientists).

**Sample Call**:
```json
{
  "park_code": "yose",
  "state_code": "CA",
  "search_term": "naturalist"
}
```

**Returns**: Information about park personnel and historical figures.

## Tours and Activities Tools

### 19. get_tours_tool
**Purpose**: Retrieve tours with stops at special places, campgrounds, and visitor centers.

**Sample Call**:
```json
{
  "park_code": "grca",
  "state_code": "AZ",
  "search_term": "guided"
}
```

**Returns**: Available tours with itineraries and descriptions.

### 20. get_thingstodo_tool
**Purpose**: Get suggested activities recommended by and for specific parks.

**Sample Call**:
```json
{
  "park_code": "yell",
  "state_code": "WY",
  "search_term": "geyser"
}
```

**Returns**: Recommended activities and attractions.

### 21. get_passport_stamp_locations_tool
**Purpose**: Get locations that have national park passport stamps.

**Sample Call**:
```json
{
  "park_code": "yose",
  "state_code": "CA",
  "search_term": "stamp"
}
```

**Returns**: Locations where visitors can get passport stamps.

## Fees and Passes Tools

### 22. get_feespasses_tool
**Purpose**: Retrieve information about fees and passes for parks.

**Sample Call**:
```json
{
  "park_code": "yell",
  "state_code": "WY",
  "search_term": "annual pass"
}
```

**Returns**: Fee schedules and pass information.

## Multimedia and Content Tools

### 23. get_multimedia_galleries_tool
**Purpose**: Retrieve photo and media galleries created by parks.

**Sample Call**:
```json
{
  "park_code": "yose",
  "state_code": "CA",
  "search_term": "waterfall"
}
```

**Returns**: Media galleries with photos and descriptions.

### 24. get_multimedia_galleries_assets_tool
**Purpose**: Get gallery assets by unique asset ID or gallery ID.

**Sample Call**:
```json
{
  "park_code": "yell",
  "state_code": "WY",
  "search_term": "asset_id"
}
```

**Returns**: Specific media assets and files.

### 25. get_audios_tool
**Purpose**: Retrieve metadata for audio files created by parks.

**Sample Call**:
```json
{
  "park_code": "grca",
  "state_code": "AZ",
  "search_term": "tour"
}
```

**Returns**: Audio content metadata and access information.

### 26. get_videos_tool
**Purpose**: Get metadata for video files created by parks.

**Sample Call**:
```json
{
  "park_code": "yell",
  "state_code": "WY",
  "search_term": "documentary"
}
```

**Returns**: Video content metadata and links.

### 27. get_webcams_tool
**Purpose**: Retrieve information about park webcams including descriptions and URLs.

**Sample Call**:
```json
{
  "park_code": "yell",
  "state_code": "WY",
  "search_term": "live"
}
```

**Returns**: Webcam locations and streaming URLs.

## Transportation and Infrastructure Tools

### 28. get_roadevents_tool
**Purpose**: Get information about road events by park and event type (incident or workzone).

**Sample Call**:
```json
{
  "park_code": "yell",
  "state_code": "WY",
  "search_term": "construction"
}
```

**Returns**: Current road conditions and construction information.

### 29. get_map_metadata_tool
**Purpose**: Retrieve geometry boundaries for parks specified by site code.

**Sample Call**:
```json
{
  "park_code": "yose",
  "state_code": "CA",
  "search_term": "boundary"
}
```

**Returns**: Geographic boundary data and mapping information.

## Parameter Guidelines

### Common Parameters:
- **park_code**: 4-letter park identifier (e.g., "yose" for Yosemite, "yell" for Yellowstone)
- **state_code**: 2-letter state abbreviation (e.g., "CA", "WY", "AZ")
- **search_term**: Keywords to filter results (can be empty string "" for all results)

### Popular Park Codes:
- **yose**: Yosemite National Park (CA)
- **yell**: Yellowstone National Park (WY/MT/ID)
- **grca**: Grand Canyon National Park (AZ)
- **grsm**: Great Smoky Mountains National Park (TN/NC)
- **zion**: Zion National Park (UT)
- **acad**: Acadia National Park (ME)
- **romo**: Rocky Mountain National Park (CO)
- **olym**: Olympic National Park (WA)

### Tips for Effective Use:
1. Use specific search terms to narrow results
2. Leave search_term as "" to get all available data
3. Some tools work with general queries (id: null) for system-wide information
4. Park codes are case-insensitive but typically lowercase
5. State codes should match the primary state where the park is located

This comprehensive toolkit provides access to virtually all public information about National Parks, from basic visitor information to detailed multimedia content and real-time conditions.