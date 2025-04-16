App Structure
Split into logical apps for clarity and maintainability:

/it_asset_register
├── /assets               # Asset models, serials, brands, purchase info
├── /companies            # Multi-company support
├── /users                # Tracks current/previous user and roles
├── /maintenance          # Repair/service history and scheduling
├── /reports              # Aggregated data & replacement guidance
├── /core                 # Shared utils, permissions, base models